import pytest
import datetime
from app.services.catalogue_service import catalogue_service
from app.services.pricing_service import pricing_service
from app.services.kyc_service import kyc_service
from app.services.ocr_service import ocr_service
from app.services.advisor_service import advisor_service
from app.services.order_service import order_service
from app.services.lead_scoring_service import lead_scoring_service
from app.services.analytics_service import analytics_service
from app.schemas.domain import ProductSelection, AdvisorRequest

def test_catalogue_loaded():
    products = catalogue_service.get_all_products()
    assert len(products) == 25, f"Expected 25 products, got {len(products)}"
    p01 = catalogue_service.get_product("P01")
    assert p01["product_name"] == "Biz Fibre 100"
    assert p01["price_inr_per_month"] == 999.0

def test_catalogue_eligibility_and_dependencies():
    # P09 (Backup 4G/5G) requires one of P01|P02|P03|P05|P06
    check_no_dep = catalogue_service.check_eligibility(
        product_id="P09",
        city_tier=1,
        employee_count=5,
        num_sites=1,
        has_gstin=True,
        selected_product_ids=[]
    )
    assert not check_no_dep["eligible"]
    assert any("prerequisite connectivity" in r for r in check_no_dep["reasons"])

    check_with_dep = catalogue_service.check_eligibility(
        product_id="P09",
        city_tier=1,
        employee_count=5,
        num_sites=1,
        has_gstin=True,
        selected_product_ids=["P01"]
    )
    assert check_with_dep["eligible"]

    # P06 (Internet Leased Line 100) requires GSTIN=Y and min_employees=25
    check_no_gst = catalogue_service.check_eligibility(
        product_id="P06",
        city_tier=1,
        employee_count=10,
        num_sites=1,
        has_gstin=False
    )
    assert not check_no_gst["eligible"]
    assert any("Requires valid, active GSTIN" in r for r in check_no_gst["reasons"])
    assert any("Requires minimum 25 employees" in r for r in check_no_gst["reasons"])

def test_pricing_calculation_and_gst():
    biz = {
        "business_name": "Test Enterprise",
        "segment": "micro",
        "city": "Bengaluru",
        "city_tier": 1,
        "employee_count": 2,
        "num_sites": 1,
        "has_gstin": True
    }
    # P01 (999/mo, 0 setup) + P07 (299/mo, 0 setup, qty 2)
    selected = [
        ProductSelection(product_id="P01", quantity=1),
        ProductSelection(product_id="P07", quantity=2)
    ]
    quote = pricing_service.calculate_quote(biz, selected)
    
    expected_mrc = 999.0 + (299.0 * 2)  # 1597.0
    assert quote["monthly_recurring_inr"] == expected_mrc
    assert quote["applicable_gst_amount_monthly"] == round((expected_mrc * 18.0) / 100.0, 2)
    assert quote["contract_months"] == 12
    assert "UDY-QUO-2026-" in quote["quote_id"]

def test_mock_gstin_lookup_and_statuses():
    # Active GSTIN (K02)
    res_active = kyc_service.lookup_gstin("19EOGXH4115Y1ZL")
    assert res_active["found"]
    assert res_active["valid"]
    assert res_active["status"] == "Active"

    # Cancelled GSTIN (K01)
    res_cancelled = kyc_service.lookup_gstin("37IHKXV5167L1ZS")
    assert res_cancelled["found"]
    assert not res_cancelled["valid"]
    assert res_cancelled["status"] == "Cancelled"

    # Suspended GSTIN
    res_suspended = kyc_service.lookup_gstin("23QYBXS1811Q1ZD")
    assert res_suspended["found"]
    assert not res_suspended["valid"]
    assert res_suspended["status"] == "Suspended"

    # Format validator accepts 'X' as 4th char of PAN
    valid_pan_x = kyc_service.validate_gstin_format("27XUIXG0767D1ZP")
    assert valid_pan_x["valid"]

def test_mock_udyam_lookup():
    res = kyc_service.lookup_udyam("UDYAM-WB-00-5053330")
    assert res["found"]
    assert res["valid"]
    assert res["data"]["enterprise_name"] == "Harmony Dental Care"

