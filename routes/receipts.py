from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from database import SessionLocal
from models import Payment, Tenant

router = APIRouter(prefix='/receipts', tags=['Receipts'])

def number_to_words(n):
    if n == 0: return "Zero"
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def get_words(num):
        if num < 20: return ones[num]
        elif num < 100: return tens[num // 10] + (" " + ones[num % 10] if num % 10 != 0 else "")
        elif num < 1000: return ones[num // 100] + " Hundred" + (" and " + get_words(num % 100) if num % 100 != 0 else "")
        elif num < 100000: return get_words(num // 1000) + " Thousand" + (" " + get_words(num % 1000) if num % 1000 != 0 else "")
        return str(num)
        
    return "Rupees " + get_words(int(n)).strip() + " Only"

@router.get('/{payment_id}')
def print_receipt(request: Request, payment_id: str):
    db = SessionLocal()
    try:
        p = db.query(Payment).filter_by(id=payment_id).first()
        tenant = db.query(Tenant).filter_by(id=p.tenant_id).first() if p else None
        
        receipt = {
            'receipt_no': p.receipt_no if p else '',
            'tenant_name': tenant.name if tenant else '',
            'tenant_id': p.tenant_id if p else '',
            'unit_no': p.unit_no if p else '',
            'amount': p.amount if p else 0,
            'amount_in_words': number_to_words(p.amount) if p else '',
            'payment_date': p.payment_date if p else '',
            'payment_method': p.payment_method if p else '',
            'reference_no': p.reference_no if p else '',
            'month': p.month if p else '',
            'landlord': 'Abdul Nazar',
            'landlord_address': 'Muzammil House, Vanoor Maruthakkad, Alathur P.O., Alathur Taluk'
        }
        
        return request.app.state.templates.TemplateResponse(request, 'receipt_print.html', {'request': request, 'receipt': receipt})
    finally:
        db.close()
