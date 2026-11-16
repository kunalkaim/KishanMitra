import os
import json
import numpy as np
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.document import KnowledgeDocument, KnowledgeChunk
from app.rag.embeddings.embedding_provider import get_embedding_provider
from app.rag.retrieval.vector_store import PersistentChromaVectorStore

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST_PATH = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "metadata", "document_manifest.json")
CHUNKS_DIR = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "processed", "chunks")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "reports")


def index_knowledge_corpus():
    print("=" * 70)
    print("STAGE 7 & 8: MULTILINGUAL EMBEDDINGS & PERSISTENT VECTOR INDEXING")
    print("=" * 70)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    db: Session = SessionLocal()
    vector_store = PersistentChromaVectorStore()
    embedding_provider = get_embedding_provider()
    print(f"Active Embedding Provider: {embedding_provider.model_name} (dim={embedding_provider.dimension})")

    total_chunks_indexed = 0
    total_docs_indexed = 0

    try:
        for doc_meta in manifest["documents"]:
            doc_id = doc_meta["document_id"]
            title = doc_meta["title"]
            chunk_file = os.path.join(CHUNKS_DIR, f"{doc_id}_chunks.json")

            if not os.path.exists(chunk_file):
                print(f"Skipping {doc_id} (no chunks generated; e.g. scanned document).")
                # Record in DB as scanned / pending OCR
                existing_doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
                if not existing_doc:
                    db_doc = KnowledgeDocument(
                        id=doc_id,
                        title=title,
                        source_organization=doc_meta["publisher"],
                        category=doc_meta["document_type"],
                        publication_date=doc_meta["publication_date"],
                        document_type=doc_meta["document_type"],
                        file_path=doc_meta["file_path"],
                        is_verified=True
                    )
                    db.add(db_doc)
                    db.commit()
                continue

            with open(chunk_file, "r", encoding="utf-8") as cf:
                chunk_data = json.load(cf)

            chunks = chunk_data.get("chunks", [])
            if not chunks:
                continue

            print(f"\n[Indexing] {title}")
            print(f"  Total Chunks: {len(chunks)}")

            # 1. Update / Insert DB Document Record
            db_doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
            if not db_doc:
                db_doc = KnowledgeDocument(
                    id=doc_id,
                    title=title,
                    source_organization=doc_meta["publisher"],
                    category=doc_meta["document_type"],
                    publication_date=doc_meta["publication_date"],
                    document_type=doc_meta["document_type"],
                    file_path=doc_meta["file_path"],
                    is_verified=True
                )
                db.add(db_doc)
                db.commit()
            else:
                db_doc.title = title
                db_doc.publication_date = doc_meta["publication_date"]
                db.commit()

            # 2. Extract chunk texts and compute embeddings
            chunk_texts = [c["chunk_text"] for c in chunks]
            chunk_ids = [c["chunk_id"] for c in chunks]
            metadatas = [
                {
                    "document_id": doc_id,
                    "document_title": title,
                    "publisher": c["publisher"],
                    "publication_date": c["publication_date"],
                    "page_start": c["page_start"],
                    "page_end": c["page_end"],
                    "source_url": c["source_url"],
                    "crops": c["crops"],
                    "categories": c["categories"],
                    "is_historical": c["is_historical"]
                }
                for c in chunks
            ]

            print(f"  Generating {len(chunk_texts)} multilingual embeddings...")
            embeddings = embedding_provider.encode_documents(chunk_texts)
            print(f"  ✓ Generated embeddings array of shape {embeddings.shape}")

            # 3. Store in Chroma Vector Store
            vector_store.add_chunks(
                chunk_ids=chunk_ids,
                embeddings=embeddings,
                texts=chunk_texts,
                metadatas=metadatas
            )
            print(f"  ✓ Upserted {len(chunks)} vectors to Chroma persistent store.")

            # 4. Insert / Update KnowledgeChunk in SQL database
            for c in chunks:
                c_id = c["chunk_id"]
                existing_chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == c_id).first()
                if not existing_chunk:
                    db_chunk = KnowledgeChunk(
                        id=c_id,
                        document_id=doc_id,
                        chunk_text=c["chunk_text"],
                        chunk_index=c["chunk_index"],
                        metadata_json={
                            "page_start": c["page_start"],
                            "page_end": c["page_end"],
                            "crops": c["crops"],
                            "categories": c["categories"],
                            "is_historical": c["is_historical"]
                        }
                    )
                    db.add(db_chunk)
                else:
                    existing_chunk.chunk_text = c["chunk_text"]
                    existing_chunk.metadata_json = {
                        "page_start": c["page_start"],
                        "page_end": c["page_end"],
                        "crops": c["crops"],
                        "categories": c["categories"],
                        "is_historical": c["is_historical"]
                    }
            db.commit()
            print(f"  ✓ Synced {len(chunks)} chunk records into relational database.")

            total_chunks_indexed += len(chunks)
            total_docs_indexed += 1

        print("\n" + "=" * 70)
        print("INDEXING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Documents Indexed in Vector DB:  {total_docs_indexed}")
        print(f"Knowledge Chunks Stored:         {total_chunks_indexed}")
        print(f"Chroma Total Collection Count:   {vector_store.count()}")

    finally:
        db.close()


if __name__ == "__main__":
    index_knowledge_corpus()
