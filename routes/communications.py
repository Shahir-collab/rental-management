import os
from datetime import datetime
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from database import SessionLocal
from models import CommunicationLog, Tenant

router = APIRouter(prefix='/communications', tags=['Communications'])

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
def list_communications(request: Request):
    db = SessionLocal()
    try:
        logs_db = db.query(CommunicationLog).order_by(CommunicationLog.logged_at.desc()).all()
        logs = []
        for log in logs_db:
            tenant = db.query(Tenant).filter(Tenant.id == log.tenant_id).first()
            tenant_name = tenant.name if tenant else 'Unknown'
            logs.append({
                'id': log.id,
                'tenant_name': tenant_name,
                'tenant_id': log.tenant_id,
                'unit_no': log.unit_no,
                'log_type': log.log_type,
                'subject': log.subject,
                'description': log.description,
                'logged_at': log.logged_at,
                'follow_up_date': log.follow_up_date,
                'status': log.status
            })
        return request.app.state.templates.TemplateResponse('communications.html', {'request': request, 'logs': logs})
    finally:
        db.close()

@router.get('/new')
def new_communication(request: Request, tenant_id: str = None):
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        return request.app.state.templates.TemplateResponse('communication_form.html', {
            'request': request,
            'tenants': tenants,
            'selected_tenant': tenant_id,
            'mode': 'create'
        })
    finally:
        db.close()

@router.post('/new')
def create_communication(
    tenant_id: str = Form(...),
    log_type: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    follow_up_date: str = Form(None)
):
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        unit_no = tenant.current_unit if tenant else None
        
        fud = None
        if follow_up_date:
            fud = datetime.strptime(follow_up_date, '%Y-%m-%d').date()

        log = CommunicationLog(
            id=get_next_id(db, CommunicationLog, 'COM'),
            tenant_id=tenant_id,
            unit_no=unit_no,
            log_type=log_type,
            subject=subject,
            description=description,
            logged_at=datetime.utcnow(),
            follow_up_date=fud,
            status='Open',
            created_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        return RedirectResponse(url='/communications', status_code=303)
    finally:
        db.close()

@router.get('/{log_id}/edit')
def edit_communication(request: Request, log_id: str):
    db = SessionLocal()
    try:
        log = db.query(CommunicationLog).filter(CommunicationLog.id == log_id).first()
        tenants = db.query(Tenant).all()
        return request.app.state.templates.TemplateResponse('communication_form.html', {
            'request': request,
            'tenants': tenants,
            'log': log,
            'mode': 'edit'
        })
    finally:
        db.close()

@router.post('/{log_id}/edit')
def update_communication(
    log_id: str,
    tenant_id: str = Form(...),
    log_type: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    follow_up_date: str = Form(None)
):
    db = SessionLocal()
    try:
        log = db.query(CommunicationLog).filter(CommunicationLog.id == log_id).first()
        if log:
            log.tenant_id = tenant_id
            log.log_type = log_type
            log.subject = subject
            log.description = description
            
            fud = None
            if follow_up_date:
                fud = datetime.strptime(follow_up_date, '%Y-%m-%d').date()
            log.follow_up_date = fud
            
            tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if tenant:
                log.unit_no = tenant.current_unit

            db.commit()
        return RedirectResponse(url='/communications', status_code=303)
    finally:
        db.close()

@router.post('/{log_id}/close')
def close_communication(log_id: str):
    db = SessionLocal()
    try:
        log = db.query(CommunicationLog).filter(CommunicationLog.id == log_id).first()
        if log:
            log.status = 'Closed'
            db.commit()
        return RedirectResponse(url='/communications', status_code=303)
    finally:
        db.close()
