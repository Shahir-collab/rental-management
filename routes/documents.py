import os
import uuid
import shutil
from datetime import datetime
from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.responses import RedirectResponse, FileResponse
from database import SessionLocal
from models import Document, Tenant, RentalAgreement

router = APIRouter(prefix='/documents', tags=['Documents'])

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

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'documents')
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

@router.get('/')
def list_documents(request: Request):
    db = SessionLocal()
    try:
        docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
        documents = []
        for doc in docs:
            tenant = db.query(Tenant).filter(Tenant.id == doc.tenant_id).first()
            tenant_name = tenant.name if tenant else 'Unknown'
            documents.append({
                'id': doc.id,
                'tenant_name': tenant_name,
                'tenant_id': doc.tenant_id,
                'unit_no': doc.unit_no,
                'doc_type': doc.doc_type,
                'original_filename': doc.original_filename,
                'uploaded_at': doc.uploaded_at
            })
        return request.app.state.templates.TemplateResponse(request, 'documents.html', {'request': request, 'documents': documents})
    finally:
        db.close()

@router.get('/upload')
def upload_form(request: Request):
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        agreements = db.query(RentalAgreement).all()
        return request.app.state.templates.TemplateResponse(request, 'document_upload.html', {
            'request': request,
            'tenants': tenants,
            'agreements': agreements
        })
    finally:
        db.close()

@router.post('/upload')
async def upload_document(
    tenant_id: str = Form(...),
    agreement_id: str = Form(None),
    unit_no: str = Form(...),
    doc_type: str = Form(...),
    remarks: str = Form(None),
    file: UploadFile = File(...)
):
    db = SessionLocal()
    try:
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(DOCUMENTS_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        doc = Document(
            id=get_next_id(db, Document, 'DOC'),
            tenant_id=tenant_id,
            agreement_id=agreement_id,
            unit_no=unit_no,
            doc_type=doc_type,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            uploaded_at=datetime.utcnow(),
            remarks=remarks
        )
        db.add(doc)
        db.commit()
        return RedirectResponse(url='/documents', status_code=303)
    finally:
        db.close()

@router.get('/{doc_id}/download')
def download_document(doc_id: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc and os.path.exists(doc.file_path):
            return FileResponse(path=doc.file_path, filename=doc.original_filename)
        return RedirectResponse(url='/documents', status_code=303)
    finally:
        db.close()

@router.post('/{doc_id}/delete')
def delete_document(doc_id: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
            db.delete(doc)
            db.commit()
        return RedirectResponse(url='/documents', status_code=303)
    finally:
        db.close()
