---
name: x-scoring
description: Load when evaluating X posts for reply opportunities. Contains the X Opportunity Score formula (topic_relevance + author_size + reply_window + recency + diary_overlap - saturation_penalty - not_original_penalty), decision gates, and scoring examples. Adapted from katelyn-scoring-formulas for X-specific dimensions. Read during x-kol-scan when deciding which posts are worth surfacing.
---

# X Scoring Formulas

> X 帖子评分引擎。每次评估帖子时用这里的公式，不凭感觉。
> 从 katelyn-scoring-formulas 适配，针对 X 的核心区别：回复窗口 > 热度。

---

## 一、X Opportunity Score（帖子评分）

### 完整公式

```
x_opportunity_score =
    topic_relevance         (0-5)
  + author_size_score       (0-3)
  + reply_window_score      (0-5, 核心维度)
  + recency_score           (0-3)
  # diary matching 由 x-reply-briefing 的 LLM 直接判断，不在评分公式里
  - reply_saturation_penalty (-5 if >25 replies)
  - not_original_penalty     (-10 if 转发/回复/引用，不是原创帖)
```

### 分量拆解

#### topic_relevance (0-5)

按帖子内容对献之垂直领域的匹配度：

- **5** = 核心命中（"Claude Code agent"、"build in public AI"、"AI indie hacker"、"shipped my AI product"）
- **4** = 高度相关（"AI startup lessons"、"solo founder shipping"、"vibe coding"）
- **3** = 领域相关（"side project launch"、"startup fundraising"、"indie dev struggles"）
- **2** = 擦边（"tech layoffs"、"SaaS pricing"、"remote work"）
- **1** = 勉强相关
- **0** = 无关 → 直接跳过

#### author_size_score (0-3)

```
if followers >= 100K:    3  (大V，回复曝光高)
elif followers >= 50K:   2
elif followers >= 10K:   1
elif followers >= 5K:    0  (太小，除非是同龄 builder)
else:                    SKIP (不评分，直接跳过)
```

**例外**：如果 author 在 x-kol-list.json 里且 vertical=young_builder，即使 followers < 10K 也按 1 分算。同龄 builder 优先。

#### reply_window_score (0-5) ⭐ 核心维度

这是 X 和 Reddit 最大的区别。Reddit 看热度，X 看回复窗口。

```
if reply_count <= 3:     5  (黄金窗口 — 极早期，大概率被作者看到)
elif reply_count <= 10:  4  (很好 — 还在前列)
elif reply_count <= 25:  3  (好 — 最后机会)
elif reply_count <= 50:  1  (边缘 — 可能被淹没)
else:                    0  (太拥挤)
```

**reply_count > 50 且 author_followers > 200K → 直接跳过**（大V热帖，你的回复一定被淹没）

#### recency_score (0-3)

```
if age < 1h:     3  (刚发 — 最佳回复时机)
elif age < 3h:   2  (热乎 — 赶紧)
elif age < 12h:  1  (还行)
elif age < 48h:  0  (可以看但回复效果差)
elif age < 7d:   0
else:            SKIP (超过 7 天不评分)
```

#### diary_overlap_bonus (0-5)

当 `state/x-diary-today.json` 存在且非空时生效：

```
if post.topic 和 diary.theme 直接重合（同一技术/同一问题）:   5
elif post.topic 和 diary.theme 相关但不完全一样:              3
elif post.topic 和 diary.theme 有松散关联:                    1
else:                                                         0
```

匹配逻辑：对比帖子内容和日记中的 problems_solved / themes / current_status 关键词。

**没有日记时**：diary_overlap_bonus 固定为 0，不影响其他维度。

#### reply_saturation_penalty (-5)

```
if reply_count > 25:    -5
```

这是硬性惩罚。>25 条回复 = 你几乎不可能被看到。

#### not_original_penalty (-10)

```
if post is 转发(repost):   -10 (直接排除)
if post is 回复(reply):    -10 (直接排除)
if post is 引用转发(quote): -5  (可能有价值但降权)
```

**原创帖子 only。** 这是铁律。

---

## 二、决策门

```
if x_opportunity_score >= 12:
    🔥 HIGH PRIORITY → 立即标记为候选，紧急推送
elif x_opportunity_score >= 8:
    ⭐ GOOD → 标记为候选，进入下一轮 briefing
elif x_opportunity_score >= 5:
    🟡 MARGINAL → 存储但在 briefing 中排最后
else:
    SKIP → 记录到 state/x-processed-posts.json，记跳过原因
```

### 紧急推送条件

以下条件**同时满足**时，不等 briefing 时间，立即推送 Telegram：

```
x_opportunity_score >= 12
AND reply_count <= 5
AND age < 1h
```

---

## 三、评分示例

### 示例 1：黄金机会

```
Post: "Day 42 of building my AI product. Just hit first 10 paying users."
Author: @marc_louvion (170K followers)
Reply count: 4
Age: 45 minutes
Diary today: "今天 Likely You 拿到第 3 个付费用户"
```

```
topic_relevance:     5 (build in public + AI product)
author_size:         3 (>100K)
reply_window:        5 (<=3... wait, 4 replies = 4)
recency:             3 (<1h)
diary_overlap:       5 (都在聊付费用户里程碑)
saturation:          0
not_original:        0

score = 5 + 3 + 4 + 3 + 5 = 20 → 🔥 HIGH PRIORITY + 紧急推送
```

### 示例 2：普通机会

```
Post: "Hot take: most AI wrappers will die in 2026"
Author: @svpino (447K followers)
Reply count: 18
Age: 5 hours
No diary today
```

```
topic_relevance:     4 (AI startup 相关)
author_size:         3 (>100K)
reply_window:        3 (10-25)
recency:             2 (3-12h)
diary_overlap:       0 (无日记)
saturation:          0
not_original:        0

score = 4 + 3 + 3 + 2 + 0 = 12 → 🔥 HIGH PRIORITY
```

### 示例 3：跳过

```
Post: "Congratulations @someone on the launch! 🎉"
Author: @levelsio (850K followers)
This is a reply to someone else's post
```

```
not_original_penalty: -10 → 直接跳过
reason: "not_original_post (reply)"
```

### 示例 4：太拥挤

```
Post: "We just launched Claude 4.7"
Author: @AnthropicAI (500K followers)
Reply count: 340
Age: 2 hours
```

```
reply_count > 50 AND followers > 200K → 直接跳过
reason: "too_crowded (340 replies on 500K account)"
```

---

## 四、每次 briefing 排序规则

```
1. 先按 x_opportunity_score 降序
2. 同分时，diary_overlap 高的排前面
3. 同分同 diary 时，recency 高的排前面
4. 每次 briefing 最多展示 5 条
5. 剩余的写 "还有 N 条备选"
```

---

## 五、更新记录

- 2026-04-10：首次建立（从 katelyn-scoring-formulas 适配 X 维度）
