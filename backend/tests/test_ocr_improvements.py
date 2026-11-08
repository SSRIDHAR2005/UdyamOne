import importlib.util
import pytest

from app.services.kyc_service import kyc_service
from app.services.ocr_service import ocr_service

try:
    import cv2
    import numpy as np
except ImportError:  # preprocessing remains optional for minimal installs
    cv2 = None
    np = None


def test_gstin_checksum_accepts_known_specimen_and_rejects_changed_checksum():
    assert kyc_service.validate_gstin_format("19EOGXH4115Y1ZL")["valid"]
    bad = kyc_service.validate_gstin_format("19EOGXH4115Y1ZA")
    assert not bad["valid"]
    assert "checksum" in bad["reason"].lower()


def test_gstin_rejects_incomplete_structure_and_state_code():
    assert not kyc_service.validate_gstin_format("19EOGXH4115Y1Z")["valid"]
    assert not kyc_service.validate_gstin_format("00EOGXH4115Y1ZL")["valid"]


def test_udyam_requires_complete_number_and_known_state():
    assert kyc_service.validate_udyam_format("UDYAM-WB-00-5053330")["valid"]
    assert not kyc_service.validate_udyam_format("UDYAM-WB-0O-5053330")["valid"]
    assert not kyc_service.validate_udyam_format("UDYAM-ZZ-00-5053330")["valid"]
    assert not kyc_service.validate_udyam_format("UDYAM-WB-00-50533")["valid"]


def test_identifier_parser_uses_context_and_does_not_repair_lookalikes():
    valid_text = "Goods and Services Tax Registration Certificate\nGSTIN: 19EOGXH4115Y1ZL"
    parsed = ocr_service.parse_ocr_text(valid_text, "gst_certificate", "gst.png")
    assert parsed["gstin"] == "19EOGXH4115Y1ZL"

    lookalike_text = "Goods and Services Tax Registration Certificate\nGSTIN: 19EOGXH4115Y1Z1"
    parsed_lookalike = ocr_service.parse_ocr_text(lookalike_text, "gst_certificate", "gst.png")
    assert parsed_lookalike["gstin"] == "19EOGXH4115Y1Z1"
    assert not kyc_service.validate_gstin_format(parsed_lookalike["gstin"])["valid"]

    unrelated_text = "Invoice reference 19EOGXH4115Y1ZL"
    assert ocr_service.parse_ocr_text(unrelated_text, "generic", "scan.png")["gstin"] is None


def test_gstin_candidate_with_ocr_lookalike_is_exposed_but_fails_validation():
    parsed = ocr_service.parse_ocr_text(
        "GSTIN: 19E0GXH4115Y1ZL", "gst_certificate", "gst.png"
    )
    # Preserve what OCR actually read for the user to correct; never silently
    # change the zero to the visually similar letter O.
    assert parsed["gstin"] == "19E0GXH4115Y1ZL"
    assert not kyc_service.validate_gstin_format(parsed["gstin"])["valid"]


def test_udyam_parser_does_not_convert_o_to_zero():
    parsed = ocr_service.parse_ocr_text("UDYAM REGISTRATION CERTIFICATE\nUDYAM-WB-0O-5053330", "udyam_certificate", "udyam.png")
    assert parsed["udyam_number"] is None


def test_uploaded_content_cannot_reuse_cached_text_by_filename():
    original = ocr_service.cached_dump.copy()
    try:
        ocr_service.cached_dump["K02_gst_certificate.png"] = "GSTIN: 19EOGXH4115Y1ZL"
        parsed = ocr_service.extract_document_fields("K02_gst_certificate.png", b"not an image", "gst_certificate")
        assert parsed["gstin"] is None
    finally:
        ocr_service.cached_dump = original


def test_wrongly_labelled_certificate_is_detectable():
    parsed = ocr_service.extract_document_fields("mislabelled.png", b"", "gst_certificate")
    assert parsed["detected_document_type"] == "unknown"


