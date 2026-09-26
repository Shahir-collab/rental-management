from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from database import SessionLocal
from models import Residence, Payment, Tenant
import io
import csv
from datetime import date

router = APIRouter(prefix='/reports', tags=['Reports'])

@router.get('/')
def reports_dashboard(request: Request):
    db = SessionLocal()
    try:
        residences = db.query(Residence).filter_by(move_out=None).all()
        total_expected = sum((r.monthly_rent or 0) for r in residences)
        
        payments = db.query(Payment).all()
        total_collected = sum((p.amount or 0) for p in payments)
        
        outstanding = total_expected - total_collected
        collection_rate = (total_collected / total_expected * 100) if total_expected > 0 else 0
        
        monthly_data = [{'month': 'Current', 'expected': total_expected, 'collected': total_collected}]
        
        payment_methods = {}
        for p in payments:
            m = p.payment_method or 'Unknown'
            payment_methods[m] = payment_methods.get(m, 0) + (p.amount or 0)
            
        tenants = db.query(Tenant).all()
        tenant_summary = []
        for t in tenants:
            res = db.query(Residence).filter_by(tenant_id=t.id, move_out=None).first()
            pays = db.query(Payment).filter_by(tenant_id=t.id).all()
            total_paid = sum((p.amount or 0) for p in pays)
            m_rent = res.monthly_rent if res else 0
            tenant_summary.append({
                'tenant_name': t.name,
                'unit_no': res.unit_no if res else '',
                'monthly_rent': m_rent,
                'total_paid': total_paid,
                'balance': m_rent - total_paid,
                'status': t.current_status
            })
            
        return request.app.state.templates.TemplateResponse('reports.html', {
            'request': request,
            'total_expected': total_expected,
            'total_collected': total_collected,
            'outstanding': outstanding,
            'collection_rate': collection_rate,
            'monthly_data': monthly_data,
            'tenant_summary': tenant_summary,
            'payment_methods': payment_methods
        })
    finally:
        db.close()

@router.get('/export')
def export_csv():
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Tenant Name', 'Unit No', 'Monthly Rent', 'Total Paid', 'Balance', 'Status'])
        
        for t in tenants:
            res = db.query(Residence).filter_by(tenant_id=t.id, move_out=None).first()
            pays = db.query(Payment).filter_by(tenant_id=t.id).all()
            total_paid = sum((p.amount or 0) for p in pays)
            m_rent = res.monthly_rent if res else 0
            writer.writerow([
                t.name,
                res.unit_no if res else '',
                m_rent,
                total_paid,
                m_rent - total_paid,
                t.current_status
            ])
            
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=tenant_summary.csv"}
        )
    finally:
        db.close()
