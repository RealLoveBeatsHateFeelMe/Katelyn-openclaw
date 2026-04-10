import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open("C:/Users/32247/Desktop/olivia_session.jsonl", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line.strip())
        t = obj.get("type","")
        ts = obj.get("timestamp","")
        if t == "message":
            msg = obj.get("message",{})
            role = msg.get("role","")
            content = msg.get("content","")
            if role == "user":
                if isinstance(content, list):
                    text = " ".join([c.get("text","")[:300] for c in content if c.get("type")=="text"])
                else:
                    text = str(content)[:300]
                print(f"{ts} [USER] {text[:300]}")
            elif role == "assistant":
                if isinstance(content, list):
                    texts = [c.get("text","")[:300] for c in content if c.get("type")=="text" and c.get("text")]
                    tools = [c.get("name","") for c in content if c.get("type")=="tool_use"]
                    out = " ".join(texts)[:300]
                    if tools:
                        out += " | TOOLS: " + ",".join(tools)
                    print(f"{ts} [OLIVIA] {out}")
                else:
                    print(f"{ts} [OLIVIA] {str(content)[:300]}")
        elif t == "custom" and obj.get("customType") == "usage":
            data = obj.get("data",{})
            cost = data.get("estimatedCostUsd","")
            usage = data.get("usage",{})
            print(f'{ts} [COST] ${cost} in={usage.get("inputTokens",0)} out={usage.get("outputTokens",0)} cache_read={usage.get("cacheRead",0)} cache_write={usage.get("cacheWrite",0)}')
