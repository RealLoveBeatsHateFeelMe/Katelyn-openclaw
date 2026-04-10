#!/bin/bash
echo "=== Verification ==="
for f in /home/xzwz778/.openclaw/workspace-lizhuochen/skills/*/SKILL.md; do
    dir=$(basename $(dirname "$f"))
    name=$(head -3 "$f" | grep 'name:' | sed 's/name: //')
    lines=$(wc -l < "$f")
    echo "$dir | name:$name | lines: $lines"
done
echo "=== Total Count ==="
ls /home/xzwz778/.openclaw/workspace-lizhuochen/skills/*/SKILL.md | wc -l
echo "=== DONE ==="
