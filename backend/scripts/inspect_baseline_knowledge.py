import sqlite3
import json
import chromadb
import os

print("==================================================================")
print("SECTION 1: BASELINE KNOWLEDGE RETRIEVAL INSPECTION")
print("==================================================================")

db_path = "kisanmitra.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("\n--- Baseline Documents in SQLite ---")
cur.execute("SELECT id, title, source_organization, category, publication_date, document_type, is_verified FROM knowledge_documents WHERE id NOT LIKE 'gbpuat%'")
base_docs = cur.fetchall()
base_doc_ids = [d[0] for d in base_docs]
print(f"Total baseline documents: {len(base_docs)}")
for d in base_docs:
    print(f"Doc ID: {d[0]}")
    print(f"  Title: {d[1]}")
    print(f"  Organization: {d[2]} | Category: {d[3]} | Pub Date: {d[4]}")
    print(f"  Type: {d[5]} | Verified: {d[6]}")

print("\n--- Baseline Chunks in SQLite ---")
cur.execute("SELECT id, document_id, chunk_index, length(chunk_text), chunk_text, metadata_json FROM knowledge_chunks WHERE document_id NOT LIKE 'gbpuat%'")
chunks = cur.fetchall()
print(f"Total baseline chunks: {len(chunks)}")
for c in chunks:
    meta = json.loads(c[5]) if isinstance(c[5], str) else c[5]
    print(f"\nChunk ID: {c[0]}")
    print(f"  Document ID: {c[1]}")
    print(f"  Chunk Index: {c[2]} | Text Length: {c[3]} characters")
    print(f"  Metadata: {json.dumps(meta, ensure_ascii=False)}")
    print(f"  Full Text Preview:\n    {c[4][:140]}...")

conn.close()

# Inspect ChromaDB
chroma_path = os.path.abspath("backend/app/storage/vector_index")
client = chromadb.PersistentClient(path=chroma_path)
col = client.get_collection("kisanmitra_kb")
all_chroma_data = col.get()
chroma_ids = all_chroma_data["ids"]
chroma_metas = all_chroma_data["metadatas"]

print(f"\n--- ChromaDB Check for Baseline Knowledge ---")
print(f"Total vectors in ChromaDB: {len(chroma_ids)}")

chroma_doc_ids = set()
for m in chroma_metas:
    chroma_doc_ids.add(m.get("document_id"))

print("Document IDs present in ChromaDB:")
for cdid in chroma_doc_ids:
    print(f"  - {cdid}")

print("\nAre baseline document IDs present in ChromaDB?")
for bdid in base_doc_ids:
    present = bdid in chroma_doc_ids
    print(f"  - {bdid}: {'PRESENT' if present else 'EXCLUDED / MISSING'}")

baseline_chunk_ids = [c[0] for c in chunks]
missing_chunks = [cid for cid in baseline_chunk_ids if cid not in chroma_ids]
print(f"\nBaseline Chunk IDs present in ChromaDB: {len(baseline_chunk_ids) - len(missing_chunks)} / {len(baseline_chunk_ids)}")
