from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from typing import Optional
from database import SessionLocal
import models
from datetime import datetime

router = APIRouter(prefix="/manage")

def get_next_id(db, model_class, prefix):
    existing = db.query(model_class).all()
    max_num = 0
    for obj in existing:
        try:
            num = int(obj.id.split('-')[1])
            if num > max_num:
                max_num = num
        except:
            pass
    return f'{prefix}-{max_num + 1:03d}'

# Tenant CRUD
@router.get("/tenants/new")
async def create_tenant_form(request: Request):
    return request.app.state.templates.TemplateResponse(request, 'tenant_form.html', {'request': request, 'mode': 'create', 'tenant': {}})

@router.post("/tenants/new")
async def create_tenant(
    name: str = Form(...),
    father_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    alt_phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    tenant_type: Optional[str] = Form(None),
    permanent_address: Optional[str] = Form(None),
    current_address: Optional[str] = Form(None),
    full_address: Optional[str] = Form(None),
    current_unit: Optional[str] = Form(None),
    current_status: Optional[str] = Form('Active'),
    notes: Optional[str] = Form(None)
):
    db = SessionLocal()
    try:
        tenant_id = get_next_id(db, models.Tenant, 'TEN')
        new_tenant = models.Tenant(
            id=tenant_id,
            name=name,
            father_name=father_name,
            phone=phone,
            alt_phone=alt_phone,
            email=email,
            tenant_type=tenant_type,
            permanent_address=permanent_address,
            current_address=current_address,
            full_address=full_address,
            current_unit=current_unit,
            current_status=current_status,
            notes=notes
        )
        db.add(new_tenant)
        db.commit()
        return RedirectResponse(url=f"/tenants/{tenant_id}", status_code=303)
    finally:
        db.close()

@router.get("/tenants/{id}/edit")
async def edit_tenant_form(request: Request, id: str):
    db = SessionLocal()
    try:
        tenant = db.query(models.Tenant).filter(models.Tenant.id == id).first()
        return request.app.state.templates.TemplateResponse(request, 'tenant_form.html', {'request': request, 'mode': 'edit', 'tenant': tenant})
    finally:
        db.close()

@router.post("/tenants/{id}/edit")
async def edit_tenant(
    id: str,
    name: str = Form(...),
    father_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    alt_phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    tenant_type: Optional[str] = Form(None),
    permanent_address: Optional[str] = Form(None),
    current_address: Optional[str] = Form(None),
    full_address: Optional[str] = Form(None),
    current_unit: Optional[str] = Form(None),
    current_status: Optional[str] = Form('Active'),
    notes: Optional[str] = Form(None)
):
    db = SessionLocal()
    try:
        tenant = db.query(models.Tenant).filter(models.Tenant.id == id).first()
        if tenant:
            tenant.name = name
            tenant.father_name = father_name
            tenant.phone = phone
            tenant.alt_phone = alt_phone
            tenant.email = email
            tenant.tenant_type = tenant_type
            tenant.permanent_address = permanent_address
            tenant.current_address = current_address
            tenant.full_address = full_address
            tenant.current_unit = current_unit
            tenant.current_status = current_status
            tenant.notes = notes
            db.commit()
        return RedirectResponse(url=f"/tenants/{id}", status_code=303)
    finally:
        db.close()

@router.post("/tenants/{id}/delete")
async def delete_tenant(id: str):
    db = SessionLocal()
    try:
        tenant = db.query(models.Tenant).filter(models.Tenant.id == id).first()
        if tenant:
            db.delete(tenant)
            db.commit()
        return RedirectResponse(url="/tenants", status_code=303)
    finally:
        db.close()


# Agreement CRUD
@router.get("/agreements/new")
async def create_agreement_form(request: Request):
    db = SessionLocal()
    try:
        tenants = db.query(models.Tenant).all()
        units = db.query(models.Unit).all()
        return request.app.state.templates.TemplateResponse(request, 'agreement_form.html', {'request': request, 'mode': 'create', 'agreement': {}, 'tenants': tenants, 'units': units})
    finally:
        db.close()

