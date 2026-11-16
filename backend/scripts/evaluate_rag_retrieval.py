import os
import json
from app.rag.generation.answer_generator import AgriculturalAnswerGenerator

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "reports")


TEST_CASES = [
    {
        "test_id": "TC-01-EN-CROP-RICE",
        "category": "English Agricultural Question (Crops)",
        "query": "What are the recommended sowing times, seed rates and varieties for rice in Uttarakhand Tarai and Bhabhar?",
        "expected_crop": "Rice / Paddy",
        "expected_page": 1,
        "is_supported": True
    },
    {
        "test_id": "TC-02-HI-CROP-MILLETS",
        "category": "Hindi Agricultural Question (Hill Millets)",
        "query": "उत्तराखंड में मंडुआ (रागी) और झंगोरा की उन्नत किस्में और बीज दर क्या हैं?",
        "expected_crop": "Mandua / Jhangora",
        "expected_page": 1,
        "is_supported": True
    },
    {
        "test_id": "TC-03-EN-VEGETABLES-TOMATO",
        "category": "Crop-Specific Horticultural Advisory (Tomato)",
        "query": "Which tomato varieties are recommended for Uttarakhand and what is their nursery sowing time?",
        "expected_crop": "Tomato",
        "expected_page": 2,
        "is_supported": True
    },
    {
        "test_id": "TC-04-EN-ALLIED-FISHERIES",
        "category": "Allied Agricultural Practices (Fisheries & Pond Management)",
        "query": "How should farmers prepare pond for fish culture using cow dung or compost?",
        "expected_crop": "Fisheries",
        "expected_page": 3,
        "is_supported": True
    },
    {
        "test_id": "TC-05-EN-REGIONAL-MAIZE",
        "category": "Regional Agro-Climatic Sowing Windows (Maize)",
        "query": "What is the recommended sowing window for maize in the hill zone vs plain zone of Uttarakhand?",
        "expected_crop": "Maize",
        "expected_page": 1,
        "is_supported": True
    },
    {
        "test_id": "TC-06-UNSUPPORTED-COFFEE",
        "category": "Questions Outside Knowledge Base (Unsupported Crop)",
        "query": "What is the ideal pruning schedule and shade canopy management for Arabica coffee plantations in Kerala?",
        "expected_crop": None,
        "expected_page": None,
        "is_supported": False
    },
    {
        "test_id": "TC-07-OUT-OF-SCOPE-LIVE-WEATHER",
        "category": "Questions Requesting Current Weather (Static Document Guardrail)",
        "query": "What is today's current live rainfall and temperature in Dehradun?",
        "expected_crop": None,
        "expected_page": None,
        "is_supported": False
    },
    {
        "test_id": "TC-08-OUT-OF-SCOPE-LIVE-MANDI",
        "category": "Questions Requesting Live Mandi Prices (Static Document Guardrail)",
        "query": "What is the live mandi price of Basmati rice in Raipur mandi today?",
        "expected_crop": None,
        "expected_page": None,
        "is_supported": False
    }
]


def run_retrieval_evaluation():
    print("=" * 70)
    print("STAGE 13 & 14: RETRIEVAL QUALITY & CITATION ACCURACY EVALUATION")
    print("=" * 70)

    generator = AgriculturalAnswerGenerator()
    results = []
    passed_count = 0

    for tc in TEST_CASES:
        t_id = tc["test_id"]
        q = tc["query"]
        cat = tc["category"]
        expected_supported = tc["is_supported"]

        print(f"\n[{t_id}] {cat}")
        print(f"Query: \"{q}\"")

        res = generator.generate_answer(q, top_k=2)
        answer = res["answer"]
        mode = res["answer_mode"]
        sources = res.get("sources", [])
        has_hist = res.get("has_historical_warning", False)

        test_passed = False
        reasons = []

        if expected_supported:
            if mode in ["rag", "retrieval_only"] and len(sources) > 0:
                top_source = sources[0]
                expected_p = tc.get("expected_page")
                page_match = (top_source["page_start"] == expected_p or top_source["page_end"] == expected_p)
                if page_match:
                    test_passed = True
                    reasons.append(f"Correct page {expected_p} retrieved.")
                else:
                    reasons.append(f"Page mismatch: retrieved {top_source['page_start']} vs expected {expected_p}")
                
                if has_hist:
                    reasons.append("Historical 2020 advisory warning correctly flagged.")
            else:
                reasons.append(f"Expected evidence retrieval, but mode was: {mode}")
        else:
            if mode in ["insufficient_evidence", "live_data_disclaimer"]:
                test_passed = True
                reasons.append(f"Honest rejection/guardrail triggered: {mode}")
            else:
                reasons.append(f"Expected rejection or disclaimer, got mode: {mode}")

        if test_passed:
            passed_count += 1
            print("  ✓ TEST PASSED:", "; ".join(reasons))
        else:
            print("  ✗ TEST FAILED:", "; ".join(reasons))

        print(f"  Answer Snippet: {answer[:160]}...")
        if sources:
            print(f"  Top Citation: {sources[0]['document_title']} (Page {sources[0]['page_start']}) [Score: {sources[0]['retrieval_score']}%]")

        results.append({
            "test_id": t_id,
            "category": cat,
            "query": q,
            "passed": test_passed,
            "answer_mode": mode,
            "reasons": reasons,
            "sources_count": len(sources),
            "top_source": sources[0] if sources else None
        })

    pass_rate = (passed_count / len(TEST_CASES)) * 100
    print("\n" + "=" * 70)
    print(f"EVALUATION SUMMARY: {passed_count}/{len(TEST_CASES)} Tests Passed ({pass_rate:.1f}%)")
    print("=" * 70)

    eval_report = {
        "evaluation_name": "KisanMitra Multilingual Agricultural RAG Evaluation",
        "total_tests": len(TEST_CASES),
        "passed_tests": passed_count,
        "pass_rate_percentage": pass_rate,
        "embedding_provider": generator.retriever.embedding_provider.model_name,
        "llm_provider": generator.llm_provider.provider_name,
        "test_results": results
    }

    report_path = os.path.join(REPORTS_DIR, "retrieval_evaluation.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(eval_report, f, indent=2, ensure_ascii=False)
    print(f"Saved evaluation report to: {report_path}")


if __name__ == "__main__":
    run_retrieval_evaluation()
