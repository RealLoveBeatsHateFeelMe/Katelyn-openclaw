---
name: x-reply-briefing
description: For each candidate tweet, fetch reply context (via x-reply-context skill), then generate full Chinese translation, diary connection (verbatim quote), and 3 short English reply drafts (≤25 words each, real-person tone, A=共鸣 B=反观察 C=短问). Push each candidate as separate Telegram message.
---

# X Reply Briefing — 真人腔版（v5）

## 核心目标

让献之看完 briefing 就能改 1-2 个词发出去 —— 不用读英文原文、不用翻日记、不用想措辞。

**关键认知**：X 不是论坛，不是邮件。X 上 reply 的目的是**刷脸熟**。
- 短（≤25 词）
- 真人腔（lowercase i / imo / tbh / fwiw / 破折号）
- 观点先行（第一个词就是态度）
- 不要论证、不要分点、不要"开放式收尾问题"

之前 Reddit 版 katelyn-farm-ops 已经掌握这套规则。X 版用同样的精神。

## 触发

Cron: `0 10,15,21 * * *` PT（每天 3 次，比 x-kol-scan 晚 30 分钟）

## 工作流

### Step 1：读 skills + 状态

- 本 skill
- `x-scoring`
- `x-reply-context` — 看帖子下 reply 的工作流
- `state/x-processed-posts.json` — 取 status=candidate
- `diary.md`

### Step 2：筛选 top 5 候选

按 x_opportunity_score 降序取前 5 条 candidate。

### Step 3：读日记全文

直接读 `/home/node/.openclaw/workspace-katelyn/diary.md`。

### Step 4：对每个候选 fetch reply context

按 x-reply-context 的分支逻辑：
- reply_count == 0 → 跳过 API（"first_mover"）
- 1-4 → fetch 全部 reply（"early_window"）
- 5+ → fetch + 分析（"crowded"）

每次 curl 之间 sleep 6（rate limit）。

### Step 5：对每个候选生成完整内容

一次生成所有字段：

```json
{
  "tweet_translation": "完整翻译（不是摘要）",
  "angle_type": "strong_match | loose_match | no_match",
  "diary_connection": "必须引用日记原话（不能编）",
  "reply_context": "<from x-reply-context>",
  "reply_drafts": {
    "A_resonance": {
      "text": "+1, [具体经历/数据点]. ≤25 words.",
      "word_count": 19,
      "why": "1 句话说为什么这个 angle 适合"
    },
    "B_contrarian": {
      "text": "actually [大家没说的角度]. ≤25 words.",
      "word_count": 22,
      "why": "..."
    },
    "C_question": {
      "text": "genuine q — [具体细节]? ≤25 words.",
      "word_count": 17,
      "why": "..."
    }
  }
}
```

### Step 5a：tweet_translation 硬要求

| 推文长度 | 翻译要求 |
|---------|---------|
| < 200 字 | 完整意译 |
| 200-500 字 | **完整翻译**，可分 2-3 段 |
| > 500 字 thread | **每段都翻**，保留段落结构 |

不要"1-2 句摘要"。读者看完中文就知道作者说了什么。

### Step 5b：diary_connection 硬要求

格式：
```
日记原文："{从 diary.md 复制的原话}"
（出处：{主题名}）

这条推文正好在聊 {推文核心}，和你日记里的 {具体观点} 相关。
```

**禁止**：编造、模糊引用、改写日记。
如果日记里真的没有 → angle_type = no_match，diary_connection = "日记里没有直接对应内容。从 builder 视角切入。"

### Step 5c：reply_drafts 硬要求 ⭐ 核心

**3 个草稿固定模板**：

#### A — 共鸣 + 数据点

格式："+1, [具体经历/数据]" 或 "yeah [observation], [data point]"
目的：最容易被 like，刷脸熟
长度：≤20 词最佳，≤25 词上限

例子：
- "+1. tracked 3090s in HK — up 60% since Jan, way ahead of US."
- "this is exactly what i saw last week — 4 of 5 startups switched."
- "fwiw same here. burned 3 weeks before realizing it was the postcss config."

#### B — 反观察 / 白空间

格式："actually [大家没说的角度]" 或 "the part everyone's missing: [angle]"
目的：突出，可能被作者注意到
长度：≤22 词
**优先用 reply_context.white_space_angles 里的角度**

例子：
- "actually the wild part is rental — vast.ai 4090 went up 3x while sale prices flat."
- "contrarian take: the bottleneck isn't compute, it's procurement contracts."
- "the part nobody's saying: this only matters in the bay. SF ≠ rest of world."

#### C — 短问

格式："genuine q — [具体技术细节]?" 或 "wait, does [edge case] also [behavior]?"
目的：最容易被作者回（技术问题作者大概率回答）
长度：≤17 词最佳

例子：
- "genuine q — does this hold for inference-only chips like T4? or only training-grade?"
- "wait — is this enterprise procurement or also consumer?"
- "curious — did you measure this on bare metal or in containers?"

#### 通用硬规则

每个草稿：
- ✅ ≤25 词（数英文单词，超就重写）
- ✅ 真人腔标记（lowercase i / imo / tbh / fwiw / wait / actually / +1 / 破折号 / 省略号）
- ✅ 观点先行（第一个词就是态度）
- ✅ 一个因果暗示就够（不解释、不扩展、不举例）
- ❌ 禁止"As someone who..."模板开头
- ❌ 禁止 "Great post!" / "Interesting take!" 这种空夸
- ❌ 禁止开放式收尾问题（"thoughts?" 可以，"how do you think this will evolve over time?" 不行）
- ❌ 禁止超过 1 个标点符号的复杂结构
- ❌ 禁止任何形式的列表 / 分点 / "first, second, third"