@router.post("/agreements/new")
async def create_agreement(
    tenant_id: str = Form(...),
    unit_no: Optional[str] = Form(None),
    landlord: Optional[str] = Form('Abdul Nazar'),
    agreement_date: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    lease_months: Optional[int] = Form(None),
    monthly_rent: Optional[float] = Form(None),
    security_deposit: Optional[float] = Form(None),
    rent_due_date: Optional[int] = Form(None),
    permitted_use: Optional[str] = Form(None),
    stamp_paper_value: Optional[float] = Form(None),
    stamp_paper_grn: Optional[str] = Form(None),
    late_interest_rate: Optional[float] = Form(None),
    notice_period: Optional[int] = Form(None),
    signature_status: Optional[str] = Form(None),
    agreement_status: Optional[str] = Form('Active'),
    remarks: Optional[str] = Form(None)
):
    db = SessionLocal()
    try:
        agreement_id = get_next_id(db, models.RentalAgreement, 'AGR')
        new_agreement = models.RentalAgreement(
            id=agreement_id,
            tenant_id=tenant_id,
            unit_no=unit_no,
            landlord=landlord,
            agreement_date=datetime.strptime(agreement_date, '%Y-%m-%d').date() if agreement_date else None,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None,
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
            lease_months=lease_months,
            monthly_rent=monthly_rent,
            security_deposit=security_deposit,
            rent_due_date=rent_due_date,
            permitted_use=permitted_use,
            stamp_paper_value=stamp_paper_value,
            stamp_paper_grn=stamp_paper_grn,
            late_interest_rate=late_interest_rate,
            notice_period=notice_period,
            signature_status=signature_status,
            agreement_status=agreement_status,
            remarks=remarks
        )
        db.add(new_agreement)
        db.commit()
        return RedirectResponse(url=f"/agreements/{agreement_id}", status_code=303)
    finally:
        db.close()

@router.get("/agreements/{id}/edit")
async def edit_agreement_form(request: Request, id: str):
    db = SessionLocal()
    try:
        agreement = db.query(models.RentalAgreement).filter(models.RentalAgreement.id == id).first()
        tenants = db.query(models.Tenant).all()
        units = db.query(models.Unit).all()
        return request.app.state.templates.TemplateResponse(request, 'agreement_form.html', {'request': request, 'mode': 'edit', 'agreement': agreement, 'tenants': tenants, 'units': units})
    finally:
        db.close()

@router.post("/agreements/{id}/edit")
async def edit_agreement(
    id: str,
    tenant_id: str = Form(...),
    unit_no: Optional[str] = Form(None),
    landlord: Optional[str] = Form(None),
    agreement_date: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    lease_months: Optional[int] = Form(None),
    monthly_rent: Optional[float] = Form(None),
    security_deposit: Optional[float] = Form(None),
    rent_due_date: Optional[int] = Form(None),
    permitted_use: Optional[str] = Form(None),
    stamp_paper_value: Optional[float] = Form(None),
    stamp_paper_grn: Optional[str] = Form(None),
    late_interest_rate: Optional[float] = Form(None),
    notice_period: Optional[int] = Form(None),
    signature_status: Optional[str] = Form(None),
    agreement_status: Optional[str] = Form('Active'),
    remarks: Optional[str] = Form(None)
):
    db = SessionLocal()
    try:
        agreement = db.query(models.RentalAgreement).filter(models.RentalAgreement.id == id).first()
        if agreement:
            agreement.tenant_id = tenant_id
            agreement.unit_no = unit_no
            agreement.landlord = landlord
            agreement.agreement_date = datetime.strptime(agreement_date, '%Y-%m-%d').date() if agreement_date else None
            agreement.start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            agreement.end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            agreement.lease_months = lease_months
            agreement.monthly_rent = monthly_rent
            agreement.security_deposit = security_deposit
            agreement.rent_due_date = rent_due_date
            agreement.permitted_use = permitted_use
            agreement.stamp_paper_value = stamp_paper_value
            agreement.stamp_paper_grn = stamp_paper_grn
            agreement.late_interest_rate = late_interest_rate
            agreement.notice_period = notice_period
            agreement.signature_status = signature_status
            agreement.agreement_status = agreement_status
            agreement.remarks = remarks
            db.commit()
        return RedirectResponse(url=f"/agreements/{id}", status_code=303)
    finally:
        db.close()

