import os
import sys
import json
import sqlite3
import chromadb

print("==================================================================")
print("KISANMITRA: PHASE 4.2.1 READ-ONLY POST-INGESTION INTEGRITY AUDIT")
print("==================================================================")

# 1. Inspect ChromaDB Collection
chroma_path = os.path.abspath("backend/app/storage/vector_index")
print(f"\n[SECTION 1: CHROMADB PERSISTENT STORE AUDIT]")
print(f"ChromaDB Path: {chroma_path} (Exists: {os.path.exists(chroma_path)})")

client = chromadb.PersistentClient(path=chroma_path)
collections = client.list_collections()
print(f"Collections Found: {[c.name for c in collections]}")

col = client.get_collection("kisanmitra_kb")
total_vectors = col.count()
print(f"Total Vectors in 'kisanmitra_kb': {total_vectors}")

data = col.get()
ids = data["ids"]
docs = data["documents"]
metas = data["metadatas"]

doc_dist = {}
for cid, doc_text, meta in zip(ids, docs, metas):
    did = meta.get("document_id")
    doc_dist[did] = doc_dist.get(did, 0) + 1

print("\nChromaDB Distribution by Document:")
for did, cnt in sorted(doc_dist.items()):
    print(f"  - {did}: {cnt} vectors")

print("\n--- Detailed Audit of All 24 Vectors ---")
for i, (cid, doc_text, meta) in enumerate(zip(ids, docs, metas), 1):
    did = meta.get("document_id")
    page = meta.get("page_start")
    pub_date = meta.get("publication_date")
    is_hist = meta.get("is_historical")
    title = meta.get("document_title")
    text_len = len(doc_text)
    print(f"{i:02d}. ID: {cid}")
    print(f"    Title: {title} (Page {page})")
    print(f"    Pub Date: {pub_date} | Historical: {is_hist} | Text Len: {text_len} chars")

# 2. Inspect Both Relational Databases
print(f"\n[SECTION 2: RELATIONAL DATABASE RECONCILIATION]")

db_paths = [
    ("Root Local Database", "kisanmitra.db"),
    ("Backend Working Dir Database", "backend/kisanmitra.db")
]

for label, p in db_paths:
    print(f"\n--- {label}: {p} ---")
    if os.path.exists(p):
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        
        cur.execute("SELECT count(*) FROM knowledge_documents")
        k_docs_count = cur.fetchone()[0]
        print(f"  knowledge_documents: {k_docs_count} rows")
        cur.execute("SELECT id, title, source_organization, publication_date FROM knowledge_documents")
        for r in cur.fetchall():
            print(f"    - ID: {r[0][:16]}... | Title: {r[1]} | Pub: {r[2]} | Date: {r[3]}")
        
        cur.execute("SELECT count(*) FROM knowledge_chunks")
        k_chunks_count = cur.fetchone()[0]
        print(f"  knowledge_chunks: {k_chunks_count} rows")
        cur.execute("SELECT document_id, count(*), min(chunk_index), max(chunk_index) FROM knowledge_chunks GROUP BY document_id")
        for r in cur.fetchall():
            print(f"    - Doc ID: {r[0][:24]}... | Chunks: {r[1]} | Indices: [{r[2]}..{r[3]}]")
            
        conn.close()
    else:
        print(f"  File not found at {p}")

# 3. Source Document Physical Audit
print(f"\n[SECTION 3: SOURCE PDF & EXTRACTED TEXT AUDIT]")
raw_dir = "datasets/agricultural_knowledge/raw/gbpuat"
extracted_dir = "datasets/agricultural_knowledge/processed/extracted_text"
chunk_dir = "datasets/agricultural_knowledge/processed/chunks"

raw_files = os.listdir(raw_dir) if os.path.exists(raw_dir) else []
print(f"Raw Staged PDFs ({len(raw_files)}): {raw_files}")

ext_files = os.listdir(extracted_dir) if os.path.exists(extracted_dir) else []
print(f"Extracted JSONs ({len(ext_files)}): {ext_files}")

chunk_files = os.listdir(chunk_dir) if os.path.exists(chunk_dir) else []
print(f"Chunk JSONs ({len(chunk_files)}): {chunk_files}")

for cf in chunk_files:
    if cf.endswith(".json"):
        with open(os.path.join(chunk_dir, cf), "r", encoding="utf-8") as f:
            cdata = json.load(f)
            chunks_list = cdata.get("chunks", [])
            print(f"  - {cf}: {len(chunks_list)} chunks in file")
