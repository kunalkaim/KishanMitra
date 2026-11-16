import os
import sys
import json

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.document import KnowledgeDocument, KnowledgeChunk
from app.rag.retrieval.vector_store import PersistentChromaVectorStore

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST_PATH = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "metadata", "document_manifest.json")
CHUNKS_DIR = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "processed", "chunks")


def sync_relational_knowledge_base():
    print("=" * 70)
    print("KISANMITRA: RELATIONAL DATABASE & CHROMADB SYNCHRONIZATION")
    print("=" * 70)

    if not os.path.exists(MANIFEST_PATH):
        raise FileNotFoundError(f"Manifest not found at {MANIFEST_PATH}")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    db = SessionLocal()
    vector_store = PersistentChromaVectorStore()
    chroma_count = vector_store.count()
    print(f"Current ChromaDB Vectors Count: {chroma_count}")

    synced_docs = 0
    synced_chunks = 0

    try:
        for doc_meta in manifest.get("documents", []):
            doc_id = doc_meta["document_id"]
            title = doc_meta["title"]
            chunk_file = os.path.join(CHUNKS_DIR, f"{doc_id}_chunks.json")

            if not os.path.exists(chunk_file):
                print(f"[Notice] No chunk JSON file for {doc_id}; skipping chunk sync.")
                continue

            with open(chunk_file, "r", encoding="utf-8") as cf:
                chunk_data = json.load(cf)

            chunks = chunk_data.get("chunks", [])
            print(f"\n[Processing Document] {title} ({doc_id})")
            print(f"  Available Chunks in File: {len(chunks)}")

            # 1. Upsert KnowledgeDocument
            db_doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
            if not db_doc:
                db_doc = KnowledgeDocument(
                    id=doc_id,
                    title=title,
                    source_organization=doc_meta.get("publisher", "GBPUAT Pantnagar"),
                    category=doc_meta.get("document_type", "Agricultural Extension Publication"),
                    publication_date=doc_meta.get("publication_date", "2026-01-01"),
                    document_type=doc_meta.get("document_type", "PDF / Research Bulletin"),
                    file_path=doc_meta.get("file_path"),
                    is_verified=True
                )
                db.add(db_doc)
                print(f"  + Inserted KnowledgeDocument: {doc_id}")
            else:
                db_doc.title = title
                db_doc.publication_date = doc_meta.get("publication_date", db_doc.publication_date)
                db_doc.file_path = doc_meta.get("file_path", db_doc.file_path)
                print(f"  ✓ KnowledgeDocument already exists: {doc_id}")

            db.commit()
            synced_docs += 1

            # 2. Upsert KnowledgeChunk records
            for c in chunks:
                c_id = c["chunk_id"]
                existing_chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == c_id).first()
                chunk_meta = {
                    "document_id": doc_id,
                    "document_title": title,
                    "publisher": c.get("publisher", doc_meta.get("publisher")),
                    "publication_date": c.get("publication_date", doc_meta.get("publication_date")),
                    "page_start": c.get("page_start"),
                    "page_end": c.get("page_end"),
                    "source_url": c.get("source_url"),
                    "crops": c.get("crops", []),
                    "categories": c.get("categories", []),
                    "is_historical": c.get("is_historical", False),
                    "token_estimate": c.get("token_estimate", 0)
                }

                if not existing_chunk:
                    new_chunk = KnowledgeChunk(
                        id=c_id,
                        document_id=doc_id,
                        chunk_text=c["chunk_text"],
                        chunk_index=c.get("chunk_index", 0),
                        metadata_json=chunk_meta
                    )
                    db.add(new_chunk)
                    synced_chunks += 1
                else:
                    existing_chunk.chunk_text = c["chunk_text"]
                    existing_chunk.metadata_json = chunk_meta

            db.commit()
            print(f"  ✓ Synchronized {len(chunks)} chunks into relational database.")

        # Post-synchronization verification
        print("\n" + "=" * 70)
        print("SYNCHRONIZATION COMPLETED: FINAL AUDIT VERIFICATION")
        print("=" * 70)

        total_sql_docs = db.query(KnowledgeDocument).count()
        total_sql_chunks = db.query(KnowledgeChunk).count()
        ingested_sql_chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.document_id.in_([
                "gbpuat-uttarakhand-kharif-advisory-2020",
                "gbpuat-pant-prasar-sandesh-apr-jun-2026",
                "gbpuat-pant-prasar-sandesh-jul-sep-2026"
            ])
        ).count()
        seed_chunks = total_sql_chunks - ingested_sql_chunks

        print(f"Total SQL Documents:          {total_sql_docs}")
        print(f"  - Baseline Seed Documents:  {total_sql_docs - 3}")
        print(f"  - Ingested PDF Documents:   3")
        print(f"Total SQL Chunks:             {total_sql_chunks}")
        print(f"  - Baseline Seed Chunks:     {seed_chunks}")
        print(f"  - Ingested PDF Chunks:      {ingested_sql_chunks}")
        print(f"ChromaDB Total Vectors:       {chroma_count}")

        # Check 1:1 mapping between ChromaDB vector IDs and SQL chunk IDs
        chroma_data = vector_store.collection.get()
        chroma_ids = set(chroma_data["ids"])
        sql_chunk_rows = db.query(KnowledgeChunk.id).filter(
            KnowledgeChunk.document_id.in_([
                "gbpuat-uttarakhand-kharif-advisory-2020",
                "gbpuat-pant-prasar-sandesh-apr-jun-2026",
                "gbpuat-pant-prasar-sandesh-jul-sep-2026"
            ])
        ).all()
        sql_ids = {r[0] for r in sql_chunk_rows}

        missing_in_sql = chroma_ids - sql_ids
        missing_in_chroma = sql_ids - chroma_ids

        print(f"ChromaDB <-> SQL Ingested Parity:")
        print(f"  - Vectors Missing in SQL:    {len(missing_in_sql)}")
        print(f"  - Ingested SQL Missing in Vector Store: {len(missing_in_chroma)}")

        if not missing_in_sql and not missing_in_chroma and ingested_sql_chunks == 24 and chroma_count == 24:
            print(">>> STATUS: PERFECT 100% PARITY ACHIEVED BETWEEN RELATIONAL AND VECTOR STORES! <<<")
        else:
            print(">>> WARNING: Parity discrepancy detected. <<<")

    finally:
        db.close()


if __name__ == "__main__":
    sync_relational_knowledge_base()
