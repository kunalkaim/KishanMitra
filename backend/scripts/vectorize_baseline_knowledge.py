import os
import sys
import json
import sqlite3

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag.embeddings.embedding_provider import get_embedding_provider
from app.rag.retrieval.vector_store import PersistentChromaVectorStore

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "kisanmitra.db")


def vectorize_baseline_knowledge():
    print("=" * 70)
    print("KISANMITRA: PHASE 4.2.3 BASELINE KNOWLEDGE VECTORIZATION")
    print("=" * 70)

    # 1. Connect to SQLite and fetch the 3 baseline documents & 7 chunks
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, title, source_organization, category, publication_date FROM knowledge_documents WHERE id NOT LIKE 'gbpuat%'")
    base_docs = {r[0]: {"title": r[1], "publisher": r[2], "category": r[3], "pub_date": r[4]} for r in cur.fetchall()}
    print(f"Loaded {len(base_docs)} baseline documents from SQLite:")
    for did, dinfo in base_docs.items():
        print(f"  - [{did[:8]}...] {dinfo['title']}")

    cur.execute("SELECT id, document_id, chunk_index, chunk_text, metadata_json FROM knowledge_chunks WHERE document_id NOT LIKE 'gbpuat%' ORDER BY document_id, chunk_index")
    raw_chunks = cur.fetchall()
    print(f"\nLoaded {len(raw_chunks)} baseline chunks from SQLite.")
    conn.close()

    if len(raw_chunks) != 7:
        raise ValueError(f"Expected 7 baseline chunks, found {len(raw_chunks)}")

    # 2. Check existing ChromaDB collection
    vector_store = PersistentChromaVectorStore()
    initial_chroma_count = vector_store.count()
    print(f"\nCurrent ChromaDB Vector Count: {initial_chroma_count} (Expected: 24)")

    # 3. Prepare texts, ids, and compatible metadata
    chunk_ids = []
    chunk_texts = []
    metadatas = []

    # Domain crop & category mapping based on verified source text
    domain_mapping = {
        "3890a264-a348-463c-aa77-0ff391f6b2b0": {
            "crops": "Rajma / Kidney Beans, Pulses",
            "categories": "Plant Protection & IPM, Disease Management",
            "crop_season": "Kharif",
            "applicable_period_start": "unknown",
            "applicable_period_end": "unknown",
            "region": "Almora / Uttarakhand Mid-Hills (Munsyari belt)",
            "temporal_status": "evergreen_advisory"
        },
        "b57ff0dd-6c6d-4c15-b20c-00dd9d5eb833": {
            "crops": "Wheat / Rabi Wheat, Cereals",
            "categories": "Plant Protection & IPM, Disease Management",
            "crop_season": "Rabi",
            "applicable_period_start": "unknown",
            "applicable_period_end": "unknown",
            "region": "Almora / Uttarakhand Hill Valleys",
            "temporal_status": "seasonal_rabi"
        },
        "e199cc74-055d-4234-b1bb-10a08b878725": {
            "crops": "Mandua / Finger Millet / मंडुआ, Millets",
            "categories": "Hill Millets Agronomy, Varietal Selection & Sowing",
            "crop_season": "Kharif",
            "applicable_period_start": "06-10",
            "applicable_period_end": "06-25",
            "region": "Uttarakhand Mid-Hills",
            "temporal_status": "seasonal_kharif"
        },
        "d902c95d-0543-4264-a741-3db613f9ee26": {
            "crops": "Mandua / Finger Millet / मंडुआ, Millets",
            "categories": "Hill Millets Agronomy, Sowing Practices",
            "crop_season": "Kharif",
            "applicable_period_start": "06-10",
            "applicable_period_end": "06-25",
            "region": "Uttarakhand Mid-Hills",
            "temporal_status": "evergreen_guidance"
        },
        "b66744c6-4cb5-48c3-86f2-cbb562b6d12d": {
            "crops": "Jhangora / Barnyard Millet / झंगोरा, Bhatt / Black Soybean / भट्ट, Millets",
            "categories": "Hill Millets Agronomy, Intercropping",
            "crop_season": "Kharif",
            "applicable_period_start": "unknown",
            "applicable_period_end": "unknown",
            "region": "Uttarakhand Mid-Hills",
            "temporal_status": "evergreen_guidance"
        },
        "66fd7bd8-13b8-4e7c-9bbd-5379453016c7": {
            "crops": "Basmati Rice / Paddy / धान, Cereals",
            "categories": "Cereal Crop Management, Agronomy & Nutrition",
            "crop_season": "Kharif",
            "applicable_period_start": "unknown",
            "applicable_period_end": "unknown",
            "region": "Tarai-Bhabhar Region (Udham Singh Nagar, Nainital plains)",
            "temporal_status": "evergreen_guidance"
        },
        "91209cca-e198-407f-82aa-4b916388e77f": {
            "crops": "Basmati Rice / Paddy / धान, Cereals",
            "categories": "Cereal Crop Management, Water Management",
            "crop_season": "Kharif",
            "applicable_period_start": "unknown",
            "applicable_period_end": "unknown",
            "region": "Tarai-Bhabhar Region",
            "temporal_status": "evergreen_guidance"
        }
    }

    for cid, did, cidx, ctext, cmeta in raw_chunks:
        doc_info = base_docs.get(did, {})
        mapping = domain_mapping.get(cid, {})

        chunk_ids.append(cid)
        chunk_texts.append(ctext)

        # Build schema compliant with HybridAgriculturalRetriever
        meta_dict = {
            "document_id": str(did),
            "document_title": str(doc_info.get("title", "Baseline Package of Practices")),
            "publisher": str(doc_info.get("publisher", "ICAR-VPKAS / GBPUAT / KVK Matela")),
            "publication_date": str(doc_info.get("pub_date", "2025-2026")),
            "page_start": 1,
            "page_end": 1,
            "source_url": "",
            "is_historical": False,
            "crops": str(mapping.get("crops", "")),
            "categories": str(mapping.get("categories", "")),
            "crop_season": str(mapping.get("crop_season", "unknown")),
            "applicable_period_start": str(mapping.get("applicable_period_start", "unknown")),
            "applicable_period_end": str(mapping.get("applicable_period_end", "unknown")),
            "region": str(mapping.get("region", "Uttarakhand")),
            "temporal_status": str(mapping.get("temporal_status", "evergreen_guidance")),
            "token_estimate": len(ctext.split())
        }
        metadatas.append(meta_dict)

    # 4. Generate Embeddings using existing multilingual model
    embedding_provider = get_embedding_provider()
    print(f"\nActive Embedding Provider: {embedding_provider.model_name} (dim={embedding_provider.dimension})")
    print(f"Generating embeddings for {len(chunk_texts)} chunks...")
    embeddings = embedding_provider.encode_documents(chunk_texts)
    print(f"✓ Embeddings generated with shape: {embeddings.shape}")

    # 5. Idempotent Upsert into ChromaDB
    print("\nUpserting 7 baseline vectors into ChromaDB 'kisanmitra_kb'...")
    vector_store.add_chunks(
        chunk_ids=chunk_ids,
        embeddings=embeddings,
        texts=chunk_texts,
        metadatas=metadatas
    )

    final_chroma_count = vector_store.count()
    print(f"✓ Upsert successful! Final ChromaDB Vector Count: {final_chroma_count} (Expected: 31)")

    # 6. Parity Verification
    print("\n" + "=" * 70)
    print("PARITY VERIFICATION: SQLITE (31) <-> CHROMADB (31)")
    print("=" * 70)

    chroma_data = vector_store.collection.get()
    all_chroma_ids = set(chroma_data["ids"])

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM knowledge_chunks")
    all_sql_ids = {r[0] for r in cur.fetchall()}
    conn.close()

    missing_in_chroma = all_sql_ids - all_chroma_ids
    missing_in_sql = all_chroma_ids - all_sql_ids

    print(f"Total SQL Chunks:                 {len(all_sql_ids)}")
    print(f"Total ChromaDB Vectors:           {len(all_chroma_ids)}")
    print(f"Missing in ChromaDB:              {len(missing_in_chroma)}")
    print(f"Missing in SQLite:                {len(missing_in_sql)}")

    if len(all_sql_ids) == 31 and len(all_chroma_ids) == 31 and not missing_in_chroma and not missing_in_sql:
        print("\n>>> STATUS: PERFECT 100% PARITY (31 / 31) ACHIEVED! <<<")
    else:
        print("\n>>> WARNING: Parity discrepancy detected! <<<")


if __name__ == "__main__":
    vectorize_baseline_knowledge()
