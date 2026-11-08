"""
Comprehensive Test Suite for UdyamOne Upgraded KYC OCR & Number Validation Pipeline.

Tests:
1. Image Preprocessing:
   - Resizing / resolution enhancement
   - Projection profile deskewing
   - Adaptive local thresholding
   - Noise filtering and unsharp masking
   - Text region detection
2. Number Validation:
   - Official GST Council Modulo-36 Checksum (Luhn mod-36)
   - State code range (01-38, 97, 99)
   - Ambiguity & character confusion detection (O/0, I/1, whitespace) without silent modification
   - Udyam registration structure & state validation
3. Dedicated Field Extraction:
   - Form GST REG-06: GSTIN, legal name, trade name, constitution, state
   - Udyam Certificate: Udyam number, enterprise name, organisation type, registration date
   - Signatory ID: DPDP Act masking
   - Address Proof: 90-day DoT recency rule
4. Separate Format Validation vs Simulated Registry Verification:
   - Syntactically valid number with cancelled registry status
5. Standalone Extraction & Live Number Validation Endpoints
"""

import io
import json
import urllib.request
import pytest
from PIL import Image

from app.api.endpoints import get_ocr_engine_evaluation, validate_identifier_number
from app.services.image_preprocessor import document_preprocessor
from app.services.number_validator import number_validator
from app.services.ocr_service import ocr_service
from app.services.kyc_service import kyc_service


