import os, sys
sys.path.insert(0, os.path.abspath("backend"))
from app.rag.retrieval.hybrid_retriever import HybridAgriculturalRetriever

retriever = HybridAgriculturalRetriever()

hindi_queries = [
    "मंडुआ (Finger millet) की बुवाई का समय और VL Mandua किस्में",
    "बासमती धान में खैरा रोग (Zinc deficiency) और पौध रोपाई की विधि",
    "मुनस्यारी राजमा में एन्थ्रेक्नोज और ट्राइकोडर्मा (Trichoderma) उपचार",
    "गेहूं में पीला रतुआ (Yellow rust) और गोमूत्र (Cow urine) छिड़काव"
]

for q in hindi_queries:
    print("\n" + "=" * 60)
    print("Query:", q)
    results = retriever.retrieve(q, top_k=3)
    for r in results:
        cit = r.get("citation", {})
        print(f"  Top: {r['chunk_id']} | Score: {r['hybrid_score']} | Title: {cit.get('document_title')}")
        print(f"    Snippet: {r['text'][:120]}...")
