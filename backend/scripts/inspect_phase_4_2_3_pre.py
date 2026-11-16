import sqlite3
import json
import chromadb
import os

print("==================================================================")
print("PHASE 4.2.3: PRE-IMPLEMENTATION INSPECTION")
print("==================================================================")

db_path = "kisanmitra.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("\n--- 3 Baseline Documents in SQLite ---")
cur.execute("SELECT id, title, source_organization, category, publication_date, document_type, file_path, is_verified FROM knowledge_documents WHERE id NOT LIKE 'gbpuat%'")
docs = cur.fetchall()
doc_dict = {}
for d in docs:
    doc_dict[d[0]] = {
        "id": d[0],
        "title": d[1],
        "organization": d[2],
        "category": d[3],
        "publication_date": d[4],
        "document_type": d[5],
        "file_path": d[6],
        "is_verified": d[7]
    }
    print(f"Document ID: {d[0]}")
    print(f"  Title: {d[1]}")
    print(f"  Organization: {d[2]} | Category: {d[3]}")
    print(f"  Publication Date: {d[4]} | Type: {d[5]}")

print("\n--- 7 Baseline Chunks in SQLite ---")
cur.execute("SELECT id, document_id, chunk_index, chunk_text, metadata_json FROM knowledge_chunks WHERE document_id NOT LIKE 'gbpuat%' ORDER BY document_id, chunk_index")
chunks = cur.fetchall()
for c in chunks:
    meta = json.loads(c[4]) if isinstance(c[4], str) else c[4]
    doc = doc_dict.get(c[1], {})
    print(f"\nChunk ID: {c[0]}")
    print(f"  Document ID: {c[1]} ({doc.get('title')})")
    print(f"  Chunk Index: {c[2]} | Text Length: {len(c[3])} chars")
    print(f"  Stored Metadata: {json.dumps(meta, ensure_ascii=False)}")
    print(f"  Chunk Content:\n    {c[3]}")

conn.close()

# Inspect ChromaDB
chroma_path = os.path.abspath("backend/app/storage/vector_index")
client = chromadb.PersistentClient(path=chroma_path)
col = client.get_collection("kisanmitra_kb")
total_chroma = col.count()
print(f"\n--- ChromaDB Collection Status ---")
print(f"Collection Name: 'kisanmitra_kb'")
print(f"Total Current Vectors: {total_chroma}")

# Inspect sample Chroma metadata to see exact schema expected by HybridAgriculturalRetriever
data = col.get(limit=2)
sample_meta = data["metadatas"][0] if data["metadatas"] else {}
print(f"\nSample Existing Chroma Vector Metadata Schema:")
for k, v in sample_meta.items():
    print(f"  {k} ({type(v).__name__}): {v}")
