export interface Product {
  product_id: string;
  category: string;
  product_name: string;
  description: string;
  unit: string;
  price_min_inr_per_month: number;
  price_max_inr_per_month: number;
  price_inr_per_month: number;
  one_time_setup_inr: number;
  min_contract_months: number;
  available_city_tiers: number[];
  min_employees: number;
  min_sites: number;
  requires_gstin: boolean;
  requires_one_of: string[];
  typical_install_days: number;
  target_segments: string[];
}

export interface ProductSelection {
  product_id: string;
  quantity: number;
  is_addon?: boolean;
}

export interface RecommendedTier {
  tier_name: string;
  tagline: string;
  target_fit_reason: string;
  monthly_total_inr: number;
  one_time_setup_inr: number;
  standalone_price_inr: number;
  savings_inr: number;
  contract_months: number;
  products: any[];
  optional_addons: any[];
  why_recommended: string;
  potential_limitations?: string;
}

export interface AdvisorResponse {
  business_profile: any;
  language: string;
  summary_message: string;
  recommendations: RecommendedTier[];
  disclaimer: string;
}

export interface QuoteData {
  quote_id: string;
  created_at: string;
  expires_at: string;
  business_name: string;
  segment: string;
  city: string;
  city_tier: number;
  tier_name?: string;
  items: any[];
  monthly_recurring_inr: number;
  one_time_setup_inr: number;
  calculated_savings_inr: number;
  applicable_gst_percent: number;
  applicable_gst_amount_monthly: number;
  total_first_month_inr: number;
  contract_months: number;
  validation_warnings: string[];
  terms_and_conditions: string[];
}

export interface KYCResult {
  verification_id: string;
  overall_status: 'PASS' | 'REVIEW_REQUIRED' | 'FAILED';
  confidence_score: number;
  summary?: string;
  document_results?: Record<string, any>;
  gstin_verification: any;
  udyam_verification: any;
  document_validations?: any[];
  detected_issues: string[];
  warnings?: string[];
  corrective_actions: string[];
  recommended_next_action?: string;
  audit_trail: any[];
  disclaimer?: string;
}

export interface OrderData {
  order_id: string;
  order_number: string;
  created_at: string;
  updated_at?: string;
  current_status: string;
  status_history: {
    stage: string;
    timestamp: string | null;
    completed: boolean;
    note: string;
  }[];
  estimated_activation_date: string;
  confirmed_appointment_date: string | null;
  delay_alert: string | null;
  business_name: string;
  contact_name: string;
  installation_address: string;
  installation_address_source?: string;
  city?: string;
  pincode?: string;
  num_sites?: number;
  quote_id?: string;
  is_demo?: boolean;
  activated_at?: string | null;
  monthly_amount_inr: number;
  setup_charges_inr: number;
  assigned_technician: string;
  technician_contact: string;
  items_summary: any[];
  notifications: any[];
}

export interface LeadItem {
  lead_id: string;
  business_name: string;
  business_type: string;
  segment: string;
  city: string;
  city_tier: number;
  has_gstin: boolean;
  gstin?: string;
  monthly_telecom_spend_inr: number;
  stage_reached: string;
  outcome: string;
  drop_reason?: string;
  lead_source: string;
  lead_score: number;
  lead_priority: 'HIGH' | 'MEDIUM' | 'LOW';
  key_factors: string[];
  recommended_action: string;
}

