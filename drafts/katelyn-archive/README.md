# Katelyn 草稿归档

> 这些是从 Katelyn workspace 移出来的 skill 草稿。Katelyn 现在专注于纯 Reddit 养号（farm-ops + reflection），其他偏题工作将由独立的新 agent 承担。
>
> 归档时间：2026-04-09

---

## 为什么归档

Katelyn 之前同时做四件事：
1. **farm-ops** — Reddit 养号 ✅ Katelyn 的核心职责
2. **distro-intel** — 学别人怎么发 ❌ 偏题
3. **topic-radar** — 名人话题雷达 + 八字引擎对照 ❌ 应该是单独的名人 agent
4. **reflection** — 宽泛策略感触 ❌ 太杂，废话率高（已重写为纯 karma 反思）

**单一职责原则**：每个 agent 只做一件事，做到极致。多功能 agent 的 workspace 不可避免会膨胀污染。

献之的指令："Katelyn 是不是应该只做 Reddit 养号的内容？不然的话 workspace 真的很容易被污染。"

---

## 归档的 6 个 skills

### 1. `katelyn-distro-intel/`

**做什么**：每天扫 r/SideProject、X、Medium、Hacker News，找过去 7 天 solo dev / indie maker 发的爆款帖子，提取可偷的套路。

**为什么从 Katelyn 移出**：这是"学营销"的工作，不是"养号"的工作。和 Katelyn 的 farm-ops 工作性质完全不同。

**未来给谁**：可以是一个独立的"Distribution Intel Agent"（"DI"），或者并入未来的 Olivia 营销升级。

---

### 2. `katelyn-topic-radar/`

**做什么**：扫名人热搜（r/popheads、r/MMA、r/UFC、r/Entrepreneur 等），调用 Likely You 引擎 API 拉八字六维度数据（大运/流年/六亲/性格/感情/婚恋），对照公开 career 事件生成 ENGINE vs REALITY briefing。

**为什么从 Katelyn 移出**：这是"名人八字分析"的核心工作流，本应由独立的"名人八字 Agent"承担。Katelyn 是养号，不是内容生产。

**未来给谁**：未来要建的"名人八字 Agent"（暂定名 "BaziDemo"）。这个 agent 应该直接负责：
- 每周扫热门名人
- 自动调引擎 API
- 输出完整六维度对照
- 拆成多条 Telegram 消息（因为单条 4096 字符上限）

**重要**：这个 skill 已经包含了详细的引擎 API 调用方式 + 6 维度强制列表 + 多条 Telegram 消息分发规则。新 agent 可以直接复用。

---

### 3. `katelyn-celebrity-playbook/`

**做什么**：名人选择标准 + Taylor Swift 完整基准（3 特质 + 3 大运 + 流年精度对照 + 感情窗口）+ ENGINE vs REALITY 框架。

**为什么从 Katelyn 移出**：这是"如何选名人 + 如何分析"的方法论，配套 topic-radar 用。

**未来给谁**：未来"名人八字 Agent"。和 katelyn-topic-radar 一起复用。

---

### 4. `katelyn-twitter-playbook/`

**做什么**：X (Twitter) 发帖规则 — 线程结构、hashtag 策略、时间窗口、爆款钩子模板、互动节奏。

**为什么从 Katelyn 移出**：Katelyn 只做 Reddit。X 的运营节奏完全不同（更高频、更短、更靠 thread 结构）。

**未来给谁**：未来要建的 "X/Twitter 养号 Agent" 或并入更大的多平台分发系统。

---

### 5. `katelyn-medium-playbook/`

**做什么**：Medium 长文 7 段结构（Hook → 方法论 → 引擎输出 → 事件对比 → 3 大验证点 → 局限性 → 邀请）+ SEO 关键词库 + publication 投稿策略。

**为什么从 Katelyn 移出**：Medium 是长文场景，和 Reddit 养号完全不同的内容形态。

**未来给谁**：未来"内容长文 Agent" 或者并入名人八字 Agent 的输出环节（一个名人分析自动转换成 Medium 长文）。

---

### 6. `katelyn-mma-strategy/`

**做什么**：MMA 垂直完整策略 — 创始人 credibility / 200 万用户 0 竞品 / UFC 赛前 2-3 天发布节奏 / 不预测单场比赛 / UFC Freedom 250（2026-06-14）大爆发窗口 / Fighter career arc 分析框架。

**为什么从 Katelyn 移出**：这是"分发策略"层面的内容，不是 Katelyn 养号的"单条回复" 层面。

**未来给谁**：未来名人八字 Agent + Distribution Intel Agent 共用。MMA 是 Likely You 的核心垂直之一。

---

## 怎么恢复一个 skill

如果未来要给某个新 agent 用：

```bash
# 假设新 agent 的 workspace 是 /home/xzwz778/.openclaw/workspace-bazidemo
cp -r "drafts/katelyn-archive/katelyn-topic-radar" /home/xzwz778/.openclaw/workspace-bazidemo/skills/
# 然后改 skill 名字（避免 katelyn- 前缀），改 description 适配新 agent
```

**注意**：恢复时要重新审视 description，因为这些 skill 的 description 是写给 Katelyn 用的（"Load when Katelyn is..."）。给新 agent 用时要改成新 agent 的角色描述。

---

## Katelyn 现在保留的 skills

- katelyn-farm-ops（养号清单）
- katelyn-reflection（v2 — 自动 Reddit username 追踪 + karma 反思）
- katelyn-brand-voice
- katelyn-scoring-formulas
- katelyn-reddit-playbook
- katelyn-product-context
- katelyn-goals
- katelyn-decisions
- 第三方：reddit / bird / workspace-meta

---

## 相关文档

- 主架构教训：`../openclaw 经验.md`
- Katelyn 当前 plan：`C:\Users\32247\.claude\plans\dazzling-popping-pascal.md`
