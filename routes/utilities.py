"""Utilities route — serves /utilities page."""
from fastapi import APIRouter, Request
from database import SessionLocal
from models import UtilityCharge

router = APIRouter(prefix="/utilities", tags=["utilities"])


@router.get("/")
def list_utilities(request: Request):
    db = SessionLocal()
    try:
        charges_raw = db.query(UtilityCharge).order_by(UtilityCharge.month.desc()).all()

        utilities = []
        for c in charges_raw:
            utilities.append({
                "id": c.id,
                "unit_no": c.unit_id or "",
                "tenant_name": c.tenant_name or "",
                "month": c.month or "",
                "prev_reading": c.prev_reading,
                "curr_reading": c.curr_reading,
                "units_consumed": c.units_consumed,
                "elec_rate": c.elec_rate,
                "elec_amount": c.elec_amount or 0,
                "water": c.water_charge or 0,
                "maintenance": c.maintenance_charge or 0,
                "parking": c.parking_charge or 0,
                "other": c.other_charge or 0,
                "total": c.total_charges or 0,
                "paid": c.amount_paid or 0,
                "balance": c.balance or 0,
                "date": c.payment_date,
                "method": c.payment_method or "",
            })

        return request.app.state.templates.TemplateResponse(request, "utilities.html", {
            "request": request,
            "utilities": utilities,
        })
    finally:
        db.close()
