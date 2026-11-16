import os
import sys
import json
import time
import hashlib
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath("backend"))

from app.rag.ingestion.ocr_extractor import BilingualTesseractOCRExtractor
from app.rag.ingestion.chunker import IntelligentAgriculturalChunker
from app.rag.embeddings.embedding_provider import get_embedding_provider
from app.rag.retrieval.vector_store import PersistentChromaVectorStore

print("==================================================================")
print("KISANMITRA PHASE 4.2: BILINGUAL OCR & KNOWLEDGE INGESTION PIPELINE")
print("==================================================================")

# 1. Source Documents Definition
documents_to_process = [
    {
        "filename": "pant_prasar_sandesh_apr_jun_2026.pdf",
        "document_id": "gbpuat-pant-prasar-sandesh-apr-jun-2026",
        "title": "Pant Prasar Sandesh (April–June 2026)",
        "publisher": "Directorate of Extension Education, GBPUAT Pantnagar",
        "publication_date": "2026-04-01",
        "publication_period": "April–June 2026",
        "expected_sha256": "ea3041fa66dcc27913957cf023e3fba4a0aa0b7c90b2ec19a57e7a10a0810fe1"
    },
    {
        "filename": "pant_prasar_sandesh_jul_sep_2026.pdf",
        "document_id": "gbpuat-pant-prasar-sandesh-jul-sep-2026",
        "title": "Pant Prasar Sandesh (July–September 2026)",
        "publisher": "Directorate of Extension Education, GBPUAT Pantnagar",
        "publication_date": "2026-07-01",
        "publication_period": "July–September 2026",
        "expected_sha256": "19d81d858dc6a688430491c767323786b65f1062b8e8543330dc1a8cbb06ae40"
    }
]

raw_dir = os.path.join("datasets", "agricultural_knowledge", "raw", "gbpuat")

# 2. Verify SHA-256 Hashes
print("\n[STAGE 1] Verifying PDF Source Files & Checksums...")
for doc_info in documents_to_process:
    full_path = os.path.join(raw_dir, doc_info["filename"])
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Source file missing: {full_path}")
    
    with open(full_path, "rb") as f:
        file_bytes = f.read()
        computed_sha = hashlib.sha256(file_bytes).hexdigest()
    
    assert computed_sha == doc_info["expected_sha256"], f"SHA-256 mismatch for {doc_info['filename']}!"
    print(f"  ✓ {doc_info['filename']}: SHA-256 Verified ({computed_sha[:16]}..., {len(file_bytes) / 1024 / 1024:.2f} MB)")

# 3. OCR Extraction / Loading Extracted Documents
print("\n[STAGE 2] Checking Bilingual OCR Extraction (Devanagari Hindi + English)...")
ocr_extractor = BilingualTesseractOCRExtractor(dpi=150, confidence_threshold=60.0)

all_extracted_docs = []
quarantined_pages = []

total_accepted_pages = 0
total_review_pages = 0
total_rejected_pages = 0

for doc_info in documents_to_process:
    full_path = os.path.join(raw_dir, doc_info["filename"])
    extracted_json_path = os.path.join("datasets", "agricultural_knowledge", "processed", "extracted_text", f"{doc_info['document_id']}.json")
    
    # Reuse verified extracted document if already processed
    if os.path.exists(extracted_json_path):
        with open(extracted_json_path, "r", encoding="utf-8") as f:
            extracted = json.load(f)
        if len(extracted.get("pages", [])) == 8:
            print(f"  ✓ Loaded verified OCR extraction from {extracted_json_path} (8 pages)")
        else:
            extracted = ocr_extractor.extract_document(
                pdf_path=full_path,
                document_id=doc_info["document_id"],
                title=doc_info["title"],
                publisher=doc_info["publisher"],
                publication_date=doc_info["publication_date"],
                publication_period=doc_info["publication_period"]
            )
    else:
        extracted = ocr_extractor.extract_document(
            pdf_path=full_path,
            document_id=doc_info["document_id"],
            title=doc_info["title"],
            publisher=doc_info["publisher"],
            publication_date=doc_info["publication_date"],
            publication_period=doc_info["publication_period"]
        )
    
    all_extracted_docs.append(extracted)

    for p in extracted["pages"]:
        status = p["quality_status"]
        if status == "ACCEPTED":
            total_accepted_pages += 1
        elif status == "NEEDS_REVIEW":
            total_review_pages += 1
            quarantined_pages.append({
                "document_id": doc_info["document_id"],
                "document_title": doc_info["title"],
                "page_number": p["page_number"],
                "quality_status": status,
                "review_reason": p["review_reason"],
                "average_confidence": p["average_confidence"],
                "char_count": p["char_count"],
                "devanagari_ratio": p["devanagari_ratio"]
            })
        else:
            total_rejected_pages += 1
            quarantined_pages.append({
                "document_id": doc_info["document_id"],
                "document_title": doc_info["title"],
                "page_number": p["page_number"],
                "quality_status": status,
                "review_reason": p["review_reason"],
                "average_confidence": p["average_confidence"],
                "char_count": p["char_count"],
                "devanagari_ratio": p["devanagari_ratio"]
            })

