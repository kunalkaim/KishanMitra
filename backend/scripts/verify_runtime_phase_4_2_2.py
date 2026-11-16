import urllib.request
import json
import os

print("==================================================================")
print("PHASE 4.2.2 RUNTIME VERIFICATION SCRIPT")
print("==================================================================")

base_url = "http://127.0.0.1:8000"

# 1. Health check
print("\n[1. API Health Check]")
try:
    with urllib.request.urlopen(f"{base_url}/health") as resp:
        print(f"GET /health: {resp.status}")
        data = json.loads(resp.read().decode())
        print(f"Response: {data}")
except Exception as e:
    print(f"Error: {e}")

# 2. Assistant Health Check
print("\n[2. Assistant Health Check]")
try:
    with urllib.request.urlopen(f"{base_url}/api/v1/assistant/health") as resp:
        print(f"GET /api/v1/assistant/health: {resp.status}")
        data = json.loads(resp.read().decode())
        print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# 3. Knowledge Stats Check
print("\n[3. Knowledge Statistics Check]")
try:
    with urllib.request.urlopen(f"{base_url}/api/v1/assistant/knowledge-stats") as resp:
        print(f"GET /api/v1/assistant/knowledge-stats: {resp.status}")
        stats = json.loads(resp.read().decode())
        print(f"Statistics:\n{json.dumps(stats, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# 4. Document Listing
print("\n[4. Document Listing Check]")
try:
    with urllib.request.urlopen(f"{base_url}/api/v1/documents/") as resp:
        print(f"GET /api/v1/documents/: {resp.status}")
        docs = json.loads(resp.read().decode())
        print(f"Total Documents returned: {len(docs)}")
        for d in docs:
            print(f"  - [{d.get('id')[:8]}...] {d.get('title')} ({d.get('source_organization')})")
except Exception as e:
    print(f"Error: {e}")

# 5. Hybrid Retrieval (Hindi Query)
print("\n[5. Hybrid Retrieval: Hindi Query]")
hindi_payload = json.dumps({"query": "खेत बचाओ अभियान क्या है?", "top_k": 3}).encode("utf-8")
req = urllib.request.Request(
    f"{base_url}/api/v1/assistant/retrieve",
    data=hindi_payload,
    headers={"Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(req) as resp:
        print(f"POST /api/v1/assistant/retrieve (Hindi): {resp.status}")
        res = json.loads(resp.read().decode())
        print(f"Retrieved {len(res.get('results', []))} results:")
        for r in res.get("results", []):
            cit = r.get("citation", {})
            print(f"  - Chunk: {r.get('chunk_id')}")
            print(f"    Title: {cit.get('document_title')} | Page: {cit.get('page_start')} | Score: {r.get('hybrid_score')}")
except Exception as e:
    print(f"Error: {e}")

# 6. Hybrid Retrieval (English Query)
print("\n[6. Hybrid Retrieval: English Query]")
eng_payload = json.dumps({"query": "What are the recommended sowing practices for basmati rice?", "top_k": 3}).encode("utf-8")
req = urllib.request.Request(
    f"{base_url}/api/v1/assistant/retrieve",
    data=eng_payload,
    headers={"Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(req) as resp:
        print(f"POST /api/v1/assistant/retrieve (English): {resp.status}")
        res = json.loads(resp.read().decode())
        print(f"Retrieved {len(res.get('results', []))} results:")
        for r in res.get("results", []):
            cit = r.get("citation", {})
            print(f"  - Chunk: {r.get('chunk_id')}")
            print(f"    Title: {cit.get('document_title')} | Page: {cit.get('page_start')} | Score: {r.get('hybrid_score')}")
except Exception as e:
    print(f"Error: {e}")

# 7. Grounded Assistant Chat (with Gemini provider & 2026 citation)
print("\n[7. Grounded Assistant Chat: Gemini generation & 2026 citation check]")
chat_payload = json.dumps({
    "message": "पंत प्रसार संदेश (अप्रैल–जून 2026) के अनुसार खेत बचाओ अभियान की थीम और उद्देश्य क्या है?",
    "language": "hi"
}).encode("utf-8")
req = urllib.request.Request(
    f"{base_url}/api/v1/assistant/chat",
    data=chat_payload,
    headers={"Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(req) as resp:
        print(f"POST /api/v1/assistant/chat: {resp.status}")
        chat_res = json.loads(resp.read().decode())
        print(f"Response Mode: {chat_res.get('mode')}")
        print(f"LLM Provider: {chat_res.get('model')}")
        print(f"Sources Count: {len(chat_res.get('sources', []))}")
        for s in chat_res.get("sources", []):
            print(f"  Citation Source: {s.get('document_title')} (Page {s.get('page_start')}, Pub Date: {s.get('publication_date')})")
        print("\nAnswer Content Preview:")
        print(chat_res.get("content")[:350] + "...")
except Exception as e:
    print(f"Error: {e}")
