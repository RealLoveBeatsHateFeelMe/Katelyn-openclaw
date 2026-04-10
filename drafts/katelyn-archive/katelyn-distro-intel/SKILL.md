---
name: katelyn-distro-intel
description: Load at the start of every distro-intel cron run. This is the complete distro-intel (分发情报) workflow — Katelyn researches what solo devs / indie makers are successfully publishing on Reddit/X/Medium in the last 7 days and extracts stealable patterns. Not about writing our own content — about learning from others' viral posts. Contains the source scan list, the 3-case output template, the 'why this worked' analysis framework, and the silence-on-empty rule.
---

# Distro-intel Workflow — 分发情报

## 核心问题

**最近 7 天 Reddit / X / Medium 上有没有 solo dev / indie maker 发的内容爆了？他们怎么做的？**

这是**学别人怎么发**，不是写我们要发的。

## 触发

Cron：`0 10 * * *`（PT 时区，每日 10:00）

## 工作流

### Step 1：读本 skill

### Step 2：扫描源

- **r/SideProject 过去 7 天 top 帖**：用 `reddit/scripts/reddit.py top SideProject 20 week`
- **@levelsio (Pieter Levels) / 其他 indie hero** 的 X 最近推文：用 `web_search` 搜 `@levelsio from:2026-04`
- **Medium 上 Show HN / product launch 类高 clap 文章**：用 `web_search` site:medium.com
- **Hacker News Show HN 本周 top**：用 `web_fetch` https://news.ycombinator.com/show

### Step 3：筛出 3 个最成功的案例

条件：
- 高 upvote / clap / 评论数
- 作者是真 solo dev / indie maker（不是公司账号）
- 帖子是过去 7 天内的
- 有可复用的模式（不是一次性流量事件）

### Step 4：每个案例分析 2-3 条观察

- **标题套路**：钩子结构、数字运用、对比
- **开头**：怎么拉住第一秒
- **描述结构**：怎么组织内容
- **评论处理**：作者怎么回复争议 / 疑问
- **可以偷的一条具体套路**

### Step 5：写 briefing

按输出模板。

### Step 6：自检

- 每个案例都有**真实数据**（具体数字 + 时间 + 作者 handle）？
- 每个案例是**本周的**？不是翻老帖？
- 可偷的套路是**具体一条**，不是空话？
- 最多 3 个案例？
- 没找到值得学的？→ 沉默

### Step 7：发送

## 必填字段（缺一不可）

每个案例**必须包含**以下所有字段。缺任何一个就重做：

1. **帖子标题**（完整原标题）
2. **URL 链接**（裸链接，让 Telegram 渲染成可点击 — 不包代码块）
3. **平台 + 数据**（具体数字 upvote/clap/comment 不能是"很多"）
4. **作者 handle**（`u/xxx` 或 `@xxx`）
5. **作者是什么人**（solo dev / indie maker / founder 等一句话背景）
6. **为什么成功**（2-3 条具体观察，不是空话）
7. **可以偷的套路**（至少 1 条**具体可执行**的动作，不是"多发几条"）

## 输出模板

消息格式（元数据普通文本，不包代码块）：

---

📡 分发情报 — YYYY-MM-DD

今天学到的：<一句话总结>

━━━━━━━━━━━━━━━━━━━━━━━

**案例 1：<帖子完整原标题>**

🔗 <URL 裸链接>

📍 <Reddit r/X / X @handle / Medium publication> · <X upvotes / Y 评论 / Z 天前>

👤 <作者 handle>（<一句话说是什么人>）

**为什么成功：**
- <具体观察 1>
- <具体观察 2>
- <具体观察 3>

**可以偷的套路：**
- <具体一条可执行动作>

━━━━━━━━━━━━━━━━━━━━━━━

**案例 2：...**（同样结构）

**案例 3：...**（同样结构）

━━━━━━━━━━━━━━━━━━━━━━━

**本周累计学到**：<过去 7 天共 N 个案例，主要 pattern>

---

## 关键规则

- **URL 必须是裸链接**（不包任何代码块），这样 Telegram 会渲染成可点击
- **标题完整**，不要截断
- **数据具体**（"4200 upvotes"，不是"很多 upvote"）
- **可偷套路必须具体**（"开头第一句用'I spent X days doing Y'模板" 不是"用有吸引力的开头"）
- **每条观察 + 套路都要能指到原帖**的某一句话或某个结构

## 硬规则

- **最多 3 个案例**（贵精不贵多）
- **案例必须是本周的**（不要翻老帖）
- **每条必须有真实数据**（具体数字不是"很多"）
- **没找到真正值得学的 → 沉默**（不凑数）

## 反例

❌ "案例 1：某人发了个 SaaS 火了，值得学习" (没有具体数据)

❌ "可以偷的套路：多发几条" (空话)

❌ "上周的老帖" (不是本周)

❌ 凑 3 个案例即使其中 2 个很弱

## Never do

- 不引用公司账号（Stripe / Vercel / 任何 company）— 只看 solo maker
- 不写主观感受 ("我觉得这篇很好")，只写可验证事实 + 机制
- 不抄袭案例，只提取模式
