from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from database import SessionLocal
from models import Tenant, Unit, Residence, RentalAgreement
import csv
from io import StringIO

router = APIRouter(prefix="/import-export", tags=["import_export"])

@router.get("/")
def import_export_page(request: Request):
    return request.app.state.templates.TemplateResponse(request, "import_export.html", {"request": request})

@router.post("/import")
async def import_data(request: Request, file: UploadFile = File(...)):
    # Placeholder for actual import logic
    content = await file.read()
    return request.app.state.templates.TemplateResponse(request, "import_export.html", {"request": request, "message": f"Successfully processed {file.filename}"})

@router.get("/export-csv")
def export_csv():
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Name", "Phone", "Email", "Status"])
        for t in tenants:
            writer.writerow([t.id, t.name, t.phone, t.email, t.current_status])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=tenants.csv"}
        )
    finally:
        db.close()
