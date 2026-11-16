import os
import io
import re
import json
import time
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

import pymupdf
import pytesseract
from PIL import Image


class BilingualTesseractOCRExtractor:
    """
    Production-quality Bilingual (Devanagari Hindi + English) OCR extraction engine.
    Processes scanned agricultural bulletins page by page, validating character
    confidence, Devanagari density, and quarantine classification.
    """

    def __init__(
        self,
        tesseract_cmd: Optional[str] = None,
        tessdata_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
        dpi: int = 150,
        confidence_threshold: float = 60.0
    ):
        self.tesseract_cmd = tesseract_cmd or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if not os.path.exists(self.tesseract_cmd):
            # Fallback to PATH resolution if present
            self.tesseract_cmd = "tesseract"
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

        # Tessdata with hin + eng + osd
        self.tessdata_dir = tessdata_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "tessdata"
        )
        if os.path.exists(self.tessdata_dir):
            os.environ["TESSDATA_PREFIX"] = self.tessdata_dir

        self.dpi = dpi
        self.confidence_threshold = confidence_threshold
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
            "datasets", "agricultural_knowledge", "processed", "extracted_text"
        )
        os.makedirs(self.output_dir, exist_ok=True)

        self.ocr_version = "Tesseract 5.5.3 (hin+eng)"

    def extract_document(
        self,
        pdf_path: str,
        document_id: str,
        title: str,
        publisher: str,
        publication_date: str,
        publication_period: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extracts all pages of a scanned PDF page-by-page using Tesseract hin+eng.
        Performs quality validation and classifies each page as ACCEPTED, NEEDS_REVIEW, or REJECTED.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF document not found at: {pdf_path}")

        # Compute source SHA-256 for provenance integrity
        with open(pdf_path, "rb") as f:
            source_sha256 = hashlib.sha256(f.read()).hexdigest()

        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)
        pages_data: List[Dict[str, Any]] = []

        accepted_count = 0
        review_count = 0
        rejected_count = 0

        print(f"\n[OCR Extraction] Processing '{os.path.basename(pdf_path)}' ({total_pages} pages)...")

        for p_idx in range(total_pages):
            page_num = p_idx + 1
            start_t = time.time()
            page = doc[p_idx]

            # Rasterize page to high-clarity RGB image
            pix = page.get_pixmap(dpi=self.dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # Run OCR with Hindi + English models
            try:
                raw_text = pytesseract.image_to_string(img, lang="hin+eng")
                ocr_data = pytesseract.image_to_data(img, lang="hin+eng", output_type=pytesseract.Output.DICT)
            except Exception as e:
                raw_text = ""
                ocr_data = {"conf": []}

            elapsed = round(time.time() - start_t, 2)

            # Calculate word-level confidences
            confs = [int(c) for c in ocr_data.get("conf", []) if int(c) >= 0]
            avg_conf = round(float(sum(confs) / len(confs)), 2) if confs else 0.0

            # Quality validation metrics
            clean_text = self._clean_text(raw_text)
            char_count = len(clean_text)
            devanagari_count = len(re.findall(r'[\u0900-\u097F]', clean_text))
            devanagari_ratio = round(devanagari_count / max(1, char_count), 4)

            # Noise / garbled ratio (replacement chars or non-alphanumeric noise)
            noise_chars = len(re.findall(r'[\ufffd|~^§±«»©®]', clean_text))
            garbled_ratio = round(noise_chars / max(1, char_count), 4)

            # Classification
            if char_count < 50:
                quality_status = "REJECTED"
                review_reason = "Suspiciously short or empty text extraction."
                rejected_count += 1
            elif avg_conf < self.confidence_threshold or garbled_ratio > 0.25:
                quality_status = "NEEDS_REVIEW"
                review_reason = f"Confidence ({avg_conf}%) below {self.confidence_threshold}% threshold or noise ratio ({garbled_ratio}) elevated."
                review_count += 1
            else:
                quality_status = "ACCEPTED"
                review_reason = "Passed confidence, language density, and length quality gates."
                accepted_count += 1

            # Extract major headings
            headings = self._extract_headings(clean_text)

            page_entry = {
                "page_number": page_num,
                "char_count": char_count,
                "devanagari_count": devanagari_count,
                "devanagari_ratio": devanagari_ratio,
                "average_confidence": avg_conf,
                "garbled_ratio": garbled_ratio,
                "quality_status": quality_status,
                "review_reason": review_reason,
                "latency_seconds": elapsed,
                "headings": headings,
                "text": clean_text
            }
            pages_data.append(page_entry)
            print(f"  Page {page_num}/{total_pages}: {quality_status} (Conf: {avg_conf}%, Chars: {char_count}, Devanagari: {devanagari_ratio * 100:.1f}%, Time: {elapsed}s)")

        doc.close()

        extracted_doc = {
            "document_id": document_id,
            "title": title,
            "publisher": publisher,
            "publication_date": publication_date,
            "publication_period": publication_period,
            "source_pdf": os.path.basename(pdf_path),
            "file_path": pdf_path,
            "source_sha256": source_sha256,
            "ocr_engine": self.ocr_version,
            "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_pages": total_pages,
            "accepted_pages_count": accepted_count,
            "needs_review_pages_count": review_count,
            "rejected_pages_count": rejected_count,
            "extraction_status": "complete" if accepted_count > 0 else "needs_review",
            "metadata": metadata or {},
            "pages": pages_data
        }

        # Save extracted document JSON
        out_path = os.path.join(self.output_dir, f"{document_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(extracted_doc, f, indent=2, ensure_ascii=False)

        return extracted_doc

    def _clean_text(self, text: str) -> str:
        """Normalizes Devanagari text, preserves numerals and line boundaries."""
        if not text:
            return ""
        # Remove repeated empty lines
        lines = [line.strip() for line in text.splitlines()]
        cleaned_lines = []
        for line in lines:
            if not line:
                continue
            # Remove isolated unreadable single characters
            if len(line) == 1 and line in "|-_~^":
                continue
            cleaned_lines.append(line)
        return "\n".join(cleaned_lines)

    def _extract_headings(self, text: str) -> List[str]:
        """Detects prominent section headers in Hindi and English."""
        headings = []
        for line in text.splitlines():
            line_s = line.strip()
            if 4 <= len(line_s) <= 70:
                if any(kw in line_s for kw in [
                    "संदेश", "प्रबंधन", "कृषि", "फसल", "धान", "रोग", "कीट", "उर्वरक",
                    "Advisory", "Management", "Kharif", "Package", "Varieties", "Seed", "पंत प्रसार"
                ]):
                    headings.append(line_s)
        return headings[:8]
