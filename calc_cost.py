import json, sys
sys.stdout.reconfigure(encoding='utf-8')

messages = []
with open("C:/Users/32247/Desktop/olivia_session.jsonl", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line.strip())
        if obj.get("type") == "message":
            msg = obj.get("message", {})
            role = msg.get("role","")
            content = msg.get("content","")
            if isinstance(content, list):
                text = " ".join([c.get("text","") for c in content if c.get("type")=="text"])
            else:
                text = str(content)
            char_count = len(text)
            messages.append({"role": role, "chars": char_count, "ts": obj.get("timestamp","")})

# Count turns
user_turns = [m for m in messages if m["role"] == "user"]
asst_turns = [m for m in messages if m["role"] == "assistant"]

total_user_chars = sum(m["chars"] for m in user_turns)
total_asst_chars = sum(m["chars"] for m in asst_turns)

print(f"User messages: {len(user_turns)}")
print(f"Assistant messages: {len(asst_turns)}")
print(f"Total user chars: {total_user_chars:,}")
print(f"Total assistant chars: {total_asst_chars:,}")
print()

# Estimate tokens (rough: 1 token ≈ 3-4 chars for Chinese)
# System prompt: 27483 chars ≈ ~9000 tokens
sys_prompt_tokens = 9000

# Each turn resends everything before it
# Sonnet 4.5 pricing: $3/M input, $15/M output, $0.30/M cache read
# Actually Sonnet 4.6 pricing
cumulative_input = 0
total_input_cost = 0
total_output_cost = 0
total_cache_cost = 0

print("=== Per-turn cost estimate ===")
turn = 0
running_context_chars = 0
for i, m in enumerate(messages):
    running_context_chars += m["chars"]
    if m["role"] == "assistant":
        turn += 1
        # tokens ≈ chars / 3.5 for mixed zh/en
        context_tokens = sys_prompt_tokens + int(running_context_chars / 3.5)
        output_tokens = int(m["chars"] / 3.5)
        
        # With prompt caching, first turn pays full, rest mostly cache read
        if turn == 1:
            input_cost = context_tokens * 3 / 1_000_000  # $3/M input
            cache_cost = 0
        else:
            # ~90% cache hit
            cache_tokens = int(context_tokens * 0.9)
            fresh_tokens = context_tokens - cache_tokens
            input_cost = fresh_tokens * 3 / 1_000_000
            cache_cost = cache_tokens * 0.30 / 1_000_000
        
        output_cost = output_tokens * 15 / 1_000_000
        turn_cost = input_cost + output_cost + cache_cost
        total_input_cost += input_cost
        total_output_cost += output_cost
        total_cache_cost += cache_cost
        
        if turn <= 5 or turn % 5 == 0 or turn >= len(asst_turns) - 2:
            print(f"Turn {turn:2d}: ctx≈{context_tokens:6,} tok, out≈{output_tokens:4,} tok, cost≈${turn_cost:.4f}")

total = total_input_cost + total_output_cost + total_cache_cost
print(f"\n--- Estimated total: ${total:.2f} (input=${total_input_cost:.2f} output=${total_output_cost:.2f} cache=${total_cache_cost:.2f}) ---")
print(f"--- Actual reported: $5.86 ---")
print(f"\nAvg cost per turn: ${5.86/len(asst_turns):.4f}")
print(f"System prompt overhead per turn (cache): ${sys_prompt_tokens * 0.30 / 1_000_000:.4f}")
