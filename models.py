"""SQLAlchemy ORM models for the Rental Management System."""
from sqlalchemy import (
    Column, String, Integer, Float, Date, DateTime, Text, ForeignKey, Boolean, JSON
)
from sqlalchemy.orm import relationship
from database import Base
from datetime import date, datetime


class Unit(Base):
    __tablename__ = "units"
    id = Column(String(20), primary_key=True)            # UNIT-001
    unit_no = Column(String(50), unique=True, nullable=False)
    floor = Column(String(30))
    description = Column(Text)
    occupancy_status = Column(String(20), default="Vacant")  # Occupied / Vacant
    residences = relationship("Residence", back_populates="unit")
    utility_charges = relationship("UtilityCharge", back_populates="unit")


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String(20), primary_key=True)             # TEN-001
    name = Column(String(100), nullable=False)
    father_name = Column(String(100))                      # Father's / Husband's name
    phone = Column(String(20))
    alt_phone = Column(String(20))
    email = Column(String(100))
    permanent_address = Column(Text)
    current_address = Column(Text)
    full_address = Column(Text)                            # Complete address from agreement
    id_proof_type = Column(String(30))
    id_proof_submitted = Column(String(5))
    id_proof_ref = Column(String(50))
    tenant_type = Column(String(20))                       # Residential / Commercial
    num_occupants = Column(Integer)
    emergency_contact = Column(String(100))
    emergency_phone = Column(String(20))
    current_unit = Column(String(50))
    current_status = Column(String(20), default="Active")  # Active / Inactive
    notes = Column(Text)
    residences = relationship("Residence", back_populates="tenant")
    deposits = relationship("Deposit", back_populates="tenant")


class Residence(Base):
    __tablename__ = "residences"
    id = Column(String(20), primary_key=True)              # RES-001
    tenant_id = Column(String(20), ForeignKey("tenants.id"), nullable=False)
    unit_id = Column(String(20), ForeignKey("units.id"))
    unit_no = Column(String(50))
    floor = Column(String(30))
    period_no = Column(Integer, default=1)
    move_in = Column(Date)
    move_out = Column(Date)
    monthly_rent = Column(Float, default=0)
    security_deposit = Column(Float, default=0)
    reason_leaving = Column(Text)
    source_file = Column(Text)
    remarks = Column(Text)
    tenant = relationship("Tenant", back_populates="residences")
    unit = relationship("Unit", back_populates="residences")
    agreements = relationship("RentalAgreement", back_populates="residence")
    deposits_list = relationship("Deposit", back_populates="residence")
    rent_charges = relationship("RentCharge", back_populates="residence")

    @property
    def duration_days(self):
        end = self.move_out or date.today()
        return (end - self.move_in).days if self.move_in else 0

    @property
    def duration_months(self):
        return round(self.duration_days / 30.44, 1)

    @property
    def is_active(self):
        return self.move_out is None


class RentalAgreement(Base):
    __tablename__ = "rental_agreements"
    id = Column(String(20), primary_key=True)              # AGR-001
    tenant_id = Column(String(20), ForeignKey("tenants.id"))
    residence_id = Column(String(20), ForeignKey("residences.id"))
    unit_no = Column(String(50))
    landlord = Column(String(100))
    agreement_date = Column(Date)                          # Date of signing
    start_date = Column(Date)
    end_date = Column(Date)
    lease_months = Column(Integer)                         # 11 months etc.
    monthly_rent = Column(Float, default=0)
    security_deposit = Column(Float, default=0)
    advance_rent = Column(Float)
    rent_due_date = Column(String(50))
    permitted_use = Column(String(200))                    # "Electronic Repair Shop", etc.
    stamp_paper_value = Column(Float)                      # ₹200, ₹500
    stamp_paper_grn = Column(String(100))                  # GRN reference
    late_interest_rate = Column(Float)                     # 12.0 (percent per annum)
    notice_period = Column(String(50))                     # "1 month" or null
    signature_status = Column(String(100))                 # "Both signed", "Tenant unsigned"
    renewal_status = Column(String(30))
    agreement_status = Column(String(20), default="Active")  # Active / Expired
    doc_reference = Column(Text)
    source_file = Column(Text)
    remarks = Column(Text)
    residence = relationship("Residence", back_populates="agreements")
    agreement_witnesses = relationship("AgreementWitness", back_populates="agreement")

    @property
    def days_remaining(self):
        if self.end_date:
            return (self.end_date - date.today()).days
        return None

    @property
    def is_expiring_soon(self):
        d = self.days_remaining
        return d is not None and 0 <= d <= 90


