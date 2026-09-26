"""
Import enriched contract data from the 8 detailed rental agreements.
Run AFTER the base import_excel.py has populated the database.
This script UPDATES existing records with enriched fields.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date
from database import SessionLocal, init_db
from models import Tenant, Unit, Residence, RentalAgreement, Deposit, Witness, AgreementWitness

LANDLORD = "Abdul Nazar"
LANDLORD_FATHER = "Kabeer"
LANDLORD_ADDRESS = "Muzammil House, Vanoor Maruthakkad, Kattussery Amsom Desom, Alathur P.O., Alathur Taluk"

CONTRACTS = [
    {   # RENT 1
        "tenant_name": "Rafeek",
        "father_name": "Abdulla",
        "full_address": "Palliparambu House, Vengannur, Puthiyankam Amsom Desom, Alathur P.O., Alathur Taluk",
        "unit_no": "15/1592 B",
        "monthly_rent": 3200,
        "security_deposit": 18000,
        "agreement_date": date(2026, 9, 7),
        "start_date": date(2026, 9, 7),
        "lease_months": 11,
        "stamp_paper_value": 200,
        "stamp_paper_grn": "KL026481504202627E",
        "permitted_use": "Electronic Repair Shop",
        "late_interest_rate": 12.0,
        "notice_period": None,
        "rent_due_date": "7th of every month",
        "tenant_type": "Commercial",
        "signature_status": "Both signed",
        "witnesses": [{"name": "Suresh", "role": "Witness 1"}],
    },
    {   # RENT 2
        "tenant_name": "Anfal. H",
        "father_name": "Haneefa",
        "full_address": "Raula Manzil, Malyamparambu, Vengannur, Alathur Grama Panchayat, Alathur P.O., Puthiyankam Amsom, Alathur Village, Alathur Taluk",
        "unit_no": "15/1595",
        "monthly_rent": 3000,
        "security_deposit": 20000,
        "agreement_date": date(2026, 5, 7),
        "start_date": date(2026, 5, 7),
        "lease_months": 11,
        "stamp_paper_value": 500,
        "stamp_paper_grn": "N 713029",
        "permitted_use": "AH Minerals India LLP Office",
        "late_interest_rate": 12.0,
        "notice_period": "1 month",
        "rent_due_date": "7th of every month",
        "tenant_type": "Commercial",
        "signature_status": "Both signed",
        "witnesses": [
            {"name": "Unknown (Anfi House)", "address": "Anfi House, Melikaparamb, Alathur", "role": "Witness 1"},
            {"name": "Bilal A", "address": "Malikaparamb, Alathur", "role": "Witness 2"},
        ],
    },
    {   # RENT 3
        "tenant_name": "Swaminathan",
        "father_name": "Chinnan",
        "full_address": "Moramparambu House, Vanoor, Kattussery Amsom Desom, Alathur P.O., Alathur Taluk",
        "unit_no": "15/1592 A",
        "monthly_rent": 3200,
        "security_deposit": 20000,
        "agreement_date": date(2026, 9, 7),
        "start_date": date(2026, 9, 7),
        "lease_months": 11,
        "stamp_paper_value": 200,
        "stamp_paper_grn": "KL026481062202627E",
        "permitted_use": "Ironing / Pressing Shop",
        "late_interest_rate": 12.0,
        "notice_period": None,
        "rent_due_date": "7th of every month",
        "tenant_type": "Commercial",
        "signature_status": "Both signed",
        "witnesses": [{"name": "Suresh", "address": "Moramparambu, Vanoor", "role": "Witness 1 (S/o Swaminathan)"}],
    },
    {   # RENT 4
        "tenant_name": "V. Rajesh",
        "father_name": "Vellappan",
        "full_address": "Kuruppath House, Tarur Amsom Desom, Tarur P.O., Alathur Taluk",
        "unit_no": "15/1595",
        "monthly_rent": 18000,
        "security_deposit": 75000,
        "agreement_date": date(2026, 9, 7),
        "start_date": date(2026, 9, 7),
        "lease_months": 11,
        "stamp_paper_value": 200,
        "stamp_paper_grn": "KL026481985202627E",
        "permitted_use": "Textile / Clothing Shop",
        "late_interest_rate": 12.0,
        "notice_period": None,
        "rent_due_date": "7th of every month",
        "tenant_type": "Commercial",
        "signature_status": "Both signed, witnesses blank",
        "witnesses": [],
    },
    {   # RENT 5
        "tenant_name": "V. Rajesh",
        "father_name": "Vellappan",
        "full_address": "Kuruppath House, Tarur Amsom Desom, Tarur P.O., Alathur Taluk",
        "unit_no": "15/1591",
        "monthly_rent": 7000,
        "security_deposit": 50000,
        "agreement_date": date(2026, 9, 7),
        "start_date": date(2026, 9, 7),
        "lease_months": 11,
        "stamp_paper_value": 200,
        "stamp_paper_grn": "KL026482294202627E",
        "permitted_use": "Stitching Shop / Tailoring Unit",
        "late_interest_rate": 12.0,
        "notice_period": None,
        "rent_due_date": "7th of every month",
        "tenant_type": "Commercial",
        "signature_status": "Both signed, witnesses blank",
        "witnesses": [],
    },
    {   # RENT 6
        "tenant_name": "Shafna",
        "father_name": "W/o Noushad",
        "full_address": "Zainaba Colony, Alathur Amsom Desom, Alathur P.O., Alathur Taluk",
        "unit_no": "15/1597",
        "monthly_rent": 4200,
        "security_deposit": 10000,
        "agreement_date": date(2026, 9, 7),
        "start_date": date(2026, 9, 7),
        "lease_months": 11,
        "stamp_paper_value": 200,
        "stamp_paper_grn": "KL026482576202627E",
        "permitted_use": "Residential / Living",
        "late_interest_rate": 12.0,
        "notice_period": None,
        "rent_due_date": "7th of every month",
        "tenant_type": "Residential",
        "signature_status": "Both signed",
        "witnesses": [{"name": "Shafir S", "role": "Witness 1"}],
    },
    {   # RENT 7 + RENT 8 (duplicate, merged)
        "tenant_name": "Shalini A. M.",
        "father_name": "Abdul Khadar",
        "full_address": "Muchikkulam House, Nechur P.O., Tarur Amsom Desom, Alathur Taluk",
        "unit_no": "15/1592 C",
        "monthly_rent": 3000,
        "security_deposit": 20000,
        "agreement_date": date(2026, 9, 7),
        "start_date": date(2026, 9, 7),
        "lease_months": 11,
        "stamp_paper_value": 200,
        "stamp_paper_grn": "KL026480684202627E",
        "permitted_use": "Ayurveda Clinic",
        "late_interest_rate": 12.0,
        "notice_period": None,
        "rent_due_date": "7th of every month",
        "tenant_type": "Commercial",
        "signature_status": "Tenant name written but no handwritten signature; witnesses blank. Duplicate copy (RENT 8) has landlord signature also missing.",
        "witnesses": [],
    },
]


def find_tenant(db, name):
    """Find tenant by name (fuzzy match)."""
    name_lower = name.lower().strip()
    for t in db.query(Tenant).all():
        t_lower = t.name.lower().strip()
        # Exact or partial match
        if t_lower == name_lower:
            return t
        if name_lower in t_lower or t_lower in name_lower:
            return t
        # Handle "V. Rajesh" vs "Rajesh" or "Anfal. H" vs "Anfal H."
        clean_name = name_lower.replace(".", "").replace(" ", "")
        clean_t = t_lower.replace(".", "").replace(" ", "")
        if clean_name == clean_t or clean_name in clean_t or clean_t in clean_name:
            return t
    return None


def find_unit(db, unit_no):
    """Find unit by unit number."""
    return db.query(Unit).filter(Unit.unit_no == unit_no).first()


def find_agreement_by_contract(db, tenant_id, unit_no, start_date):
    """Find existing agreement matching this contract."""
    return db.query(RentalAgreement).filter(
        RentalAgreement.tenant_id == tenant_id,
        RentalAgreement.unit_no == unit_no,
        RentalAgreement.start_date == start_date
    ).first()


def get_next_id(db, model_class, prefix):
    """Get next available ID for a model."""
    existing = db.query(model_class).all()
    max_num = 0
    for obj in existing:
        try:
            num = int(obj.id.split("-")[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            pass
    return f"{prefix}-{max_num + 1:03d}"


def run_enrichment():
    db = SessionLocal()
    try:
        stats = {"tenants_updated": 0, "agreements_updated": 0, "agreements_created": 0,
                 "deposits_updated": 0, "deposits_created": 0, "witnesses_created": 0,
                 "units_created": 0, "residences_created": 0}

        for i, c in enumerate(CONTRACTS, 1):
            print(f"\n--- Processing RENT {i}: {c['tenant_name']} @ {c['unit_no']} ---")

            # 1. Find or create tenant
            tenant = find_tenant(db, c["tenant_name"])
            if not tenant:
                tid = get_next_id(db, Tenant, "TEN")
                tenant = Tenant(
                    id=tid, name=c["tenant_name"],
                    father_name=c["father_name"],
                    full_address=c["full_address"],
                    tenant_type=c["tenant_type"],
                    current_unit=c["unit_no"],
                    current_status="Active",
                )
                db.add(tenant)
                db.flush()
                print(f"  Created tenant: {tid} ({c['tenant_name']})")
            else:
                # Update enriched fields
                tenant.father_name = c["father_name"]
                tenant.full_address = c["full_address"]
                if c["tenant_type"]:
                    tenant.tenant_type = c["tenant_type"]
                stats["tenants_updated"] += 1
                print(f"  Updated tenant: {tenant.id} ({tenant.name}) - added father_name, full_address")

            # 2. Find or create unit
            unit = find_unit(db, c["unit_no"])
            if not unit:
                uid = get_next_id(db, Unit, "UNIT")
                unit = Unit(
                    id=uid, unit_no=c["unit_no"],
                    description=f"{c['permitted_use']} unit",
                    occupancy_status="Occupied",
                )
                db.add(unit)
                db.flush()
                stats["units_created"] += 1
                print(f"  Created unit: {uid} ({c['unit_no']})")

            # 3. Find or create agreement
            from dateutil.relativedelta import relativedelta
            end_date = c["start_date"] + relativedelta(months=c["lease_months"])

            agr = find_agreement_by_contract(db, tenant.id, c["unit_no"], c["start_date"])
            if agr:
                # Update with enriched fields
                agr.agreement_date = c["agreement_date"]
                agr.lease_months = c["lease_months"]
                agr.stamp_paper_value = c["stamp_paper_value"]
                agr.stamp_paper_grn = c["stamp_paper_grn"]
                agr.permitted_use = c["permitted_use"]
                agr.late_interest_rate = c["late_interest_rate"]
                agr.notice_period = c["notice_period"]
                agr.rent_due_date = c["rent_due_date"]
                agr.signature_status = c["signature_status"]
                agr.landlord = LANDLORD
                agr.monthly_rent = c["monthly_rent"]
                agr.security_deposit = c["security_deposit"]
                agr.end_date = end_date
                stats["agreements_updated"] += 1
                print(f"  Updated agreement: {agr.id} with enriched fields")
            else:
                agr_id = get_next_id(db, RentalAgreement, "AGR")
                # Find or create matching residence
                res = db.query(Residence).filter(
                    Residence.tenant_id == tenant.id,
                    Residence.unit_no == c["unit_no"],
                ).order_by(Residence.move_in.desc()).first()

                if not res:
                    res_id = get_next_id(db, Residence, "RES")
                    res = Residence(
                        id=res_id, tenant_id=tenant.id,
                        unit_id=unit.id if unit else None,
                        unit_no=c["unit_no"],
                        period_no=1,
                        move_in=c["start_date"],
                        monthly_rent=c["monthly_rent"],
                        security_deposit=c["security_deposit"],
                        source_file="Updated contracts",
                    )
                    db.add(res)
                    db.flush()
                    stats["residences_created"] += 1
                    print(f"  Created residence: {res_id}")

                agr = RentalAgreement(
                    id=agr_id, tenant_id=tenant.id,
                    residence_id=res.id, unit_no=c["unit_no"],
                    landlord=LANDLORD,
                    agreement_date=c["agreement_date"],
                    start_date=c["start_date"],
                    end_date=end_date,
                    lease_months=c["lease_months"],
                    monthly_rent=c["monthly_rent"],
                    security_deposit=c["security_deposit"],
                    rent_due_date=c["rent_due_date"],
                    permitted_use=c["permitted_use"],
                    stamp_paper_value=c["stamp_paper_value"],
                    stamp_paper_grn=c["stamp_paper_grn"],
                    late_interest_rate=c["late_interest_rate"],
                    notice_period=c["notice_period"],
                    signature_status=c["signature_status"],
                    agreement_status="Active",
                    source_file="Updated contracts",
                )
                db.add(agr)
                db.flush()
                stats["agreements_created"] += 1
                print(f"  Created agreement: {agr_id}")

            # 4. Update or create deposit
            dep = db.query(Deposit).filter(
                Deposit.tenant_id == tenant.id,
                Deposit.unit_no == c["unit_no"],
            ).first()
            if dep:
                dep.security_deposit = c["security_deposit"]
                dep.deposit_date = c["agreement_date"]
                dep.status = "Held"
                stats["deposits_updated"] += 1
                print(f"  Updated deposit: {dep.id}")
            else:
                dep_id = get_next_id(db, Deposit, "DEP")
                dep = Deposit(
                    id=dep_id, tenant_id=tenant.id,
                    residence_id=agr.residence_id,
                    unit_no=c["unit_no"],
                    security_deposit=c["security_deposit"],
                    deposit_date=c["agreement_date"],
                    status="Held",
                    source_file="Updated contracts",
                )
                db.add(dep)
                db.flush()
                stats["deposits_created"] += 1
                print(f"  Created deposit: {dep_id}")

            # 5. Create witnesses
            for w in c.get("witnesses", []):
                # Check if witness already exists by name
                existing_w = db.query(Witness).filter(Witness.name == w["name"]).first()
                if not existing_w:
                    wid = get_next_id(db, Witness, "WIT")
                    existing_w = Witness(
                        id=wid, name=w["name"],
                        address=w.get("address", ""),
                    )
                    db.add(existing_w)
                    db.flush()
                    stats["witnesses_created"] += 1
                    print(f"  Created witness: {wid} ({w['name']})")

                # Link witness to agreement
                existing_link = db.query(AgreementWitness).filter(
                    AgreementWitness.agreement_id == agr.id,
                    AgreementWitness.witness_id == existing_w.id,
                ).first()
                if not existing_link:
                    aw = AgreementWitness(
                        agreement_id=agr.id, witness_id=existing_w.id,
                        tenant_id=tenant.id, tenant_name=tenant.name,
                        role=w.get("role", "Witness"),
                        date=c["agreement_date"],
                        source_file="Updated contracts",
                    )
                    db.add(aw)

        db.commit()

        print("\n" + "=" * 60)
        print("ENRICHMENT COMPLETE")
        for k, v in stats.items():
            print(f"  {k}: {v}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_enrichment()
