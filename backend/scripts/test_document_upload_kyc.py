"""
UdyamOne - Test Genuine Document-Upload KYC Workflow
Tests:
1. Genuine multipart/form-data upload with all 4 clean documents (K02) -> PASS
2. Cancelled GSTIN document (K01) -> FAILED
3. Name mismatch document (K07: Shri vs Neelgiri) -> REVIEW_REQUIRED
4. Expired utility bill document (K11: >90 days old) -> REVIEW_REQUIRED
5. Corrupted/blank GST document (K04) -> FAILED
6. Invalid file extension rejection (.exe) -> HTTP 400
7. Missing consent rejection -> FAILED
8. Masked ID privacy compliance check
"""
import io
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api/v1"
DOCS_DIR = Path("backend/data/kyc_documents")

def make_multipart_request(endpoint: str, fields: dict, files: dict):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = io.BytesIO()

    # Add text fields
    for name, value in fields.items():
        if value is None:
            continue
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.write(f"{value}\r\n".encode("utf-8"))

    # Add files
    for name, (filename, content, content_type) in files.items():
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode("utf-8"))
        body.write(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
        body.write(content)
        body.write(b"\r\n")

    body.write(f"--{boundary}--\r\n".encode("utf-8"))
    payload = body.getvalue()

    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(payload))
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def run_all_tests():
    print("=" * 65)
    print("UDYAMONE GENUINE DOCUMENT-UPLOAD KYC TEST SUITE")
    print("=" * 65)

    # -------------------------------------------------------------
    # 1. Clean Pass Test (K02: Harmony Dental Care)
    # -------------------------------------------------------------
    print("\n--- TEST 1: All 4 Clean Documents (K02: Harmony Dental Care) ---")
    k02_files = {
        "gst_certificate": ("K02_gst_certificate.png", (DOCS_DIR / "K02_gst_certificate.png").read_bytes(), "image/png"),
        "udyam_certificate": ("K02_udyam_certificate.png", (DOCS_DIR / "K02_udyam_certificate.png").read_bytes(), "image/png"),
        "signatory_id": ("K02_signatory_id.png", (DOCS_DIR / "K02_signatory_id.png").read_bytes(), "image/png"),
        "address_proof": ("K02_address_proof.png", (DOCS_DIR / "K02_address_proof.png").read_bytes(), "image/png")
    }
    status, data = make_multipart_request("/kyc/verify-documents", {
        "business_name": "Harmony Dental Care",
        "applicant_name": "Joseph Shah",
        "applicant_role": "Managing Partner",
        "gstin": "19EOGXH4115Y1ZL",
        "udyam_number": "UDYAM-WB-00-5053330",
        "consent_given": "true"
    }, k02_files)

    assert status == 200, f"Expected 200, got {status}: {data}"
    assert data["overall_status"] == "PASS", f"Expected PASS, got {data['overall_status']}"
    doc_res = data["document_results"]
    assert doc_res["gst_certificate"]["status"] == "VERIFIED"
    assert doc_res["udyam_certificate"]["status"] == "VERIFIED"
    assert doc_res["signatory_id"]["status"] == "VERIFIED"
    assert doc_res["address_proof"]["status"] == "VERIFIED"
    
    # Masking check
    masked_id = doc_res["signatory_id"]["extracted_fields"]["masked_id"]
    assert "816907" not in masked_id or "*" in masked_id
    print(f"  Overall Status: {data['overall_status']} (Confidence: {data['confidence_score']})")
    print(f"  GST Certificate: {doc_res['gst_certificate']['status']}")
    print(f"  Udyam Certificate: {doc_res['udyam_certificate']['status']}")
    print(f"  Signatory ID: {doc_res['signatory_id']['status']} (Masked ID: {masked_id})")
    print(f"  Address Proof: {doc_res['address_proof']['status']}")
    print("  ✓ Test 1 PASSED!")

    # -------------------------------------------------------------
    # 2. Cancelled GSTIN Test (K01: Vindhya Tours)
    # -------------------------------------------------------------
    print("\n--- TEST 2: Cancelled GSTIN Document (K01) ---")
    k01_files = {
        "gst_certificate": ("K01_gst_certificate.png", (DOCS_DIR / "K01_gst_certificate.png").read_bytes(), "image/png"),
        "udyam_certificate": ("K01_udyam_certificate.png", (DOCS_DIR / "K01_udyam_certificate.png").read_bytes(), "image/png"),
        "signatory_id": ("K01_signatory_id.png", (DOCS_DIR / "K01_signatory_id.png").read_bytes(), "image/png"),
        "address_proof": ("K01_address_proof.png", (DOCS_DIR / "K01_address_proof.png").read_bytes(), "image/png")
    }
    status, data = make_multipart_request("/kyc/verify-documents", {
        "business_name": "Vindhya Tours & Travels",
        "applicant_name": "Neha Kaur",
        "applicant_role": "Proprietor",
        "gstin": "37IHKXV5167L1ZS",
        "consent_given": "true"
    }, k01_files)

    assert status == 200
    assert data["overall_status"] == "FAILED"
    assert any("cancelled" in iss.lower() for iss in data["detected_issues"])
    print(f"  Overall Status: {data['overall_status']} (Expected: FAILED)")
    print(f"  Detected Issue: {data['detected_issues'][0]}")
    print("  ✓ Test 2 PASSED!")

    # -------------------------------------------------------------
    # 3. Name Mismatch Test (K07: Shri vs Neelgiri)
    # -------------------------------------------------------------
    print("\n--- TEST 3: Name Mismatch (K07: Shri vs Neelgiri) ---")
    k07_files = {
        "gst_certificate": ("K07_gst_certificate.png", (DOCS_DIR / "K07_gst_certificate.png").read_bytes(), "image/png"),
        "udyam_certificate": ("K07_udyam_certificate.png", (DOCS_DIR / "K07_udyam_certificate.png").read_bytes(), "image/png"),
        "signatory_id": ("K07_signatory_id.png", (DOCS_DIR / "K07_signatory_id.png").read_bytes(), "image/png"),
        "address_proof": ("K07_address_proof.png", (DOCS_DIR / "K07_address_proof.png").read_bytes(), "image/png")
    }
    status, data = make_multipart_request("/kyc/verify-documents", {
        "business_name": "Shri Physio Clinic",
        "applicant_name": "Neha Banerjee",
        "applicant_role": "Manager",
        "gstin": "07CPCXN0398P1ZT",
        "udyam_number": "UDYAM-DL-00-9565547",
        "consent_given": "true"
    }, k07_files)

    assert status == 200
    assert data["overall_status"] == "REVIEW_REQUIRED"
    assert data["document_results"]["udyam_certificate"]["status"] == "NEEDS_REVIEW"
    print(f"  Overall Status: {data['overall_status']} (Expected: REVIEW_REQUIRED)")
    print(f"  Udyam Status: {data['document_results']['udyam_certificate']['status']}")
    print("  ✓ Test 3 PASSED!")

    # -------------------------------------------------------------
    # 4. Expired Utility Bill Test (K11: >90 Days Old)
    # -------------------------------------------------------------
    print("\n--- TEST 4: Expired Utility Bill (K11: >90 Days Old) ---")
    k11_files = {
        "gst_certificate": ("K11_gst_certificate.png", (DOCS_DIR / "K11_gst_certificate.png").read_bytes(), "image/png"),
        "udyam_certificate": ("K11_udyam_certificate.png", (DOCS_DIR / "K11_udyam_certificate.png").read_bytes(), "image/png"),
        "signatory_id": ("K11_signatory_id.png", (DOCS_DIR / "K11_signatory_id.png").read_bytes(), "image/png"),
        "address_proof": ("K11_address_proof.png", (DOCS_DIR / "K11_address_proof.png").read_bytes(), "image/png")
    }
    status, data = make_multipart_request("/kyc/verify-documents", {
        "business_name": "Trinity Bake House Pvt Ltd",
        "applicant_name": "Vikram Pillai",
        "applicant_role": "Owner",
        "gstin": "03KGZXT1320R1ZZ",
        "udyam_number": "UDYAM-PB-00-9719478",
        "consent_given": "true"
    }, k11_files)

    assert status == 200
    assert data["overall_status"] == "REVIEW_REQUIRED"
    assert data["document_results"]["address_proof"]["status"] == "NEEDS_REVIEW"
    print(f"  Overall Status: {data['overall_status']} (Expected: REVIEW_REQUIRED)")
    print(f"  Address Proof Status: {data['document_results']['address_proof']['status']}")
    print("  ✓ Test 4 PASSED!")

    # -------------------------------------------------------------
    # 5. Corrupted/Blank Document Test (K04)
    # -------------------------------------------------------------
    print("\n--- TEST 5: Corrupted/Blank GST Document (K04) ---")
    k04_files = {
        "gst_certificate": ("K04_gst_certificate.png", (DOCS_DIR / "K04_gst_certificate.png").read_bytes(), "image/png"),
        "udyam_certificate": ("K04_udyam_certificate.png", (DOCS_DIR / "K04_udyam_certificate.png").read_bytes(), "image/png"),
        "signatory_id": ("K04_signatory_id.png", (DOCS_DIR / "K04_signatory_id.png").read_bytes(), "image/png"),
        "address_proof": ("K04_address_proof.png", (DOCS_DIR / "K04_address_proof.png").read_bytes(), "image/png")
    }
    status, data = make_multipart_request("/kyc/verify-documents", {
        "business_name": "Saffron Dental Care LLP",
        "applicant_name": "Fatima Pillai",
        "applicant_role": "Partner",
        "gstin": "27PZSXS1936O1ZH",
        "udyam_number": "UDYAM-MH-00-6131836",
        "consent_given": "true"
    }, k04_files)

    assert status == 200
    assert data["overall_status"] == "FAILED"
    assert data["document_results"]["gst_certificate"]["status"] == "FAILED"
    print(f"  Overall Status: {data['overall_status']} (Expected: FAILED)")
    print(f"  GST Cert Status: {data['document_results']['gst_certificate']['status']}")
    print("  ✓ Test 5 PASSED!")

    # -------------------------------------------------------------
    # 6. Invalid File Type Rejection (.exe)
    # -------------------------------------------------------------
    print("\n--- TEST 6: Invalid File Type Rejection (.exe) ---")
    bad_files = {
        "gst_certificate": ("malicious_payload.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-msdownload")
    }
    status, data = make_multipart_request("/kyc/verify-documents", {
        "business_name": "Test Store",
        "applicant_name": "Ramesh Gupta",
        "consent_given": "true"
    }, bad_files)

    assert status == 400
    print(f"  Caught HTTP {status} as expected: '{data['detail']}'")
    print("  ✓ Test 6 PASSED!")

    # -------------------------------------------------------------
    # 7. Missing Consent Rejection
    # -------------------------------------------------------------
    print("\n--- TEST 7: Missing Consent Rejection ---")
    status, data = make_multipart_request("/kyc/verify-documents", {
        "business_name": "Harmony Dental Care",
        "applicant_name": "Joseph Shah",
        "consent_given": "false"
    }, k02_files)

    assert status == 200
    assert data["overall_status"] == "FAILED"
    assert any("consent" in iss.lower() for iss in data["detected_issues"])
    print(f"  Overall Status: {data['overall_status']} (Expected: FAILED)")
    print(f"  Issue: {data['detected_issues'][0]}")
    print("  ✓ Test 7 PASSED!")

    print("\n" + "=" * 65)
    print("ALL GENUINE DOCUMENT UPLOAD TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == "__main__":
    run_all_tests()

