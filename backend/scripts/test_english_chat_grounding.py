import urllib.request
import json
import time

base_url = "http://127.0.0.1:8000"

english_chat_tests = [
    {
        "name": "Baseline 1 (English): Hill Millets (ICAR-VPKAS)",
        "message": "What are the recommended sowing practices, seed rate, and blast-resistant varieties for Mandua according to ICAR-VPKAS?"
    },
    {
        "name": "Baseline 2 (English): Basmati Rice (GBPUAT)",
        "message": "What are the transplanting spacing and zinc deficiency (Khaira disease) management recommendations for Basmati rice in the Tarai-Bhabhar region according to GBPUAT?"
    },
    {
        "name": "Baseline 3 (English): Himalayan Pulses IPM (KVK Matela)",
        "message": "What seed treatment and agronomic practices are recommended for Munsyari Rajma to manage anthracnose and root rot according to KVK Matela?"
    }
]

for t in english_chat_tests:
    print("\n" + "=" * 70)
    print(f"Testing Chat: {t['name']}")
    print("=" * 70)
    payload = json.dumps({"message": t["message"], "language": "en"}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/api/v1/assistant/chat",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"Answer Mode: {data.get('answer_mode')}")
        print(f"Provider: {data.get('provider_name')}")
        sources = data.get("retrieved_sources", [])
        print(f"Retrieved Sources ({len(sources)}):")
        for s in sources:
            print(f"  [{s.get('source_id')}] {s.get('document_title')} - Page {s.get('page_start')} ({s.get('publisher')}) [Relevance: {s.get('relevance_score')}]")
        print(f"\nResponse Content:\n{data.get('content')}\n")
    time.sleep(1)
