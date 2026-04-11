---
name: x-reply-briefing
description: Load at the start of every x-reply-briefing cron run. Reads candidate posts from state/x-processed-posts.json, reads 献之's diary markdown file, then uses LLM judgment to match diary content to posts and generate reply angle hints. Pushes formatted Telegram briefing.
---

# X Reply Briefing — Briefing 生成

## 核心任务

读候选帖子 + 读献之的日记 md + 判断哪些帖子和日记里的经历能对上 + 推送 Telegram briefing。

**不做结构化解析。** 直接读 md 原文，靠 LLM 语义理解做匹配。

## 触发

Cron：`0 10,15,21 * * *`（PT 时区，每天 10:00 / 15:00 / 21:00）

## 工作流

### Step 1：读 skills

- 本 skill
- `x-scoring` — 确认评分维度

### Step 2：读候选帖子

- `state/x-processed-posts.json` — 取 `status == "candidate"` 的帖子
- 按 `x_opportunity_score` 降序排列
- 取前 20 条

### Step 3：读献之的日记

日记文件路径（按优先级尝试）：
1. `/home/node/.openclaw/workspace-katelyn/diary.md`
2. 如果不存在，检查 `/home/node/.openclaw/workspace-katelyn/drafts/diary-*.md`

**直接读全文。** 不解析、不提取关键词、不转 JSON。

日记里会包含：
- 今天遇到的问题
- 怎么解决的
- 仍然存在的问题
- 当前在 build 什么
- 感悟、观察、情绪

### Step 4：匹配 + 生成回复角度

**一次性把 20 个帖子 + 日记全文喂给自己，做以下判断：**

对每个帖子问自己：
1. 日记里有没有任何经历、问题、解决方案和这个帖子讨论的话题相关？
2. 如果有 → 生成 1-2 句中文回复角度提示，指出具体是日记里哪段经历可以用
3. 如果没有 → 标记"无日记关联"，给一个通用的 builder 视角回复建议

**匹配标准很宽松**：不需要话题完全一样，只要有共通的经验或感悟就算。比如：
- 帖子聊 "distribution is hard"，日记里你搭了 4 个 agent 做自动分发 → 相关
- 帖子聊 "first 10 paying users"，日记里你在想定价策略 → 相关
- 帖子聊 "Claude Code vs LangChain"，日记里你在 debug Claude Code → 相关

### Step 5：排序

```
1. 有日记关联的帖子排前面
2. 同类帖子内按 x_opportunity_score 降序
3. 最多展示 5 条
```

### Step 6：格式化 Telegram briefing

```
🐦 X Reply 机会 — {date} {time} PT

📊 扫描候选 {total} 条，筛出 {count} 条

═══════════════════════════

🔥 #1 — @{handle} ({followers} followers)
💬 {reply_count} · ❤️ {like_count} · ⏰ {age}
📝 "{tweet_text 前 120 字}"

🎯 {回复角度提示 — 指出日记里哪段经历能用}

🔗 {url}

───────────────────────────

⭐ #2 — ...

═══════════════════════════

📋 跳过：{skip_reasons}

💡 15 分钟内回复 = 3-5x 曝光
```

**规则**：
- 最多 5 条
- 🔥 = 有日记关联 + 高分，⭐ = 高分但无日记关联，🟢 = 一般
- 回复角度用中文，帖子原文保留英文

### Step 7：发送 Telegram + 更新状态

推送到 Katelyn Telegram bot。展示过的帖子 status 改为 "briefed"。

## 没有日记时

如果日记文件不存在或为空：
- 正常推送 briefing，纯按 opportunity score 排序
- 所有角度提示为通用建议
- 末尾加：`📝 日记文件为空。写了日记后下次 briefing 会更精准。`

## 没有候选帖子时

- 不推送（静默）
- 连续 2 轮都没有候选 → 推送：`🐦 最近 2 轮都没有找到合适机会。可能需要扩展 KOL 列表。`

## 绝对不做

- 不生成英文回复草稿（献之自己写）
- 不自动发布到 X
- 不暴露文件路径
- 不做结构化日记解析（直接读 md 原文）

## 更新记录

- 2026-04-11：v2 简化 — 去掉结构化日记解析，直接读 md + LLM 语义匹配
- 2026-04-10：v1 首次建立