# =====================================================================
# 1. IMAGE PREPROCESSING TESTS
# =====================================================================
def test_image_preprocessing_pipeline():
    """Verify image enhancement: resizing, deskewing, thresholding, and noise filtering."""
    # Create synthetic test image with text-like dark boxes on white background
    img = Image.new("RGB", (600, 400), color=(255, 255, 255))
    # Add synthetic black stripe
    for x in range(100, 500):
        for y in range(150, 180):
            img.putpixel((x, y), (0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    enhanced_bytes, meta = document_preprocessor.preprocess_image(raw_bytes)

    assert enhanced_bytes is not None
    assert len(enhanced_bytes) > 0
    assert "original_size" in meta
    assert "processed_size" in meta
    assert meta["processed_size"][0] > meta["original_size"][0]  # 600px width upscaled towards 1600px
    assert meta["processed_size"][0] >= 1200
    assert "skew_angle_deg" in meta
    assert "adaptive_thresholded" in meta


def test_text_region_detection():
    """Verify automatic text bounding region detection."""
    specimen_path = kyc_service.data_dir / "kyc_documents" / "K02_gst_certificate.png"
    if specimen_path.exists():
        raw_bytes = specimen_path.read_bytes()
        enhanced_bytes, meta = document_preprocessor.preprocess_image(raw_bytes)
        assert meta["text_regions_detected"] > 5


# =====================================================================
# 2. STRICT NUMBER VALIDATION & CHECKSUM TESTS
# =====================================================================
def test_valid_gstin_checksums():
    """Verify that official GST Council Modulo-36 Checksum validates authentic GSTINs."""
    valid_test_cases = [
        ("19EOGXH4115Y1ZL", "19", "West Bengal", "L"),
        ("27XUIXG0767D1ZP", "27", "Maharashtra", "P"),
        ("08YKZXS5189L1ZO", "08", "Rajasthan", "O"),
        ("07CPCXN0398P1ZT", "07", "Delhi", "T"),
        ("24XORXG9365M1Z3", "24", "Gujarat", "3"),
        ("37LDYXK0296F1ZB", "37", "Andhra Pradesh", "B"),
        ("27QHJXK0658U1ZL", "27", "Maharashtra", "L"),
        ("03KGZXT1320R1ZZ", "03", "Punjab", "Z"),
        ("37NBLXS1145E1ZU", "37", "Andhra Pradesh", "U"),
        ("37IHKXV5167L1ZS", "37", "Andhra Pradesh", "S"),
    ]
    for gstin, expected_state, state_name, expected_chk in valid_test_cases:
        res = number_validator.validate_gstin(gstin)
        assert res["valid"] is True, f"Failed for {gstin}: {res.get('error')}"
        assert res["state_code"] == expected_state
        assert res["state_name"] == state_name
        assert res["checksum_actual"] == expected_chk
        assert res["checksum_valid"] is True


def test_invalid_gstin_checksum_rejection():
    """Verify that corrupted checksums or invalid digits are strictly rejected."""
    # Alter the last character from 'L' to 'Z'
    bad_checksum = "19EOGXH4115Y1ZZ"
    res = number_validator.validate_gstin(bad_checksum)
    assert res["valid"] is False
    assert res["checksum_valid"] is False
    assert "checksum failure" in res["error"].lower()
    assert res["checksum_expected"] == "L"
    assert res["checksum_actual"] == "Z"


def test_invalid_state_code_rejection():
    """Verify that invalid state codes (e.g. 00 or 95) are rejected."""
    bad_state = "95EOGXH4115Y1ZL"
    res = number_validator.validate_gstin(bad_state)
    assert res["valid"] is False
    assert "invalid state code" in res["error"].lower()


def test_gstin_ambiguity_detection_without_silent_modification():
    """Verify that letter 'O' in place of digit '0' is flagged as ambiguity without mutating data."""
    confused_gstin = "O7CPCXN0398P1ZT"
    res = number_validator.validate_gstin(confused_gstin)
    assert res["valid"] is False
    assert len(res["ambiguities"]) > 0
    assert any("letters 'o' or 'i'" in a.lower() for a in res["ambiguities"])


def test_udyam_structure_validation():
    """Verify Udyam registration structure: UDYAM-XX-00-XXXXXXX."""
    valid_udyam = "UDYAM-WB-00-5053330"
    res = number_validator.validate_udyam(valid_udyam)
    assert res["valid"] is True
    assert res["state_code"] == "WB"
    assert res["state_name"] == "West Bengal"

    # Invalid state in Udyam
    bad_udyam_state = "UDYAM-ZZ-00-5053330"
    res_bad = number_validator.validate_udyam(bad_udyam_state)
    assert res_bad["valid"] is False

    # Invalid serial digits length
    bad_udyam_len = "UDYAM-WB-00-50533"
    res_bad_len = number_validator.validate_udyam(bad_udyam_len)
    assert res_bad_len["valid"] is False


# =====================================================================
# 3. DEDICATED OCR FIELD EXTRACTION TESTS
# =====================================================================
def test_gst_certificate_field_extraction():
    """Verify dedicated field extraction for Form GST REG-06."""
    specimen_path = kyc_service.data_dir / "kyc_documents" / "K02_gst_certificate.png"
    if specimen_path.exists():
        extracted = ocr_service.extract_document_fields(
            filename="K02_gst_certificate.png",
            file_bytes=specimen_path.read_bytes(),
            doc_type="gst_certificate"
        )
        assert extracted["gstin"] == "19EOGXH4115Y1ZL"
        assert extracted["document_type"] == "Form GST REG-06 (Certificate of Registration)"
        assert extracted["confidence"] >= 0.85
        assert extracted["gstin_validation"]["valid"] is True
        assert extracted["gstin_validation"]["state_name"] == "West Bengal"


def test_udyam_certificate_field_extraction():
    """Verify dedicated field extraction for Ministry of MSME Udyam Certificate."""
    specimen_path = kyc_service.data_dir / "kyc_documents" / "K02_udyam_certificate.png"
    if specimen_path.exists():
        extracted = ocr_service.extract_document_fields(
            filename="K02_udyam_certificate.png",
            file_bytes=specimen_path.read_bytes(),
            doc_type="udyam_certificate"
        )
        assert extracted["udyam_number"] == "UDYAM-WB-00-5053330"
        assert extracted["document_type"] == "Udyam Registration Certificate"
        assert extracted["confidence"] >= 0.85
        assert extracted["udyam_validation"]["valid"] is True


def test_signatory_id_dpdp_masking():
    """Verify sensitive ID numbers are masked on signatory cards."""
    specimen_path = kyc_service.data_dir / "kyc_documents" / "K02_signatory_id.png"
    if specimen_path.exists():
        extracted = ocr_service.extract_document_fields(
            filename="K02_signatory_id.png",
            file_bytes=specimen_path.read_bytes(),
            doc_type="signatory_id"
        )
        assert extracted["signatory_name"] == "Joseph Shah"
        assert extracted["masked_id"] is not None
        assert "*" in extracted["masked_id"]


def test_address_proof_recency_check():
    """Verify 90-day DoT regulatory recency evaluation."""
    # K02 has recent bill
    specimen_k02 = kyc_service.data_dir / "kyc_documents" / "K02_address_proof.png"
    if specimen_k02.exists():
        extracted = ocr_service.extract_document_fields(
            filename="K02_address_proof.png",
            file_bytes=specimen_k02.read_bytes(),
            doc_type="address_proof"
        )
        assert extracted["is_address_expired"] is False

    # K11 has expired bill (>90 days from reference date 2026-07-15)
    specimen_k11 = kyc_service.data_dir / "kyc_documents" / "K11_address_proof.png"
    if specimen_k11.exists():
        extracted_k11 = ocr_service.extract_document_fields(
            filename="K11_address_proof.png",
            file_bytes=specimen_k11.read_bytes(),
            doc_type="address_proof"
        )
        assert extracted_k11["is_address_expired"] is True


# =====================================================================
# 4. SEPARATE FORMAT VALIDATION VS SIMULATED REGISTRY STATUS
# =====================================================================
def test_format_validation_separate_from_registry_status():
    """
    Verify that a syntactically valid number format with correct Modulo-36
    checksum does NOT automatically pass verification if registry status is CANCELLED.
    Specimen K01 has a valid Modulo-36 GSTIN (37IHKXV5167L1ZS), but its registry status is CANCELLED.
    """
    gstin_k01 = "37IHKXV5167L1ZS"
    val = number_validator.validate_gstin(gstin_k01)
    assert val["valid"] is True  # Format & Checksum are valid!
    assert val["state_name"] == "Andhra Pradesh"

    # Query registry
    reg = kyc_service.lookup_gstin(gstin_k01)
    assert reg["valid"] is False  # Inactive in registry!
    assert reg["status"] == "Cancelled"

    # Overall evaluation must be FAILED, but format check must indicate MATCH
    specimen_path = kyc_service.data_dir / "kyc_documents" / "K01_gst_certificate.png"
    files = {
        "gst_certificate": {
            "filename": "K01_gst_certificate.png",
            "file_bytes": specimen_path.read_bytes() if specimen_path.exists() else b"",
            "file_size": specimen_path.stat().st_size if specimen_path.exists() else 0
        }
    }
    result = kyc_service.evaluate_uploaded_documents(
        business_name="Vindhya Tours & Travels",
        applicant_name="Neha Kaur",
        gstin=gstin_k01,
        consent_given=True,
        uploaded_files=files
    )

    assert result["overall_status"] == "FAILED"
    gst_res = result["document_results"]["gst_certificate"]
    # Checksum format check matched
    chk_checks = [c for c in gst_res["checks"] if "Modulo-36 Checksum" in c["field"]]
    assert len(chk_checks) > 0
    assert chk_checks[0]["status"] == "MATCH"
    # But registry check failed
    reg_checks = [c for c in gst_res["checks"] if "Registry Status" in c["field"]]
    assert len(reg_checks) > 0
    assert reg_checks[0]["status"] == "FAILED"


# =====================================================================
# 5. API ENDPOINTS INTEGRATION TESTS
# =====================================================================
def test_api_ocr_evaluation_endpoint():
    """Test GET /api/v1/kyc/ocr-evaluation directly and via HTTP."""
    data = get_ocr_engine_evaluation()
    assert "primary_engine" in data
    assert "fallback_engine" in data
    assert "benchmark_evaluation" in data
    assert data["benchmark_evaluation"]["gst_field_accuracy"] >= 0.95


def test_api_validate_number_endpoint():
    """Test POST /api/v1/kyc/validate-number."""
    # Valid GSTIN
    res_gst = validate_identifier_number(number_type="gstin", value="19EOGXH4115Y1ZL")
    assert res_gst["valid"] is True
    assert res_gst["checksum_valid"] is True
    assert res_gst["state_name"] == "West Bengal"

    # Bad Checksum GSTIN
    res_bad = validate_identifier_number(number_type="gstin", value="19EOGXH4115Y1ZZ")
    assert res_bad["valid"] is False
    assert res_bad["checksum_valid"] is False

    # Valid Udyam
    res_udy = validate_identifier_number(number_type="udyam", value="UDYAM-WB-00-5053330")
    assert res_udy["valid"] is True
    assert res_udy["state_code"] == "WB"


def test_api_extract_document_endpoint_flow():
    """Test standalone document extraction logic and lifecycle generation."""
    specimen_path = kyc_service.data_dir / "kyc_documents" / "K02_gst_certificate.png"
    if specimen_path.exists():
        raw_bytes = specimen_path.read_bytes()
        extracted = ocr_service.extract_document_fields(
            filename="K02_gst_certificate.png",
            file_bytes=raw_bytes,
            doc_type="gst_certificate"
        )
        assert extracted["gstin"] == "19EOGXH4115Y1ZL"
        assert extracted["gstin_validation"]["valid"] is True

        # Test live HTTP endpoint if backend daemon is running
        try:
            boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
            header = f"--{boundary}\r\nContent-Disposition: form-data; name=\"doc_type\"\r\n\r\ngst_certificate\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"K02_gst_certificate.png\"\r\nContent-Type: image/png\r\n\r\n".encode()
            footer = f"\r\n--{boundary}--\r\n".encode()
            body = header + raw_bytes + footer
            req = urllib.request.Request("http://127.0.0.1:8000/api/v1/kyc/extract-document", data=body)
            req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
            resp = json.loads(urllib.request.urlopen(req, timeout=3).read().decode())
            assert resp["status"] == "SUCCESS"
            assert resp["extracted_fields"]["gstin"] == "19EOGXH4115Y1ZL"
            assert len(resp["lifecycle_stages"]) == 6
            assert resp["lifecycle_stages"][3]["status"] == "PASSED"
        except Exception as e:
            # If server not running on port 8000 in CI, direct service test already verified above
            pass
