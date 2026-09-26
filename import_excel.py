"""Import data from Rental_Management_System.xlsx into the SQLite database."""
import os, json, sys
from datetime import date, datetime
import openpyxl
from sqlalchemy.orm import Session

# Add parent to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, init_db, Base
from models import (
    Unit, Tenant, Residence, RentalAgreement, Witness,
    AgreementWitness, Deposit, RentCharge, UtilityCharge,
    BuildingExpense, DataIssue, SourceRecord
)

EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "Rental_Management_System.xlsx")

def _val(cell):
    """Return cell value, converting datetime to date if needed."""
    v = cell
    if isinstance(v, datetime):
        return v.date()
    return v

def _str(v):
    """Safely convert to string or None."""
    if v is None:
        return None
    return str(v).strip() if str(v).strip() else None

def _float(v):
    """Safely convert to float or 0."""
    if v is None:
        return 0.0
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0

def _int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None

def _map_id(old_prefix, new_prefix, num_str):
    """Map old IDs like T01 -> TEN-001."""
    try:
        n = int(num_str)
    except (ValueError, TypeError):
        n = 0
    return f"{new_prefix}{n:03d}"

def import_units(ws, db: Session):
    """Import from 'Units & Building' sheet."""
    print("  Importing Units...")
    for row in range(2, ws.max_row + 1):
        old_id = _str(ws.cell(row, 1).value)
        if not old_id:
            continue
        num = int(old_id.replace("U", ""))
        unit = Unit(
            id=f"UNIT-{num:03d}",
            unit_no=_str(ws.cell(row, 2).value) or "",
            floor=_str(ws.cell(row, 3).value),
            description=_str(ws.cell(row, 4).value),
            occupancy_status=_str(ws.cell(row, 9).value) or "Vacant",
        )
        db.merge(unit)
    db.commit()
    print(f"    -> {db.query(Unit).count()} units")

def import_tenants(ws, db: Session):
    """Import from 'Tenant Master' sheet."""
    print("  Importing Tenants...")
    for row in range(2, ws.max_row + 1):
        old_id = _str(ws.cell(row, 1).value)
        if not old_id:
            continue
        num = int(old_id.replace("T", ""))
        tenant = Tenant(
            id=f"TEN-{num:03d}",
            name=_str(ws.cell(row, 2).value) or "",
            phone=_str(ws.cell(row, 3).value),
            alt_phone=_str(ws.cell(row, 4).value),
            email=_str(ws.cell(row, 5).value),
            permanent_address=_str(ws.cell(row, 6).value),
            current_address=_str(ws.cell(row, 7).value),
            id_proof_type=_str(ws.cell(row, 8).value),
            id_proof_submitted=_str(ws.cell(row, 9).value),
            id_proof_ref=_str(ws.cell(row, 10).value),
            tenant_type=_str(ws.cell(row, 11).value),
            num_occupants=_int(ws.cell(row, 12).value),
            emergency_contact=_str(ws.cell(row, 13).value),
            emergency_phone=_str(ws.cell(row, 14).value),
            current_unit=_str(ws.cell(row, 15).value),
            current_status=_str(ws.cell(row, 20).value) or "Inactive",
            notes=_str(ws.cell(row, 21).value),
        )
        db.merge(tenant)
    db.commit()
    print(f"    -> {db.query(Tenant).count()} tenants")

def _unit_id_lookup(db, unit_no):
    """Find a unit ID by unit_no (partial match)."""
    if not unit_no:
        return None
    u = db.query(Unit).filter(Unit.unit_no == unit_no).first()
    if u:
        return u.id
    # Try partial match
    for unit in db.query(Unit).all():
        if unit.unit_no in unit_no or unit_no in unit.unit_no:
            return unit.id
    return None