@router.post("/agreements/{id}/delete")
async def delete_agreement(id: str):
    db = SessionLocal()
    try:
        agreement = db.query(models.RentalAgreement).filter(models.RentalAgreement.id == id).first()
        if agreement:
            db.delete(agreement)
            db.commit()
        return RedirectResponse(url="/agreements", status_code=303)
    finally:
        db.close()

# Unit CRUD
@router.get("/units/new")
async def create_unit_form(request: Request):
    return request.app.state.templates.TemplateResponse(request, 'unit_form.html', {'request': request, 'mode': 'create', 'unit': {}})

@router.post("/units/new")
async def create_unit(
    unit_no: str = Form(...),
    floor: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    occupancy_status: Optional[str] = Form('Vacant')
):
    db = SessionLocal()
    try:
        unit_id = get_next_id(db, models.Unit, 'UNT')
        new_unit = models.Unit(
            id=unit_id,
            unit_no=unit_no,
            floor=floor,
            description=description,
            occupancy_status=occupancy_status
        )
        db.add(new_unit)
        db.commit()
        return RedirectResponse(url=f"/units", status_code=303)
    finally:
        db.close()

@router.get("/units/{id}/edit")
async def edit_unit_form(request: Request, id: str):
    db = SessionLocal()
    try:
        unit = db.query(models.Unit).filter(models.Unit.id == id).first()
        return request.app.state.templates.TemplateResponse(request, 'unit_form.html', {'request': request, 'mode': 'edit', 'unit': unit})
    finally:
        db.close()

@router.post("/units/{id}/edit")
async def edit_unit(
    id: str,
    unit_no: str = Form(...),
    floor: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    occupancy_status: Optional[str] = Form('Vacant')
):
    db = SessionLocal()
    try:
        unit = db.query(models.Unit).filter(models.Unit.id == id).first()
        if unit:
            unit.unit_no = unit_no
            unit.floor = floor
            unit.description = description
            unit.occupancy_status = occupancy_status
            db.commit()
        return RedirectResponse(url=f"/units", status_code=303)
    finally:
        db.close()


# Deposit CRUD
@router.get("/deposits/new")
async def create_deposit_form(request: Request):
    db = SessionLocal()
    try:
        tenants = db.query(models.Tenant).all()
        return request.app.state.templates.TemplateResponse(request, 'deposit_form.html', {'request': request, 'mode': 'create', 'deposit': {}, 'tenants': tenants})
    finally:
        db.close()

@router.post("/deposits/new")
async def create_deposit(
    tenant_id: str = Form(...),
    unit_no: Optional[str] = Form(None),
    security_deposit: Optional[float] = Form(None),
    deposit_date: Optional[str] = Form(None),
    advance_rent: Optional[float] = Form(None),
    status: Optional[str] = Form('Held'),
    remarks: Optional[str] = Form(None)
):
    db = SessionLocal()
    try:
        deposit_id = get_next_id(db, models.Deposit, 'DEP')
        new_deposit = models.Deposit(
            id=deposit_id,
            tenant_id=tenant_id,
            unit_no=unit_no,
            security_deposit=security_deposit,
            deposit_date=datetime.strptime(deposit_date, '%Y-%m-%d').date() if deposit_date else None,
            advance_rent=advance_rent,
            status=status,
            remarks=remarks
        )
        db.add(new_deposit)
        db.commit()
        return RedirectResponse(url=f"/deposits", status_code=303)
    finally:
        db.close()

@router.get("/deposits/{id}/edit")
async def edit_deposit_form(request: Request, id: str):
    db = SessionLocal()
    try:
        deposit = db.query(models.Deposit).filter(models.Deposit.id == id).first()
        tenants = db.query(models.Tenant).all()
        return request.app.state.templates.TemplateResponse(request, 'deposit_form.html', {'request': request, 'mode': 'edit', 'deposit': deposit, 'tenants': tenants})
    finally:
        db.close()

