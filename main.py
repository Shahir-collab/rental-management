"""
Rental Management System \u2014 Web Application
=============================================
FastAPI application entry point.

Run with:  python main.py
Open:      http://localhost:8000
"""
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Ensure our app directory is on the path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

from database import init_db, engine, Base, IS_CLOUD, SessionLocal
try:
    from database import DB_PATH
except ImportError:
    DB_PATH = None
from import_excel import run_import, EXCEL_PATH

# --------------- App Setup ---------------
app = FastAPI(title="Rental Management System", version="1.0.0")

# Static files
static_dir = os.path.join(APP_DIR, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Documents directory for uploads
docs_dir = os.path.join(APP_DIR, "documents")
os.makedirs(docs_dir, exist_ok=True)

# Templates
template_dir = os.path.join(APP_DIR, "templates")
os.makedirs(template_dir, exist_ok=True)
templates = Jinja2Templates(directory=template_dir)

# Make undefined variables return empty/falsy instead of crashing
from jinja2 import ChainableUndefined
templates.env.undefined = ChainableUndefined

# Store templates on app state so routes can access them
app.state.templates = templates

# --------------- Custom Jinja2 Filters ---------------
def fmt_inr(value):
    """Format a number as Indian Rupees with commas."""
    if value is None:
        return "\u20b90"
    try:
        v = float(value)
        if v == int(v):
            return f"\u20b9{int(v):,}"
        return f"\u20b9{v:,.2f}"
    except (ValueError, TypeError):
        return f"\u20b9{value}"

def fmt_date(value):
    """Format a date as DD-MMM-YYYY."""
    if value is None:
        return "\u2014"
    try:
        if hasattr(value, 'strftime'):
            return value.strftime("%d-%b-%Y")
        return str(value)
    except Exception:
        return str(value)

def fmt_pct(value):
    """Format a percentage."""
    if value is None:
        return "0%"
    try:
        return f"{float(value):.1f}%"
    except (ValueError, TypeError):
        return "0%"

templates.env.filters["inr"] = fmt_inr
templates.env.filters["fdate"] = fmt_date
templates.env.filters["pct"] = fmt_pct

# --------------- Register Routes ---------------
from routes.dashboard import router as dashboard_router
from routes.units import router as units_router
from routes.tenants import router as tenants_router
from routes.rent import router as rent_router
from routes.agreements import router as agreements_router
from routes.witnesses import router as witnesses_router
from routes.deposits import router as deposits_router
from routes.utilities import router as utilities_router
from routes.expenses import router as expenses_router
from routes.data_quality import router as data_quality_router
from routes.search import router as search_router
from routes.import_export import router as import_export_router
from routes.crud import router as crud_router
from routes.payments import router as payments_router
from routes.rent_revisions import router as rent_revisions_router
from routes.receipts import router as receipts_router
from routes.reports import router as reports_router
from routes.documents import router as documents_router
from routes.communications import router as communications_router
from routes.move_workflow import router as move_workflow_router

app.include_router(dashboard_router)
app.include_router(units_router)
app.include_router(tenants_router)
app.include_router(rent_router)
app.include_router(agreements_router)
app.include_router(witnesses_router)
app.include_router(deposits_router)
app.include_router(utilities_router)
app.include_router(expenses_router)
app.include_router(data_quality_router)
app.include_router(search_router)
app.include_router(import_export_router)
app.include_router(crud_router)
app.include_router(payments_router)
app.include_router(rent_revisions_router)
app.include_router(receipts_router)
app.include_router(reports_router)
app.include_router(documents_router)
app.include_router(communications_router)
app.include_router(move_workflow_router)

# --------------- Startup ---------------
@app.on_event("startup")
async def startup():
    """Initialize database and import data if needed."""
    if IS_CLOUD:
        # Cloud: always create tables, import if empty
        from models import Unit
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            count = db.query(Unit).count()
            if count == 0:
                print("\n[STARTUP] Cloud DB empty. Running initial import...")
                run_import()
            else:
                print(f"\n[STARTUP] Cloud DB has {count} units. Skipping import.")
        finally:
            db.close()
    else:
        if DB_PATH and not os.path.exists(DB_PATH):
            print("\n[STARTUP] Database not found. Running initial import...")
            run_import()
        else:
            Base.metadata.create_all(bind=engine)
            print(f"\n[STARTUP] Database loaded: {DB_PATH}")
    print("[STARTUP] Application ready!\n")


# --------------- Run ---------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("\n" + "=" * 60)
    print("  RENTAL MANAGEMENT SYSTEM")
    print(f"  http://localhost:{port}")
    print("=" * 60 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=not IS_CLOUD)
