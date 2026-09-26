from datetime import datetime
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from database import SessionLocal
from models import MoveEvent, Residence, Unit, Tenant, Deposit

router = APIRouter(prefix='/move', tags=['Move Workflow'])

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

@router.get('/in')
def move_in_form(request: Request, unit_id: str = None):
    db = SessionLocal()
    try:
        unit = db.query(Unit).filter(Unit.id == unit_id).first()
        tenants = db.query(Tenant).all()
        return request.app.state.templates.TemplateResponse(request, 'move_form.html', {
            'request': request,
            'event_type': 'Move-In',
            'unit': unit,
            'tenants': tenants
        })
    finally:
        db.close()

@router.post('/in')
def process_move_in(
    tenant_id: str = Form(...),
    unit_no: str = Form(...),
    event_date: str = Form(...),
    meter_reading: str = Form(None),
    condition_notes: str = Form(None),
    remarks: str = Form(None),
    agreement_signed: bool = Form(False),
    deposit_collected: bool = Form(False),
    keys_handed: bool = Form(False),
    inspection_done: bool = Form(False)
):
    db = SessionLocal()
    try:
        date_obj = datetime.strptime(event_date, '%Y-%m-%d').date() if event_date else datetime.utcnow().date()
        
        # Create Residence
        residence = Residence(
            id=get_next_id(db, Residence, 'RES'),
            tenant_id=tenant_id,
            unit_id=None,
            unit_no=unit_no,
            move_in=date_obj,
            monthly_rent=0,
            security_deposit=0
        )
        unit = db.query(Unit).filter(Unit.unit_no == unit_no).first()
        if unit:
            residence.unit_id = unit.id
            unit.occupancy_status = 'Occupied'
        db.add(residence)
        db.flush()

        move_event = MoveEvent(
            id=get_next_id(db, MoveEvent, 'MOV'),
            tenant_id=tenant_id,
            unit_no=unit_no,
            residence_id=residence.id,
            event_type='Move-In',
            event_date=date_obj,
            agreement_signed=agreement_signed,
            deposit_collected=deposit_collected,
            keys_handed=keys_handed,
            inspection_done=inspection_done,
            meter_reading=meter_reading,
            condition_notes=condition_notes,
            remarks=remarks,
            created_at=datetime.utcnow()
        )
        db.add(move_event)

        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if tenant:
            tenant.current_unit = unit_no
            tenant.current_status = 'Active'

        db.commit()
        if unit:
            return RedirectResponse(url=f'/units/{unit.id}', status_code=303)
        return RedirectResponse(url='/units', status_code=303)
    finally:
        db.close()

@router.get('/out')
def move_out_form(request: Request, residence_id: str = None):
    db = SessionLocal()
    try:
        residence = db.query(Residence).filter(Residence.id == residence_id).first()
        tenant = None
        deposits_held = 0
        if residence:
            tenant = db.query(Tenant).filter(Tenant.id == residence.tenant_id).first()
            deposits = db.query(Deposit).filter(
                Deposit.tenant_id == residence.tenant_id, 
                Deposit.unit_no == residence.unit_no,
                Deposit.status == 'Held'
            ).all()
            deposits_held = sum([d.security_deposit for d in deposits])

        return request.app.state.templates.TemplateResponse(request, 'move_form.html', {
            'request': request,
            'event_type': 'Move-Out',
            'residence': residence,
            'tenant': tenant,
            'deposits_held': deposits_held
        })
    finally:
        db.close()

@router.post('/out')
def process_move_out(
    residence_id: str = Form(...),
    tenant_id: str = Form(...),
    unit_no: str = Form(...),
    event_date: str = Form(...),
    meter_reading: str = Form(None),
    condition_notes: str = Form(None),
    deposit_deductions: float = Form(0),
    deposit_refund: float = Form(0),
    final_settlement: str = Form(None),
    remarks: str = Form(None),
    agreement_signed: bool = Form(False),
    deposit_collected: bool = Form(False),
    keys_handed: bool = Form(False),
    inspection_done: bool = Form(False)
):
    db = SessionLocal()
    try:
        date_obj = datetime.strptime(event_date, '%Y-%m-%d').date() if event_date else datetime.utcnow().date()

        move_event = MoveEvent(
            id=get_next_id(db, MoveEvent, 'MOV'),
            tenant_id=tenant_id,
            unit_no=unit_no,
            residence_id=residence_id,
            event_type='Move-Out',
            event_date=date_obj,
            agreement_signed=agreement_signed,
            deposit_collected=deposit_collected,
            keys_handed=keys_handed,
            inspection_done=inspection_done,
            meter_reading=meter_reading,
            condition_notes=condition_notes,
            deposit_deductions=deposit_deductions,
            deposit_refund=deposit_refund,
            final_settlement=final_settlement,
            remarks=remarks,
            created_at=datetime.utcnow()
        )
        db.add(move_event)

        residence = db.query(Residence).filter(Residence.id == residence_id).first()
        if residence:
            residence.move_out = date_obj

        unit = db.query(Unit).filter(Unit.unit_no == unit_no).first()
        if unit:
            unit.occupancy_status = 'Vacant'

        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if tenant:
            tenant.current_unit = None
            tenant.current_status = 'Inactive'

        db.commit()
        return RedirectResponse(url='/units', status_code=303)
    finally:
        db.close()