@router.post("/deposits/{id}/edit")
async def edit_deposit(
    id: str,
    tenant_id: str = Form(...),
    unit_no: Optional[str] = Form(None),
    security_deposit: Optional[float] = Form(None),
    deposit_date: Optional[str] = Form(None),
    advance_rent: Optional[float] = Form(None),
    status: Optional[str] = Form('Held'),
    remarks: Optional[str] = Form(None)
):
    db = SessionLocal()
    try:
        deposit = db.query(models.Deposit).filter(models.Deposit.id == id).first()
        if deposit:
            deposit.tenant_id = tenant_id
            deposit.unit_no = unit_no
            deposit.security_deposit = security_deposit
            deposit.deposit_date = datetime.strptime(deposit_date, '%Y-%m-%d').date() if deposit_date else None
            deposit.advance_rent = advance_rent
            deposit.status = status
            deposit.remarks = remarks
            db.commit()
        return RedirectResponse(url=f"/deposits", status_code=303)
    finally:
        db.close()


# Witness CRUD
@router.get("/witnesses/new")
async def create_witness_form(request: Request):
    return request.app.state.templates.TemplateResponse(request, 'witness_form.html', {'request': request, 'mode': 'create', 'witness': {}})

@router.post("/witnesses/new")
async def create_witness(
    name: str = Form(...),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None)
):
    db = SessionLocal()
    try:
        witness_id = get_next_id(db, models.Witness, 'WIT')
        new_witness = models.Witness(
            id=witness_id,
            name=name,
            phone=phone,
            address=address
        )
        db.add(new_witness)
        db.commit()
        return RedirectResponse(url=f"/witnesses", status_code=303)
    finally:
        db.close()

@router.get("/witnesses/{id}/edit")
async def edit_witness_form(request: Request, id: str):
    db = SessionLocal()
    try:
        witness = db.query(models.Witness).filter(models.Witness.id == id).first()
        return request.app.state.templates.TemplateResponse(request, 'witness_form.html', {'request': request, 'mode': 'edit', 'witness': witness})
    finally:
        db.close()

@router.post("/witnesses/{id}/edit")
async def edit_witness(
    id: str,
    name: str = Form(...),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None)
):
    db = SessionLocal()
    try:
        witness = db.query(models.Witness).filter(models.Witness.id == id).first()
        if witness:
            witness.name = name
            witness.phone = phone
            witness.address = address
            db.commit()
        return RedirectResponse(url=f"/witnesses", status_code=303)
    finally:
        db.close()


# Agreement Renewal
@router.get("/agreements/{agr_id}/renew")
async def renew_agreement_form(request: Request, agr_id: str):
    db = SessionLocal()
    try:
        old = db.query(models.RentalAgreement).filter(models.RentalAgreement.id == agr_id).first()
        if not old:
            return RedirectResponse(url="/agreements", status_code=303)
        tenants = db.query(models.Tenant).all()
        units = db.query(models.Unit).all()
        # Pre-fill with old agreement data but new dates
        from dateutil.relativedelta import relativedelta
        new_start = old.end_date or datetime.now().date()
        new_end = new_start + relativedelta(months=old.lease_months or 11)
        agreement = {
            'tenant_id': old.tenant_id,
            'unit_no': old.unit_no,
            'landlord': old.landlord or 'Abdul Nazar',
            'agreement_date': new_start.isoformat() if hasattr(new_start, 'isoformat') else str(new_start),
            'start_date': new_start.isoformat() if hasattr(new_start, 'isoformat') else str(new_start),
            'end_date': new_end.isoformat() if hasattr(new_end, 'isoformat') else str(new_end),
            'lease_months': old.lease_months or 11,
            'monthly_rent': old.monthly_rent,
            'security_deposit': old.security_deposit,
            'rent_due_date': old.rent_due_date,
            'permitted_use': old.permitted_use,
            'stamp_paper_value': old.stamp_paper_value,
            'late_interest_rate': old.late_interest_rate,
            'notice_period': old.notice_period,
            'agreement_status': 'Active',
            'remarks': f'Renewal of {old.id}',
        }
        return request.app.state.templates.TemplateResponse(request, 'agreement_form.html', {
            'request': request, 'mode': 'create', 'agreement': agreement,
            'tenants': [{'id': t.id, 'name': t.name} for t in tenants],
            'units': [{'id': u.id, 'unit_no': u.unit_no} for u in units],
            'renew_from': old.id,
        })
    finally:
        db.close()
