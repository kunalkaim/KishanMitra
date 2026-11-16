import os
import re
import json
import uuid
from typing import Dict, Any, List, Optional


class IntelligentAgriculturalChunker:
    """
    Agricultural knowledge chunker aware of:
    - Section and heading boundaries
    - Paragraph splits
    - Page transitions and exact page citations
    - Crop, agronomic category, and seasonal metadata
    """

    def __init__(
        self,
        chunk_size_chars: int = 1500,
        chunk_overlap_chars: int = 250,
        output_dir: Optional[str] = None
    ):
        self.chunk_size_chars = chunk_size_chars
        self.chunk_overlap_chars = chunk_overlap_chars
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
            "datasets", "agricultural_knowledge", "processed", "chunks"
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def chunk_extracted_document(self, extracted_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        doc_id = extracted_doc["document_id"]
        title = extracted_doc["title"]
        publisher = extracted_doc["publisher"]
        pub_date = extracted_doc["publication_date"]
        source_url = extracted_doc.get("metadata", {}).get("source_url", "")
        state = extracted_doc.get("metadata", {}).get("state", "Uttarakhand")
        is_historical = (pub_date < "2024-01-01")

        chunks: List[Dict[str, Any]] = []
        chunk_index = 0

        pages = extracted_doc.get("pages", [])
        
        # Iterate page by page to guarantee strict page attribution
        for page_obj in pages:
            page_num = page_obj["page_number"]
            page_text = page_obj["text"].strip()
            
            if not page_text or len(page_text) < 40:
                continue

            # Quality Gate: Only chunk pages that are verified and ACCEPTED
            # Skip pages that are quarantined (NEEDS_REVIEW) or REJECTED
            quality_status = page_obj.get("quality_status")
            if quality_status and quality_status != "ACCEPTED":
                continue

            # Split page into logical paragraphs / sections
            paragraphs = re.split(r'\n\s*\n', page_text)
            
            current_chunk_text = ""
            current_headings = list(page_obj.get("headings", []))

            for para in paragraphs:
                para_clean = para.strip()
                if not para_clean:
                    continue

                if len(current_chunk_text) + len(para_clean) < self.chunk_size_chars:
                    if current_chunk_text:
                        current_chunk_text += "\n\n" + para_clean
                    else:
                        current_chunk_text = para_clean
                else:
                    # Flush current chunk
                    if current_chunk_text:
                        chunk_item = self._create_chunk_record(
                            doc_id=doc_id,
                            chunk_index=chunk_index,
                            text=current_chunk_text,
                            title=title,
                            publisher=publisher,
                            pub_date=pub_date,
                            source_url=source_url,
                            page_start=page_num,
                            page_end=page_num,
                            state=state,
                            is_historical=is_historical,
                            headings=current_headings
                        )
                        chunks.append(chunk_item)
                        chunk_index += 1

                    # Start new chunk with overlap if feasible
                    if len(current_chunk_text) > self.chunk_overlap_chars:
                        overlap_tail = current_chunk_text[-self.chunk_overlap_chars:].strip()
                        current_chunk_text = overlap_tail + "\n\n" + para_clean
                    else:
                        current_chunk_text = para_clean

            # Flush final remaining text on page
            if current_chunk_text and len(current_chunk_text.strip()) > 30:
                chunk_item = self._create_chunk_record(
                    doc_id=doc_id,
                    chunk_index=chunk_index,
                    text=current_chunk_text,
                    title=title,
                    publisher=publisher,
                    pub_date=pub_date,
                    source_url=source_url,
                    page_start=page_num,
                    page_end=page_num,
                    state=state,
                    is_historical=is_historical,
                    headings=current_headings
                )
                chunks.append(chunk_item)
                chunk_index += 1

        # Save to processed/chunks/
        out_path = os.path.join(self.output_dir, f"{doc_id}_chunks.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({
                "document_id": doc_id,
                "document_title": title,
                "total_chunks": len(chunks),
                "chunks": chunks
            }, f, indent=2, ensure_ascii=False)

        return chunks

    def _create_chunk_record(
        self,
        doc_id: str,
        chunk_index: int,
        text: str,
        title: str,
        publisher: str,
        pub_date: str,
        source_url: str,
        page_start: int,
        page_end: int,
        state: str,
        is_historical: bool,
        headings: List[str]
    ) -> Dict[str, Any]:
        crops_found = self._detect_crops(text)
        categories_found = self._detect_categories(text)

        return {
            "chunk_id": f"{doc_id}-c{chunk_index:04d}",
            "document_id": doc_id,
            "chunk_index": chunk_index,
            "chunk_text": text.strip(),
            "document_title": title,
            "publisher": publisher,
            "publication_date": pub_date,
            "source_url": source_url,
            "page_start": page_start,
            "page_end": page_end,
            "state": state,
            "districts": ["All Uttarakhand", "Hill & Plain zones"],
            "crops": crops_found,
            "categories": categories_found,
            "is_historical": is_historical,
            "headings": headings,
            "token_estimate": len(text.split())
        }

    def _detect_crops(self, text: str) -> List[str]:
        t_low = text.lower()
        candidates = {
            "Rice / Paddy / धान": ["rice", "paddy", "धान", "बासमती", "basmati", "narendra", "pant dhan"],
            "Maize / मक्का": ["maize", "मक्का", "corn", "kanchan", "naveen", "vivek maize"],
            "Finger Millet / Mandua / मंडुआ": ["finger millet", "mandua", "मंडुआ", "ragi", "रागी", "vl mandua"],
            "Barnyard Millet / Jhangora / झंगोरा": ["barnyard", "jhangora", "झंगोरा", "prj 1", "vl 207"],
            "Soybean / Bhatt / भट्ट": ["soybean", "bhatt", "भट्ट", "vl bhatt", "काला सोयाबीन"],
            "Pigeonpea / Arhar / अरहर": ["pigeonpea", "arhar", "अरहर", "upas 120"],
            "Tomato / टमाटर": ["tomato", "टमाटर", "himsona", "naveen 2000", "arka rakshak"],
            "Chilli & Capsicum / मिर्च": ["chilli", "capsicum", "मिर्च", "शिमला मिर्च"],
            "Gourds / लौकी / खीरा": ["gourd", "cucumber", "लौकी", "खीरा", "करेला"],
            "Fisheries / मत्स्य पालन": ["fish", "fisheries", "मत्स्य", "तालाब", "pond", "cow dung"],
            "Dairy & Fodder / चारा": ["fodder", "dairy", "चारा", "cowpea", "sorghum", "पशुपालन"]
        }
        detected = []
        for label, keywords in candidates.items():
            if any(kw in t_low for kw in keywords):
                detected.append(label)
        return detected or ["General Agriculture / सामान्य कृषि"]

    def _detect_categories(self, text: str) -> List[str]:
        t_low = text.lower()
        candidates = {
            "Varietal Selection & Sowing": ["varieties", "variety", "sowing", "प्रजातियां", "बुवाई", "बीज दर", "seed rate"],
            "Soil & Nutrient Management": ["fertilizer", "npk", "urea", "dung", "compost", "उर्वरक", "खाद", "गोबर"],
            "Plant Protection & Disease Management": ["disease", "pest", "blast", "blight", "रोग", "कीट", "उपचार", "fungicide"],
            "Water & Pond Management": ["water", "irrigation", "moisture", "जल", "सिंचाई", "pond", "तालाब"],
            "Horticulture & Vegetables": ["vegetable", "tomato", "chilli", "सब्जी", "उद्यानिकी"],
            "Animal Husbandry & Fisheries": ["dairy", "poultry", "fish", "पशुपालन", "मत्स्य"]
        }
        detected = []
        for label, keywords in candidates.items():
            if any(kw in t_low for kw in keywords):
                detected.append(label)
        return detected or ["Agronomic Advisory"]