class Witness(Base):
    __tablename__ = "witnesses"
    id = Column(String(20), primary_key=True)              # WIT-001
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    id_type = Column(String(30))
    id_ref = Column(String(50))
    agreement_witnesses = relationship("AgreementWitness", back_populates="witness")


class AgreementWitness(Base):
    __tablename__ = "agreement_witnesses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agreement_id = Column(String(20), ForeignKey("rental_agreements.id"), nullable=False)
    witness_id = Column(String(20), ForeignKey("witnesses.id"), nullable=False)
    tenant_id = Column(String(20))
    tenant_name = Column(String(100))
    residence_id = Column(String(20))
    role = Column(String(30))
    date = Column(Date)
    source_file = Column(Text)
    remarks = Column(Text)
    agreement = relationship("RentalAgreement", back_populates="agreement_witnesses")
    witness = relationship("Witness", back_populates="agreement_witnesses")


class Deposit(Base):
    __tablename__ = "deposits"
    id = Column(String(20), primary_key=True)              # DEP-001
    tenant_id = Column(String(20), ForeignKey("tenants.id"), nullable=False)
    residence_id = Column(String(20), ForeignKey("residences.id"))
    unit_no = Column(String(50))
    security_deposit = Column(Float, default=0)
    deposit_date = Column(Date)
    advance_rent = Column(Float)
    advance_date = Column(Date)
    adjusted = Column(String(50))
    refund_date = Column(Date)
    refund_amount = Column(Float)
    remaining = Column(Float)
    status = Column(String(20), default="Unknown")
    source_file = Column(Text)
    remarks = Column(Text)
    tenant = relationship("Tenant", back_populates="deposits")
    residence = relationship("Residence", back_populates="deposits_list")


class RentCharge(Base):
    __tablename__ = "rent_charges"
    id = Column(String(20), primary_key=True)              # CHG-001
    residence_id = Column(String(20), ForeignKey("residences.id"))
    month = Column(String(20))
    unit_no = Column(String(50))
    tenant_id = Column(String(20), ForeignKey("tenants.id"))
    tenant_name = Column(String(100))
    monthly_rent = Column(Float, default=0)
    prev_arrears = Column(Float, default=0)
    other_charges = Column(Float, default=0)
    late_fee = Column(Float, default=0)
    total_due = Column(Float, default=0)
    amount_paid = Column(Float, default=0)
    balance = Column(Float, default=0)
    payment_date = Column(Date)
    payment_method = Column(String(30))
    receipt_no = Column(String(50))
    payment_status = Column(String(20), default="Pending")
    late_days = Column(Integer)
    source_file = Column(Text)
    original_ref = Column(Text)
    remarks = Column(Text)
    residence = relationship("Residence", back_populates="rent_charges")


class UtilityCharge(Base):
    __tablename__ = "utility_charges"
    id = Column(String(20), primary_key=True)              # UTL-001
    unit_id = Column(String(20), ForeignKey("units.id"))
    tenant_name = Column(String(100))
    month = Column(String(20))
    prev_reading = Column(Float)
    curr_reading = Column(Float)
    units_consumed = Column(Float)
    elec_rate = Column(Float)
    elec_amount = Column(Float)
    water_charge = Column(Float)
    maintenance_charge = Column(Float)
    parking_charge = Column(Float)
    other_charge = Column(Float)
    total_charges = Column(Float, default=0)
    amount_paid = Column(Float, default=0)
    balance = Column(Float, default=0)
    payment_date = Column(Date)
    payment_method = Column(String(30))
    remarks = Column(Text)
    unit = relationship("Unit", back_populates="utility_charges")


class BuildingExpense(Base):
    __tablename__ = "building_expenses"
    id = Column(String(20), primary_key=True)              # EXP-001
    date = Column(Date)
    category = Column(String(50))
    description = Column(Text)
    unit_or_area = Column(String(50))
    vendor = Column(String(100))
    amount = Column(Float, default=0)
    payment_method = Column(String(30))
    receipt_no = Column(String(50))
    paid_by = Column(String(100))
    source_file = Column(Text)
    remarks = Column(Text)


