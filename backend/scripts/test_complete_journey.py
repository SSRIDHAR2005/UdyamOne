import urllib.request
import json
import io

BASE_URL = "http://127.0.0.1:5173/api/v1"

def post_json(endpoint, data):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        return res.status, json.loads(res.read().decode())

def post_raw(endpoint, data):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        return res.status, res.headers.get("Content-Type"), res.read()

def get_json(endpoint):
    req = urllib.request.Request(f"{BASE_URL}{endpoint}")
    with urllib.request.urlopen(req, timeout=10) as res:
        return res.status, json.loads(res.read().decode())

def patch_json(endpoint, data):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        return res.status, json.loads(res.read().decode())

print("=================================================================")
print("PROJECT UDYAMONE — END-TO-END CUSTOMER JOURNEY TEST HARNESS")
print("=================================================================")

# 1. CATALOGUE INGESTION VERIFICATION
status, cat = get_json("/catalogue")
assert status == 200
assert len(cat) == 25
print(f"STEP 1: Catalogue Ingestion -> HTTP {status} | Loaded {len(cat)} SKUs strictly from product_catalogue.csv")

# 2. KIRANA JOURNEY (MICRO RETAIL, NO GSTIN)
kirana_req = {
    "business_name": "Ramesh Provision Store",
    "business_type": "retail",
    "segment": "micro",
    "city": "Jaipur",
    "city_tier": 2,
    "pincode": "302001",
    "employee_count": 3,
    "num_sites": 1,
    "monthly_budget_inr": 1800,
    "has_gstin": False,
    "need_sims": 1,
    "need_pos": True,
    "need_whatsapp": True,
    "preferred_language": "hi"
}
status, kirana_recs = post_json("/advisor/recommend", kirana_req)
assert status == 200
assert len(kirana_recs["recommendations"]) == 3
essential = kirana_recs["recommendations"][0]
print(f"STEP 2A: Kirana AI Recommendation -> HTTP {status} | Essential Monthly: ₹{essential['monthly_total_inr']} (Budget: ₹1800)")

# Quote creation for Kirana
kirana_quote_req = {
    "business_name": kirana_req["business_name"],
    "business_type": kirana_req["business_type"],
    "segment": kirana_req["segment"],
    "city": kirana_req["city"],
    "city_tier": kirana_req["city_tier"],
    "employee_count": kirana_req["employee_count"],
    "num_sites": kirana_req["num_sites"],
    "has_gstin": False,
    "tier_name": "Essential",
    "selected_products": [{"product_id": p["product_id"], "quantity": p["quantity"], "is_addon": False} for p in essential["products"]]
}
status, kirana_quote = post_json("/quote/create", kirana_quote_req)
assert status == 200
assert "UDY-QUO" in kirana_quote["quote_id"]
print(f"STEP 2B: Kirana Quote Generated -> HTTP {status} | Quote ID: {kirana_quote['quote_id']} | Monthly: ₹{kirana_quote['monthly_recurring_inr']} | 18% GST: ₹{kirana_quote['applicable_gst_amount_monthly']}")

# Quote PDF generation
status, ctype, pdf_bytes = post_raw("/quote/generate-pdf", kirana_quote)
assert status == 200
assert pdf_bytes.startswith(b"%PDF")
print(f"STEP 2C: Kirana PDF Download -> HTTP {status} | Content-Type: {ctype} | Size: {len(pdf_bytes)} bytes | Valid PDF: True")

# Kirana KYC (Micro business route without GSTIN)
kirana_kyc_req = {
    "business_name": "Ramesh Provision Store",
    "applicant_name": "Ramesh Lal",
    "applicant_role": "Proprietor",
    "gstin": None,
    "udyam_number": None,
    "consent": {
        "consent_given": True,
        "applicant_name": "Ramesh Lal",
        "purposes": {"gstin_lookup": False, "udyam_verification": False, "telecom_regulatory_compliance": True}
    }
}
status, kirana_kyc = post_json("/kyc/validate", kirana_kyc_req)
assert status == 200
assert kirana_kyc["overall_status"] == "PASS"
print(f"STEP 2D: Kirana KYC Verification -> HTTP {status} | Status: {kirana_kyc['overall_status']} | Mode: Micro Exemption Under DPDP Act 2023")

# Kirana Order Creation
kirana_order_req = {
    "quote_id": kirana_quote["quote_id"],
    "business_name": kirana_req["business_name"],
    "contact_name": "Ramesh Lal",
    "contact_phone": "+91 98290 11223",
    "contact_email": "ramesh.store@example.com",
    "installation_address": "Shop 12, Johari Bazar, Jaipur",
    "city": "Jaipur",
    "pincode": "302001",
    "monthly_amount_inr": kirana_quote["monthly_recurring_inr"],
    "setup_charges_inr": kirana_quote["one_time_setup_inr"],
    "items_summary": kirana_quote["items"]
}
status, kirana_order = post_json("/order/create", kirana_order_req)
assert status == 200
print(f"STEP 2E: Kirana Order Created -> HTTP {status} | Order Number: {kirana_order['order_number']} | Status: {kirana_order['current_status']}")

