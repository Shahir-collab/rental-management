"""Rent collection route — serves /rent page."""
from fastapi import APIRouter, Request
from database import SessionLocal
from models import RentCharge
from sqlalchemy import func

router = APIRouter(prefix="/rent", tags=["rent"])


@router.get("/")
def rent_collection(request: Request):
    db = SessionLocal()
    try:
        charges_raw = db.query(RentCharge).order_by(RentCharge.id).all()

        charges = []
        for c in charges_raw:
            charges.append({
                "id": c.id,
                "month": c.month or "",
                "unit": c.unit_no or "",
                "tenant_id": c.tenant_id or "",
                "tenant": c.tenant_name or "",
                "rent": c.monthly_rent or 0,
                "arrears": c.prev_arrears or 0,
                "other": c.other_charges or 0,
                "late_fee": c.late_fee or 0,
                "total_due": c.total_due or 0,
                "paid": c.amount_paid or 0,
                "balance": c.balance or 0,
                "date": c.payment_date,
                "method": c.payment_method or "",
                "receipt": c.receipt_no or "",
                "status": c.payment_status or "Pending",
                "late_days": c.late_days,
                "remarks": c.remarks or "",
            })

        total_due = sum(c["total_due"] for c in charges)
        total_paid = sum(c["paid"] for c in charges)
        outstanding = sum(c["balance"] for c in charges)
        collection_pct = (total_paid / total_due * 100) if total_due > 0 else 0.0

        summary = {
            "total_due": total_due,
            "total_paid": total_paid,
            "outstanding": outstanding,
            "collection_pct": round(collection_pct, 1),
        }

        return request.app.state.templates.TemplateResponse(request, "rent_collection.html", {
            "request": request,
            "charges": charges,
            "summary": summary,
        })
    finally:
        db.close()
