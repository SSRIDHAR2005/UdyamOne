import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from app.database import Base

def get_utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime, default=get_utc_now)
    expires_at = Column(DateTime)
    
    # Business Details
    business_name = Column(String(255), nullable=False)
    business_type = Column(String(100))
    segment = Column(String(100))  # micro, prof, multi, mfg
    city = Column(String(100))
    city_tier = Column(Integer, default=1)
    pincode = Column(String(10))
    employee_count = Column(Integer, default=1)
    num_sites = Column(Integer, default=1)
    has_gstin = Column(Boolean, default=False)
    gstin = Column(String(20), nullable=True)

    # Bundle & Pricing
    tier_name = Column(String(50))  # Essential, Growth, Advanced, Custom
    selected_products = Column(JSON)  # List of product configurations with quantities
    monthly_recurring_inr = Column(Float, nullable=False)
    one_time_setup_inr = Column(Float, default=0.0)
    calculated_savings_inr = Column(Float, default=0.0)
    contract_months = Column(Integer, default=12)
    terms_accepted = Column(Boolean, default=False)
    status = Column(String(50), default="GENERATED")  # GENERATED, ACCEPTED, ABANDONED, EXPIRED

class KYCVerification(Base):
    __tablename__ = "kyc_verifications"

    id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime, default=get_utc_now)
    quote_id = Column(String(64), nullable=True, index=True)
    
    # Business identification submitted
    business_name = Column(String(255))
    gstin = Column(String(20), nullable=True)
    udyam_number = Column(String(30), nullable=True)
    applicant_name = Column(String(150), nullable=True)
    applicant_role = Column(String(100), nullable=True)

    # DPDP Consent
    consent_given = Column(Boolean, default=False)
    consent_version = Column(String(50))
    consent_timestamp = Column(DateTime, nullable=True)
    consent_purposes = Column(JSON)  # granular purpose map

    # Mock registry lookups
    gstin_lookup_result = Column(JSON, nullable=True)
    udyam_lookup_result = Column(JSON, nullable=True)

    # Document extraction & validation
    documents_uploaded = Column(JSON)  # list of uploaded file metadata
    ocr_extracted_data = Column(JSON)
    validation_checks = Column(JSON)  # check results with pass/fail reasons
    overall_status = Column(String(50), default="PENDING")  # PASS, REVIEW_REQUIRED, FAILED
    decision_notes = Column(Text, nullable=True)

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(64), primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    quote_id = Column(String(64), ForeignKey("quotes.id"), nullable=False)
    kyc_id = Column(String(64), ForeignKey("kyc_verifications.id"), nullable=True)
    
    # Customer Details
    business_name = Column(String(255))
    contact_name = Column(String(150))
    contact_phone = Column(String(20))
    contact_email = Column(String(150))
    installation_address = Column(Text)
    city = Column(String(100))
    pincode = Column(String(10))

    # Pricing snapshot
    monthly_amount_inr = Column(Float)
    setup_charges_inr = Column(Float)
    items_summary = Column(JSON)

    # Status & Timeline
    # Statuses: PLACED, KYC_VERIFIED, CONFIRMED, FEASIBILITY_CHECKED, INSTALLATION_SCHEDULED, INSTALLATION_IN_PROGRESS, ACTIVATED
    current_status = Column(String(50), default="PLACED")
    status_history = Column(JSON)  # list of {stage, timestamp, note, completed}
    
    assigned_technician = Column(String(100), default="Airtel Field Engineer Team")
    technician_contact = Column(String(50), default="+91 1800-103-4444")
    estimated_activation_date = Column(DateTime)
    confirmed_appointment_date = Column(DateTime, nullable=True)
    delay_alert = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

class PartnerLeadInteraction(Base):
    __tablename__ = "partner_lead_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(String(50), index=True)
    created_at = Column(DateTime, default=get_utc_now)
    partner_id = Column(String(50), default="PARTNER-DEL-01")
    action_type = Column(String(50))  # CALL, VISIT_SCHEDULED, RECOVERY_LINK_SENT, ASSIGNED, STATUS_CHANGE
    outcome = Column(String(100))
    notes = Column(Text)
    assigned_to = Column(String(100), nullable=True)