def import_residences(ws, db: Session):
    """Import from 'Residence History' sheet."""
    print("  Importing Residences...")
    for row in range(2, ws.max_row + 1):
        old_id = _str(ws.cell(row, 1).value)
        if not old_id:
            continue
        num = int(old_id.replace("RES", ""))
        tenant_old = _str(ws.cell(row, 2).value)
        tenant_num = int(tenant_old.replace("T", ""))
        unit_no = _str(ws.cell(row, 4).value) or ""

        res = Residence(
            id=f"RES-{num:03d}",
            tenant_id=f"TEN-{tenant_num:03d}",
            unit_id=_unit_id_lookup(db, unit_no),
            unit_no=unit_no,
            floor=_str(ws.cell(row, 5).value),
            period_no=_int(ws.cell(row, 6).value) or 1,
            move_in=_val(ws.cell(row, 7).value),
            move_out=_val(ws.cell(row, 8).value),
            monthly_rent=_float(ws.cell(row, 12).value),
            security_deposit=_float(ws.cell(row, 13).value),
            reason_leaving=_str(ws.cell(row, 20).value),
            source_file=_str(ws.cell(row, 21).value),
            remarks=_str(ws.cell(row, 22).value),
        )
        db.merge(res)
    db.commit()
    print(f"    -> {db.query(Residence).count()} residences")

def import_agreements(ws, db: Session):
    """Import from 'Rental Agreements' sheet."""
    print("  Importing Agreements...")
    for row in range(2, ws.max_row + 1):
        old_id = _str(ws.cell(row, 1).value)
        if not old_id:
            continue
        num = int(old_id.replace("AGR", ""))
        tenant_old = _str(ws.cell(row, 2).value)
        tenant_num = int(tenant_old.replace("T", ""))
        res_old = _str(ws.cell(row, 5).value)
        res_num = int(res_old.replace("RES", ""))

        agr = RentalAgreement(
            id=f"AGR-{num:03d}",
            tenant_id=f"TEN-{tenant_num:03d}",
            residence_id=f"RES-{res_num:03d}",
            unit_no=_str(ws.cell(row, 4).value),
            landlord=_str(ws.cell(row, 6).value),
            start_date=_val(ws.cell(row, 7).value),
            end_date=_val(ws.cell(row, 8).value),
            monthly_rent=_float(ws.cell(row, 9).value),
            security_deposit=_float(ws.cell(row, 10).value),
            advance_rent=_float(ws.cell(row, 11).value) if ws.cell(row, 11).value else None,
            rent_due_date=_str(ws.cell(row, 12).value),
            renewal_status=_str(ws.cell(row, 14).value),
            agreement_status=_str(ws.cell(row, 15).value) or "Expired",
            doc_reference=_str(ws.cell(row, 16).value),
            source_file=_str(ws.cell(row, 17).value),
            remarks=_str(ws.cell(row, 18).value),
        )
        db.merge(agr)
    db.commit()
    print(f"    -> {db.query(RentalAgreement).count()} agreements")

def import_witnesses(ws, db: Session):
    """Import from 'Witness Records' sheet."""
    print("  Importing Witnesses...")
    for row in range(2, ws.max_row + 1):
        old_id = _str(ws.cell(row, 1).value)
        if not old_id:
            continue
        num = int(old_id.replace("W", ""))
        witness_name = _str(ws.cell(row, 6).value) or ""

        # Create/update Witness record
        wit = Witness(
            id=f"WIT-{num:03d}",
            name=witness_name,
            phone=_str(ws.cell(row, 7).value),
            address=_str(ws.cell(row, 8).value),
            id_type=_str(ws.cell(row, 9).value),
            id_ref=_str(ws.cell(row, 10).value),
        )
        db.merge(wit)

        # Create AgreementWitness link
        agr_old = _str(ws.cell(row, 5).value)
        if agr_old:
            agr_num = int(agr_old.replace("AGR", ""))
            aw = AgreementWitness(
                agreement_id=f"AGR-{agr_num:03d}",
                witness_id=f"WIT-{num:03d}",
                tenant_id=_str(ws.cell(row, 2).value),
                tenant_name=_str(ws.cell(row, 3).value),
                residence_id=_str(ws.cell(row, 4).value),
                role=_str(ws.cell(row, 11).value),
                date=_val(ws.cell(row, 13).value),
                source_file=_str(ws.cell(row, 14).value),
                remarks=_str(ws.cell(row, 15).value),
            )
            db.add(aw)
    db.commit()
    print(f"    -> {db.query(Witness).count()} witnesses, {db.query(AgreementWitness).count()} links")