def test_user_confirmation_is_required_before_registry_lookup_in_upload_flow():
    result = kyc_service.evaluate_uploaded_documents(
        business_name="Example Business",
        applicant_name="Applicant",
        gstin="19EOGXH4115Y1ZL",
        udyam_number="UDYAM-WB-00-5053330",
        consent_given=True,
        identifiers_confirmed=False,
        uploaded_files={},
    )
    assert result["gstin_verification"]["status"] == "SKIPPED"
    assert result["udyam_verification"]["status"] == "SKIPPED"
    assert "Confirm" in result["recommended_next_action"]


def test_valid_manually_corrected_gstin_overrides_ocr_mismatch(monkeypatch):
    def fake_extract(filename, file_bytes=None, doc_type="generic"):
        return {
            "gstin": "19E0GXH4115Y1ZL",  # OCR confused O with 0
            "legal_name": "Joseph Shah (Prop. Harmony Dental Care)",
            "trade_name": "Harmony Dental Care",
            "service_address": "Kolkata, West Bengal",
            "is_corrupted_or_blank": False,
            "confidence": 0.98,
            "field_confidence": {"gstin": 0.98},
            "ocr_engine": "rapidocr_onnxruntime",
        }

    monkeypatch.setattr(ocr_service, "extract_document_fields", fake_extract)
    result = kyc_service.evaluate_uploaded_documents(
        business_name="Harmony Dental Care",
        applicant_name="Joseph Shah",
        gstin="19EOGXH4115Y1ZL",  # corrected from the uploaded certificate
        udyam_number=None,
        consent_given=True,
        identifiers_confirmed=True,
        uploaded_files={
            "gst_certificate": {
                "filename": "gst.png",
                "file_bytes": b"test image bytes",
                "file_size": 16,
            }
        },
    )
    gst_doc = result["document_results"]["gst_certificate"]
    assert gst_doc["status"] != "FAILED"
    assert gst_doc["extracted_fields"]["gstin"] == "19EOGXH4115Y1ZL"
    assert gst_doc["extracted_fields"]["gstin_ocr_candidate"] == "19E0GXH4115Y1ZL"
    assert gst_doc["extracted_fields"]["gstin_source"] == "MANUAL_CONFIRMED"
    assert any(check["status"] == "MANUAL_CONFIRMED" for check in gst_doc["checks"])
    assert result["gstin_verification"]["valid"]


def test_opencv_preprocessing_produces_enhanced_copies_without_mutating_source():
    if cv2 is None or np is None:
        return
    source = np.full((500, 700, 3), 245, dtype=np.uint8)
    cv2.putText(source, "GSTIN 19EOGXH4115Y1ZL", (30, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (20, 20, 20), 2)
    original = source.copy()
    variants = ocr_service._preprocess_image(source)
    assert len(variants) >= 2
    assert variants[0].shape[0] >= source.shape[0]
    assert np.array_equal(source, original)


@pytest.mark.skipif(importlib.util.find_spec("rapidocr") is None, reason="RapidOCR optional runtime is not installed")
def test_rapidocr_runtime_extracts_gstin_from_clear_document_image():
    if cv2 is None or np is None:
        pytest.skip("OpenCV is not installed")
    image = np.full((480, 1500, 3), 255, dtype=np.uint8)
    cv2.putText(image, "GST REGISTRATION CERTIFICATE", (35, 150), cv2.FONT_HERSHEY_SIMPLEX,
                1.8, (10, 10, 10), 4, cv2.LINE_AA)
    cv2.putText(image, "GSTIN: 19EOGXH4115Y1ZL", (35, 300), cv2.FONT_HERSHEY_SIMPLEX,
                1.8, (10, 10, 10), 4, cv2.LINE_AA)
    ok, encoded = cv2.imencode(".png", image)
    assert ok
    extracted = ocr_service.extract_document_fields("clear_gst.png", encoded.tobytes(), "gst_certificate")
    assert extracted["ocr_engine"] == "rapidocr_onnxruntime"
    assert extracted["gstin"] == "19EOGXH4115Y1ZL"
    assert extracted["field_confidence"]["gstin"] > 0
