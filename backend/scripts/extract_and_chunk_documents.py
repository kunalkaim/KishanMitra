import os
import json
from app.rag.ingestion.pdf_extractor import PDFTextExtractor
from app.rag.ingestion.chunker import IntelligentAgriculturalChunker

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST_PATH = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "metadata", "document_manifest.json")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "reports")


def process_all_documents():
    print("=" * 70)
    print("STAGE 5 & 6: PAGE-BY-PAGE PDF EXTRACTION & INTELLIGENT CHUNKING")
    print("=" * 70)

    if not os.path.exists(MANIFEST_PATH):
        raise FileNotFoundError(f"Manifest not found at {MANIFEST_PATH}")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    extractor = PDFTextExtractor()
    chunker = IntelligentAgriculturalChunker(chunk_size_chars=1200, chunk_overlap_chars=200)

    total_pages_extracted = 0
    total_pages_native = 0
    total_pages_ocr_needed = 0
    total_chunks_created = 0

    extraction_records = []
    chunk_records = []

    for doc_meta in manifest["documents"]:
        doc_id = doc_meta["document_id"]
        title = doc_meta["title"]
        publisher = doc_meta["publisher"]
        pub_date = doc_meta["publication_date"]
        pdf_path = os.path.join(PROJECT_ROOT, doc_meta["file_path"].replace("/", os.sep))

        print(f"\n[Processing] {title}")
        print(f"  PDF File: {pdf_path}")

        extracted_doc = extractor.extract_document(
            pdf_path=pdf_path,
            document_id=doc_id,
            title=title,
            publisher=publisher,
            publication_date=pub_date,
            metadata=doc_meta
        )

        pages = extracted_doc["pages"]
        p_native = extracted_doc["pages_extracted_native"]
        p_ocr = extracted_doc["pages_requiring_ocr"]

        total_pages_extracted += len(pages)
        total_pages_native += p_native
        total_pages_ocr_needed += p_ocr

        print(f"  Pages Total: {len(pages)} | Native Extracted: {p_native} | Requiring OCR: {p_ocr}")

        # Intelligent chunking
        chunks = chunker.chunk_extracted_document(extracted_doc)
        total_chunks_created += len(chunks)
        print(f"  Intelligent Chunks Created: {len(chunks)}")

        for c in chunks:
            print(f"    - Chunk {c['chunk_id']}: Pages {c['page_start']}-{c['page_end']} | {c['token_estimate']} tokens | Crops: {c['crops'][:2]}")

        extraction_records.append({
            "document_id": doc_id,
            "title": title,
            "total_pages": len(pages),
            "native_pages": p_native,
            "ocr_pages_needed": p_ocr,
            "chunks_count": len(chunks)
        })

    # Save extraction report
    extraction_report = {
        "status": "success",
        "total_documents": len(manifest["documents"]),
        "total_pages": total_pages_extracted,
        "total_native_pages": total_pages_native,
        "total_pages_requiring_ocr": total_pages_ocr_needed,
        "total_chunks_generated": total_chunks_created,
        "documents": extraction_records
    }

    report_path = os.path.join(REPORTS_DIR, "extraction_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(extraction_report, f, indent=2)

    print("\n" + "=" * 70)
    print("EXTRACTION & CHUNKING SUMMARY")
    print("=" * 70)
    print(f"Total Documents:           {len(manifest['documents'])}")
    print(f"Total Pages Analyzed:      {total_pages_extracted}")
    print(f"Pages with Native Text:    {total_pages_native}")
    print(f"Pages Requiring OCR:       {total_pages_ocr_needed}")
    print(f"Total Chunks Generated:    {total_chunks_created}")
    print(f"Saved extraction report to: {report_path}")


if __name__ == "__main__":
    process_all_documents()