def import_deposits(ws, db: Session):
    """Import from 'Deposits & Advances' sheet."""
    print("  Importing Deposits...")
    for row in range(2, ws.max_row + 1):
        old_id = _str(ws.cell(row, 1).value)
        if not old_id:
            continue
        num = int(old_id.replace("DEP", ""))
        tenant_old = _str(ws.cell(row, 2).value)
        tenant_num = int(tenant_old.replace("T", ""))
        res_old = _str(ws.cell(row, 5).value)
        res_num = int(res_old.replace("RES", ""))

        dep = Deposit(
            id=f"DEP-{num:03d}",
            tenant_id=f"TEN-{tenant_num:03d}",
            residence_id=f"RES-{res_num:03d}",
            unit_no=_str(ws.cell(row, 4).value),
            security_deposit=_float(ws.cell(row, 6).value),
            deposit_date=_val(ws.cell(row, 7).value),
            advance_rent=_float(ws.cell(row, 8).value) if ws.cell(row, 8).value else None,
            advance_date=_val(ws.cell(row, 9).value),
            adjusted=_str(ws.cell(row, 10).value),
            refund_date=_val(ws.cell(row, 11).value),
            refund_amount=_float(ws.cell(row, 12).value) if ws.cell(row, 12).value else None,
            remaining=_float(ws.cell(row, 13).value) if ws.cell(row, 13).value else None,
            status=_str(ws.cell(row, 14).value) or "Unknown",
            source_file=_str(ws.cell(row, 15).value),
            remarks=_str(ws.cell(row, 16).value),
        )
        db.merge(dep)
    db.commit()
    print(f"    -> {db.query(Deposit).count()} deposits")

def import_rent_charges(ws, db: Session):
    """Import from 'Rent Collection' sheet."""
    print("  Importing Rent Charges...")
    for row in range(2, ws.max_row + 1):
        old_id = _str(ws.cell(row, 1).value)
        if not old_id:
            continue
        tenant_old = _str(ws.cell(row, 4).value)
        tenant_num = int(tenant_old.replace("T", ""))
        res_old = _str(ws.cell(row, 6).value)
        res_num = int(res_old.replace("RES", ""))

        num = int(old_id.replace("PAY", ""))
        charge = RentCharge(
            id=f"CHG-{num:03d}",
            residence_id=f"RES-{res_num:03d}",
            month=_str(ws.cell(row, 2).value),
            unit_no=_str(ws.cell(row, 3).value),
            tenant_id=f"TEN-{tenant_num:03d}",
            tenant_name=_str(ws.cell(row, 5).value),
            monthly_rent=_float(ws.cell(row, 7).value),
            prev_arrears=_float(ws.cell(row, 8).value),
            other_charges=_float(ws.cell(row, 9).value),
            late_fee=_float(ws.cell(row, 10).value),
            total_due=_float(ws.cell(row, 11).value),
            amount_paid=_float(ws.cell(row, 12).value) if ws.cell(row, 12).value else 0,
            balance=_float(ws.cell(row, 13).value),
            payment_date=_val(ws.cell(row, 14).value),
            payment_method=_str(ws.cell(row, 15).value),
            receipt_no=_str(ws.cell(row, 16).value),
            payment_status=_str(ws.cell(row, 17).value) or "Pending",
            late_days=_int(ws.cell(row, 18).value),
            source_file=_str(ws.cell(row, 19).value),
            original_ref=_str(ws.cell(row, 20).value),
            remarks=_str(ws.cell(row, 21).value),
        )
        db.merge(charge)
    db.commit()
    print(f"    -> {db.query(RentCharge).count()} rent charges")

