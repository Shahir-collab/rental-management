"""Units route — serves /units page."""
from fastapi import APIRouter, Request
from database import SessionLocal
from models import Unit, Residence, RentalAgreement

router = APIRouter(prefix="/units", tags=["units"])


@router.get("/")
def list_units(request: Request):
    db = SessionLocal()
    try:
        units_raw = db.query(Unit).order_by(Unit.unit_no).all()

        units = []
        for u in units_raw:
            # Find active residence for this unit
            active_res = db.query(Residence).filter(
                Residence.unit_id == u.id,
                Residence.move_out == None
            ).first()

            tenant_name = ""
            tenant_type = ""
            monthly_rent = 0
            if active_res and active_res.tenant:
                tenant_name = active_res.tenant.name
                tenant_type = active_res.tenant.tenant_type or ""
                monthly_rent = active_res.monthly_rent or 0

            units.append({
                "id": u.id,
                "unit_no": u.unit_no,
                "floor": u.floor or "",
                "description": u.description or "",
                "occupancy_status": u.occupancy_status or "Vacant",
                "tenant_name": tenant_name,
                "tenant_type": tenant_type,
                "monthly_rent": monthly_rent,
            })

        return request.app.state.templates.TemplateResponse("units.html", {
            "request": request,
            "units": units,
        })
    finally:
        db.close()


@router.get("/{unit_id}")
def unit_detail(request: Request, unit_id: str):
    db = SessionLocal()
    try:
        unit = db.query(Unit).filter(Unit.id == unit_id).first()
        if not unit:
            return request.app.state.templates.TemplateResponse("unit_detail.html", {
                "request": request, "unit": None, "current_residence": None, "history": []
            })

        residences_raw = db.query(Residence).filter(
            Residence.unit_id == unit_id
        ).order_by(Residence.move_in.desc()).all()

        current_residence = None
        history = []
        for r in residences_raw:
            agr = db.query(RentalAgreement).filter_by(residence_id=r.id).first()
            entry = {
                "id": r.id,
                "tenant_name": r.tenant.name if r.tenant else "",
                "tenant_id": r.tenant_id,
                "tenant_type": r.tenant.tenant_type if r.tenant else "",
                "agreement_status": agr.agreement_status if agr else "None",
                "period_no": r.period_no,
                "move_in": r.move_in,
                "move_out": r.move_out,
                "duration_months": r.duration_months,
                "duration": f"{r.duration_months} mo",
                "monthly_rent": r.monthly_rent or 0,
                "rent": r.monthly_rent or 0,
                "is_active": r.move_out is None,
                "status": "Active" if r.move_out is None else "Past",
                "reason_leaving": r.reason_leaving or "",
            }
            history.append(entry)
            if r.move_out is None:
                current_residence = entry

        unit_data = {
            "id": unit.id,
            "unit_no": unit.unit_no,
            "floor": unit.floor or "",
            "description": unit.description or "",
            "occupancy_status": unit.occupancy_status or "Vacant",
        }

        return request.app.state.templates.TemplateResponse("unit_detail.html", {
            "request": request,
            "unit": unit_data,
            "current_residence": current_residence,
            "history": history,
        })
    finally:
        db.close()