#### why 字段要求

每个草稿配 1 句中文说明 "为什么这个 angle 适合这条帖子"。15 字内。

例子：
- "数据 + 地区差，作者爱 like"
- "蹭白空间，作者可能注意到"
- "技术细节问题，作者大概率回"

### Step 6：分条 Telegram 推送

**每条候选 = 一条独立 Telegram 消息。** 不合并。

**消息格式**：

```
🔥 #{N} / {total} — @{handle} ({followers}k followers)
💬 {reply_count} · ❤️ {like_count} · ⏰ {age}
🔗 https://x.com/{handle}/status/{id}

━━━ 推文原文 ━━━
{tweet_text}

━━━ 中文翻译 ━━━
{tweet_translation}

━━━ 日记关联 ━━━
{diary_connection}

━━━ 现有回复扫描 ━━━
{根据 context_type 显示}

━━━ 3 个 reply 草稿（≤25 词，改 1-2 个词再发）━━━

A — 共鸣 + 数据：
"{A_resonance.text}"
（{A_resonance.word_count} 词 · {A_resonance.why}）

B — 反观察：
"{B_contrarian.text}"
（{B_contrarian.word_count} 词 · {B_contrarian.why}）

C — 短问：
"{C_question.text}"
（{C_question.word_count} 词 · {C_question.why}）
```

#### "现有回复扫描" 段格式

**Case A (first_mover)**：
```
🌟 你是第一个回的，先发优势。
```

**Case B (early_window)**：
```
📊 已有 {N} 条 reply（太少看不出模式，直接 ship）
```

**Case C (crowded)**：
```
📊 {N} 条 reply 分析：

避免：
• {patterns_to_avoid[0]}
• {patterns_to_avoid[1]}

白空间：
• {white_space_angles[0]}
• {white_space_angles[1]}

作者engaged 的：
• 点赞了 @{author}: "{text}"（{why_works}）
• 回复了 @{author}: "{text}"（{why_works}）
```

#### 头部消息（第一条之前）

```
🐦 X Reply 机会 — {date} {time} PT
📊 候选 {total} 条 · 展示 {shown} 条
（接下来 {shown} 条独立消息，逐条看）
```

#### 结尾消息（最后一条之后）

```
━━━━━━━━━━━━━━
💡 草稿改 1-2 个词再发，避免一字不差被 bot 检测
💡 15 分钟内 reply = 3-5x 曝光
```

emoji 标识：
- 🔥 = strong_match
- ⭐ = loose_match
- 🟢 = no_match

### Step 7：更新状态

展示过的 post status: candidate → briefed。

## 没有日记/没有候选时

- diary 空 → 所有 angle_type = no_match，头部加："📝 日记为空，写了 /day 后下次精准"
- 候选 0 条 → 静默退出
- 连续 2 轮空 → 推 "🐦 最近 2 轮无机会"

## 示例（一条好的 briefing）

```
🔥 #1 / 3 — @karpathy (1.2M followers)
💬 47 · ❤️ 8.2K · ⏰ 3h
🔗 https://x.com/karpathy/status/...

━━━ 推文原文 ━━━
The wild thing about AI compute right now: 
old GPUs are appreciating in value.

━━━ 中文翻译 ━━━
AI 算力现在最离谱的事：旧 GPU 在升值。

━━━ 日记关联 ━━━
日记原文："分发问题 = 产品问题（2026-04-11 根本洞察）"
（出处：分发战略）

虽然不是直接同主题，但 builder 都在思考"反常识资源稀缺性"。

━━━ 现有回复扫描 ━━━
📊 47 条 reply 分析：

避免：
• 23 条都在说 "agree, X is the bottleneck"
• 8 条幽默向（"my 2018 GPU is now an asset 😂"）

白空间：
• 二手 GPU 的地理差异
• 租用 vs 购买临界点变化

作者engaged 的：
• 点赞了 @xyz: "fwiw I tracked 3090 prices, up 40% in 6mo"（数据 + 短）

━━━ 3 个 reply 草稿 ━━━

A — 共鸣 + 数据：
"+1. tracked 3090s in HK — up 60% since Jan, way ahead of US."
（19 词 · 地区数据，作者爱 like）

B — 反观察：
"actually the wild part is rental — vast.ai 4090 went up 3x while sale prices flat."
（19 词 · 蹭白空间）

C — 短问：
"genuine q — does this hold for inference chips like T4? or only training-grade?"
（17 词 · 技术细节，作者可能回）
```

## 绝对不做

- 不写中文论证型 reply_direction（v4 的错误）
- 不分点（"第一句... 第二句..."）
- 不写超过 25 词的草稿
- 不写"开放式收尾问题"
- diary_connection 不能编
- 不合并候选成一条 Telegram
- 不暴露文件路径

## 更新记录

- 2026-04-20 v5：reply_direction 改成 3 个 ≤25 词英文草稿（A/B/C 模板），加 reply_context 分析
- 2026-04-12 v4：分条推送，5-8 句中文论证（实测论文腔太重，废弃）
- 2026-04-11 v3：完整翻译 + 日记原文引用
- 2026-04-11 v2：去结构化日记
- 2026-04-10 v1：首版