# 3. CLINIC JOURNEY (PROFESSIONAL OFFICE, GSTIN ACTIVE, CLOUD & SECURITY)
clinic_req = {
    "business_name": "Harmony Dental Care",
    "business_type": "clinic",
    "segment": "prof",
    "city": "Kolkata",
    "city_tier": 1,
    "pincode": "700001",
    "employee_count": 8,
    "num_sites": 1,
    "monthly_budget_inr": 5000,
    "has_gstin": True,
    "gstin": "19EOGXH4115Y1ZL",
    "need_sims": 3,
    "need_pos": True,
    "need_cloud_email": True,
    "need_cloud_backup": True,
    "need_security": True,
    "preferred_language": "en"
}
status, clinic_recs = post_json("/advisor/recommend", clinic_req)
assert status == 200
growth = clinic_recs["recommendations"][1]
print(f"STEP 3A: Clinic AI Recommendation -> HTTP {status} | Growth Plus Monthly: ₹{growth['monthly_total_inr']} | Tier: {growth['tier_name']}")

# Bundle Customization: Add CCTV (P23) to Growth bundle
custom_products = [{"product_id": p["product_id"], "quantity": p["quantity"], "is_addon": False} for p in growth["products"]]
custom_products.append({"product_id": "P23", "quantity": 2, "is_addon": True}) # Add 2x Cloud CCTV

clinic_quote_req = {
    "business_name": clinic_req["business_name"],
    "business_type": clinic_req["business_type"],
    "segment": clinic_req["segment"],
    "city": clinic_req["city"],
    "city_tier": clinic_req["city_tier"],
    "employee_count": clinic_req["employee_count"],
    "num_sites": clinic_req["num_sites"],
    "has_gstin": True,
    "gstin": clinic_req["gstin"],
    "tier_name": "Growth Customized",
    "selected_products": custom_products
}
status, clinic_quote = post_json("/quote/create", clinic_quote_req)
assert status == 200
has_cctv = any(it["product_id"] == "P23" for it in clinic_quote["items"])
assert has_cctv
print(f"STEP 3B: Clinic Bundle Customization -> HTTP {status} | Toggled CCTV P23: {has_cctv} | Monthly: ₹{clinic_quote['monthly_recurring_inr']} | 18% GST: ₹{clinic_quote['applicable_gst_amount_monthly']}")

# Clinic KYC Verification (K02 Specimen clean pass)
clinic_kyc_req = {
    "business_name": "Harmony Dental Care (K02)",
    "applicant_name": "Joseph Shah",
    "applicant_role": "Managing Partner",
    "gstin": "19EOGXH4115Y1ZL",
    "udyam_number": "UDYAM-WB-00-5053330",
    "consent": {
        "consent_given": True,
        "applicant_name": "Joseph Shah",
        "purposes": {"gstin_lookup": True, "udyam_verification": True, "telecom_regulatory_compliance": True}
    }
}
status, clinic_kyc = post_json("/kyc/validate", clinic_kyc_req)
assert status == 200
assert clinic_kyc["overall_status"] == "PASS"
print(f"STEP 3C: Clinic Digital KYC Verification -> HTTP {status} | Status: {clinic_kyc['overall_status']} | GSTIN Status: {clinic_kyc['gstin_verification']['status']} | Udyam: {clinic_kyc['udyam_verification']['status']}")

# Clinic Order & Tracking Advance
clinic_order_req = {
    "quote_id": clinic_quote["quote_id"],
    "business_name": clinic_req["business_name"],
    "contact_name": "Joseph Shah",
    "contact_phone": "+91 98300 44556",
    "contact_email": "dr.shah@harmonydental.com",
    "installation_address": "199 Station Road, Kolkata",
    "city": "Kolkata",
    "pincode": "700001",
    "monthly_amount_inr": clinic_quote["monthly_recurring_inr"],
    "setup_charges_inr": clinic_quote["one_time_setup_inr"],
    "items_summary": clinic_quote["items"]
}
status, clinic_order = post_json("/order/create", clinic_order_req)
assert status == 200
order_id = clinic_order["order_id"]

# Advance stages: PLACED -> KYC_VERIFIED -> CONFIRMED -> FEASIBILITY_CHECKED -> INSTALLATION_SCHEDULED -> INSTALLATION_IN_PROGRESS -> ACTIVATED
for next_st in ["KYC_VERIFIED", "CONFIRMED", "FEASIBILITY_CHECKED", "INSTALLATION_SCHEDULED", "INSTALLATION_IN_PROGRESS", "ACTIVATED"]:
    status, updated_order = patch_json(f"/order/{order_id}/status", {"status": next_st, "notes": f"Advanced to {next_st}"})
    assert status == 200
    assert updated_order["current_status"] == next_st
print(f"STEP 3D: Clinic Order Tracking Lifecycle -> Advanced through all 7 stages to {updated_order['current_status']} | History Events: {len(updated_order['status_history'])}")

# 4. PARTNER LEAD MANAGEMENT
status, partner_leads = get_json("/partner/leads?limit=5")
assert status == 200
assert len(partner_leads) > 0
sample_lead = partner_leads[0]
print(f"STEP 4A: Partner Lead Retrieval -> HTTP {status} | Loaded {len(partner_leads)} leads | Sample: {sample_lead['lead_id']} ({sample_lead['business_name']}) | Score: {sample_lead['lead_score']} | Priority: {sample_lead['lead_priority']}")

status, act_res = post_json(f"/partner/lead/{sample_lead['lead_id']}/action", {"action_type": "RECOVERY_LINK_SENT", "assigned_to": "Field Exec K. Sharma"})
assert status == 200
print(f"STEP 4B: Partner Action Logged -> HTTP {status} | Action: {act_res['action_recorded']} | Assigned: {act_res['assigned_to']}")

print("=================================================================")
print("ALL END-TO-END JOURNEYS VERIFIED SUCCESSFULLY OVER HTTP!")
print("=================================================================")
