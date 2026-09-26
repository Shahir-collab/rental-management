"""Data quality route — serves /data-quality page."""
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from database import SessionLocal
from models import DataIssue

router = APIRouter(prefix="/data-quality", tags=["data_quality"])


@router.get("/")
def data_quality_issues(request: Request):
    db = SessionLocal()
    try:
        issues_raw = db.query(DataIssue).order_by(DataIssue.id).all()

        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Informational": 4}
        issues_raw.sort(key=lambda x: severity_order.get(x.severity, 5))

        issues = []
        for i in issues_raw:
            issues.append({
                "id": i.id,
                "category": i.category or "",
                "description": i.description or "",
                "source_file": i.source_file or "",
                "source_record": i.source_record or "",
                "tenant": i.tenant_id or "",
                "unit": i.unit_no or "",
                "severity": i.severity or "Medium",
                "suggested_action": i.suggested_action or "",
                "status": i.status or "Open",
                "notes": i.notes or "",
            })

        severity_counts = {
            "critical": sum(1 for i in issues if i["severity"] == "Critical"),
            "high": sum(1 for i in issues if i["severity"] == "High"),
            "medium": sum(1 for i in issues if i["severity"] == "Medium"),
            "low": sum(1 for i in issues if i["severity"] == "Low"),
            "info": sum(1 for i in issues if i["severity"] == "Informational"),
        }

        return request.app.state.templates.TemplateResponse("data_quality.html", {
            "request": request,
            "issues": issues,
            "severity_counts": severity_counts,
        })
    finally:
        db.close()


@router.post("/{issue_id}/status")
def update_issue_status(request: Request, issue_id: str, status: str = Form(...)):
    db = SessionLocal()
    try:
        issue = db.query(DataIssue).filter(DataIssue.id == issue_id).first()
        if issue:
            issue.status = status
            db.commit()
        return RedirectResponse(url="/data-quality", status_code=303)
    finally:
        db.close()
