"""Witnesses route — serves /witnesses page."""
from fastapi import APIRouter, Request
from database import SessionLocal
from models import Witness, AgreementWitness

router = APIRouter(prefix="/witnesses", tags=["witnesses"])


@router.get("/")
def list_witnesses(request: Request):
    db = SessionLocal()
    try:
        witnesses_raw = db.query(Witness).order_by(Witness.name).all()

        witnesses = []
        for w in witnesses_raw:
            # Get agreement links
            links = db.query(AgreementWitness).filter(
                AgreementWitness.witness_id == w.id
            ).all()

            for link in links:
                witnesses.append({
                    "id": w.id,
                    "name": w.name,
                    "address": w.address or "",
                    "phone": w.phone or "",
                    "role": link.role or "",
                    "tenant_name": link.tenant_name or "",
                    "agreement_id": link.agreement_id or "",
                    "date": link.date,
                    "remarks": link.remarks or "",
                })

            # If no links, still show witness
            if not links:
                witnesses.append({
                    "id": w.id,
                    "name": w.name,
                    "address": w.address or "",
                    "phone": w.phone or "",
                    "role": "",
                    "tenant_name": "",
                    "agreement_id": "",
                    "date": None,
                    "remarks": "",
                })

        return request.app.state.templates.TemplateResponse("witnesses.html", {
            "request": request,
            "witnesses": witnesses,
        })
    finally:
        db.close()