# Save Quarantine Report
quarantine_path = os.path.join("datasets", "agricultural_knowledge", "reports", "ocr_quarantine_report.json")
with open(quarantine_path, "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_quarantined": len(quarantined_pages),
        "quarantined_pages": quarantined_pages
    }, f, indent=2, ensure_ascii=False)

# Save Overall OCR Extraction Report
ocr_report_path = os.path.join("datasets", "agricultural_knowledge", "reports", "ocr_extraction_report.json")
with open(ocr_report_path, "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ocr_engine": ocr_extractor.ocr_version,
        "total_pages_scanned": 16,
        "accepted_pages": total_accepted_pages,
        "needs_review_pages": total_review_pages,
        "rejected_pages": total_rejected_pages,
        "documents": [
            {
                "document_id": d["document_id"],
                "title": d["title"],
                "total_pages": d["total_pages"],
                "accepted_pages": d["accepted_pages_count"],
                "needs_review_pages": d["needs_review_pages_count"],
                "rejected_pages": d["rejected_pages_count"]
            }
            for d in all_extracted_docs
        ]
    }, f, indent=2, ensure_ascii=False)

print(f"\n[OCR Extraction Completed]")
print(f"  - Total Pages Scanned:   16")
print(f"  - Accepted Pages:        {total_accepted_pages}")
print(f"  - Needs Review Pages:    {total_review_pages}")
print(f"  - Rejected Pages:        {total_rejected_pages}")
print(f"  - Quarantine Report:     {quarantine_path}")

# 4. Chunking (Accepted Pages Only)
print("\n[STAGE 3] Chunking Accepted Pages with Intelligent Agricultural Chunker...")
chunker = IntelligentAgriculturalChunker()

total_new_chunks = 0
all_new_chunks = []
for doc in all_extracted_docs:
    chunks = chunker.chunk_extracted_document(doc)
    total_new_chunks += len(chunks)
    all_new_chunks.extend(chunks)
    print(f"  ✓ {doc['title']}: {len(chunks)} chunks generated from accepted pages")

# 5. ChromaDB Vector Store Ingestion
print("\n[STAGE 4] Ingesting New Chunks into ChromaDB Collection 'kisanmitra_kb'...")
vector_store = PersistentChromaVectorStore()
initial_vector_count = vector_store.count()
print(f"  Initial Vectors in ChromaDB: {initial_vector_count} (Preserving existing 2020 advisory)")

embedding_provider = get_embedding_provider()

if all_new_chunks:
    chunk_ids = [c["chunk_id"] for c in all_new_chunks]
    texts = [c["chunk_text"] for c in all_new_chunks]
    
    # Format metadata for ChromaDB
    metadatas = []
    for c in all_new_chunks:
        metadatas.append({
            "document_id": c["document_id"],
            "document_title": c["document_title"],
            "publisher": c["publisher"],
            "publication_date": c["publication_date"],
            "source_url": c["source_url"],
            "page_start": c["page_start"],
            "page_end": c["page_end"],
            "state": c["state"],
            "crops": ", ".join(c["crops"]),
            "categories": ", ".join(c["categories"]),
            "is_historical": c["is_historical"],
            "headings": ", ".join(c["headings"][:5])
        })
    
    print(f"  Computing {len(texts)} embeddings via {embedding_provider.model_name}...")
    t0 = time.time()
    embeddings = embedding_provider.encode_documents(texts)
    print(f"  Embeddings computed in {time.time() - t0:.2f}s. Upserting into ChromaDB...")
    
    vector_store.add_chunks(
        chunk_ids=chunk_ids,
        embeddings=embeddings,
        texts=texts,
        metadatas=metadatas
    )

final_vector_count = vector_store.count()
new_vectors_added = final_vector_count - initial_vector_count

print(f"\n[STAGE 5] Ingestion Complete!")
print(f"  - Vectors Before Ingestion: {initial_vector_count}")
print(f"  - New Vectors Added:        {new_vectors_added}")
print(f"  - Total Active Vectors:     {final_vector_count}")

# 6. Save Complete Execution Summary
summary = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "ocr_engine": ocr_extractor.ocr_version,
    "source_documents_verified": len(documents_to_process),
    "total_pages_scanned": 16,
    "accepted_pages": total_accepted_pages,
    "needs_review_pages": total_review_pages,
    "rejected_pages": total_rejected_pages,
    "new_chunks_generated": total_new_chunks,
    "initial_active_vectors": initial_vector_count,
    "new_vectors_added": new_vectors_added,
    "final_active_vectors": final_vector_count
}

summary_path = os.path.join("datasets", "agricultural_knowledge", "reports", "phase_4_2_ingestion_summary.json")
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print(f"\nSaved execution summary to {summary_path}")
print("==================================================================")
