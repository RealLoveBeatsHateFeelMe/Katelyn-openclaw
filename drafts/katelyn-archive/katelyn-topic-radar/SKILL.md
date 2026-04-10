---
name: katelyn-topic-radar
description: Load at the start of every topic-radar cron run. This is the complete topic-radar (话题雷达) workflow — Katelyn scans which celebrities/topics are being heavily discussed this week across r/popheads/r/MMA/r/UFC/r/Entrepreneur/r/technology/X, then calls the Likely You engine API to pull the six-dimension astro-engine output (personality/dayun/liunian/feeling/marriage/liuqin) for each candidate, compares it against publicly verifiable career events, and generates a 3-candidate recommendation briefing with recommendation score and publish-where suggestions. Contains the engine API call format, the six-dimension analysis template, and the Taylor Swift benchmark.
---

# Topic-radar Workflow — 话题雷达

## 核心问题

**本周哪些名人/话题讨论量高？谁适合做 Likely You demo？**

Topic-radar 是 Katelyn 最有产品价值的情报线。成功的一次 = 找到一个还没被开发但可以写出 Taylor Swift 级别验证点的名人。

## 触发

Cron：`0 14 * * *`（PT 时区，每日 14:00）

## 工作流

### Step 1：读本 skill

### Step 2：读关键 skills

- `katelyn-celebrity-playbook` — 名人选择标准 + Taylor Swift 基准 + ENGINE vs REALITY 对照框架
- `katelyn-product-context` — 产品定位 + 禁词
- `katelyn-mma-strategy` — 如果候选是 MMA fighter，读这个
- `katelyn-brand-voice` — 禁词和输出风格

### Step 3：扫描热度

用 `reddit/scripts/reddit.py top <sub> 20 week` 扫下面社区的本周 top：

- r/popheads（流行音乐名人）
- r/MMA（UFC fighters）
- r/UFC（UFC 具体赛事）
- r/Entrepreneur（tech founders）
- r/technology（Elon / Sam Altman 类）
- r/hiphopheads（音乐人候选）

用 `web_search` 搜 X 上最近的名人热搜：
- `"<celebrity>" site:twitter.com since:2026-04-02`

### Step 4：筛出 3 个候选

条件（硬性）：
- **公开生日可查**（Wikipedia / 官方传记）
- **career 事件够多**（至少 10 年公开履历）
- **本周被活跃讨论**（3 篇以上社区帖 或 X 热搜）
- **可做 demo**（受众和 Likely You 目标用户重叠）
- **不违反品牌禁区**（不要 astrology 相关讨论里的名人）

### Step 5：对每个候选调用引擎 API

引擎 API：
- URL：`$LIKELYYOU_ENGINE_URL`（环境变量，默认 `https://web-production-7e1ed.up.railway.app/v1/agent/profile`）
- 认证：Header `X-Katelyn-Key: $LIKELYYOU_ENGINE_KEY`
- Method：POST
- Body：
  ```json
  {
    "birth_date": "YYYY-MM-DD",
    "is_male": true | false,
    "birth_time": "HH:MM"  // 选填，能查到就用，查不到留空走无时辰模式
  }
  ```

**优先无时辰模式**（只传 `birth_date` + `is_male`）。

**如果查到具体生辰和位置**，用时辰试一次，然后用**时柱的冲**（搬家/换工作年份）验证时柱是否正确。如果时柱对不上，回退到无时辰模式。

**用 bash 工具**调用：
```bash
curl -sS -X POST "$LIKELYYOU_ENGINE_URL" \
  -H "X-Katelyn-Key: $LIKELYYOU_ENGINE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"birth_date":"1989-12-13","is_male":false}'
```

返回的 JSON 有 6 个维度：
- `personality.dominant_traits`（三大特质 + 占比）
- `dayun.current` + `dayun.future`（大运时间线）
- `liunian`（流年标签 + 评分）
- `feeling`（感情窗口 by year）
- `liuqin`（六亲助力：比劫 / 食伤 / 印 / 财 / 官）
- `marriage.structure_type` + `marriage.hints`（婚恋结构）

