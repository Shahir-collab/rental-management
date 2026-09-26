from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from database import SessionLocal
from models import Payment, Tenant, RentCharge, Residence
from datetime import date
import datetime

router = APIRouter(prefix='/payments', tags=['Payments'])

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
def list_payments(request: Request):
    db = SessionLocal()
    try:
        payments_db = db.query(Payment).order_by(Payment.payment_date.desc()).all()
        payments = []
        for p in payments_db:
            tenant = db.query(Tenant).filter_by(id=p.tenant_id).first()
            payments.append({
                'id': p.id,
                'receipt_no': p.receipt_no,
                'tenant_name': tenant.name if tenant else p.tenant_id,
                'unit_no': p.unit_no,
                'month': p.month,
                'amount': p.amount,
                'payment_date': p.payment_date,
                'payment_method': p.payment_method,
                'reference_no': p.reference_no
            })
        return request.app.state.templates.TemplateResponse('payments.html', {'request': request, 'payments': payments})
    finally:
        db.close()

@router.get('/new')
def new_payment_form(request: Request, tenant_id: str = None, month: str = None):
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).filter_by(current_status='Active').all()
        return request.app.state.templates.TemplateResponse('payment_form.html', {'request': request, 'mode': 'create', 'tenants': tenants, 'current_month': datetime.date.today().strftime('%b %Y')})
    finally:
        db.close()

@router.post('/new')
def create_payment(tenant_id: str = Form(...), unit_no: str = Form(...), amount: float = Form(...), payment_date: date = Form(...), payment_method: str = Form(...), reference_no: str = Form(None), month: str = Form(...), remarks: str = Form(None)):
    db = SessionLocal()
    try:
        pay_id = get_next_id(db, Payment, 'PAY')
        receipt_no = f"RCP-{pay_id.split('-')[1]}"
        
        rent_charge = db.query(RentCharge).filter_by(tenant_id=tenant_id, month=month).first()
        rent_charge_id = rent_charge.id if rent_charge else None
        
        pay = Payment(
            id=pay_id,
            rent_charge_id=rent_charge_id,
            tenant_id=tenant_id,
            unit_no=unit_no,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            receipt_no=receipt_no,
            reference_no=reference_no,
            month=month,
            remarks=remarks,
            created_at=date.today()
        )
        db.add(pay)
        
        if rent_charge:
            rent_charge.amount_paid = (rent_charge.amount_paid or 0) + amount
            rent_charge.balance = (rent_charge.total_due or 0) - rent_charge.amount_paid
            if rent_charge.balance <= 0:
                rent_charge.payment_status = 'Paid'
            elif rent_charge.amount_paid > 0:
                rent_charge.payment_status = 'Partial'
                
        db.commit()
        return RedirectResponse(url='/payments', status_code=303)
    finally:
        db.close()

@router.post('/generate-monthly')
def generate_monthly(request: Request):
    db = SessionLocal()
    try:
        today = date.today()
        current_month = today.strftime('%b %Y')
        last_month = (today.replace(day=1) - datetime.timedelta(days=1)).strftime('%b %Y')
        
        active_residences = db.query(Residence).filter_by(move_out=None).all()
        for res in active_residences:
            existing_charge = db.query(RentCharge).filter_by(tenant_id=res.tenant_id, month=current_month).first()
            if not existing_charge:
                prev_charge = db.query(RentCharge).filter_by(tenant_id=res.tenant_id, month=last_month).first()
                prev_arrears = prev_charge.balance if prev_charge else 0
                
                tenant = db.query(Tenant).filter_by(id=res.tenant_id).first()
                monthly_rent = res.monthly_rent or 0
                total_due = monthly_rent + prev_arrears
                
                new_charge = RentCharge(
                    id=get_next_id(db, RentCharge, 'CHG'),
                    residence_id=res.id,
                    month=current_month,
                    unit_no=res.unit_no,
                    tenant_id=res.tenant_id,
                    tenant_name=tenant.name if tenant else None,
                    monthly_rent=monthly_rent,
                    prev_arrears=prev_arrears,
                    other_charges=0,
                    late_fee=0,
                    total_due=total_due,
                    amount_paid=0,
                    balance=total_due,
                    payment_date=None,
                    payment_method=None,
                    receipt_no=None,
                    payment_status='Pending',
                    late_days=0,
                    remarks=None
                )
                db.add(new_charge)
                db.commit() 
    finally:
        db.close()
    return RedirectResponse(url='/rent', status_code=303)
