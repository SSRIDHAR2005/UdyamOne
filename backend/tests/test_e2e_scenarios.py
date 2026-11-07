import pytest
from app.services.advisor_service import advisor_service
from app.services.pricing_service import pricing_service
from app.services.kyc_service import kyc_service
from app.schemas.domain import AdvisorRequest, ProductSelection

def test_kirana_micro_scenario():
    # 1. Kirana persona
    req = AdvisorRequest(
        business_name="Gupta Provision Store",
        business_type="kirana",
        segment="micro",
        city="Varanasi",
        city_tier=2,
        employee_count=3,
        num_sites=1,
        has_gstin=False,
        monthly_budget_inr=2000.0,
        need_pos=True,
        need_whatsapp=True
    )
    recs = advisor_service.recommend_bundles(req)
    assert len(recs.recommendations) == 3
    essential_tier = recs.recommendations[0]
    assert essential_tier.tier_name == "Essential"
    assert essential_tier.monthly_total_inr <= 2500
    
    # 2. Quote calculation
    selections = [
        ProductSelection(product_id=p["product_id"], quantity=p["quantity"], is_addon=False)
        for p in essential_tier.products
    ]
    quote = pricing_service.calculate_quote(
        business_details=req.model_dump(),
        selected_products=selections,
        tier_name="Essential"
    )
    assert quote["monthly_recurring_inr"] > 0
    assert quote["applicable_gst_percent"] == 18.0

    # 3. Micro business KYC without GSTIN (allowed for micro tier)
    kyc_eval = kyc_service.evaluate_kyc(
        business_name="Gupta Provision Store",
        applicant_name="Ram Gupta",
        applicant_role="Owner",
        gstin=None,
        udyam_number=None,
        consent_given=True,
        uploaded_documents=[
            {"doc_type": "signatory_id"},
            {"doc_type": "address_proof"}
        ]
    )
    assert kyc_eval["overall_status"] == "PASS"

def test_clinic_professional_scenario():
    # 1. Clinic persona
    req = AdvisorRequest(
        business_name="Arogya Polyclinic",
        business_type="clinic",
        segment="prof",
        city="Bengaluru",
        city_tier=1,
        employee_count=8,
        num_sites=1,
        has_gstin=True,
        gstin="29HLDXH5566X1ZB",
        monthly_budget_inr=5000.0,
        need_cloud_email=True,
        need_security=True
    )
    recs = advisor_service.recommend_bundles(req)
    growth_tier = recs.recommendations[1]
    assert growth_tier.tier_name == "Growth"
    growth_pids = [p["product_id"] for p in growth_tier.products]
    assert "P02" in growth_pids or "P16" in growth_pids or "P20" in growth_pids

def test_restaurant_multisite_scenario():
    # 1. Restaurant 3-site persona
    req = AdvisorRequest(
        business_name="Flavors of Malabar",
        business_type="restaurant",
        segment="multi",
        city="Kochi",
        city_tier=2,
        employee_count=22,
        num_sites=3,
        has_gstin=True,
        gstin="32TZAXB5481U1Z1",
        monthly_budget_inr=10000.0,
        need_failover_backup=True,
        need_cctv=True
    )
    recs = advisor_service.recommend_bundles(req)
    adv_tier = recs.recommendations[2]
    assert adv_tier.tier_name == "Advanced"
    pids = [p["product_id"] for p in adv_tier.products]
    assert "P03" in pids or "P02" in pids or "P09" in pids

def test_manufacturer_leased_line_scenario():
    # 1. Auto manufacturer persona
    req = AdvisorRequest(
        business_name="Precision Auto Component Works",
        business_type="manufacturing",
        segment="mfg",
        city="Pune",
        city_tier=1,
        employee_count=35,
        num_sites=1,
        has_gstin=True,
        gstin="27XUIXG0767D1ZP",
        monthly_budget_inr=25000.0,
        need_dedicated_leased_line=True,
        need_security=True
    )
    recs = advisor_service.recommend_bundles(req)
    adv_tier = recs.recommendations[2]
    pids = [p["product_id"] for p in adv_tier.products]
    assert "P05" in pids or "P06" in pids or "P21" in pids