### Step 6：对照公开 career 事件

对每个候选，用 `web_search` 或 `web_fetch` 查他/她的公开 career 事件：
- Wikipedia 完整传记
- 主要 career 里程碑（职业转折 / 大奖 / 爆款作品）
- 感情事件（公开的结婚 / 离婚 / 分手）
- 健康 / 争议事件

**把引擎输出的每个维度对照真实事件**：

| 维度 | 引擎输出 | 真实事件 | 匹配度 ★ |
|------|---------|---------|----------|
| 大运当前 | "偏门技术/思维突破 2017-2026" | Folklore indie folk + 重录 6 张专辑 | ★★★★★ |
| 流年 2022 | "前一般后好" | 10 月 Midnights 打破记录 | ★★★★★ |
| ... | ... | ... | ... |

### Step 7：写 briefing

每个候选按模板输出（见下）。**推荐指数**基于：
- 讨论度 × 引擎可验证度 × 社区 fit 度

### Step 8：更新 trend-signals

把发现的候选追加到 `state/trend-signals.json` 的 `active_trends`。

### Step 9：发送

## 引擎 API 返回的完整数据结构

引擎调用返回的 JSON 包含 6 个核心维度。**topic-radar briefing 必须列出每个维度的所有数据点对照真实事件**，不是只挑一两个。

### 1. `dayun` — 大运（最重要！）

```json
"dayun": {
  "current": {"start_year": 2017, "end_year": 2026, "ganzi": "己卯", "is_good": true},
  "future": [
    {"start_year": 2027, "end_year": 2036, "ganzi": "庚辰", "is_good": true},
    {"start_year": 2037, "end_year": 2046, "ganzi": "辛巳", "is_good": true},
    ...
  ]
}
```

**强制要求**：列出从**当前大运开始往前回溯 1-2 段** + **当前大运** + **未来 2-3 段**，总共 **5-6 段大运对照**。每段都要写：
- 起止年份
- 干支
- is_good（好/坏）
- **对照该名人在那段时间的真实 career 事件**

**关键**：过去大运（往前回溯）是验证准确度的核心。如果某段大运标"好运 / 创新"而那段时间真的有大事件，就证明引擎有效。

### 2. `liunian` — 流年（10 年逐年对照，最重要！）

```json
"liunian": [
  {"year": 2021, "rating": "凶", "score": -2.0},
  {"year": 2022, "rating": "前一般后好", "score": 0.5},
  {"year": 2023, "rating": "波折", "score": -1.0},
  ...
]
```

**强制要求**：列出引擎返回的**所有 10 年流年**。每年都要写：
- 年份
- rating（凶 / 好 / 波折 / 一般 / 前后差异）
- score
- **对照该名人那一年的真实事件**（career / 感情 / 健康 / 重大决定）

**关键**：流年是逐年精度对照，能验证到半年（"前一般后好"对应下半年发生的事）。

### 3. `liuqin` — 六亲助力（重要！）

```json
"liuqin": [
  {"group": "比劫", "shishen": "劫财", "source": "兄弟姐妹/同辈朋友/同学同事", "strength": "用神有力，助力较多"},
  {"group": "食伤", "shishen": "食神", "source": "子女/晚辈/技术/才艺产出", "strength": "用神有力，助力较多"}
]
```

**强制要求**：列出**所有六亲组**。每组都要写：
- group + shishen
- source（这一组对应的真实人物类别）
- strength
- **对照该名人在这个领域的真实情况**（家庭关系 / 朋友圈 / 同行 / 子女）

**关键**：六亲是验证人物关系结构的核心。Taylor Swift 的"比劫强"对应 Swifties + Squad 闺蜜，"食伤强"对应词曲创作产出。这些是最强的对照点。