def test_kyc_validation_planted_scenarios():
    # Test K02: Clean Valid Pass
    ocr_k02 = ocr_service.extract_document_fields("K02_gst_certificate.png")
    eval_k02 = kyc_service.evaluate_kyc(
        business_name="Harmony Dental Care",
        applicant_name="Joseph Shah",
        applicant_role="Managing Partner",
        gstin="19EOGXH4115Y1ZL",
        udyam_number="UDYAM-WB-00-5053330",
        consent_given=True,
        uploaded_documents=[
            {"doc_type": "gst_certificate"},
            {"doc_type": "udyam_certificate"},
            {"doc_type": "signatory_id"},
            {"doc_type": "address_proof"}
        ],
        ocr_extracted_data={"address_bill_date": "2026-05-22", "trade_name": "Harmony Dental Care"}
    )
    assert eval_k02["overall_status"] == "PASS"

    # Test K01: Cancelled GSTIN
    eval_k01 = kyc_service.evaluate_kyc(
        business_name="Vindhya Tours & Travels",
        applicant_name="Neha Kaur",
        applicant_role="Owner",
        gstin="37IHKXV5167L1ZS",
        consent_given=True,
        uploaded_documents=[
            {"doc_type": "gst_certificate"},
            {"doc_type": "signatory_id"},
            {"doc_type": "address_proof"}
        ]
    )
    assert eval_k01["overall_status"] == "FAILED"
    assert any("CANCELLED" in iss for iss in eval_k01["detected_issues"])

    # Test K11: Expired Address Proof (>90 days from 2026-07-15)
    eval_k11 = kyc_service.evaluate_kyc(
        business_name="Trinity Bake House Pvt Ltd",
        applicant_name="Vikram Pillai",
        applicant_role="Owner",
        gstin="03KGZXT1320R1ZZ",
        consent_given=True,
        uploaded_documents=[
            {"doc_type": "gst_certificate"},
            {"doc_type": "signatory_id"},
            {"doc_type": "address_proof"}
        ],
        ocr_extracted_data={"address_bill_date": "2025-10-31"}  # 257 days old
    )
    assert eval_k11["overall_status"] == "REVIEW_REQUIRED"
    assert any("expired" in iss.lower() for iss in eval_k11["detected_issues"])

def test_dpdp_consent_enforcement():
    eval_no_consent = kyc_service.evaluate_kyc(
        business_name="Any Business",
        applicant_name="Any User",
        applicant_role="Proprietor",
        consent_given=False
    )
    assert eval_no_consent["overall_status"] in ["REVIEW_REQUIRED", "FAILED"]
    assert any("consent is missing" in iss.lower() for iss in eval_no_consent["detected_issues"])

def test_predictive_lead_scoring():
    meta = lead_scoring_service.metrics
    assert meta["roc_auc"] >= 0.65, f"Expected ROC-AUC >= 0.65, got {meta['roc_auc']}"
    assert meta["recall"] >= 0.50

    # Prediction test
    lead_pred = lead_scoring_service.predict_lead({
        "city_tier": 1,
        "employee_count": 8,
        "num_sites": 1,
        "has_gstin": "Y",
        "has_udyam": "Y",
        "monthly_telecom_spend_inr": 4500,
        "lead_source": "Referral",
        "segment": "prof"
    })
    assert lead_pred["lead_priority"] in ["HIGH", "MEDIUM"]
    assert len(lead_pred["key_factors"]) > 0

def test_executive_analytics_funnel_numbers():
    funnel = analytics_service.get_funnel_and_kpis()["historical_funnel"]
    assert funnel["total_leads"] == 5000
    assert funnel["contacted"] == 3406
    assert funnel["needs_assessed"] == 1974
    assert funnel["quote_accepted"] == 861
    assert funnel["kyc_complete"] == 588
    assert funnel["activated"] == 368

def test_order_activation_lifecycle():
    mock_quote = {
        "quote_id": "TEST-QUO-001",
        "business_name": "Test Clinic",
        "monthly_recurring_inr": 2500.0,
        "one_time_setup_inr": 0.0,
        "items": [{"product_name": "Biz Fibre 100", "quantity": 1, "typical_install_days": 5}]
    }
    cust = {"business_name": "Test Clinic", "city": "Jaipur"}
    before_create = datetime.datetime.now().astimezone()
    ord_obj = order_service.create_order(mock_quote, "KYC-001", cust)
    created_at = datetime.datetime.fromisoformat(ord_obj["created_at"])
    target_at = datetime.datetime.fromisoformat(ord_obj["estimated_activation_date"])
    assert abs((created_at - before_create).total_seconds()) < 5
    assert target_at - created_at == datetime.timedelta(days=5)
    assert ord_obj["monthly_amount_inr"] == mock_quote["monthly_recurring_inr"]
    assert ord_obj["current_status"] == "KYC_VERIFIED"

    # Advance stage
    updated = order_service.update_order_status(ord_obj["order_id"], "ACTIVATED", "Line active")
    assert updated["current_status"] == "ACTIVATED"
    assert datetime.datetime.fromisoformat(updated["activated_at"]) <= datetime.datetime.now().astimezone()
