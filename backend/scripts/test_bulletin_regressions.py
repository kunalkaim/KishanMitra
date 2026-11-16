import urllib.request
import json

base_url = "http://127.0.0.1:8000"

bulletin_tests = [
    {
        "name": "Regression 1: 2020 Kharif Advisory",
        "message": "उत्तराखंड खरीफ एडवाइजरी 2020 के अनुसार तराई-भाबर के लिए धान की संस्तुत प्रजातियां क्या हैं?"
    },
    {
        "name": "Regression 2: April–June 2026 Bulletin",
        "message": "पंत प्रसार संदेश (अप्रैल–जून 2026) के अनुसार खेत बचाओ अभियान की थीम और उद्देश्य क्या है?"
    },
    {
        "name": "Regression 3: July–September 2026 Bulletin",
        "message": "पंत प्रसार संदेश (जुलाई–सितंबर 2026) के अनुसार आगामी त्रैमास (अक्टूबर-दिसंबर) के मुख्य कृषि कार्य क्या हैं?"
    }
]

for t in bulletin_tests:
    print("\n" + "=" * 70)
    print(f"Testing Bulletin Regression: {t['name']}")
    print("=" * 70)
    payload = json.dumps({"message": t["message"], "language": "hi"}).encode("utf-8")
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
        print(f"\nResponse Content Preview:\n{data.get('content')[:280]}...\n")
