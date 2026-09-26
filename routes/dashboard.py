from fastapi import APIRouter, Request
from database import SessionLocal
from models import Unit, Tenant, Residence, RentalAgreement, Deposit, RentCharge, DataIssue, CommunicationLog, Payment
from sqlalchemy import func
from datetime import date, timedelta

router = APIRouter(tags=["dashboard"])

@router.get("/")
def dashboard(request: Request):
    db = SessionLocal()
    try:
        units_total = db.query(Unit).count()
        units_occupied = db.query(Unit).filter(Unit.occupancy_status == 'Occupied').count()
        units_vacant = units_total - units_occupied
        occupancy_pct = (units_occupied / units_total * 100) if units_total > 0 else 0.0

        monthly_rent_active = db.query(func.sum(Residence.monthly_rent)).filter(Residence.move_out == None).scalar() or 0.0
        deposits_held = db.query(func.sum(Deposit.security_deposit)).filter(Deposit.status == 'Held').scalar() or 0.0

        total_tenants = db.query(Tenant).count()
        active_tenants_count = db.query(Tenant).filter(Tenant.current_status == 'Active').count()
        inactive_tenants_count = total_tenants - active_tenants_count

        active_agreements_count = db.query(RentalAgreement).filter(RentalAgreement.agreement_status == 'Active').count()
        expired_agreements_count = db.query(RentalAgreement).filter(RentalAgreement.agreement_status == 'Expired').count()
        
        # expiring soon means active and end_date in next 30 days
        agreements = db.query(RentalAgreement).filter(RentalAgreement.agreement_status == 'Active').all()
        expiring_soon_count = sum(1 for a in agreements if a.days_remaining is not None and a.days_remaining <= 30)

        data_issues_count = db.query(DataIssue).filter(DataIssue.status == 'Open').count()

        active_residences = db.query(Residence).filter(Residence.move_out == None).all()
        active_tenants_list = []
        for res in active_residences:
            tenant = res.tenant
            if not tenant: continue
            agr = db.query(RentalAgreement).filter_by(residence_id=res.id, agreement_status='Active').first()
            active_tenants_list.append({
                "name": tenant.name,
                "unit_no": res.unit_no,
                "monthly_rent": res.monthly_rent,
                "agreement_end": agr.end_date if agr else None,
                "days_remaining": agr.days_remaining if agr else None,
                "tenant_id": tenant.id
            })
            
        tenant_type_residential = db.query(Tenant).filter(Tenant.tenant_type == 'Residential').count()
        tenant_type_commercial = db.query(Tenant).filter(Tenant.tenant_type == 'Commercial').count()

        charges_total_due = db.query(func.sum(RentCharge.total_due)).scalar() or 0.0
        charges_total_paid = db.query(func.sum(RentCharge.amount_paid)).scalar() or 0.0
        charges_outstanding = db.query(func.sum(RentCharge.balance)).scalar() or 0.0

        # ---- Alerts ----
        alerts = []
        # Expiring agreements (within 30 days)
        for a in agreements:
            if a.days_remaining is not None and 0 <= a.days_remaining <= 30:
                t = db.query(Tenant).filter(Tenant.id == a.tenant_id).first()
                alerts.append({
                    "type": "warning",
                    "icon": "clock",
                    "message": f"Agreement {a.id} for {t.name if t else 'Unknown'} (Unit {a.unit_no}) expires in {a.days_remaining} days",
                    "link": f"/agreements/{a.id}",
                })
        # Expired agreements still marked Active
        for a in agreements:
            if a.days_remaining is not None and a.days_remaining < 0:
                t = db.query(Tenant).filter(Tenant.id == a.tenant_id).first()
                alerts.append({
                    "type": "danger",
                    "icon": "alert",
                    "message": f"Agreement {a.id} for {t.name if t else 'Unknown'} (Unit {a.unit_no}) has expired ({abs(a.days_remaining)} days ago)",
                    "link": f"/agreements/{a.id}",
                })
        # Overdue rent charges
        overdue = db.query(RentCharge).filter(RentCharge.payment_status.in_(["Pending", "Partial"])).all()
        for c in overdue:
            alerts.append({
                "type": "danger",
                "icon": "rupee",
                "message": f"Overdue rent for {c.tenant_name or 'Unknown'} - {c.month} (Balance: {c.balance:,.0f})",
                "link": "/rent",
            })
        # Open follow-ups from communication log
        open_comms = db.query(CommunicationLog).filter(
            CommunicationLog.status == "Open",
            CommunicationLog.follow_up_date != None,
            CommunicationLog.follow_up_date <= date.today()
        ).all()
        for c in open_comms:
            t = db.query(Tenant).filter(Tenant.id == c.tenant_id).first()
            alerts.append({
                "type": "warning",
                "icon": "chat",
                "message": f"Follow-up due for {t.name if t else 'Unknown'}: {c.subject}",
                "link": "/communications",
            })

        context = {
            "request": request,
            "units_total": units_total,
            "units_occupied": units_occupied,
            "units_vacant": units_vacant,
            "occupancy_pct": round(occupancy_pct, 2),
            "monthly_rent_active": monthly_rent_active,
            "deposits_held": deposits_held,
            "active_tenants_count": active_tenants_count,
            "inactive_tenants_count": inactive_tenants_count,
            "total_tenants": total_tenants,
            "active_agreements_count": active_agreements_count,
            "expired_agreements_count": expired_agreements_count,
            "expiring_soon_count": expiring_soon_count,
            "data_issues_count": data_issues_count,
            "active_tenants_list": active_tenants_list,
            "tenant_type_residential": tenant_type_residential,
            "tenant_type_commercial": tenant_type_commercial,
            "charges_total_due": charges_total_due,
            "charges_total_paid": charges_total_paid,
            "charges_outstanding": charges_outstanding,
            "alerts": alerts,
        }
        return request.app.state.templates.TemplateResponse("dashboard.html", context)
    finally:
        db.close()
