import pytest
from app.services.kyc_service import kyc_service
from app.services.ocr_service import ocr_service

# Complete test suite for all 12 student specimen applicants (K01 to K12)
SPECIMEN_CASES = [
    {
        "id": "K01",
        "business_name": "Vindhya Tours & Travels",
        "applicant_name": "Neha Kaur",
        "applicant_role": "Proprietor",
        "gstin": "37IHKXV5167L1ZS",
        "udyam": "",  # Missing Udyam number on certificate
        "expected_status": "FAILED",
        "expected_issue_substr": "CANCELLED"
    },
    {
        "id": "K02",
        "business_name": "Harmony Dental Care",
        "applicant_name": "Joseph Shah",
        "applicant_role": "Managing Partner",
        "gstin": "19EOGXH4115Y1ZL",
        "udyam": "UDYAM-WB-00-5053330",
        "expected_status": "PASS",
        "expected_issue_substr": None
    },
    {
        "id": "K03",
        "business_name": "Ganesh Woodcraft",
        "applicant_name": "Joseph Singh",
        "applicant_role": "Owner",
        "gstin": "27XUIXG0767D1ZP",
        "udyam": "UDYAM-MH-00-9516696",
        "expected_status": "PASS",
        "expected_issue_substr": None
    },
    {
        "id": "K04",
        "business_name": "Saffron Dental Care LLP",
        "applicant_name": "Fatima Pillai",
        "applicant_role": "Partner",
        "gstin": "27PZSXS1936O1ZH",
        "udyam": "UDYAM-MH-00-6131836",
        "expected_status": "FAILED",
        "expected_issue_substr": "corrupted"  # Blank/incomplete GST cert
    },
    {
        "id": "K05",
        "business_name": "Balaji Realty LLP",
        "applicant_name": "Anita Shah",
        "applicant_role": "Owner",
        "gstin": "32TZAXB5481U1Z1",
        "udyam": "UDYAM-KL-00-5521886",
        "expected_status": "REVIEW_REQUIRED",
        "expected_issue_substr": "missing"  # Missing Udyam document file
    },
    {
        "id": "K06",
        "business_name": "Saffron Unisex Salon",
        "applicant_name": "Pooja Shah",
        "applicant_role": "Owner",
        "gstin": "08YKZXS5189L1ZO",
        "udyam": "UDYAM-RJ-00-6577157",
        "expected_status": "PASS",
        "expected_issue_substr": None
    },
    {
        "id": "K07",
        "business_name": "Shri Physio Clinic",  # Application name
        "applicant_name": "Neha Banerjee",
        "applicant_role": "Manager",
        "gstin": "07CPCXN0398P1ZT",
        "udyam": "UDYAM-DL-00-9565547",
        "expected_status": "REVIEW_REQUIRED",
        "expected_issue_substr": "mismatch"  # Certificate says Neelgiri Physio Clinic
    },
    {
        "id": "K08",
        "business_name": "Green Leaf Legal Associates",
        "applicant_name": "Joseph Rao",
        "applicant_role": "Office Admin",
        "gstin": "24XORXG9365M1Z3",
        "udyam": "UDYAM-GJ-00-9158296",
        "expected_status": "PASS",
        "expected_issue_substr": None
    },
    {
        "id": "K09",
        "business_name": "Kaveri Insurance Advisors",
        "applicant_name": "Anita Kulkarni",
        "applicant_role": "Office Admin",
        "gstin": "37LDYXK0296F1ZB",
        "udyam": "UDYAM-AP-00-9751562",
        "expected_status": "PASS",
        "expected_issue_substr": None
    },
    {
        "id": "K10",
        "business_name": "Kaveri Stays LLP",
        "applicant_name": "Nisha Arora",
        "applicant_role": "Owner",
        "gstin": "27QHJXK0658U1ZL",
        "udyam": "UDYAM-MH-00-7183141",
        "expected_status": "PASS",
        "expected_issue_substr": None
    },
    {
        "id": "K11",
        "business_name": "Trinity Bake House Pvt Ltd",
        "applicant_name": "Vikram Pillai",
        "applicant_role": "Owner",
        "gstin": "03KGZXT1320R1ZZ",
        "udyam": "UDYAM-PB-00-9719478",
        "expected_status": "REVIEW_REQUIRED",
        "expected_issue_substr": "expired"  # Bill dated 2025-10-31 >90d
    },
    {
        "id": "K12",
        "business_name": "Star Electronics",
        "applicant_name": "Pooja Agarwal",
        "applicant_role": "Owner",
        "gstin": "37NBLXS1145E1ZU",
        "udyam": "UDYAM-AP-00-5186772",
        "expected_status": "PASS",
        "expected_issue_substr": None
    }
]

@pytest.mark.parametrize("case", SPECIMEN_CASES, ids=[c["id"] for c in SPECIMEN_CASES])
def test_all_12_kyc_specimens(case):
    specimen_id = case["id"]
    
    # Assemble mock uploaded documents
    doc_files = [
        f"{specimen_id}_gst_certificate.png",
        f"{specimen_id}_udyam_certificate.png",
        f"{specimen_id}_signatory_id.png",
        f"{specimen_id}_address_proof.png"
    ]
    docs_uploaded = []
    ocr_data = {}

    for df in doc_files:
        # Planted defect: K05 has no udyam certificate file
        if specimen_id == "K05" and "udyam" in df:
            continue
        
        dtype = "gst_certificate" if "gst" in df else ("udyam_certificate" if "udyam" in df else ("signatory_id" if "signatory" in df else "address_proof"))
        docs_uploaded.append({"filename": df, "doc_type": dtype})
        
        extracted = ocr_service.extract_document_fields(df, doc_type=dtype)
        ocr_data.update({k: v for k, v in extracted.items() if v is not None})

    # Planted defect: K04 is a blank GST certificate
    if specimen_id == "K04":
        ocr_data["is_corrupted_or_blank"] = True

    eval_result = kyc_service.evaluate_kyc(
        business_name=case["business_name"],
        applicant_name=case["applicant_name"],
        applicant_role=case["applicant_role"],
        gstin=case["gstin"],
        udyam_number=case["udyam"] if case["udyam"] else None,
        consent_given=True,
        uploaded_documents=docs_uploaded,
        ocr_extracted_data=ocr_data
    )

    assert eval_result["overall_status"] == case["expected_status"], (
        f"Specimen {specimen_id} expected {case['expected_status']}, got {eval_result['overall_status']}. "
        f"Issues: {eval_result['detected_issues']}"
    )

    if case["expected_issue_substr"]:
        has_expected_issue = any(
            case["expected_issue_substr"].lower() in iss.lower()
            for iss in eval_result["detected_issues"]
        )
        assert has_expected_issue, (
            f"Specimen {specimen_id} expected issue containing '{case['expected_issue_substr']}', "
            f"got issues: {eval_result['detected_issues']}"
        )
