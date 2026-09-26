"""Tenants route — serves /tenants and /tenants/{id} pages."""
from fastapi import APIRouter, Request
from database import SessionLocal
from models import Tenant, Residence, RentalAgreement, Deposit, AgreementWitness, Witness, RentCharge

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/")
def list_tenants(request: Request, status: str = None, type: str = None):
    db = SessionLocal()
    try:
        query = db.query(Tenant)
        if status:
            query = query.filter(Tenant.current_status == status)
        if type:
            query = query.filter(Tenant.tenant_type == type)
        tenants_raw = query.order_by(Tenant.name).all()

        tenants = []
        for t in tenants_raw:
            res_count = db.query(Residence).filter(Residence.tenant_id == t.id).count()
            agr_count = db.query(RentalAgreement).filter(RentalAgreement.tenant_id == t.id).count()
            tenants.append({
                "id": t.id,
                "name": t.name,
                "tenant_type": t.tenant_type or "",
                "current_unit": t.current_unit or "",
                "current_status": t.current_status or "Inactive",
                "notes": t.notes or "",
                "residence_count": res_count,
                "agreement_count": agr_count,
            })

        return request.app.state.templates.TemplateResponse("tenants.html", {
            "request": request,
            "tenants": tenants,
        })
    finally:
        db.close()


@router.get("/{tenant_id}")
def tenant_profile(request: Request, tenant_id: str):
    db = SessionLocal()
    try:
        tenant_raw = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant_raw:
            return request.app.state.templates.TemplateResponse("tenant_profile.html", {
                "request": request, "tenant": None, "residences": [],
                "agreements": [], "agreement_witnesses": [], "deposits": [],
                "stats": {}
            })

        # Serialize tenant
        tenant = {
            "id": tenant_raw.id,
            "name": tenant_raw.name,
            "phone": tenant_raw.phone or "",
            "alt_phone": tenant_raw.alt_phone or "",
            "email": tenant_raw.email or "",
            "permanent_address": tenant_raw.permanent_address or "",
            "current_address": tenant_raw.current_address or "",
            "tenant_type": tenant_raw.tenant_type or "",
            "current_unit": tenant_raw.current_unit or "",
            "current_status": tenant_raw.current_status or "Inactive",
            "notes": tenant_raw.notes or "",
        }

        # Get residences
        residences_raw = db.query(Residence).filter(
            Residence.tenant_id == tenant_id
        ).order_by(Residence.move_in.desc()).all()

        residences = []
        total_months = 0
        total_rent_due = 0
        for r in residences_raw:
            months = r.duration_months
            total_months += months
            rent_due = round(months) * (r.monthly_rent or 0)
            total_rent_due += rent_due
            residences.append({
                "id": r.id,
                "unit_no": r.unit_no or "",
                "floor": r.floor or "",
                "period_no": r.period_no,
                "move_in": r.move_in,
                "move_out": r.move_out,
                "duration_months": months,
                "monthly_rent": r.monthly_rent or 0,
                "security_deposit": r.security_deposit or 0,
                "is_active": r.move_out is None,
                "reason_leaving": r.reason_leaving or "",
            })

        # Get agreements
        agreements_raw = db.query(RentalAgreement).filter(
            RentalAgreement.tenant_id == tenant_id
        ).order_by(RentalAgreement.start_date.desc()).all()

        agreements = []
        for a in agreements_raw:
            agreements.append({
                "id": a.id,
                "unit_no": a.unit_no or "",
                "start_date": a.start_date,
                "end_date": a.end_date,
                "monthly_rent": a.monthly_rent or 0,
                "rent": a.monthly_rent or 0,
                "security_deposit": a.security_deposit or 0,
                "deposit": a.security_deposit or 0,
                "status": a.agreement_status or "Expired",
                "landlord": a.landlord or "",
                "days_remaining": a.days_remaining,
                "remarks": a.remarks or "",
            })

        # Get witnesses linked to this tenant's agreements
        agr_ids = [a["id"] for a in agreements]
        aw_links = db.query(AgreementWitness).filter(
            AgreementWitness.agreement_id.in_(agr_ids)
        ).all() if agr_ids else []

        witnesses = []
        for aw in aw_links:
            w = db.query(Witness).filter(Witness.id == aw.witness_id).first()
            if w:
                witnesses.append({
                    "witness_name": w.name,
                    "role": aw.role or "",
                    "agreement_id": aw.agreement_id,
                    "address": w.address or "",
                })

        # Get deposits
        deposits_raw = db.query(Deposit).filter(
            Deposit.tenant_id == tenant_id
        ).all()
        deposits = []
        total_deposits = 0
        for d in deposits_raw:
            total_deposits += d.security_deposit or 0
            deposits.append({
                "id": d.id,
                "unit_no": d.unit_no or "",
                "amount": d.security_deposit or 0,
                "date": d.deposit_date,
                "status": d.status or "Unknown",
                "remaining": d.remaining,
                "remarks": d.remarks or "",
            })

        # Get rent charges for this tenant
        charges = db.query(RentCharge).filter(
            RentCharge.tenant_id == tenant_id
        ).all()
        total_paid = sum(c.amount_paid or 0 for c in charges)
        total_outstanding = total_rent_due - total_paid

        stats = {
            "total_stays": len(residences),
            "total_months": round(total_months, 1),
            "total_rent_due": total_rent_due,
            "total_paid": total_paid,
            "total_outstanding": max(0, total_outstanding),
            "total_deposits": total_deposits,
        }

        return request.app.state.templates.TemplateResponse("tenant_profile.html", {
            "request": request,
            "tenant": tenant,
            "residences": residences,
            "agreements": agreements,
            "witnesses": witnesses,
            "deposits": deposits,
            "stats": stats,
        })
    finally:
        db.close()