class DataIssue(Base):
    __tablename__ = "data_issues"
    id = Column(String(20), primary_key=True)              # ISS-001
    category = Column(String(50))
    description = Column(Text)
    source_file = Column(Text)
    source_record = Column(Text)
    tenant_id = Column(String(20))
    unit_no = Column(String(50))
    severity = Column(String(20))   # Critical / High / Medium / Low / Informational
    suggested_action = Column(Text)
    status = Column(String(20), default="Open")
    notes = Column(Text)


class SourceRecord(Base):
    __tablename__ = "source_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sheet_name = Column(String(50))
    row_number = Column(Integer)
    original_data = Column(Text)   # JSON string of original row


class RentRevision(Base):
    """Tracks every rent change with full history."""
    __tablename__ = "rent_revisions"
    id = Column(String(20), primary_key=True)               # REV-001
    tenant_id = Column(String(20), ForeignKey("tenants.id"), nullable=False)
    unit_no = Column(String(50))
    residence_id = Column(String(20), ForeignKey("residences.id"))
    agreement_id = Column(String(20), ForeignKey("rental_agreements.id"))
    old_rent = Column(Float, default=0)
    new_rent = Column(Float, default=0)
    effective_date = Column(Date)
    reason = Column(Text)
    approved_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    tenant = relationship("Tenant")
    residence = relationship("Residence")


class Payment(Base):
    """Records individual rent payments."""
    __tablename__ = "payments"
    id = Column(String(20), primary_key=True)               # PAY-001
    rent_charge_id = Column(String(20), ForeignKey("rent_charges.id"))
    tenant_id = Column(String(20), ForeignKey("tenants.id"), nullable=False)
    unit_no = Column(String(50))
    amount = Column(Float, default=0)
    payment_date = Column(Date)
    payment_method = Column(String(30))                      # Cash/UPI/Bank Transfer/Cheque
    receipt_no = Column(String(50))
    reference_no = Column(String(100))                       # UPI ref, cheque no
    month = Column(String(20))                               # e.g. "Sep 2026"
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    tenant = relationship("Tenant")
    rent_charge = relationship("RentCharge")


class Document(Base):
    """File uploads linked to tenants/agreements."""
    __tablename__ = "documents"
    id = Column(String(20), primary_key=True)               # DOC-001
    tenant_id = Column(String(20), ForeignKey("tenants.id"))
    agreement_id = Column(String(20), ForeignKey("rental_agreements.id"))
    unit_no = Column(String(50))
    doc_type = Column(String(50))                            # Agreement/ID Proof/Photo/Receipt/Other
    filename = Column(String(255))                           # stored filename
    original_filename = Column(String(255))                  # user's original filename
    file_path = Column(Text)                                 # relative path in documents/
    uploaded_at = Column(DateTime, default=datetime.now)
    remarks = Column(Text)
    tenant = relationship("Tenant")
    agreement = relationship("RentalAgreement")


class CommunicationLog(Base):
    """Notes, calls, complaints per tenant."""
    __tablename__ = "communication_logs"
    id = Column(String(20), primary_key=True)               # COM-001
    tenant_id = Column(String(20), ForeignKey("tenants.id"), nullable=False)
    unit_no = Column(String(50))
    log_type = Column(String(30))                            # Call/Visit/Complaint/Note/Reminder
    subject = Column(String(200))
    description = Column(Text)
    logged_at = Column(DateTime, default=datetime.now)
    follow_up_date = Column(Date)
    status = Column(String(20), default="Open")              # Open/Closed
    created_at = Column(DateTime, default=datetime.now)
    tenant = relationship("Tenant")


class MoveEvent(Base):
    """Move-in / Move-out checklists."""
    __tablename__ = "move_events"
    id = Column(String(20), primary_key=True)               # MOV-001
    tenant_id = Column(String(20), ForeignKey("tenants.id"), nullable=False)
    unit_no = Column(String(50))
    residence_id = Column(String(20), ForeignKey("residences.id"))
    event_type = Column(String(20))                          # Move-In / Move-Out
    event_date = Column(Date)
    agreement_signed = Column(Boolean, default=False)
    deposit_collected = Column(Boolean, default=False)
    keys_handed = Column(Boolean, default=False)
    meter_reading = Column(String(50))
    condition_notes = Column(Text)
    inspection_done = Column(Boolean, default=False)
    final_settlement = Column(Float)
    deposit_deductions = Column(Float, default=0)
    deposit_refund = Column(Float, default=0)
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    tenant = relationship("Tenant")
    residence = relationship("Residence")
