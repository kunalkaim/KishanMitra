import urllib.request
import json
import time

base_url = "http://127.0.0.1:8000"

tests = [
    {
        "name": "Baseline 1: Hill Millets (ICAR-VPKAS)",
        "message": "आईसीएआर-वीपीकेएएस के अनुसार उत्तराखंड में मंडुआ (Finger millet) की बुवाई का उपयुक्त समय और अनुशंसित किस्में (जैसे VL Mandua 352) कौन सी हैं?"
    },
    {
        "name": "Baseline 2: Basmati Rice (GBPUAT)",
        "message": "जीबीपीयूएटी (GBPUAT) के अनुसार तराई-भाबर में बासमती धान की रोपाई में खैरा रोग (Zinc deficiency) की रोकथाम के लिए जिंक सल्फेट के छिड़काव की क्या संस्तुति है?"
    },
    {
        "name": "Baseline 3: Himalayan Pulses IPM (KVK Matela)",
        "message": "केवीके मटेला के अनुसार मुनस्यारी राजमा में एन्थ्रेक्नोज और जड़ सड़न से बचाव के लिए ट्राइकोडर्मा (Trichoderma harzianum) से बीज शोधन की क्या विधि है?"
    }
]

for t in tests:
    print("\n" + "=" * 70)
    print(f"Testing Chat: {t['name']}")
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
            print(f"  [{s.get('source_id')}] {s.get('document_title')} - Page {s.get('page_start')} ({s.get('publisher')})")
        print(f"\nResponse Content:\n{data.get('content')}\n")
    time.sleep(1)
