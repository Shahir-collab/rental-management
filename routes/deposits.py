"""Deposits route — serves /deposits page."""
from fastapi import APIRouter, Request
from database import SessionLocal
from models import Deposit

router = APIRouter(prefix="/deposits", tags=["deposits"])


@router.get("/")
def list_deposits(request: Request):
    db = SessionLocal()
    try:
        deposits_raw = db.query(Deposit).order_by(Deposit.deposit_date.desc()).all()

        deposits = []
        for d in deposits_raw:
            deposits.append({
                "id": d.id,
                "tenant_id": d.tenant_id,
                "tenant": d.tenant.name if d.tenant else "",
                "unit": d.unit_no or "",
                "amount": d.security_deposit or 0,
                "date": d.deposit_date,
                "advance": d.advance_rent,
                "adjusted": d.adjusted or "",
                "refund_amount": d.refund_amount,
                "remaining": d.remaining if d.remaining is not None else d.security_deposit,
                "status": d.status or "Unknown",
                "remarks": d.remarks or "",
                "source": d.source_file or "",
            })

        held = sum(d["amount"] for d in deposits if d["status"] == "Held")
        adjusted = sum(d["amount"] for d in deposits if d["status"] == "Adjusted")
        unknown = sum(d["amount"] for d in deposits if d["status"] == "Unknown")
        total = sum(d["amount"] for d in deposits)

        totals = {"total": total, "held": held, "adjusted": adjusted, "unknown": unknown}

        return request.app.state.templates.TemplateResponse(request, "deposits.html", {
            "request": request,
            "deposits": deposits,
            "totals": totals,
        })
    finally:
        db.close()