### 4. `personality.dominant_traits` — 性格特质（前 3 大）

```json
"dominant_traits": [
  {"group": "官杀", "shishen": "七杀", "percent": 46.7},
  {"group": "食伤", "shishen": "食神", "percent": 26.7},
  {"group": "比劫", "shishen": "劫财", "percent": 26.7}
]
```

**强制要求**：3 个特质 + 占比 + **对照真实性格表现**。

### 5. `feeling` — 感情窗口（10 年逐年）

```json
"feeling": {"2021": "有暧昧但难成正果", "2022": "有恋爱机会", "2023": "有恋爱机会", ...}
```

**强制要求**：列出**有信号的所有年份**对照真实感情事件。

### 6. `bazi` — 八字基础信息（开头展示）

```json
"bazi": {"day_master": "丁火", "zodiac": "蛇", "yongshen_elements": ["木","火","土"]}
```

**强制要求**：开头一行展示：日主 + 属相 + 用神。

---

## 输出模板

```
🔭 话题雷达 — YYYY-MM-DD

本周最热的 <N> 个候选（按热度排序）：

━━━━━━━━━━━━━━━━━━━━━━━
🎯 1. <名人名字> — 🔥🔥🔥

📅 公开生日：YYYY-MM-DD
🐉 八字：日主 <X> · 属相 <Y> · 用神 <Z>

📰 本周热在哪：<2026-04 具体事件 + 讨论阵地数据>

━━━━ 引擎对照 ENGINE vs REALITY ━━━━

🧬 性格特质（前 3）
- <十神 1> <X%>：[真实对照] <具体事件>
- <十神 2> <X%>：[真实对照] <具体事件>
- <十神 3> <X%>：[真实对照] <具体事件>

⏳ 大运时间线（5-6 段，过去 + 当前 + 未来）

| 大运段 | 年份 | 关键词 | 真实对照 | ★ |
|--------|------|--------|----------|---|
| 大运 1 | 1997-2006 | <关键词> | <真实事件> | ★★★★★ |
| 大运 2 | 2007-2016 | <关键词> | <真实事件> | ★★★★★ |
| **大运 3 (NOW)** | **2017-2026** | **<关键词>** | **<正在发生的事>** | **★★★★★** |
| 大运 4 | 2027-2036 | <关键词> | <未发生，待验证> | — |
| 大运 5 | 2037-2046 | <关键词> | <未发生> | — |

🗓️ 流年逐年（必须列全 10 年）

| 年份 | 引擎 rating | 真实事件 | ★ |
|------|------------|---------|---|
| 2021 | 凶 (-2) | <真实事件> | ★★★★★ |
| 2022 | 前一般后好 (0.5) | <下半年发生的事> | ★★★★★ |
| 2023 | 波折 (-1) | <真实事件> | ★★★★★ |
| 2024 | 好 (1) | <真实事件> | ★★★★★ |
| 2025 | 前好 + 小波折 | <真实事件> | ★★★★☆ |
| 2026 | 凶 (-2) | <未发生 / 待验证> | — |
| 2027 | 好 | — | — |
| 2028 | 前好后一般 | — | — |
| 2029 | 前好后一般 | — | — |
| 2030 | <rating> | — | — |

💑 感情窗口（有信号的年份）
- YYYY：<引擎标签> → <真实事件>
- YYYY：<引擎标签> → <真实事件>

👨‍👩‍👧 六亲助力（必须列全）
- <组 1>：<source> · <strength> → [真实对照] <具体事件>
- <组 2>：<source> · <strength> → [真实对照] <具体事件>

━━━━ 综合判断 ━━━━

💡 切入点：<一句话说为什么这个人的对照有爆点>

⭐ 推荐指数：★★★★☆（<X/5>）
理由：<基于上面对照的强度>

📤 怎么发：
- 主阵地：<r/X / X Thread / Medium>
- 备选：<其他平台>
- 格式：<长文 / Thread / 讨论帖>
- 时机：<马上 / 等事件发酵>

━━━━━━━━━━━━━━━━━━━━━━━

🎯 2. <第二位名人>
（同样完整结构）

🎯 3. <第三位名人>
（同样完整结构）
```

