---
name: katelyn-mma-strategy
description: Load when Katelyn is handling any MMA/UFC-related post, fighter analysis, or preparing content for an upcoming UFC event. Contains fighter career arc analysis framework, prime/decline/comeback verification point library, upcoming UFC fights to track (including UFC Freedom 250 on 2026-06-14), never-predict-fight-outcome rule, and the MMA vertical cold-start plan. Read during topic-radar and farm-ops when MMA content is involved.
---

# MMA Strategy Playbook

> 从 `产品核心.md` 的 MMA 章节提炼。Katelyn 处理 MMA 相关帖子或生成 MMA 草稿时读这份。

---

## 为什么 MMA 是核心垂直

- **创始人 credibility** — 本人练 MMA 多年，圈内真实可信度
- **文化契合** — MMA 粉丝本身就用"巅峰期 / 低谷期"理解 fighter 生涯
- **零竞品** — 这个圈子没有"分析 fighter career arc"的 AI 产品
- **大社区** — r/MMA 200 万+用户，文化偏分析向，高质量长文能自然获得流量
- **转化路径双向**：
  1. 粉丝路径：看名人运势准了 → 自己测
  2. fighter / 训练者路径：自己也练的人看到同圈运势准了 → "我什么时候状态最好"

---

## 内容形式：Career Arc 故事

**本质是人物命运故事，不是格斗技术分析，也不是比赛预测。**

### 核心产出

每场重要 UFC 比赛前 **2-3 天**，发主赛两个 fighter 的人生时间线对比文章。

- 主体 = 个人 career arc 回顾（引擎输出 vs 真实战绩）
- 比赛只是展示背景
- 嵌入三张卡片（性格卡 + 流年卡 + 大运卡）

### 不做的事

- ❌ **不预测单场比赛结果** — 顶尖选手都是长期好运加持才打到 UFC，两个好运选手对决分不出赢
- ❌ 不做技术分析（grappling vs striking breakdown）
- ❌ 不做数据对比（takedown %, significant strikes）

### 做的事

- ✅ 个人人生弧线（巅峰期、低谷期、什么时候开始下滑、upcoming 选手什么时候爆发）
- ✅ Career 里程碑对照引擎输出
- ✅ 退役 / comeback / 伤病年份验证
- ✅ 感情 / 家庭事件（公开的那些）

---

## 冷启动节奏

| 阶段 | 时间 | 做什么 |
|------|------|--------|
| Week 1 | 本周 | 了解 r/MMA 规则和语言，在 r/AskReddit 等无关 sub 攒基础 karma |
| Week 2 | 下周起 | 在 r/MMA 开始评论（不推广） |
| Week 3+ | | 跟 UFC 赛程，每场比赛前发一篇双人对比 |
| 2026-06-14 | UFC Freedom 250 | **白宫战卡 = 大爆发窗口** |

---

## Katelyn 的 MMA 扫描任务

### 社区目标

- r/MMA（200 万+）
- r/UFC（1M+）
- X MMA 圈（@arielhelwani, @lukethomasnews, @bokamotoESPN 等）

### 关键词池

- Fighter 名字 + "career" / "prime" / "decline" / "washed" / "comeback"
- "UFC [Event Name]" / "UFC [Date]"
- "career arc" + fighter name
- "is [fighter] past their prime"
- "when did [fighter] peak"

### 扫描频率

- **每日**：r/MMA /new.json 和 /hot.json
- **每周**：X 上 MMA 圈热榜
- **赛前 5 天**：锁定主赛两位选手，深挖
- **赛前 48 小时**：触发 `katelyn-ufc-eve` cron 自动生成草稿

---

## UFC 赛程数据源

Katelyn 可以通过以下 URL（公开、无 Cloudflare 问题）获取 UFC 赛程：

1. **UFC 官网赛程 API**（如果存在公开端点）
2. **Sherdog** — `https://www.sherdog.com/events/upcoming`（fighter 历史数据）
3. **Tapology** — `https://www.tapology.com/fightcenter/promotions/1-ultimate-fighting-championship-ufc`
4. **Wikipedia** — `https://en.wikipedia.org/wiki/List_of_UFC_events`

**推荐：** Wikipedia 是最稳定的，Katelyn 用 `web_fetch` 可以直接读到下周 / 下月的赛程。

---

## Fighter Career Arc 分析框架

对每个 fighter，Katelyn 需要准备：

### 基础数据

- 出生日期（必须，用来跑引擎）
- 当前年龄
- Record (wins-losses)
- 成名战
- Champion years
- 败绩年份
- 退役 / comeback 时间

### ENGINE vs REALITY 对照（写文章时）

| 引擎输出 | Real Career Event |
|---------|-------------------|
| 大运 X (年龄 A-B): 关键词 | 具体 career 里程碑 |
| 流年 YYYY: 好 / 波折 / 凶 | 具体比赛结果 / 伤病 / 大事件 |
| 感情窗口 YYYY | 公开的结婚 / 离婚 / 分手 |

---

## 2026-06-14 UFC Freedom 250 专案

**这是 Phase 1 的大爆发窗口。**

### 倒计时

- 现在起（4 月） → 建立 r/MMA karma 基础
- 5 月初 → 卡片公布后锁定主赛两位选手
- 6 月 1 日 → 开始写两位选手的 career arc 深度文章
- 6 月 7 日（赛前 1 周）→ 发第一篇
- 6 月 12 日（赛前 48h）→ 发双人对比文章
- 6 月 14 日（赛后当天）→ 验证文章（如果引擎输出符合赛后事件）

### 目标产出

1. Medium 长文 × 2（每位选手一篇）
2. Medium 长文 × 1（双人对比）
3. r/MMA 讨论帖 × 1（双人对比浓缩版，不带链接）
4. X Thread × 1（最震撼的验证点）
5. Reddit r/UFC 讨论帖 × 1（延伸话题）

---

## 成功信号

- r/MMA 帖子 upvote > 100 → 进入社区视野
- 被 MMA 分析大号引用 → 圈内认可
- 有 fighter 本人回复 → 终极社会证明
- 文章被 ESPN / MMA Fighting / Sherdog 引用 → 破圈

---

## 禁区（特别注意）

- ❌ **不预测单场胜负** — "Engine says A will beat B" = 声望毁灭
- ❌ **不点评技术** — "He should use his jab more" = 圈外人语气
- ❌ **不黑 fighter** — 就算分析显示不好的年份，语气要中性
- ❌ **不用 "destiny" / "fated" 这些词** — MMA 文化不吃这套
- ❌ **不说 "bazi" / "astrology"** — 圈子对玄学反感度极高
