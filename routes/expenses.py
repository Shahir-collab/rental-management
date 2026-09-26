"""Expenses route — serves /expenses page."""
from fastapi import APIRouter, Request
from database import SessionLocal
from models import BuildingExpense

EXPENSE_CATEGORIES = [
    "Electricity", "Water", "Cleaning", "Repairs", "Plumbing",
    "Electrical", "Lift Maintenance", "Security", "Property Tax",
    "Insurance", "Internet", "Painting", "Other"
]

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/")
def list_expenses(request: Request, category: str = None):
    db = SessionLocal()
    try:
        query = db.query(BuildingExpense)
        if category:
            query = query.filter(BuildingExpense.category == category)
        expenses_raw = query.order_by(BuildingExpense.date.desc()).all()

        expenses = []
        for e in expenses_raw:
            expenses.append({
                "id": e.id,
                "date": e.date,
                "category": e.category or "",
                "description": e.description or "",
                "amount": e.amount or 0,
                "vendor": e.vendor or "",
                "method": e.payment_method or "",
                "unit": e.unit_or_area or "",
            })

        return request.app.state.templates.TemplateResponse(request, "expenses.html", {
            "request": request,
            "expenses": expenses,
            "categories": EXPENSE_CATEGORIES,
        })
    finally:
        db.close()
