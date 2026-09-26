"""Search route — serves /search page."""
from fastapi import APIRouter, Request
from database import SessionLocal
from models import Tenant, Unit, RentalAgreement, Witness, AgreementWitness

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
def search(request: Request, q: str = ""):
    db = SessionLocal()
    try:
        tenant_results = []
        unit_results = []
        agreement_results = []
        witness_results = []

        if q and len(q.strip()) > 0:
            term = f"%{q.strip()}%"

            # Search tenants
            tenants = db.query(Tenant).filter(
                Tenant.name.ilike(term) |
                Tenant.id.ilike(term) |
                Tenant.permanent_address.ilike(term) |
                Tenant.current_unit.ilike(term)
            ).all()
            for t in tenants:
                tenant_results.append({
                    "id": t.id, "name": t.name,
                    "tenant_type": t.tenant_type or "Unknown",
                    "current_unit": t.current_unit or "",
                    "current_status": t.current_status or "",
                })

            # Search units
            units = db.query(Unit).filter(
                Unit.unit_no.ilike(term) |
                Unit.description.ilike(term)
            ).all()
            for u in units:
                unit_results.append({
                    "id": u.id, "unit_no": u.unit_no,
                    "description": u.description or "",
                    "occupancy_status": u.occupancy_status or "Vacant",
                })

            # Search agreements
            agrs = db.query(RentalAgreement).filter(
                RentalAgreement.id.ilike(term) |
                RentalAgreement.unit_no.ilike(term) |
                RentalAgreement.landlord.ilike(term)
            ).all()
            for a in agrs:
                tenant_name = ""
                if a.residence and a.residence.tenant:
                    tenant_name = a.residence.tenant.name
                agreement_results.append({
                    "id": a.id, "unit_no": a.unit_no or "",
                    "tenant_name": tenant_name,
                    "status": a.agreement_status or "Expired",
                })

            # Search witnesses
            wits = db.query(Witness).filter(Witness.name.ilike(term)).all()
            for w in wits:
                link = db.query(AgreementWitness).filter(
                    AgreementWitness.witness_id == w.id
                ).first()
                witness_results.append({
                    "id": w.id, "name": w.name,
                    "role": link.role if link else "",
                    "agreement_id": link.agreement_id if link else "",
                })

        return request.app.state.templates.TemplateResponse(request, "search_results.html", {
            "request": request,
            "query": q,
            "tenant_results": tenant_results,
            "unit_results": unit_results,
            "agreement_results": agreement_results,
            "witness_results": witness_results,
        })
    finally:
        db.close()
