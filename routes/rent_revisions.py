from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from database import SessionLocal
from models import RentRevision, Tenant, Residence, RentalAgreement
from datetime import date

router = APIRouter(prefix='/rent-revisions', tags=['Rent Revisions'])

def get_next_id(db, model_class, prefix):
    existing = db.query(model_class).all()
    max_num = 0
    for obj in existing:
        try:
            num = int(obj.id.split('-')[1])
            if num > max_num:
                max_num = num
        except: pass
    return f'{prefix}-{max_num + 1:03d}'

@router.get('/')
def list_revisions(request: Request):
    db = SessionLocal()
    try:
        revisions_db = db.query(RentRevision).all()
        revisions = []
        for r in revisions_db:
            tenant = db.query(Tenant).filter_by(id=r.tenant_id).first()
            revisions.append({
                'id': r.id,
                'tenant_name': tenant.name if tenant else r.tenant_id,
                'unit_no': r.unit_no,
                'old_rent': r.old_rent,
                'new_rent': r.new_rent,
                'effective_date': r.effective_date,
                'reason': r.reason
            })
        return request.app.state.templates.TemplateResponse(request, 'rent_revisions.html', {'request': request, 'revisions': revisions})
    finally:
        db.close()

@router.get('/new')
def new_revision_form(request: Request, tenant_id: str = None):
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).filter_by(current_status='Active').all()
        current_rent = 0
        if tenant_id:
            residence = db.query(Residence).filter_by(tenant_id=tenant_id, move_out=None).first()
            if residence:
                current_rent = residence.monthly_rent
        return request.app.state.templates.TemplateResponse(request, 'rent_revision_form.html', {'request': request, 'mode': 'create', 'tenants': tenants, 'current_rent': current_rent})
    finally:
        db.close()

@router.post('/new')
def create_revision(tenant_id: str = Form(...), old_rent: float = Form(...), new_rent: float = Form(...), effective_date: date = Form(...), reason: str = Form(...), approved_by: str = Form(...)):
    db = SessionLocal()
    try:
        residence = db.query(Residence).filter_by(tenant_id=tenant_id, move_out=None).first()
        unit_no = residence.unit_no if residence else None
        residence_id = residence.id if residence else None
        
        agreement = db.query(RentalAgreement).filter_by(tenant_id=tenant_id, agreement_status='Active').first()
        agreement_id = agreement.id if agreement else None
        
        rev = RentRevision(
            id=get_next_id(db, RentRevision, 'REV'),
            tenant_id=tenant_id,
            unit_no=unit_no,
            residence_id=residence_id,
            agreement_id=agreement_id,
            old_rent=old_rent,
            new_rent=new_rent,
            effective_date=effective_date,
            reason=reason,
            approved_by=approved_by,
            created_at=date.today()
        )
        db.add(rev)
        
        if residence:
            residence.monthly_rent = new_rent
        if agreement:
            agreement.monthly_rent = new_rent
            
        db.commit()
        return RedirectResponse(url='/rent-revisions', status_code=303)
    finally:
        db.close()
