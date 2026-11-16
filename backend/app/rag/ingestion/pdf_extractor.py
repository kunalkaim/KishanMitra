import os
import re
import json
import pymupdf
from typing import Dict, Any, List, Optional


class PDFTextExtractor:
    """
    Page-by-page PDF extraction pipeline preserving:
    - 1-based page numbers
    - Headings, paragraphs, and structured advisory tables
    - Unicode Devanagari Hindi characters
    - OCR detection and failure tracking
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
            "datasets", "agricultural_knowledge", "processed", "extracted_text"
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_document(
        self,
        pdf_path: str,
        document_id: str,
        title: str,
        publisher: str,
        publication_date: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF document not found at: {pdf_path}")

        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)
        pages_data: List[Dict[str, Any]] = []
        pages_native_count = 0
        pages_ocr_needed = 0

        for p_idx in range(total_pages):
            page_num = p_idx + 1
            page = doc[p_idx]
            
            # 1. Native text extraction
            raw_text = page.get_text("text")
            clean_text = self._clean_page_text(raw_text)

            # Detect headings and structured lines
            blocks = page.get_text("blocks")
            headings = []
            for b in blocks:
                b_text = b[4].strip()
                # Heuristic: Short capitalized or bold-like single-line headers
                if 3 < len(b_text) < 80 and ("\n" not in b_text or len(b_text.split("\n")) <= 2):
                    if any(kw in b_text.lower() for kw in ["advisory", "crop", "season", "rice", "maize", "varieties", "sowing", "management", "रोग", "प्रबंधन", "कृषि"]):
                        headings.append(b_text.replace("\n", " "))

            char_count = len(clean_text)
            requires_ocr = (char_count < 50)
            if requires_ocr:
                pages_ocr_needed += 1
                ocr_note = "Scanned/vector outline page; insufficient native digital text."
            else:
                pages_native_count += 1
                ocr_note = "Successfully extracted via native PyMuPDF digital parser."

            pages_data.append({
                "page_number": page_num,
                "char_count": char_count,
                "text": clean_text,
                "headings": headings[:10],
                "requires_ocr": requires_ocr,
                "extraction_method": "ocr_needed" if requires_ocr else "native_pdf",
                "notes": ocr_note
            })

        doc.close()

        extracted_doc = {
            "document_id": document_id,
            "title": title,
            "publisher": publisher,
            "publication_date": publication_date,
            "source_pdf": os.path.basename(pdf_path),
            "file_path": pdf_path,
            "total_pages": total_pages,
            "pages_extracted_native": pages_native_count,
            "pages_requiring_ocr": pages_ocr_needed,
            "extraction_status": "complete" if pages_native_count > 0 else "partial_scanned",
            "metadata": metadata or {},
            "pages": pages_data
        }

        # Save to processed/extracted_text/
        out_path = os.path.join(self.output_dir, f"{document_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(extracted_doc, f, indent=2, ensure_ascii=False)

        return extracted_doc

    def _clean_page_text(self, text: str) -> str:
        """Preserves Devanagari Hindi and English, removes repetitive headers/excess whitespace."""
        if not text:
            return ""
        # Remove repeated page numbers / footers
        lines = text.splitlines()
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # Skip single lone page numbers
            if stripped.isdigit() and len(stripped) <= 3:
                continue
            cleaned_lines.append(stripped)

        joined = "\n".join(cleaned_lines)
        # Collapse excessive newlines
        joined = re.sub(r'\n{3,}', '\n\n', joined)
        return joined.strip()