## 硬规则（v3，2026-04-09 加强）

1. **必须列出 5-6 段大运对照**（不是只挑当前一段）
2. **必须列出全部 10 年流年逐年对照**（不是挑 2 年）
3. **必须列出全部六亲组对照**（不是挑 1 组）
4. **必须列出 3 大性格特质对照**
5. **大运 / 流年 / 六亲是必填字段**，缺一就重做
6. 如果引擎数据某个字段是空的（比如 marriage.structure_type 经常是空），明确写 "引擎此字段为空"，**不要省略整个段落**
7. 候选数量按本周真实热度，1-3 个都行，**没找到就 1 个**
8. 表格格式必须用 Markdown 表格（Telegram 渲染好）

## 🚨 必须分多条 Telegram 消息发送

**Telegram 单条消息上限是 4096 字符**。完整的 topic-radar briefing 一定超长。

**分发策略**：
- **第 1 条消息**：标题 + 总览（"本周 N 个候选"）+ 简短列表（每个候选只列名字 + 一句话热点）
- **第 2 条消息**：候选 1 的完整对照（八字 + 性格 + 大运 + 流年 + 六亲 + 切入点 + 推荐 + 怎么发）
- **第 3 条消息**：候选 2 的完整对照
- **第 4 条消息**：候选 3 的完整对照

**用 message 工具的多次调用** — 每次发一条消息给 Telegram，等返回成功后发下一条。**不要把所有内容塞到一次 sendMessage 里**。

**示例（多条发送顺序）**：

第 1 条（≤500 字）：
```
🔭 话题雷达 — YYYY-MM-DD

本周 2 个候选：
1. Carlos Ulberg — UFC 327 主赛挑战者
2. Jiří Procházka — 前轻重量级冠军

完整对照下面分条发。
```

第 2 条（独立消息，≤3500 字）：
```
🎯 1. Carlos Ulberg
[完整 6 维度对照表]
```

第 3 条（独立消息，≤3500 字）：
```
🎯 2. Jiří Procházka
[完整 6 维度对照表]
```

**自检**：发送前心算每条消息字符数。**单条 ≤ 3500 字符**留 buffer（不是 4096，留 600 字符 buffer）。如果一个候选的对照表本身就超 3500 字，**减少表格里的解释文字** 但不要砍掉维度。

## 硬规则

- **最多 3 个候选**
- **必须是真实讨论量**（具体数字）
- **必须成功调用引擎 API**（如果 API 不可用，降级但要诚实说明）
- **必须有至少 2 个 ENGINE vs REALITY 对照**
- **今天没找到 3 个符合条件的候选 → 只推 1-2 个**（但不要凑到 3 个）

## 降级模式（引擎 API 不可用）

如果 `curl $LIKELYYOU_ENGINE_URL` 返回错误：
1. 继续扫描热度
2. 写候选名字 + 生日 + 可对照的 career 事件
3. 加一行：`⚠️ 引擎 API 暂时不可用，对照数据缺失`
4. 推送给献之

**绝不编造引擎输出**。宁可缺数据也不瞎写。

## 基准参考

`katelyn-celebrity-playbook` 里有 Taylor Swift 的完整基准（3 特质 + 70 年大运 + 流年精度到半年 + 感情窗口验证）。**写 briefing 时质量要对标这个基准**。

## Never do

- 不预测单场 UFC 比赛结果
- 不用 astrology / bazi 等禁词
- 不对 r/astrology 相关用户做推荐
- 不推荐没有公开生日的名人
- 不编造引擎输出
- 不推荐虚构人物（要真实历史 / 当代人物）
