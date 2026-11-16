import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    client = TestClient(app)
    results = {}

    print("=== Testing FastAPI RAG Endpoints ===")

    # 1. /assistant/health
    resp = client.get("/api/v1/assistant/health")
    print(f"GET /assistant/health: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    results["health"] = resp.json()

    # 2. /assistant/knowledge-stats
    resp = client.get("/api/v1/assistant/knowledge-stats")
    print(f"GET /assistant/knowledge-stats: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    results["knowledge_stats"] = resp.json()
    print(f"Stats: {results['knowledge_stats']}")

    # 3. /documents/
    resp = client.get("/api/v1/documents/")
    print(f"GET /documents/: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    docs = resp.json()
    results["documents_count"] = len(docs)
    print(f"Found {len(docs)} documents in catalog.")

    # 4. /assistant/retrieve
    retrieve_payload = {
        "query": "What are the recommended varieties and seed rates for rice in Uttarakhand?",
        "top_k": 3,
        "crop_filter": "rice"
    }
    resp = client.post("/api/v1/assistant/retrieve", json=retrieve_payload)
    print(f"POST /assistant/retrieve: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    ret_data = resp.json()
    results["retrieve"] = {
        "query": ret_data.get("query"),
        "chunks_count": ret_data.get("chunks_count"),
        "top_score": ret_data["results"][0].get("hybrid_score") if ret_data.get("results") else None
    }
    print(f"Retrieved {ret_data.get('chunks_count')} chunks for rice query.")

    # 5. /assistant/chat
    chat_payload = {
        "message": "When should I sow rice and how much seed do I need in Uttarakhand?",
        "district_context": "Haridwar",
        "crop_context": "rice"
    }
    resp = client.post("/api/v1/assistant/chat", json=chat_payload)
    print(f"POST /assistant/chat: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    chat_data = resp.json()
    results["chat"] = {
        "id": chat_data.get("id"),
        "sender_role": chat_data.get("sender_role"),
        "answer_mode": chat_data.get("answer_mode"),
        "retrieval_status": chat_data.get("retrieval_status"),
        "sources_count": len(chat_data.get("retrieved_sources", [])),
        "content_length": len(chat_data.get("content", ""))
    }
    print(f"Chat response mode: {chat_data.get('answer_mode')}, sources: {len(chat_data.get('retrieved_sources', []))}")
    print(f"Content preview: {chat_data.get('content', '')[:200]}...")

    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "datasets", "agricultural_knowledge", "reports", "api_integration_test.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved test results to {output_path}")

if __name__ == "__main__":
    run_tests()