def import_data_issues(ws, db: Session):
    """Import from 'Data Review & Issues' sheet."""
    print("  Importing Data Issues...")
    for row in range(2, ws.max_row + 1):
        old_id = _str(ws.cell(row, 1).value)
        if not old_id:
            continue
        num = int(old_id.replace("ISS", ""))
        issue = DataIssue(
            id=f"ISS-{num:03d}",
            category=_str(ws.cell(row, 2).value),
            description=_str(ws.cell(row, 3).value),
            source_file=_str(ws.cell(row, 4).value),
            source_record=_str(ws.cell(row, 5).value),
            tenant_id=_str(ws.cell(row, 6).value),
            unit_no=_str(ws.cell(row, 7).value),
            severity=_str(ws.cell(row, 8).value) or "Medium",
            suggested_action=_str(ws.cell(row, 9).value),
            status=_str(ws.cell(row, 10).value) or "Open",
            notes=_str(ws.cell(row, 11).value),
        )
        db.merge(issue)
    db.commit()
    print(f"    -> {db.query(DataIssue).count()} issues")

def import_source_records(wb, db: Session):
    """Store raw source data for traceability."""
    print("  Storing source records...")
    count = 0
    for sheet_name in ["RAW_RENT_DATA", "RAW_WITNESS_DATA"]:
        if sheet_name not in wb.sheetnames:
            continue
        ws = wb[sheet_name]
        headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
        for row in range(2, ws.max_row + 1):
            row_data = {}
            for c in range(1, ws.max_column + 1):
                val = ws.cell(row, c).value
                if isinstance(val, (datetime, date)):
                    val = val.isoformat()
                row_data[headers[c-1] or f"col_{c}"] = val
            sr = SourceRecord(
                sheet_name=sheet_name,
                row_number=row,
                original_data=json.dumps(row_data, ensure_ascii=False, default=str),
            )
            db.add(sr)
            count += 1
    db.commit()
    print(f"    -> {count} source records")


def run_import(excel_path=None):
    """Main import function."""
    path = excel_path or EXCEL_PATH
    path = os.path.abspath(path)
    print(f"\n{'='*60}")
    print(f"IMPORTING: {path}")
    print(f"{'='*60}\n")

    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}")
        return False

    # Reset and create tables
    Base.metadata.drop_all(bind=engine)
    init_db()
    print("Database tables created.\n")

    wb = openpyxl.load_workbook(path, data_only=True)
    print(f"Sheets found: {wb.sheetnames}\n")

    db = SessionLocal()
    try:
        import_units(wb["Units & Building"], db)
        import_tenants(wb["Tenant Master"], db)
        import_residences(wb["Residence History"], db)
        import_agreements(wb["Rental Agreements"], db)
        import_witnesses(wb["Witness Records"], db)
        import_deposits(wb["Deposits & Advances"], db)
        import_rent_charges(wb["Rent Collection"], db)
        import_data_issues(wb["Data Review & Issues"], db)
        import_source_records(wb, db)

        print(f"\n{'='*60}")
        print("IMPORT COMPLETE")
        print(f"{'='*60}")
        print(f"  Units:       {db.query(Unit).count()}")
        print(f"  Tenants:     {db.query(Tenant).count()}")
        print(f"  Residences:  {db.query(Residence).count()}")
        print(f"  Agreements:  {db.query(RentalAgreement).count()}")
        print(f"  Witnesses:   {db.query(Witness).count()}")
        print(f"  Deposits:    {db.query(Deposit).count()}")
        print(f"  Rent Charges:{db.query(RentCharge).count()}")
        print(f"  Data Issues: {db.query(DataIssue).count()}")
        print(f"  Source Recs: {db.query(SourceRecord).count()}")
        return True
    except Exception as e:
        db.rollback()
        print(f"ERROR during import: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    run_import()
