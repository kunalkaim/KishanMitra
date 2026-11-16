import urllib.request
import json
import time

print("==================================================================")
print("PHASE 4.2.3: COMPREHENSIVE RETRIEVAL & GROUNDING TEST SUITE")
print("==================================================================")

base_url = "http://127.0.0.1:8000"

# 1. Verify updated knowledge statistics
print("\n[STEP 1: KNOWLEDGE STATS CHECK]")
with urllib.request.urlopen(f"{base_url}/api/v1/assistant/knowledge-stats") as resp:
    stats = json.loads(resp.read().decode())
    print(f"Total Documents: {stats.get('total_documents')}")
    print(f"Active ChromaDB Vectors: {stats.get('active_vector_embeddings')}")
    print(f"Total Knowledge Chunks: {stats.get('total_knowledge_chunks')}")
    print(f"Relational Chunk Records: {stats.get('relational_chunk_records')}")

# 2. Test Retrieval for the 3 Baseline Documents
test_queries = [
    # 1. Mandua & Jhangora (ICAR-VPKAS)
    {
        "category": "Baseline: Hill Millets (ICAR-VPKAS)",
        "hindi": "मंडुआ और झंगोरा की उन्नत खेती कैसे करें?",
        "english": "What are the recommended cultivation practices for Mandua and Jhangora?",
        "expected_doc_substring": "Hill Millets"
    },
    # 2. Basmati Rice (GBPUAT)
    {
        "category": "Baseline: Basmati Rice (GBPUAT)",
        "hindi": "बासमती धान की रोपाई और जल प्रबंधन का सही तरीका क्या है?",
        "english": "What are the agronomic practices for Basmati rice in the Tarai-Bhabhar region?",
        "expected_doc_substring": "Basmati Rice"
    },
    # 3. Himalayan Vegetables IPM (KVK Matela)
    {
        "category": "Baseline: IPM in Vegetables & Pulses (KVK Matela)",
        "hindi": "पहाड़ी राजमा और फसलों में कीट एवं रोग प्रबंधन कैसे करें?",
        "english": "What integrated pest management practices are recommended for Himalayan vegetables and pulses?",
        "expected_doc_substring": "Pest & Disease Management"
    },
    # 4. Regression: 2020 Kharif Advisory
    {
        "category": "Regression: 2020 Kharif Advisory",
        "hindi": "खरीफ मौसम में मक्का और धान की बुवाई हेतु क्या सलाह दी गई है?",
        "english": "What were the Kharif 2020 advisory recommendations for crop sowing?",
        "expected_doc_substring": "Uttarakhand Kharif Season Agricultural Advisory 2020"
    },
    # 5. Regression: 2026 Bulletin (April-June)
    {
        "category": "Regression: Pant Prasar Sandesh (April–June 2026)",
        "hindi": "खेत बचाओ अभियान का उद्देश्य और थीम क्या है?",
        "english": "What is the theme and objective of Khet Bachao Abhiyan in Pant Prasar Sandesh 2026?",
        "expected_doc_substring": "Pant Prasar Sandesh (April–June 2026)"
    },
    # 6. Regression: 2026 Bulletin (July-September)
    {
        "category": "Regression: Pant Prasar Sandesh (July–September 2026)",
        "hindi": "पंत प्रसार संदेश जुलाई सितंबर 2026 में क्या मुख्य निर्देश दिए गए हैं?",
        "english": "What are the key instructions in Pant Prasar Sandesh July September 2026?",
        "expected_doc_substring": "Pant Prasar Sandesh (July–September 2026)"
    }
]

print("\n" + "=" * 70)
print("STEP 2: RUNNING HYBRID RETRIEVAL ON ALL TARGETS")
print("=" * 70)

for t in test_queries:
    print(f"\nTarget: {t['category']}")
    for lang, q in [("Hindi", t["hindi"]), ("English", t["english"])]:
        payload = json.dumps({"query": q, "top_k": 2}).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/api/v1/assistant/retrieve",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            results = data.get("results", [])
            print(f"  [{lang} Query]: '{q}'")
            if results:
                top = results[0]
                cit = top.get("citation", {})
                print(f"    Top Retrieved: {cit.get('document_title')}")
                print(f"    Chunk ID: {top.get('chunk_id')} | Score: {top.get('hybrid_score')}")
                print(f"    Snippet: {top.get('text')[:100]}...")
            else:
                print("    No results retrieved!")

# 3. Test Grounded Chat Generation with Gemini for the 3 Baseline Documents
print("\n" + "=" * 70)
print("STEP 3: RUNNING GROUNDED GEMINI CHAT ON THE 3 BASELINE DOCUMENTS")
print("=" * 70)

chat_queries = [
    {
        "label": "Baseline 1: Hill Millets Agronomy",
        "message": "आईसीएआर-वीपीकेएएस (ICAR-VPKAS) के अनुसार मंडुआ (Finger millet) की बुवाई का सही समय और उन्नत किस्में कौन सी हैं?",
        "expected_mention": "VL Mandua"
    },
    {
        "label": "Baseline 2: Basmati Rice Agronomy",
        "message": "तराई-भाबर क्षेत्र में बासमती धान की रोपाई के लिए पौध की उम्र, दूरी और खैरा रोग प्रबंधन की क्या विधि है?",
        "expected_mention": "Zinc"
    },
    {
        "label": "Baseline 3: Himalayan Pulses IPM",
        "message": "कृषि विज्ञान केंद्र मटेला के अनुसार मुनस्यारी राजमा में एन्थ्रेक्नोज और जड़ सड़न से बचाव के लिए बीज शोधन कैसे करें?",
        "expected_mention": "Trichoderma"
    }
]

for cq in chat_queries:
    print(f"\n--- Testing Chat: {cq['label']} ---")
    payload = json.dumps({"message": cq["message"], "language": "hi"}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/api/v1/assistant/chat",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print(f"Answer Mode: {res.get('answer_mode')}")
        print(f"Provider: {res.get('provider_name')}")
        sources = res.get("retrieved_sources", [])
        print(f"Sources ({len(sources)}):")
        for s in sources:
            print(f"  [{s.get('source_id')}] {s.get('document_title')} - {s.get('publisher')}")
        print(f"Content Preview:\n{res.get('content')[:250]}...\n")
    time.sleep(1)
