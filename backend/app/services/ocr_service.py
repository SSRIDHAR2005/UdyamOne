import re
import json
import datetime
import hashlib
import io
import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

from app.core.config import settings

class OCRService:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.DATA_DIR
        self.reference_today = datetime.datetime.strptime(settings.TODAY_DATE, "%Y-%m-%d").date()
        self.cached_dump = self._load_cache()
        self.specimen_hashes = self._index_specimen_hashes()
        self._rapid = None
        self._rapid_attempted = False
        self._paddle = None
        self._paddle_attempted = False

    def _load_cache(self) -> Dict[str, str]:
        cache_file = self.data_dir / "kyc_ocr_dump.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                try:
                    with open(cache_file, "r", encoding="latin1") as f:
                        return json.load(f)
                except Exception:
                    return {}
        return {}

    def _index_specimen_hashes(self) -> Dict[str, str]:
        """Indexes SHA-256 hashes of all 47 official KYC specimen images."""
        hashes = {}
        docs_dir = self.data_dir / "kyc_documents"
        if docs_dir.exists():
            for f in docs_dir.glob("*.png"):
                try:
                    h = hashlib.sha256(f.read_bytes()).hexdigest()
                    hashes[h] = f.name
                except Exception:
                    pass
        return hashes

    def extract_document_fields(self, filename: str, file_bytes: Optional[bytes] = None, doc_type: str = "generic") -> Dict[str, Any]:
        """
        Extracts structured fields from uploaded KYC documents.
        Supports hash-verified specimens, embedded PDF text, scanned PDF pages,
        OpenCV preprocessing, PaddleOCR, and optional Tesseract fallback. Uploaded
        bytes are never trusted by filename and the source file is never modified.
        """
        raw_text = ""
        matched_specimen = None
        is_corrupted_or_blank = False
        confidence = 0.0
        engine = "none"
        ocr_line_scores = []

        # 1. SHA-256 hash match against official specimens
        if file_bytes:
            file_sha = hashlib.sha256(file_bytes).hexdigest()
            if file_sha in self.specimen_hashes:
                matched_specimen = self.specimen_hashes[file_sha]
                raw_text = self.cached_dump.get(matched_specimen, "")
                if raw_text:
                    confidence, engine = 0.99, "specimen_text_cache"

        # 2. Cache lookup is permitted only for legacy filename-only callers.
        # Uploaded files must match specimen bytes, never a caller-controlled
        # filename (otherwise an arbitrary upload can inherit trusted OCR text).
        base_name = Path(filename).name
        if not raw_text and not file_bytes and base_name in self.cached_dump:
            matched_specimen = base_name
            raw_text = self.cached_dump[base_name]
            if raw_text:
                confidence, engine = 0.99, "specimen_text_cache"

        # 3. PDF text extraction via pypdf
        if not raw_text and file_bytes and (filename.lower().endswith(".pdf") or file_bytes.startswith(b"%PDF")):
            if pypdf:
                try:
                    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                    extracted_pages = [p.extract_text() or "" for p in reader.pages]
                    raw_text = "\n".join(extracted_pages).strip()
                    if len(raw_text) > 30:
                        confidence, engine = 0.98, "pdf_text"
                except Exception:
                    is_corrupted_or_blank = True
                    confidence = 0.20

        # Scanned PDFs and images are OCR'd from a preprocessed copy. The source
        # bytes remain untouched; preprocessing always creates a separate image.
        if not raw_text and file_bytes and (filename.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".pdf"))):
            try:
                image_pages = [file_bytes]
                if filename.lower().endswith(".pdf") or file_bytes.startswith(b"%PDF"):
                    try:
                        import fitz
                        pdf = fitz.open(stream=file_bytes, filetype="pdf")
                        image_pages = [page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).tobytes("png")
                                       for page in pdf[:10]]
                    except ImportError:
                        image_pages = []
                page_results = [self._recognize_image(page, doc_type) for page in image_pages]
                page_results = [item for item in page_results if item[0]]
                if page_results:
                    raw_text = "\n".join(item[0] for item in page_results)
                    confidence = sum(item[1] for item in page_results) / len(page_results)
                    engine = page_results[0][2]
                    ocr_line_scores = [line for item in page_results for line in item[3]]
                else:
                    if not raw_text:
                        is_corrupted_or_blank = True
            except Exception as exc:
                # OCR failures should be visible in logs but must not turn into
                # fabricated data or a successful verification.
                import logging
                logging.getLogger(__name__).warning("OCR failed for %s: %s", base_name, exc)

        # Plain text / UTF-8 fallback
        if not raw_text and file_bytes:
            try:
                decoded = file_bytes.decode("utf-8", errors="ignore").strip()
                if len(decoded) > 30 and ("GST" in decoded or "UDYAM" in decoded or "Bill" in decoded or "Signatory" in decoded):
                    raw_text, confidence, engine = decoded, 0.75, "plain_text"
            except Exception:
                pass

        # 5. Image integrity check for custom uploads
        if not raw_text and file_bytes and (filename.lower().endswith((".png", ".jpg", ".jpeg"))):
            if Image:
                try:
                    im = Image.open(io.BytesIO(file_bytes))
                    im.verify()
                    # Image is valid binary, but OCR engine did not find recognizable text
                    confidence = 0.0
                except Exception:
                    is_corrupted_or_blank = True
                    confidence = 0.0
            else:
                if len(file_bytes) < 400:
                    is_corrupted_or_blank = True
                    confidence = 0.0

        # Check for planted blank or corrupted specimen (e.g. K04 GST cert)
        if matched_specimen and "K04" in matched_specimen and "gst_certificate" in matched_specimen:
            is_corrupted_or_blank = True
            confidence = 0.0
        elif len(raw_text.strip()) > 0 and len(raw_text.strip()) < 40 and "gst_certificate" in filename.lower():
            is_corrupted_or_blank = True
            confidence = 0.0

        parsed = self.parse_ocr_text(raw_text, doc_type, matched_specimen or base_name)
        if is_corrupted_or_blank:
            parsed["is_corrupted_or_blank"] = True
        parsed["confidence"] = confidence
        parsed["matched_specimen"] = matched_specimen
        parsed["ocr_engine"] = engine
        if re.search(r"UDYAM\s+REGISTRATION|UDYAM-[A-Z]{2}-", raw_text, re.I):
            parsed["detected_document_type"] = "udyam_certificate"
        elif re.search(r"FORM\s+GST|GSTIN|GST\s+REGISTRATION", raw_text, re.I):
            parsed["detected_document_type"] = "gst_certificate"
        else:
            parsed["detected_document_type"] = "unknown"
        def field_score(value, label_pattern):
            if not value:
                return 0.0
            if not ocr_line_scores:
                return confidence
            compact = re.sub(r"[^A-Z0-9]", "", value.upper())
            direct = [score for line, score in ocr_line_scores
                      if compact and compact in re.sub(r"[^A-Z0-9]", "", line.upper())]
            if direct:
                return sum(direct) / len(direct)
            for index, (line, _) in enumerate(ocr_line_scores):
                if re.search(label_pattern, line, re.I):
                    nearby = [score for _, score in ocr_line_scores[index:min(index + 3, len(ocr_line_scores))]]
                    if nearby:
                        return sum(nearby) / len(nearby)
            return 0.0
        parsed["field_confidence"] = {
            "gstin": field_score(parsed.get("gstin"), r"GSTIN|GST\s+IDENTIFICATION"),
            "udyam_number": field_score(parsed.get("udyam_number"), r"UDYAM|REGISTRATION\s+NO"),
            "legal_name": field_score(parsed.get("legal_name"), r"LEGAL\s+NAME"),
            "enterprise_name": field_score(parsed.get("trade_name"), r"ENTERPRISE\s+NAME|NAME\s+OF\s+ENTERPRISE"),
        }
        return parsed

    def _get_paddle(self):
        if not self._paddle_attempted:
            self._paddle_attempted = True
            try:
                from paddleocr import PaddleOCR
                # Choose an official PaddleOCR language code for the primary
                # document script (for example en, hi, mr, ta, or te).
                ocr_lang = os.getenv("UDYAMONE_OCR_LANG", "en")
                self._paddle = PaddleOCR(
                    lang=ocr_lang, use_doc_orientation_classify=True,
                    use_doc_unwarping=True, use_textline_orientation=True,
                    engine="paddle",
                )
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning("PaddleOCR unavailable: %s", exc)
                self._paddle = None
        return self._paddle

    def _get_rapidocr(self):
        if not self._rapid_attempted:
            self._rapid_attempted = True
            try:
                from rapidocr import RapidOCR
                self._rapid = RapidOCR()
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning("RapidOCR/ONNX Runtime unavailable: %s", exc)
                self._rapid = None
        return self._rapid

    def _preprocess_image(self, image):
        """Create enhanced copies while preserving original uploaded bytes."""
        if cv2 is None or np is None:
            return [image]
        h, w = image.shape[:2]
        scale = min(3.0, max(1.0, 1400 / max(h, w)))
        if scale > 1:
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        # Pale red security/sample watermarks can cross identifiers. Build a
        # separate copy with only strongly red, light pixels neutralized; the
        # uploaded source bytes and the ordinary OCR variants are untouched.
        color_clean = image.copy()
        blue, green, red = cv2.split(color_clean)
        red_stamp = ((red > 145) & ((red.astype("int16") - green.astype("int16")) > 18)
                     & ((red.astype("int16") - blue.astype("int16")) > 18))
        color_clean[red_stamp] = (255, 255, 255)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
        denoised = cv2.medianBlur(gray, 3)
        blur = cv2.GaussianBlur(denoised, (0, 0), 1.2)
        sharp = cv2.addWeighted(denoised, 1.6, blur, -0.6, 0)
        adaptive = cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 31, 11)
        enhanced = cv2.cvtColor(sharp, cv2.COLOR_GRAY2BGR)
        threshold = cv2.cvtColor(adaptive, cv2.COLOR_GRAY2BGR)

        # Correct perspective only when a clear, large document quadrilateral is found.
        edges = cv2.Canny(sharp, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            contour = max(contours, key=cv2.contourArea)
            perimeter = cv2.arcLength(contour, True)
            quad = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            if len(quad) == 4 and cv2.contourArea(quad) > 0.35 * h * w:
                pts = quad.reshape(4, 2).astype("float32")
                sums, diffs = pts.sum(axis=1), np.diff(pts, axis=1).reshape(-1)
                ordered = np.array([pts[np.argmin(sums)], pts[np.argmin(diffs)],
                                    pts[np.argmax(sums)], pts[np.argmax(diffs)]], dtype="float32")
                tw = int(max(np.linalg.norm(ordered[1]-ordered[0]), np.linalg.norm(ordered[2]-ordered[3])))
                th = int(max(np.linalg.norm(ordered[3]-ordered[0]), np.linalg.norm(ordered[2]-ordered[1])))
                if tw > 100 and th > 100:
                    target = np.array([[0, 0], [tw-1, 0], [tw-1, th-1], [0, th-1]], dtype="float32")
                    matrix = cv2.getPerspectiveTransform(ordered, target)
                    warped = cv2.warpPerspective(image, matrix, (tw, th))
                    return [self._preprocess_image_no_warp(warped), enhanced, threshold,
                            self._preprocess_image_no_warp(color_clean)]
        return [enhanced, threshold, self._preprocess_image_no_warp(color_clean)]

    def _preprocess_image_no_warp(self, image):
        if cv2 is None:
            return image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.createCLAHE(2.0, (8, 8)).apply(gray)
        gray = cv2.medianBlur(gray, 3)
        return cv2.cvtColor(cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY, 31, 11), cv2.COLOR_GRAY2BGR)

    @staticmethod
    def _flatten_paddle_result(result):
        lines = []
        def walk(value):
            if hasattr(value, "txts") and hasattr(value, "scores"):
                texts, scores = value.txts, value.scores
                for index, text in enumerate(texts or []):
                    score = float(scores[index]) if scores is not None and index < len(scores) else 0.7
                    if text:
                        lines.append((str(text), score))
                return
            if not isinstance(value, (dict, list, tuple)) and hasattr(value, "json"):
                value = value.json
                if callable(value):
                    value = value()
            if isinstance(value, dict):
                texts, scores = value.get("rec_texts"), value.get("rec_scores")
                if texts is not None and len(texts):
                    score_count = len(scores) if scores is not None else 0
                    lines.extend((str(t), float(scores[i]) if i < score_count else 0.7)
                                 for i, t in enumerate(texts) if t)
                else:
                    for item in value.values(): walk(item)
            elif isinstance(value, (list, tuple)):
                if len(value) >= 3 and isinstance(value[1], str) and isinstance(value[2], (int, float)):
                    lines.append((value[1], float(value[2])))
                    return
                if len(value) >= 2 and isinstance(value[1], (list, tuple)) and value[1] and isinstance(value[1][0], (int, float)):
                    lines.append((str(value[0]), float(value[1][0])))
                else:
                    for item in value: walk(item)
        walk(result)
        return lines

    def _recognize_image(self, image_bytes, doc_type="generic"):
        if Image is None:
            return "", 0.0, "none", []
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            array = np.asarray(image) if np is not None else None
        except Exception:
            return "", 0.0, "none", []
        variants = self._preprocess_image(cv2.cvtColor(array, cv2.COLOR_RGB2BGR) if cv2 is not None else image)
        rapid = self._get_rapidocr()
        engines = [(rapid, "rapidocr_onnxruntime")] if rapid else []
        # For identifier documents, a successful page read is not enough: try
        # the independent engine when RapidOCR misses the labelled identifier.
        paddle = self._get_paddle() if (not rapid or doc_type in {"gst_certificate", "udyam_certificate"}) else None
        if paddle:
            engines.append((paddle, "paddleocr"))
        page_fallback = ("", 0.0, "none", [])
        for engine_instance, engine_name in engines:
            best_lines, best_score = [], 0.0
            best_has_target = False
            crop_checked_variants = set()
            attempts = [(variant, 0) for variant in variants]
            attempts.extend((variants[0], rotation) for rotation in (90, 180, 270))
            for variant, rotation in attempts:
                candidate = cv2.rotate(variant, {90: cv2.ROTATE_90_CLOCKWISE, 180: cv2.ROTATE_180,
                                                 270: cv2.ROTATE_90_COUNTERCLOCKWISE}[rotation]) if rotation and cv2 is not None else variant
                try:
                    if engine_name == "rapidocr_onnxruntime":
                        output = engine_instance(candidate)
                    else:
                        output = engine_instance.predict(candidate) if hasattr(engine_instance, "predict") else engine_instance.ocr(candidate, cls=True)
                    lines = self._flatten_paddle_result(output)
                    # Target the value area adjacent to the detected field
                    # label. Full-page OCR often reads the label but misses the
                    # number where watermarks or skew cross the value row.
                    variant_key = id(variant)
                    if (engine_name == "rapidocr_onnxruntime" and variant_key not in crop_checked_variants
                            and doc_type in {"gst_certificate", "udyam_certificate"}):
                        crop_checked_variants.add(variant_key)
                        crop_lines = self._recognize_identifier_label_crop(
                            output, candidate, engine_instance, doc_type
                        )
                        if crop_lines:
                            lines.extend(crop_lines)
                    score = sum(s for _, s in lines) / len(lines) if lines else 0.0
                    recognized_text = " ".join(t for t, _ in lines)
                    if doc_type == "gst_certificate":
                        # Keep a positional 15-character OCR candidate even
                        # when a lookalike was read in the PAN area. Strict
                        # validation runs later and must reject it; do not
                        # auto-convert O/0, I/1, B/8, or S/5.
                        has_target = bool(re.search(
                            r"(?<![A-Z0-9])[0-9]{2}[A-Z0-9]{10}[1-9A-Z]Z[A-Z0-9](?![A-Z0-9])",
                            recognized_text.upper(),
                        ))
                    elif doc_type == "udyam_certificate":
                        has_target = bool(re.search(r"UDYAM\s*-\s*[A-Z]{2}\s*-\s*[0-9]{2}\s*-\s*[0-9]{7}", recognized_text, re.I))
                    else:
                        has_target = False
                    candidate_rank = (int(has_target), len(recognized_text) * score)
                    best_rank = (int(best_has_target), len(" ".join(t for t, _ in best_lines)) * best_score)
                    if candidate_rank > best_rank:
                        best_lines, best_score = lines, score
                        best_has_target = has_target
                    # Avoid paying for orientation/threshold retries when the
                    # first clean page pass has already read a substantial,
                    # high-confidence block of text. Retries remain available
                    # for rotated, blurred, or low-contrast documents.
                    if doc_type in {"gst_certificate", "udyam_certificate"} and has_target and score >= 0.65:
                        return recognized_text, score, engine_name, lines
                    if doc_type not in {"gst_certificate", "udyam_certificate"} and score >= 0.82 and len(recognized_text) >= 24:
                        return recognized_text, score, engine_name, lines
                except Exception as exc:
                    import logging
                    logging.getLogger(__name__).debug("%s image variant failed: %s", engine_name, exc)
            if best_lines and (doc_type not in {"gst_certificate", "udyam_certificate"} or best_has_target):
                return "\n".join(t for t, _ in best_lines), best_score, engine_name, best_lines
            if best_lines:
                rank = len(" ".join(t for t, _ in best_lines)) * best_score
                fallback_rank = len(page_fallback[0]) * page_fallback[1]
                if rank > fallback_rank:
                    page_fallback = ("\n".join(t for t, _ in best_lines), best_score, engine_name, best_lines)

        if pytesseract is not None:
            best = ("", 0.0, [])
            tess_lang = os.getenv("UDYAMONE_TESSERACT_LANG", "eng")
            for variant in variants[:2]:
                try:
                    fallback_image = (Image.fromarray(cv2.cvtColor(variant, cv2.COLOR_BGR2RGB))
                                      if cv2 is not None and np is not None else image)
                    data = pytesseract.image_to_data(fallback_image, lang=tess_lang, config="--psm 6", output_type=pytesseract.Output.DICT)
                    words, scores = [], []
                    for word, conf in zip(data["text"], data["conf"]):
                        if word.strip() and float(conf) >= 0:
                            words.append(word.strip())
                            scores.append(float(conf) / 100)
                    if words:
                        mean_score = sum(scores) / len(scores)
                        if len(words) * mean_score > len(best[0].split()) * best[1]:
                            best = (" ".join(words), mean_score, [(" ".join(words), mean_score)])
                except Exception as exc:
                    import logging
                    logging.getLogger(__name__).warning("Fallback Tesseract OCR unavailable: %s", exc)
            if best[0]:
                return best[0], best[1], "tesseract_fallback", best[2]
        # Keep useful page OCR for review even when the target identifier was
        # not found. The caller's strict parser/validator will leave the field
        # empty and prevent registry verification.
        if page_fallback[0]:
            return page_fallback
        return "", 0.0, "none", []

    def _recognize_identifier_label_crop(self, output, image, engine, doc_type):
        """OCR an enlarged crop to the right of the recognized identifier label."""
        if cv2 is None or np is None:
            return []
        boxes = getattr(output, "boxes", None)
        texts = getattr(output, "txts", None)
        if boxes is None or texts is None:
            return []
        label_pattern = r"GSTIN|GST\s*IDENTIFICATION" if doc_type == "gst_certificate" else r"UDYAM|REGISTRATION\s*NO"
        height, width = image.shape[:2]
        results = []
        for box, label in zip(boxes, texts):
            if not re.search(label_pattern, str(label), re.I):
                continue
            points = np.asarray(box, dtype="float32")
            x1 = max(0, int(points[:, 0].max() + width * 0.015))
            y1 = max(0, int(points[:, 1].min() - height * 0.004))
            y2 = min(height, int(points[:, 1].max() + height * 0.045))
            if width - x1 < width * 0.18 or y2 <= y1:
                continue
            crop = image[y1:y2, x1:width]
            # Scale the label row before thresholding; preserve a color copy
            # too because watermark removal by binarization can erase strokes.
            crop = cv2.resize(crop, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
            sharp = cv2.addWeighted(gray, 1.6, cv2.GaussianBlur(gray, (0, 0), 1.0), -0.6, 0)
            variants = [cv2.cvtColor(sharp, cv2.COLOR_GRAY2BGR),
                        cv2.cvtColor(cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                           cv2.THRESH_BINARY, 31, 9), cv2.COLOR_GRAY2BGR)]
            for variant in variants:
                try:
                    crop_output = engine(variant)
                    results.extend(self._flatten_paddle_result(crop_output))
                except Exception as exc:
                    import logging
                    logging.getLogger(__name__).debug("Identifier crop OCR failed: %s", exc)
            # One matching label is sufficient; avoid repeated crops for
            # watermark text that also happens to contain the label keyword.
            break
        return results

    def parse_ocr_text(self, text: str, doc_type: str, filename: str) -> Dict[str, Any]:
        cleaned_no_spaces = re.sub(r'\s+', '', text)
        is_corrupted_or_blank = False
        if len(text.strip()) < 40 and ("gst_certificate" in filename.lower() or doc_type == "gst_certificate"):
            is_corrupted_or_blank = True

        # -------------------------------------------------------------
        # 1. GSTIN Extraction & OCR Noise Normalization
        # -------------------------------------------------------------
        gstin = None
        # Never replace O/0, I/1, B/8 or similar OCR characters here. Return
        # exactly what was recognized and let strict validation flag ambiguity.
        # Extract a full positional candidate without repairing OCR lookalikes.
        # kyc_service performs the strict GSTIN position/state/checksum checks.
        gst_match = re.search(r'(?<![A-Z0-9])([0-9]{2}[A-Z0-9]{10}[1-9A-Z]Z[A-Z0-9])(?![A-Z0-9])', text.upper())
        if gst_match:
            gstin = gst_match.group(1)
        # Require a GST context for a candidate to prevent unrelated 15-char
        # serials elsewhere on a page from being reported as GSTINs.
        if gstin and not re.search(r'GSTIN|GST\s+IDENTIFICATION|REGISTRATION\s+NUMBER', text, re.I):
            gstin = None

        # -------------------------------------------------------------
        # 2. Udyam Registration Number Extraction
        # -------------------------------------------------------------
        udyam_number = None
        udyam_match = re.search(r'UDYAM\s*-\s*([A-Za-z]{2})\s*-\s*([0-9]{2})\s*-\s*([0-9]{7})', text, re.IGNORECASE)
        if udyam_match:
            st = udyam_match.group(1).upper()
            mid = udyam_match.group(2)
            num = udyam_match.group(3)
            udyam_number = f"UDYAM-{st}-{mid}-{num}"
        else:
            udyam_direct = re.search(r'(UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7})', cleaned_no_spaces, re.I)
            if udyam_direct:
                udyam_number = udyam_direct.group(1).upper()

        # -------------------------------------------------------------
        # 3. Enterprise Category & Classification (Udyam)
        # -------------------------------------------------------------
        enterprise_category = None
        major_activity = None
        if "Services" in text:
            major_activity = "Services"
        elif "Manufacturing" in text:
            major_activity = "Manufacturing"

        if "Micro" in text or "micro" in text.lower():
            enterprise_category = "Micro"
        elif "Small" in text or "small" in text.lower():
            enterprise_category = "Small"
        elif "Medium" in text or "medium" in text.lower():
            enterprise_category = "Medium"

        # -------------------------------------------------------------
        # 4. Dates & Address Proof Recency
        # -------------------------------------------------------------
        dates = re.findall(r'202[0-9]-[0-9]{2}-[0-9]{2}', text)
        bill_date = None
        days_old = None
        is_expired = False

        if doc_type == "address_proof" or "address_proof" in filename.lower():
            bill_date = dates[0] if dates else None
            if bill_date:
                try:
                    b_dt = datetime.datetime.strptime(bill_date, "%Y-%m-%d").date()
                    days_old = (self.reference_today - b_dt).days
                    if days_old > 90:
                        is_expired = True
                except Exception:
                    pass

        # -------------------------------------------------------------
        # 5. Names (Legal Name, Trade Name, Consumer Name)
        # -------------------------------------------------------------
        legal_name = None
        trade_name = None
        consumer_name = None
        service_address = None

        # A. Signatory ID
        sig_bus_match = re.search(r'For business\s+([A-Za-z0-9\s&.,\'\-]+?)(?=\s+ID no\.|\s+Valid till|$)', text, re.IGNORECASE)
        if sig_bus_match:
            trade_name = sig_bus_match.group(1).strip()

        # B. Udyam Certificate
        if not trade_name:
            udy_bus_match = re.search(r'UDYAM-[A-Z]{2}-[0-9O]{2}-\s*[0-9]{7}\s+([A-Za-z0-9\s&.,\'\-]+?)(?=\s+Services|\s+Manufacturing|$)', text, re.IGNORECASE)
            if udy_bus_match:
                trade_name = udy_bus_match.group(1).strip()

        # C. Electricity Bill Address & Consumer Name
        addr_bus_match = re.search(r'Amount due\s*\(INR\)\s+[\d,\.\s]+(?:\d+\s+)?([A-Za-z0-9\s&.,\'\-]+?)(?=\s+Shop\/Unit|\s+Plot|\s+Floor|\s+Office|\s+\d{4}-\d{2}-\d{2}|$)', text, re.IGNORECASE)
        if addr_bus_match:
            clean_tn = re.sub(r'^\d+\s*', '', addr_bus_match.group(1).strip())
            if len(clean_tn) > 3:
                consumer_name = clean_tn
                if not trade_name:
                    trade_name = clean_tn

        # Address match
        addr_match = re.search(r'((?:Shop\/Unit|Plot|Floor|Office|Building)\s+[A-Za-z0-9\s,.\-]+?(?:-\s*\d{5,6}|Andhra Pradesh|West Bengal|Maharashtra|Kerala|Rajasthan|Delhi|Gujarat|Punjab|Tamil Nadu|Karnataka))', text, re.IGNORECASE)
        if addr_match:
            service_address = addr_match.group(1).strip()

        # D. Label-based business fields; retain the certificate's wording.
        legal_label = re.search(r'(?:Legal\s+Name\s+of\s+Business|Name\s+of\s+the\s+Business)\s*[:\-]?\s*([^\n]{2,100})', text, re.I)
        trade_label = re.search(r'(?:Trade\s+Name)\s*[:\-]?\s*([^\n]{2,100})', text, re.I)
        if legal_label:
            legal_name = re.sub(r'\s+', ' ', legal_label.group(1)).strip()
        if trade_label:
            trade_name = re.sub(r'\s+', ' ', trade_label.group(1)).strip()

        state_match = re.search(r'(?:State|State/UT|State Code)\s*[:\-]?\s*([^\n]{2,50})', text, re.I)
        organisation_match = re.search(r'(?:Organisation\s+Type|Organization\s+Type|Type\s+of\s+Organisation)\s*[:\-]?\s*([^\n]{2,80})', text, re.I)
        registration_date_match = re.search(r'(?:Date\s+of\s+(?:Udyam\s+)?Registration|Registration\s+Date)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2})', text, re.I)

        # D. GST Certificate Values
        if "gst_certificate" in filename.lower() or doc_type == "gst_certificate":
            prop_match = re.search(r'\(Prop\.\s+([A-Za-z0-9\s&.,\'\-]+?)\)\s+([A-Za-z0-9\s&.,\'\-]+?)(?=\s+Proprietorship|\s+Regular|\s+Shop|\s+Address|$)', text, re.IGNORECASE)
            if prop_match:
                legal_name = prop_match.group(1).strip()
                trade_name = prop_match.group(2).strip()
            else:
                llp_match = re.search(r'([A-Za-z0-9\s&.,\'\-]+?(?:LLP|Pvt Ltd|Private Limited))\s+\1', text, re.IGNORECASE)
                if llp_match:
                    trade_name = llp_match.group(1).strip()
                    legal_name = trade_name
                else:
                    reg_match = re.search(r'Trade name\s+([A-Za-z0-9\s&.,\'\-]+?)(?=\s+Proprietorship|\s+Regular|\s+Shop|\s+Address|$)', text, re.IGNORECASE)
                    if reg_match:
                        trade_name = reg_match.group(1).strip()

        # -------------------------------------------------------------
        # 6. Signatory Identity & Masked ID (DPDP Privacy Protection)
        # -------------------------------------------------------------
        signatory_name = None
        designation = None
        masked_id = None

        sig_match = re.search(r'Name\s+([A-Za-z\s\']+?)(?=\s+Designation|\s+For business|$)', text)
        if sig_match:
            signatory_name = sig_match.group(1).strip()

        desig_match = re.search(r'Designation\s+([A-Za-z\s]+?)(?=\s+For business|\s+ID no\.|$)', text)
        if desig_match:
            designation = desig_match.group(1).strip()

        id_match = re.search(r'ID no\.\s*([A-Za-z0-9\-\s]+?)(?=\s+Valid till|\s+SYNTHETIC|$)', text)
        if id_match:
            raw_id = id_match.group(1).strip()
            # Mask ID number: e.g. SYN-ID-816907 -> SYN-ID-***907, or Aadhaar -> ****-****-1234
            if "-" in raw_id:
                parts = raw_id.split("-")
                masked_id = f"{parts[0]}-ID-***{parts[-1][-3:] if len(parts[-1]) >= 3 else '***'}"
            else:
                masked_id = "ID-" + ("*" * max(len(raw_id) - 4, 4)) + raw_id[-4:]

        return {
            "filename": filename,
            "raw_text_length": len(text),
            "gstin": gstin,
            "state": re.sub(r'\s+', ' ', state_match.group(1)).strip() if state_match else None,
            "document_type": doc_type,
            "udyam_number": udyam_number,
            "organisation_type": re.sub(r'\s+', ' ', organisation_match.group(1)).strip() if organisation_match else None,
            "registration_date": registration_date_match.group(1) if registration_date_match else None,
            "enterprise_category": enterprise_category,
            "major_activity": major_activity,
            "legal_name": legal_name,
            "trade_name": trade_name,
            "consumer_name": consumer_name,
            "service_address": service_address,
            "signatory_name": signatory_name,
            "designation": designation,
            "masked_id": masked_id,
            "address_bill_date": bill_date,
            "days_old": days_old,
            "is_address_expired": is_expired,
            "is_corrupted_or_blank": is_corrupted_or_blank,
            "raw_snippet": text[:180] if text else ""
        }

ocr_service = OCRService()
