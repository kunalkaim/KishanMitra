import sys
import os
import json
from unittest.mock import MagicMock, patch

# Ensure backend path is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from app.main import app
from app.rag.generation.gemini_provider import (
    GeminiProvider,
    GeminiAgriculturalResponse,
    GeminiAuthError,
    GeminiQuotaError,
    GeminiTransientError
)
from app.rag.generation.llm_provider import GeminiLLMProvider, RetrievalOnlyLLMProvider
from app.rag.generation.answer_generator import AgriculturalAnswerGenerator


def run_comprehensive_tests():
    report = {
        "gemini_provider_unit_tests": {},
        "rag_retrieval_and_citations": {},
        "multilingual_tests": {},
        "fastapi_endpoints": {}
    }

    print("==================================================================")
    print("KISANMITRA PHASE 4.1: GEMINI LLM RAG INTEGRATION TEST SUITE")
    print("==================================================================")

    # -------------------------------------------------------------
    # TEST 1: Gemini Provider Unit & Mock Tests
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing Gemini Provider Structure & Parser...")
    provider = GeminiProvider(api_key="test_dummy_key", model_name="gemini-3.8-flash")
    assert provider.is_configured is True
    assert "gemini-3.8-flash" in provider.provider_name

    # Test JSON parser with clean JSON
    sample_json = json.dumps({
        "answer": "उत्तराखंड में धान की सीधी बुवाई मई के अंतिम सप्ताह से जून के मध्य तक करनी चाहिए [S1]।",
        "language": "hi",
        "citation_ids": ["S1"],
        "evidence_sufficiency": "sufficient",
        "follow_up_questions": ["बीज दर कितनी होनी चाहिए?"]
    })
    parsed = provider._parse_structured_response(sample_json)
    assert parsed["language"] == "hi"
    assert parsed["citation_ids"] == ["S1"]
    assert "धान की सीधी बुवाई" in parsed["answer"]
    report["gemini_provider_unit_tests"]["json_parsing"] = "PASSED"
    print("  ✓ Structured JSON response parsing validated.")

    # Test parser resilient fallback on unformatted text with [S1] tags
    unformatted = "Based on research, apply 10,000 kg cow dung per hectare to fish pond [S3]."
    parsed_fallback = provider._parse_structured_response(unformatted)
    assert parsed_fallback["citation_ids"] == ["S3"]
    assert "cow dung" in parsed_fallback["answer"]
    report["gemini_provider_unit_tests"]["fallback_parser"] = "PASSED"
    print("  ✓ Resilient fallback text parser validated.")

    # Test error sanitization (ensure key is NEVER printed)
    secret_key = "SECRET_KEY_12345"
    p_secret = GeminiProvider(api_key=secret_key)
    sanitized = p_secret._sanitize_error(f"Error connecting with {secret_key}")
    assert secret_key not in sanitized
    assert "[REDACTED_API_KEY]" in sanitized
    report["gemini_provider_unit_tests"]["key_sanitization"] = "PASSED"
    print("  ✓ Credential leakage prevention sanitized.")

    # -------------------------------------------------------------
    # TEST 2: Answer Generator & Citation Verification
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing Citation Verification and Evidence Mapping...")
    gen = AgriculturalAnswerGenerator()

    # Mock provider that returns specific citation tags
    mock_llm = MagicMock()
    mock_llm.provider_name = "Google Gemini (gemini-3.8-flash)"
    mock_llm.generate.return_value = {
        "answer": "For rice in Uttarakhand, recommended varieties include Govind and Pant Dhan 4 [S1]. Seed rate for direct sowing is 60-75 kg/ha [S1].",
        "language": "en",
        "citation_ids": ["S1", "S99"],  # S99 is non-existent hallucinated citation
        "evidence_sufficiency": "sufficient",
        "follow_up_questions": ["What is the recommended fertilizer schedule?"]
    }

    gen_mock = AgriculturalAnswerGenerator(llm_provider=mock_llm)
    res = gen_mock.generate_answer(
        query="What are the recommended varieties and seed rates for rice in Uttarakhand?",
        farmer_context={"district": "Haridwar", "crop": "rice"}
    )

    assert res["answer_mode"] == "rag"
    assert len(res["sources"]) >= 1
    # Check that S99 was REJECTED by backend citation authority
    cited_ids = [s.get("source_id") for s in res["sources"]]
    assert "S99" not in cited_ids
    assert "S1" in cited_ids
    assert "Uttarakhand Kharif" in res["sources"][0]["document_title"]
    assert res["sources"][0]["page_start"] == 1
    report["rag_retrieval_and_citations"]["hallucination_rejection"] = "PASSED"
    print("  ✓ Hallucinated citation [S99] successfully rejected; [S1] verified against Page 1.")

    # -------------------------------------------------------------
    # TEST 3: Multilingual & Guardrail Checks
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing Multilingual & Guardrails...")
    # Hindi Millets
    hindi_res = gen.generate_answer(
        query="मंडुआ और झंगोरा की उन्नत किस्में क्या हैं?",
        farmer_context={"district": "Almora"}
    )
    assert len(hindi_res["sources"]) > 0
    assert any("Pant Prasar Sandesh" in s["document_title"] or "Kharif" in s["document_title"] for s in hindi_res["sources"])
    assert hindi_res["sources"][0]["page_start"] in [1, 3, 6]
    report["multilingual_tests"]["hindi_retrieval"] = "PASSED"
    print("  ✓ Hindi query successfully retrieved GBPUAT Mandua/Jhangora passage.")

    # Live Weather Guardrail
    weather_res = gen.generate_answer(query="What is the live weather in Dehradun today?")
    assert weather_res["answer_mode"] == "live_data_disclaimer"
    report["multilingual_tests"]["weather_guardrail"] = "PASSED"
    print("  ✓ Real-time weather deflection guardrail operational.")

    # Out-of-Corpus Guardrail
    coffee_res = gen.generate_answer(query="Best coffee plantations in Kerala?")
    assert coffee_res["answer_mode"] == "insufficient_evidence"
    report["multilingual_tests"]["out_of_corpus_guardrail"] = "PASSED"
    print("  ✓ Out-of-scope query rejection verified.")

    # -------------------------------------------------------------
    # TEST 4: FastAPI Full-Stack Endpoints via TestClient
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing FastAPI Endpoints...")
    client = TestClient(app)

    # 1. Health
    h_resp = client.get("/api/v1/assistant/health")
    assert h_resp.status_code == 200
    h_data = h_resp.json()
    assert h_data["status"] == "healthy"
    assert "Google Gemini" in h_data["llm_provider"]
    assert h_data["llm_configured"] is True
    report["fastapi_endpoints"]["health"] = h_data
    print(f"  ✓ GET /assistant/health: 200 (LLM: {h_data['llm_provider']}, ChromaDB vectors: {h_data['vector_count']})")

    # 2. Knowledge Stats
    stats_resp = client.get("/api/v1/assistant/knowledge-stats")
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert stats_data["total_documents"] >= 3
    assert stats_data["embedding_dimension"] == 384
    assert stats_data["total_catalogued_documents"] >= 3
    assert stats_data["physically_staged_documents"] == 3
    assert stats_data["documents_successfully_extracted"] == 3
    assert stats_data["extracted_pages"] == 19
    assert stats_data["generated_chunks"] == 24
    assert stats_data["active_vector_embeddings"] == 24
    assert stats_data["documents_pending_ocr"] == 0
    report["fastapi_endpoints"]["stats"] = stats_data
    print(f"  ✓ GET /assistant/knowledge-stats: 200 (Active Vectors: {stats_data['active_vector_embeddings']}, Relational Chunks: {stats_data['relational_chunk_records']}, Pending OCR: {stats_data['documents_pending_ocr']})")

    # 3. Documents
    docs_resp = client.get("/api/v1/documents/")
    assert docs_resp.status_code == 200
    docs_data = docs_resp.json()
    assert len(docs_data) >= 3
    report["fastapi_endpoints"]["documents_count"] = len(docs_data)
    print(f"  ✓ GET /documents/: 200 ({len(docs_data)} documents cataloged)")

    # 4. Direct Retrieve
    ret_resp = client.post("/api/v1/assistant/retrieve", json={
        "query": "What are the recommended varieties and seed rates for rice in Uttarakhand?",
        "top_k": 3,
        "crop_filter": "rice"
    })
    assert ret_resp.status_code == 200
    ret_data = ret_resp.json()
    assert ret_data["chunks_count"] >= 1
    report["fastapi_endpoints"]["retrieve"] = {
        "chunks_count": ret_data["chunks_count"],
        "top_score": ret_data["results"][0].get("hybrid_score")
    }
    print(f"  ✓ POST /assistant/retrieve: 200 (Top Score: {ret_data['results'][0].get('hybrid_score')})")

    # 5. Full Chat with Gemini Pipeline & DB Persistence
    chat_resp = client.post("/api/v1/assistant/chat", json={
        "message": "When is the optimal sowing window for Rice in Uttarakhand and what seed rates are advised?",
        "district_context": "Haridwar",
        "crop_context": "rice"
    })
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert chat_data["sender_role"] == "assistant"
    assert len(chat_data["retrieved_sources"]) >= 1
    assert chat_data["retrieved_sources"][0]["page_start"] == 1
    conv_id = chat_data["id"]
    report["fastapi_endpoints"]["chat"] = {
        "id": conv_id,
        "answer_mode": chat_data["answer_mode"],
        "generation_status": chat_data["generation_status"],
        "sources_count": len(chat_data["retrieved_sources"]),
        "first_source_page": chat_data["retrieved_sources"][0]["page_start"],
        "has_historical_warning": chat_data.get("has_historical_warning")
    }
    print(f"  ✓ POST /assistant/chat: 200 (Mode: {chat_data['answer_mode']}, Sources: {len(chat_data['retrieved_sources'])}, Page: {chat_data['retrieved_sources'][0]['page_start']})")

    # 6. Conversation Listing (Persistence Verification)
    conv_resp = client.get("/api/v1/assistant/conversations")
    assert conv_resp.status_code == 200
    convs = conv_resp.json()
    assert len(convs) >= 1
    report["fastapi_endpoints"]["conversations_persisted"] = len(convs)
    print(f"  ✓ GET /assistant/conversations: 200 ({len(convs)} persisted conversations in database)")

    # Save integration test report
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "datasets", "agricultural_knowledge", "reports")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "gemini_rag_integration_report.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n==================================================================")
    print("PHASE 4.1 INTEGRATION TEST SUITE: ALL TESTS PASSED (100%)")
    print(f"Saved audit report to {out_file}")
    print("==================================================================")


if __name__ == "__main__":
    run_comprehensive_tests()
