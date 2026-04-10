import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Find all types to understand structure
types = set()
with open("C:/Users/32247/Desktop/olivia_session.jsonl", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line.strip())
        t = obj.get("type","")
        ct = obj.get("customType","")
        types.add(f"{t}:{ct}" if ct else t)
        # Look for usage/cost data anywhere
        if "usage" in str(obj)[:50] or "cost" in str(obj)[:50] or "token" in str(obj)[:50]:
            print(json.dumps(obj, ensure_ascii=False)[:300])

print(f"\nAll types: {types}")
