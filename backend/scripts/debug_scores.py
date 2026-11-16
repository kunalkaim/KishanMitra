import os, sys
sys.path.insert(0, os.path.abspath("backend"))
from app.rag.retrieval.hybrid_retriever import HybridAgriculturalRetriever

retriever = HybridAgriculturalRetriever()
print("Total vectors in retriever:", retriever.vector_store.count())

queries = [
    "मंडुआ और झंगोरा की उन्नत खेती कैसे करें?",
    "What are the recommended cultivation practices for Mandua and Jhangora?",
    "Munsyari Rajma anthracnose seed treatment Trichoderma",
    "Basmati rice transplanting zinc deficiency Khaira",
    "Yellow rust in rabi wheat cow urine",
    "Finger millet line sowing spacing Mandua"
]

for q in queries:
    print("\n" + "=" * 60)
    print("Query:", q)
    results = retriever.retrieve(q, top_k=5)
    for r in results:
        cit = r.get("citation", {})
        cid = r["chunk_id"]
        score = r["hybrid_score"]
        dense = r["dense_score"]
        keyw = r["keyword_score"]
        boost = r["domain_boost"]
        title = cit.get("document_title")
        print(f"  ID: {cid} | Score: {score} (Dense: {dense:.3f}, Key: {keyw:.3f}, Boost: {boost}) | Title: {title}")
