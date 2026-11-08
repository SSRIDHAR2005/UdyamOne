from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Advisor Schemas
class AdvisorRequest(BaseModel):
    business_name: str
    business_type: str = "retail"  # retail, clinic, restaurant, mfg, services, ca_firm, etc.
    segment: Optional[str] = None   # micro, prof, multi, mfg
    city: str = "Bengaluru"
    city_tier: int = 1
    pincode: Optional[str] = "560001"
    employee_count: int = 5
    num_sites: int = 1
    monthly_budget_inr: float = 3000.0
    current_internet: Optional[str] = "mobile_hotspot"
    current_provider: Optional[str] = "Local ISP"
    need_sims: int = 2
    need_pos: bool = True
    need_whatsapp: bool = True
    need_cctv: bool = False
    cctv_cameras_count: int = 0
    need_cloud_email: bool = False
    need_cloud_backup: bool = False
    need_security: bool = False
    need_failover_backup: bool = False
    need_dedicated_leased_line: bool = False
    has_gstin: bool = True
    gstin: Optional[str] = None
    preferred_language: str = "en"  # en, hi, ta

class ProductSelection(BaseModel):
    product_id: str
    quantity: int = 1
    is_addon: bool = False

class RecommendedTier(BaseModel):
    tier_name: str  # Essential, Growth, Advanced
    tagline: str
    target_fit_reason: str
    monthly_total_inr: float
    one_time_setup_inr: float
    standalone_price_inr: float
    savings_inr: float
    contract_months: int
    products: List[Dict[str, Any]]
    optional_addons: List[Dict[str, Any]]
    why_recommended: str
    potential_limitations: Optional[str] = None

class AdvisorResponse(BaseModel):
    business_profile: Dict[str, Any]
    language: str
    summary_message: str
    recommendations: List[RecommendedTier]
    disclaimer: str

# Voice Transcript Schemas
class VoiceTranscriptRequest(BaseModel):
    transcript: str
    language: str = "en"  # en, hi, ta

class ExtractedBusinessProfile(BaseModel):
    business_name: str
    business_category: str
    operating_city: str
    city_tier: int = 1
    number_of_sites: int = 1
    employee_count: int = 3
    requirements: List[str] = Field(default_factory=list)
    monthly_budget: float = 3000.0
    currency: str = "INR"
    business_type: str = "retail"
    segment: str = "micro"
    has_gstin: bool = False
    gstin: Optional[str] = None
    pincode: Optional[str] = "600001"
    need_sims: int = 2
    need_pos: bool = False
    need_whatsapp: bool = False
    need_cctv: bool = False
    cctv_cameras_count: int = 0
    need_cloud_email: bool = False
    need_cloud_backup: bool = False
    need_security: bool = False
    need_failover_backup: bool = False
    need_dedicated_leased_line: bool = False

class VoiceTranscriptResponse(BaseModel):
    original_transcript: str
    language: str
    extracted_profile: ExtractedBusinessProfile
    matched_catalogue_products: List[Dict[str, Any]] = Field(default_factory=list)
    unmatched_requirements: List[str] = Field(default_factory=list)
    advisor_request_payload: Dict[str, Any]
    recommendations: AdvisorResponse

# Quote Schemas
class CreateQuoteRequest(BaseModel):
    business_name: str
    business_type: str
    segment: str
    city: str
    city_tier: int
    pincode: Optional[str] = None
    employee_count: int
    num_sites: int
    has_gstin: bool
    gstin: Optional[str] = None
    tier_name: str
    selected_products: List[ProductSelection]
    custom_gst_percent: Optional[float] = None

class QuoteResponse(BaseModel):
    quote_id: str
    created_at: str
    expires_at: str
    business_name: str
    segment: str
    city: str
    city_tier: int
    num_sites: int = 1
    items: List[Dict[str, Any]]
    monthly_recurring_inr: float
    one_time_setup_inr: float
    calculated_savings_inr: float
    applicable_gst_percent: float = 18.0
    applicable_gst_amount_monthly: float
    applicable_gst_amount_setup: Optional[float] = 0.0
    tax_treatment: Optional[str] = "assumed_standard_telecom_gst"
    tax_disclosure: Optional[str] = None
    hsn_sac_category: Optional[str] = None
    total_first_month_inr: float
    contract_months: int
    validation_warnings: List[str]
    terms_and_conditions: List[str]

# KYC Schemas
class DPDPUserConsent(BaseModel):
    consent_given: bool
    version: str = "DPDP-2026-V1.0"
    purposes: Dict[str, bool]  # e.g. {"gstin_lookup": True, "udyam_verification": True, "telecom_kyc_compliance": True}
    applicant_name: str

class MockLookupRequest(BaseModel):
    identifier: str

class KYCSubmitRequest(BaseModel):
    quote_id: Optional[str] = None
    business_name: str
    gstin: Optional[str] = None
    udyam_number: Optional[str] = None
    applicant_name: str
    applicant_role: str
    consent: DPDPUserConsent
    identifiers_confirmed: bool = False

class KYCValidationResult(BaseModel):
    verification_id: str
    overall_status: str  # PASS, REVIEW_REQUIRED, FAILED
    confidence_score: float
    gstin_verification: Dict[str, Any]
    udyam_verification: Dict[str, Any]
    document_validations: List[Dict[str, Any]]
    detected_issues: List[str]
    corrective_actions: List[str]
    audit_trail: List[Dict[str, Any]]

# Order Schemas
class CreateOrderRequest(BaseModel):
    quote_id: str
    kyc_id: Optional[str] = None
    business_name: str
    contact_name: str
    contact_phone: str
    contact_email: str
    installation_address: str
    installation_address_source: Optional[str] = None
    city: str
    pincode: str
    payment_method: str = "SIMULATED_MANDATE"

class OrderStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    assigned_technician: Optional[str] = None

class OrderResponse(BaseModel):
    order_id: str
    order_number: str
    created_at: str
    updated_at: Optional[str] = None
    current_status: str
    status_history: List[Dict[str, Any]]
    estimated_activation_date: str
    confirmed_appointment_date: Optional[str] = None
    delay_alert: Optional[str] = None
    business_name: str
    contact_name: str
    installation_address: str
    installation_address_source: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    num_sites: int = 1
    quote_id: Optional[str] = None
    is_demo: bool = False
    activated_at: Optional[str] = None
    monthly_amount_inr: float
    setup_charges_inr: float
    assigned_technician: str
    technician_contact: str
    items_summary: List[Dict[str, Any]]

