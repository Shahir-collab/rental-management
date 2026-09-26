"""Agreements route — serves /agreements page."""
from fastapi import APIRouter, Request
from database import SessionLocal
from models import RentalAgreement, AgreementWitness, Witness
from datetime import date

router = APIRouter(prefix="/agreements", tags=["agreements"])


@router.get("/")
def list_agreements(request: Request, status: str = None):
    db = SessionLocal()
    try:
        query = db.query(RentalAgreement)
        if status == "Active":
            query = query.filter(RentalAgreement.agreement_status == "Active")
        elif status == "Expired":
            query = query.filter(RentalAgreement.agreement_status == "Expired")
        agreements_raw = query.order_by(RentalAgreement.start_date.desc()).all()

        agreements = []
        for a in agreements_raw:
            tenant_name = ""
            if a.residence and a.residence.tenant:
                tenant_name = a.residence.tenant.name
            days = a.days_remaining
            expiring_soon = a.is_expiring_soon

            agreements.append({
                "id": a.id,
                "tenant_id": a.tenant_id,
                "tenant_name": tenant_name,
                "unit_no": a.unit_no or "",
                "landlord": a.landlord or "",
                "start_date": a.start_date,
                "end_date": a.end_date,
                "monthly_rent": a.monthly_rent or 0,
                "rent": a.monthly_rent or 0,
                "security_deposit": a.security_deposit or 0,
                "deposit": a.security_deposit or 0,
                "rent_due_date": a.rent_due_date or "",
                "renewal_status": a.renewal_status or "",
                "status": a.agreement_status or "Expired",
                "days_remaining": days,
                "expiring_soon": expiring_soon,
                "source": a.source_file or "",
                "remarks": a.remarks or "",
            })

        return request.app.state.templates.TemplateResponse("agreements.html", {
            "request": request,
            "agreements": agreements,
            "current_status": status or "All",
        })
    finally:
        db.close()


@router.get("/{agr_id}")
def agreement_detail(request: Request, agr_id: str):
    db = SessionLocal()
    try:
        a = db.query(RentalAgreement).filter(RentalAgreement.id == agr_id).first()
        if not a:
            return request.app.state.templates.TemplateResponse("agreement_detail.html", {
                "request": request, "agreement": None, "witnesses": []
            })

        tenant_name = ""
        if a.residence and a.residence.tenant:
            tenant_name = a.residence.tenant.name

        agreement = {
            "id": a.id,
            "tenant_id": a.tenant_id,
            "tenant_name": tenant_name,
            "unit_no": a.unit_no or "",
            "landlord": a.landlord or "",
            "agreement_date": a.agreement_date,
            "start_date": a.start_date,
            "end_date": a.end_date,
            "lease_months": a.lease_months,
            "rent": a.monthly_rent or 0,
            "deposit": a.security_deposit or 0,
            "rent_due_date": a.rent_due_date or "",
            "permitted_use": a.permitted_use or "",
            "stamp_paper_value": a.stamp_paper_value,
            "stamp_paper_grn": a.stamp_paper_grn or "",
            "late_interest_rate": a.late_interest_rate,
            "notice_period": a.notice_period or "",
            "signature_status": a.signature_status or "",
            "renewal_status": a.renewal_status or "",
            "status": a.agreement_status or "Expired",
            "days_remaining": a.days_remaining,
            "source": a.source_file or "",
            "remarks": a.remarks or "",
        }

        # Get witnesses
        aw_links = db.query(AgreementWitness).filter(
            AgreementWitness.agreement_id == agr_id
        ).all()
        witnesses = []
        for aw in aw_links:
            w = db.query(Witness).filter(Witness.id == aw.witness_id).first()
            if w:
                witnesses.append({
                    "id": w.id,
                    "name": w.name,
                    "address": w.address or "",
                    "role": aw.role or "",
                    "remarks": aw.remarks or "",
                })

        return request.app.state.templates.TemplateResponse("agreement_detail.html", {
            "request": request,
            "agreement": agreement,
            "witnesses": witnesses,
        })
    finally:
        db.close()
