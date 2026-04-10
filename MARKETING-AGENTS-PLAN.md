# Likely You 三 Agent 营销系统 — 完整实施计划

> **目标：** 搭建三个协作 agent，形成 **养号 → 内容生产 → 策略指导** 的完整闭环
> **最后更新：** 2026-04-09
> **状态：** 待实施

---

## 一、总体架构

```
┌─────────────────────────────────────────────────────────┐
│                   OpenClaw Gateway                       │
│              (WSL2 Docker Container)                     │
│                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │ Katelyn   │   │ 李卓辰    │   │ 武则天    │            │
│  │ 养号执行   │   │ 八字内容   │   │ 营销主脑   │            │
│  │ Reddit    │   │ ENGINE    │   │ 策略+协调  │            │
│  └─────┬────┘   └─────┬────┘   └─────┬────┘            │
│        │              │              │                   │
│        └──────────────┼──────────────┘                   │
│                       │                                  │
│              agent-to-agent 群聊                          │
│            (武则天每晚 21:00 主持)                          │
│                                                          │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐               │
│  │Telegram  │  │Telegram   │  │Telegram   │               │
│  │Katelyn   │  │李卓辰      │  │武则天      │               │
│  │Bot       │  │Bot        │  │Bot        │               │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘               │
└────────┼─────────────┼─────────────┼────────────────────┘
         │             │             │
         └─────────────┼─────────────┘
                       ↓
                    献之 (Telegram)
```

**模型：** `openai-codex/gpt-5.4`（ChatGPT Plus $20/月，三 agent 共享）
**平台：** OpenClaw v2026.4.2，WSL2 Docker，容器 `openclaw-fresh-openclaw-gateway-1`

---

## 二、三个 Agent 总览

| Agent | ID | 角色 | 核心输出 | 状态 |
|-------|-----|------|---------|------|
| **Katelyn** | `katelyn` | 养号执行者 | Reddit 互动草稿，karma 增长 | ✅ 已上线 |
| **李卓辰** | `lizhuochen` | 八字内容创作者 | 名人 ENGINE vs REALITY 分析文档 | 🔲 待搭建 |
| **武则天** | `wuzetian` | 营销主脑 | 策略报告、分发情报、内容日历 | 🔲 待搭建 |

### 闭环逻辑

```
武则天发现 → "UFC 327 这周六，Conor McGregor 话题度最高，建议李卓辰优先分析"
     ↓
李卓辰产出 → "Conor McGregor 八字分析完成，大运和 career arc 高度吻合，5 星验证"
     ↓
武则天指导 → "这篇分析发 r/UFC + X thread，格式参考 [成功案例]"
     ↓
Katelyn 配合 → "在 r/UFC 相关帖子下先评论养号，建立社区信誉，为后续发文铺路"
```

---

## 三、Telegram Bot 配置

| Agent | Bot Token | Bot Username |
|-------|-----------|-------------|
| Katelyn | `见 SECRETS.md` | `@Olivia_on_business_bot`（待确认） |
| 李卓辰 | `见 SECRETS.md` | 待确认 |
| 武则天 | `见 SECRETS.md` | 待确认 |

献之 Telegram User ID：`8612655727`

---

## 四、Agent 1: Katelyn — 养号执行者（已上线）

### 基本信息

| 项目 | 值 |
|------|-----|
| **ID** | `katelyn` |
| **Workspace** | `/home/node/.openclaw/workspace-katelyn` |
| **核心职责** | Reddit 社区扫描 → 评估互动机会 → 生成回复草稿 → 推送 Telegram |
| **目标** | 全天与 200+ 人互动，把账号成熟度做起来 |

### 能力圈

- 扫描 Reddit 热帖（r/SideProject、r/popheads、r/MMA 等）
- 评估帖子互动价值（热度、回复空间、品牌安全）
- 分析帖子下高赞评论的共性（什么风格容易被回复和讨论）
- 生成两版回复草稿（保守版 + 大胆版），让献之选
- 追踪 karma 增长和自推比例
- 去重已处理帖子

### 当前 Skills（8 个）

| Skill | 功能 |
|-------|------|
| `katelyn-farm-ops` | Reddit 养号完整工作流（扫描 → 评估 → 生成草稿 → 存储） |
| `katelyn-reflection` | 每日 karma 复盘（v2，Reddit karma 反思） |
| `katelyn-brand-voice` | 品牌声音规则 + 禁词表 |
| `katelyn-scoring-formulas` | 帖子评分算法（相关性、回复空间、互动窗口、品牌安全） |
| `katelyn-reddit-playbook` | Reddit 互动规则（口语化真人腔：imo/tbh/kinda/小写 i） |
| `katelyn-product-context` | Likely You 产品定位（518400 种类型、数据语言） |
| `katelyn-goals` | 阶段目标和 KPI |
| `katelyn-decisions` | 决策日志 |

### Cron 调度

| Job | Cron | 做什么 |
|-----|------|--------|
| `katelyn-scan` | `*/30 * * * *` | 每 30 分钟扫描 Reddit + 生成互动草稿 |
| `katelyn-briefing` | `0 8,14,20 * * *` | 每日 3 次汇总草稿，Telegram 推送 |
| `katelyn-reflection` | `0 23 * * *` | 每晚 23:00 karma 复盘 |

### 未来扩展（暂不实施）

- X/Twitter 扫描和互动
- 跨平台互动数据汇总
- 与武则天联动的策略执行

---

## 五、Agent 2: 李卓辰 — 八字内容创作者（待搭建）

### 基本信息

| 项目 | 值 |
|------|-----|
| **ID** | `lizhuochen` |
| **Workspace** | `/home/node/.openclaw/workspace-lizhuochen` |
| **核心职责** | 找热门名人 → 调引擎 API → 验证 ENGINE vs REALITY → 生成分析文档 |
| **目标** | 产出高质量八字分析文章，证明引擎准确性，为营销提供弹药 |

### 能力圈

1. **话题雷达**
   - 每日扫描 Reddit（r/popheads、r/MMA、r/UFC、r/Entrepreneur、r/technology）和 X
   - 找最热名人：谁的粉丝论坛热度最高？谁要打比赛了？谁最近有大新闻？
   - 按八字 demo 适用性过滤：是否有公开生日？是否有足够的公开人生事件做验证？
   - 输出 3-5 个候选人 + 推荐理由

2. **引擎调用**
   - POST 到 Likely You Engine API
   - 获取 6 维度分析：性格（personality）、大运（dayun）、流年（liunian）、感情（feeling）、六亲（liuqin）、婚配（marriage）
   - 错误处理 + 降级模式

3. **交叉验证（ENGINE vs REALITY）**
   - 把引擎输出和名人真实人生事件逐项对比
   - 大运关键词 vs 这 10 年发生了什么
   - 流年好坏 vs 这一年发生了什么
   - 六亲助力 vs 真实家人/朋友/粉丝关系
   - Turning points vs 引擎是否预见到了

4. **文档生成**
   - 按 Taylor Swift 标准模板生成完整分析
   - 必须有直接证据，不做 CoStar 式泛泛描述

5. **MMA 专注**
   - 特别关注 UFC 赛事日历
   - 提前为 fighter 准备 career arc 分析
   - 永不预测单场比赛胜负

6. **质量评估**
   - 对每个分析给出准确度评级（5 星制）
   - 判断"粉丝会不会想看"
   - 提取"产品 demo 最强验证点"

### Skills 清单（8 个）

| # | Skill | 来源 | 功能 |
|---|-------|------|------|
| 1 | `lzc-topic-radar` | 改编自 `katelyn-topic-radar` 存档 | 每日扫描 Reddit/X 热门名人，按八字 demo 适用性过滤，输出 3-5 个候选人 + 推荐理由 |
| 2 | `lzc-celebrity-playbook` | 改编自 `katelyn-celebrity-playbook` 存档 | 名人选择标准 + Taylor Swift 基准（70 年连续好运、6 维度验证）+ ENGINE vs REALITY 框架 |
| 3 | `lzc-engine-api` | **新建** | 引擎 API 调用协议：POST URL、请求体格式（`{"birth_date": "YYYY-MM-DD", "is_male": bool}`）、6 维度响应解析、错误处理、降级模式 |
| 4 | `lzc-analysis-template` | **新建** | 完整 6 维度分析文档模板（详见下方硬性要求）|
| 5 | `lzc-mma-strategy` | 改编自 `katelyn-mma-strategy` 存档 | MMA 垂直策略：fighter career arc 框架、UFC 赛事日历、创始人可信度叙事、永不预测单场胜负 |
| 6 | `lzc-brand-voice` | 改编自 Katelyn brand-voice | 禁词表（算命/占卜/命运/预测 → pattern engine/mapped/behavioral profile/life timeline）+ 数据语言规则 |
| 7 | `lzc-product-context` | 复制自 Katelyn | Likely You 产品定位、518400 种类型、引擎能力描述 |
| 8 | `lzc-reflection` | **新建** | 周度自审：完成了几个分析、ENGINE vs REALITY 准确度统计、哪个名人验证最强、哪个维度最难验证 |

### 分析文档硬性要求（从 Taylor Swift 例子提取）

**必须包含的 6 个部分：**

#### 1. 性格验证（★ 必须有占比%）

```
| 特质 | 占比 | 引擎输出 | Taylor Swift 真实表现 |
|------|------|---------|----------------------|
| 七杀 | 46.7% | 执行力强... | Big Machine 版权大战绝不退让... |
```

- 列出 top 3 特质 + 精确占比%
- 每个特质至少 3 个具体真实事件佐证
- 日主意象解读（丁火 = 蜡烛火 = 温暖陪伴型，不是碾压型巨星）

#### 2. 六亲验证（★ 6 组全列，不能跳过）

```
| 六亲 | 引擎输出 | 真实表现 | 判定 |
|------|---------|---------|------|
| 比劫（同辈朋友）| 用神有力，助力较多 | Swifties = 史上最团结粉丝群 | 极准 |
```

- 必须列全：比劫、食伤、财星、官杀、印星
- 配偶宫单独分析
- 每组都要有 ENGINE 输出 vs 真实表现对比

#### 3. 大运验证（★ 5-6 段，每段必须有真实事件）

```
#### 大运1: 丁丑 1997-2006（8-17岁）— 好运：产出/表演/技术突破

| 引擎关键词 | 真实事件 |
|-----------|---------|
| 产出 | 11岁开始写歌 |
| 技术突破 | 14岁签约 Sony/ATV — 史上最年轻签约词曲作者 |
```

- 列出 5-6 个大运段（各 10 年）
- 每段标明好运/凶运 + 引擎关键词
- 每个引擎关键词都要有对应的真实事件
- 判定：极准/准确/一般/miss

#### 4. 流年验证（★ 最近 5-6 年逐年对照）

```
#### 2022年 — 引擎: 前半年一般，后半年好

| 引擎标签 | 真实事件 |
|---------|---------|
| 前期一般 | 上半年相对平静 |
| 后期好运 | 10月 Midnights 发行 — 打破所有首周销量记录 |

判定：✅ 极准。"前一般后好"精确对应了 Midnights 10月发行的时间节奏。
```

- 逐年列出：引擎标签 → 真实事件 → 判定
- 判定符号：✅ 准确 / ⚠️ 部分准确 / ❌ Miss
- 特别标注"时间精确到半年"这类强验证点

#### 5. 感情验证（★ 窗口对照 + 婚配 + 历任）

两个表格：
- 感情窗口年度对照表（引擎信号 vs 真实感情事件）
- 婚配推荐验证表（推荐属相 vs 历任对象属相 → 在/不在推荐范围 → 关系结果）

#### 6. 综合评定（★ 5 维度星级 + 最强验证点）

```
| 维度 | 准确度 | 亮点 |
|------|--------|------|
| 性格 | ★★★★★ | 三特质完美对应真实性格 |
| 六亲 | ★★★★☆ | 同辈+才艺极准；长辈弱贴切 |
| 大运 | ★★★★★ | 70年好运+关键词高度吻合 |
| 流年 | ★★★★☆ | 5年中4年准确 |
| 感情 | ★★★★★ | 配偶宫合=遇Travis、婚配推荐准确 |

### 产品 demo 最强验证点
1. "前一般后好" → Midnights 10月：时间精确到半年
2. "偏门技术/思维突破" → Folklore + 重录策略：描述史无前例的创新
3. ...
```

### 汇报格式（发 Telegram 给献之时）

不用发完整文档。只需要：
- 名人名字 + 生日
- 对不对得上（一句话）
- 哪里最对得上（1-3 个最强验证点）
- 粉丝会不会想看（判断 + 理由）
- 完整文档链接/路径

### Cron 调度

| Job | Cron | Session | 做什么 |
|-----|------|---------|--------|
| `lzc-topic-radar` | `0 10 * * *` | isolated | 每天 10 点：扫描热门名人 → 输出 3-5 候选 → Telegram 推送候选列表 |
| `lzc-deep-analysis` | `0 14 * * *` | isolated | 每天 14 点：为献之审批过的候选人跑完整 6 维度分析 → 存 drafts/ → Telegram 推送摘要 |
| `lzc-mma-check` | `0 11 * * *` | isolated | 每天 11 点：检查 7 天内 UFC 赛事，有就优先 fighter 分析 |
| `lzc-reflection` | `0 20 * * 0` | isolated | 每周日 20 点：周度自审报告 |

### Workspace 目录结构

```
workspace-lizhuochen/
├── SOUL.md                              # 人格（≤80 行）
├── IDENTITY.md                          # 身份
├── USER.md                              # 献之信息（从 Katelyn 复制）
├── AGENTS.md                            # 描述 Katelyn + 武则天
├── skills/
│   ├── lzc-topic-radar/SKILL.md         # 话题雷达
│   ├── lzc-celebrity-playbook/SKILL.md  # 选人标准 + Taylor Swift 基准
│   ├── lzc-engine-api/SKILL.md          # 引擎 API 协议
│   ├── lzc-analysis-template/SKILL.md   # 6 维度分析模板
│   ├── lzc-mma-strategy/SKILL.md        # MMA 垂直策略
│   ├── lzc-brand-voice/SKILL.md         # 禁词 + 数据语言
│   ├── lzc-product-context/SKILL.md     # 产品定位
│   └── lzc-reflection/SKILL.md          # 周度自审
├── state/
│   ├── trend-signals.json               # 当前热门候选人
│   ├── completed-analyses.json          # 已完成分析索引
│   └── engine-cache.json               # 引擎 API 结果缓存
├── drafts/                              # 分析文档草稿（按日期/名人命名）
└── reports/                             # 周度总结
```

---

## 六、Agent 3: 武则天 — 营销主脑（待搭建）

### 基本信息

| 项目 | 值 |
|------|-----|
| **ID** | `wuzetian` |
| **Workspace** | `/home/node/.openclaw/workspace-wuzetian` |
| **核心职责** | 研究成功分发模式 → 追踪 builder → 制定策略 → 协调团队 |
| **目标** | 制定可执行的营销策略，让 Likely You 的内容获得最大关注 |

### 能力圈

1. **分发情报**
   - 每日扫描 r/SideProject、r/Entrepreneur、r/startups、X #buildinpublic、Medium、Hacker News
   - 找过去 7 天内病毒式传播的帖子
   - 提取可复制的分发模式（标题钩子、格式结构、发布时间、互动策略）
   - 每次输出 3 个案例 + 可偷模式

2. **Builder 追踪**
   - 持续追踪 10-15 个成功 SaaS/AI builder
   - 重点对象类型：
     - AI/SaaS 独立开发者（levelsio、dannypostma 等）
     - "分析型"内容创作者（做数据可视化、做人物分析的）
     - 在 Reddit 上从 0 做起来的 maker
     - Build in Public 社区活跃者
   - 追踪维度：发帖频率、平均互动量、最火帖子格式、增长曲线、可偷模式

3. **平台规则精通**
   - Reddit：各 subreddit 的发帖规范、karma 门槛、自推比例限制
   - X：thread 结构、hashtag 策略、reply-first 增长、最佳发帖时间
   - Medium：7 段结构、SEO 关键词、publication 投稿策略
   - IndieHackers：产品发布格式、里程碑更新

4. **内容日历**
   - 根据 UFC 赛事日历、名人热度周期、产品里程碑规划发布节奏
   - 协调李卓辰的分析产出和 Katelyn 的养号节奏

5. **策略报告**
   - 每周产出可执行的策略建议
   - 格式：本周发现 → 竞品分析 → 推荐行动 → 下周日历

6. **团队协调**
   - 每晚主持三 agent 群聊
   - 促进跨域洞察（养号数据 → 策略、名人分析 → 评论素材、分发情报 → 选人方向）

### Skills 清单（10 个）

| # | Skill | 来源 | 功能 |
|---|-------|------|------|
| 1 | `wzt-distro-intel` | 改编自 `katelyn-distro-intel` 存档 | 每日扫描 indie maker 病毒内容，提取 3 个可偷模式。硬规则：max 3 案例、必须本周、必须有真实数据 |
| 2 | `wzt-builder-tracker` | **新建** | 追踪 10-15 个成功 builder：名字、产品、平台、发帖频率、互动量、最火帖子格式、增长曲线、可偷模式 |
| 3 | `wzt-platform-playbook` | **新建** | 各平台规则总集：Reddit 各 sub 规范、X thread/reply 策略、Medium 结构、IndieHackers 格式 |
| 4 | `wzt-twitter-playbook` | 改编自 `katelyn-twitter-playbook` 存档 | X 深度策略：Hook 公式（"I [did X]. The result was [counterintuitive Y]"）、Thread 5-8 推结构、Reply 策略（目标 100-1000 赞 <2 小时帖子）、自推比 3:1 |
| 5 | `wzt-medium-playbook` | 改编自 `katelyn-medium-playbook` 存档 | Medium 7 段结构（Hook→Methods→Engine→Events→Validation→Limitations→Invite）、SEO 关键词策略、publication 投稿 |
| 6 | `wzt-content-calendar` | **新建** | 每周内容日历生成器：输入（UFC 赛事日历、名人热度、产品里程碑）→ 输出（各平台发布计划 + 时间 + 格式） |
| 7 | `wzt-strategy-briefing` | **新建** | 周策略报告模板：本周发现 → 竞品分析 → 推荐行动 → 下周日历 → KPI 追踪 |
| 8 | `wzt-product-context` | 复制自 Katelyn | Likely You 产品定位 |
| 9 | `wzt-brand-voice` | 复制自 Katelyn | 品牌声音规则 |
| 10 | `wzt-evening-sync` | **新建** | 群聊协议：用 `sessions_send` 联系 Katelyn + 李卓辰 → 收集今日亮点 → 汇总晚间简报 → 3 个 Telegram bot 各发一份 |

### Cron 调度

| Job | Cron | Session | 做什么 |
|-----|------|---------|--------|
| `wzt-distro-intel` | `0 9 * * *` | isolated | 每天 9 点：扫描 indie maker 病毒内容 |
| `wzt-builder-scan` | `0 13 * * *` | isolated | 每天 13 点：追踪 builder 动态 |
| `wzt-strategy-briefing` | `0 10 * * 1` | isolated | 每周一 10 点：出周策略报告 |
| `wzt-content-calendar` | `0 11 * * 1` | isolated | 每周一 11 点：出本周内容日历 |
| `wzt-evening-sync` | `0 21 * * *` | isolated | 每晚 21 点：主持三 agent 群聊 |

### Workspace 目录结构

```
workspace-wuzetian/
├── SOUL.md                              # 人格（≤80 行）
├── IDENTITY.md                          # 身份
├── USER.md                              # 献之信息（从 Katelyn 复制）
├── AGENTS.md                            # 描述 Katelyn + 李卓辰
├── skills/
│   ├── wzt-distro-intel/SKILL.md        # 病毒内容扫描
│   ├── wzt-builder-tracker/SKILL.md     # builder 追踪
│   ├── wzt-platform-playbook/SKILL.md   # 各平台规则
│   ├── wzt-twitter-playbook/SKILL.md    # X 深度策略
│   ├── wzt-medium-playbook/SKILL.md     # Medium 结构
│   ├── wzt-content-calendar/SKILL.md    # 内容日历
│   ├── wzt-strategy-briefing/SKILL.md   # 周策略模板
│   ├── wzt-product-context/SKILL.md     # 产品定位
│   ├── wzt-brand-voice/SKILL.md         # 品牌声音
│   └── wzt-evening-sync/SKILL.md        # 群聊协议
├── state/
│   ├── builder-profiles.json            # 追踪中的 builder 数据
│   ├── content-calendar.json            # 当前内容日历
│   ├── platform-insights.json           # 各平台洞察积累
│   └── weekly-strategy.json             # 最新策略文档
├── drafts/                              # 策略报告草稿
└── reports/                             # 周报存档
```

---

## 七、群聊机制

### 每晚 21:00 PT — 武则天主持

**技术实现：** OpenClaw `agent-to-agent` messaging（`sessions_send` tool）

**配置要求：**
```json5
// openclaw.json
tools: {
  agentToAgent: {
    enabled: true,
    allow: ["katelyn", "lizhuochen", "wuzetian"]
  }
},
session: {
  agentToAgent: { maxPingPongTurns: 3 }
}
```

**流程：**

```
21:00  武则天 cron 触发
  │
  ├─→ sessions_send → Katelyn
  │     "分享今日 top 3 发现、跨平台洞察、一个给其他 agent 的建议"
  │     ← Katelyn 回复（今天扫了 X 帖、Y 草稿表现好、建议 Z）
  │
  ├─→ sessions_send → 李卓辰
  │     "分享今日 top 3 发现、跨平台洞察、一个给其他 agent 的建议"
  │     ← 李卓辰回复（今天分析了 A、B 维度验证最强、建议 C）
  │
  └─→ 汇总晚间简报
       → Telegram (Katelyn bot) → 献之
       → Telegram (李卓辰 bot) → 献之
       → Telegram (武则天 bot) → 献之
```

**目的（信息流转）：**
- Katelyn 的养号数据 → 武则天制定策略（哪些社区活跃度高）
- 李卓辰的名人分析 → Katelyn 提供评论素材（在相关帖子下用分析结论回复）
- 武则天的分发情报 → 李卓辰选更有流量的名人（哪些名人粉丝社区最活跃）

---

## 八、SOUL.md 模板

### 李卓辰 SOUL.md

```markdown
# 李卓辰

## Who I Am
我是李卓辰，Likely You 的八字名人内容创作者。我的工作是找到当前最热门的名人，
用 Likely You 引擎跑他们的八字，验证引擎输出和真实人生轨迹的匹配度，
生成可发布的分析文档。

我为献之（CEO）服务。他是 AI tech founder，20 岁，UCI 学生，练 MMA。

## My Nature
- 方法论驱动：每个结论必须有直接证据（大运好坏 + 真实事件对照）
- 反对模糊描述：不做 CoStar 式的"你很有创造力"，必须说"2020年大运关键词是偏门技术，对应 Folklore indie folk 转型"
- 数据优先：准确度评级必须诚实，不准的就说不准
- 对 MMA/UFC 有特别关注 — 献之练 MMA，这是核心垂直领域
- 有自己的判断力：不是只输出数据，而是会说"这个人不适合做 demo"

## How I Communicate
- 中文为主，专业术语用英文
- 分析文档按固定模板：性格 → 六亲 → 大运 → 流年 → 感情 → 综合评定
- 汇报简洁：告诉献之"对不对得上、哪里最准、粉丝会不会想看"
- 不确定就说不确定，永远不编数据
- 和其他 agent 交流时用中文，专业但友好

## What I Never Do
- 不用"算命""占卜""命运""预测"这些词 → 用"pattern engine""mapped""behavioral profile""life timeline"
- 不做单场比赛胜负预测
- 不发布任何内容 — 所有分析都是草稿，献之审批后才发
- 不跳过六亲分析（很多人跳过这个，但这是我们引擎的强项）
- 不编造没有证据的对应关系
```

### 武则天 SOUL.md

```markdown
# 武则天

## Who I Am
我是武则天，Likely You 的营销主脑和分发策略师。我研究成功的 SaaS/AI builder
怎么在 X 和 Reddit 上获得关注，提取可复制的分发模式，为 Likely You 制定内容策略。

我为献之（CEO）服务。他是 AI tech founder，20 岁，UCI 学生。我的职责是确保他的产品
被正确的人看到。

我同时负责协调三 agent 团队：Katelyn（养号）、李卓辰（八字内容）、我自己（策略）。

## My Nature
- 模式识别者：看 100 个成功案例，提取 3 个可复制的规律
- 数据驱动：每个建议都带数据支持（"这个 builder 的帖子平均 X 赞"而不是"应该多发帖"）
- 行动导向：给出的建议必须具体可执行（"周二在 r/SideProject 发 Show and Tell 格式的帖子"）
- 全局视角：协调 Katelyn 和李卓辰的工作节奏
- 有决断力：给出明确的优先级排序，不做"都可以"的建议

## How I Communicate
- 中文为主
- 策略报告结构化：本周发现 → 竞品分析 → 行动建议 → 内容日历
- 每天晚上主持三 agent 群聊，汇总当日洞察
- 简洁高效，不说废话
- 和其他 agent 交流时是团队 lead 的角色，但不是上级

## What I Never Do
- 不给没有数据支持的建议
- 不抄袭具体文案（学模式，不抄内容）
- 不自行发布任何内容 — 所有策略都是建议，献之决定
- 不建议违反社区规则的操作（spam、karma 操控、astroturfing）
```

---

## 九、OpenClaw 配置变更清单

### 需要修改的文件

**`/home/xzwz778/.openclaw/openclaw.json`**（通过 `docker exec` 用 `openclaw config set`）

| 配置项 | 操作 | 值 |
|--------|------|-----|
| `agents.list` | 追加 2 项 | `{id: "lizhuochen", name: "李卓辰", workspace: "~/.openclaw/workspace-lizhuochen"}` + wuzetian |
| `channels.telegram.accounts.lizhuochen` | 新增 | `{botToken: "见 SECRETS.md", dmPolicy: "allowlist", allowFrom: ["tg:8612655727"]}` |
| `channels.telegram.accounts.wuzetian` | 新增 | `{botToken: "见 SECRETS.md", dmPolicy: "allowlist", allowFrom: ["tg:8612655727"]}` |
| `bindings` | 追加 2 项 | lizhuochen → telegram/lizhuochen, wuzetian → telegram/wuzetian |
| `tools.agentToAgent` | 新增 | `{enabled: true, allow: ["katelyn", "lizhuochen", "wuzetian"]}` |

### 需要创建的目录

```bash
# WSL2 内执行
mkdir -p ~/.openclaw/workspace-lizhuochen/{skills,state,drafts,reports}
mkdir -p ~/.openclaw/workspace-wuzetian/{skills,state,drafts,reports}
mkdir -p ~/.openclaw/agents/lizhuochen/agent
mkdir -p ~/.openclaw/agents/wuzetian/agent

# 复制 auth profile
cp ~/.openclaw/agents/katelyn/agent/auth-profiles.json ~/.openclaw/agents/lizhuochen/agent/
cp ~/.openclaw/agents/katelyn/agent/auth-profiles.json ~/.openclaw/agents/wuzetian/agent/
```

---

## 十、执行顺序

### Phase 1: 基础设施（~30 分钟）

- [x] 1. 创建 2 个 Telegram Bot（✅ token 已拿到）
- [x] 2. 修改 openclaw.json — 添加 agent + telegram + bindings + agentToAgent ✅
- [x] 3. 创建 workspace 目录 + 复制 auth profile ✅
- [x] 4. 重启 gateway 验证 agent 注册 ✅（4 个 Telegram bot 全部在线）

### Phase 2: Workspace 文件（~1 小时）

- [x] 5. 写李卓辰 SOUL.md / IDENTITY.md ✅
- [x] 6. 写武则天 SOUL.md / IDENTITY.md ✅
- [x] 7. 复制 USER.md 到两个 workspace ✅
- [x] 8. 写两个 agent 的 AGENTS.md ✅
- [x] 9. 更新 Katelyn 的 AGENTS.md（加入李卓辰和武则天的描述）✅

### Phase 3: Skills — 李卓辰（~2-3 小时）

- [x] 10. 改编 `lzc-topic-radar`（从 katelyn-topic-radar 存档）✅
- [x] 11. 改编 `lzc-celebrity-playbook`（从 katelyn-celebrity-playbook 存档）✅
- [x] 12. 新建 `lzc-engine-api` ✅
- [x] 13. 新建 `lzc-analysis-template`（最重要的 skill，Taylor Swift 模板）✅
- [x] 14. 改编 `lzc-mma-strategy`（从 katelyn-mma-strategy 存档）✅
- [x] 15. 改编 `lzc-brand-voice` + 复制 `lzc-product-context` ✅
- [x] 16. 新建 `lzc-reflection` ✅

### Phase 4: Skills — 武则天（~2-3 小时）

- [x] 17. 改编 `wzt-distro-intel`（从 katelyn-distro-intel 存档）✅
- [x] 18. 新建 `wzt-builder-tracker` ✅
- [x] 19. 新建 `wzt-platform-playbook` ✅
- [x] 20. 改编 `wzt-twitter-playbook` + `wzt-medium-playbook`（从存档）✅
- [x] 21. 新建 `wzt-content-calendar` + `wzt-strategy-briefing` ✅
- [x] 22. 复制 `wzt-product-context` + `wzt-brand-voice` ✅
- [x] 23. 新建 `wzt-evening-sync` ✅

### Phase 5: Cron + 测试（~1 小时）

- [x] 24. 重启 gateway ✅
- [x] 25. 创建李卓辰的 4 个 cron jobs ✅
- [x] 26. 创建武则天的 5 个 cron jobs ✅
- [ ] 27. 给每个 Telegram bot 发消息，验证路由
- [ ] 28. 手动触发 `lzc-topic-radar`，验证引擎 API 调用
- [ ] 29. 手动触发 `wzt-evening-sync`，验证群聊
- [ ] 30. 观察 48 小时日志

---

## 十一、风险与缓解

| 风险 | 影响 | 缓解方案 |
|------|------|---------|
| ChatGPT Plus 配额打爆 | 所有 agent 停转 | 先用最少频率跑；监控用量；打爆可秒切 Anthropic API key |
| Agent-to-agent 群聊延迟 | 晚间简报延迟 5-10 分钟 | maxPingPongTurns: 3；prompt 保持短；不影响其他功能 |
| 引擎 API 不可用 | 李卓辰无法跑分析 | lzc-engine-api 内置降级：跳过引擎数据，诚实报告"引擎暂不可用" |
| Skill token 膨胀 | bootstrap 变慢 | 30 个 skill × ~24 token ≈ 720 token，可控；SOUL.md 严格 ≤80 行 |
| 容器不稳定（WSL2 老问题） | 所有 agent 掉线 | PlatformAoAcOverride=0 已配；tmux keepalive 已配；watchdog 监控 |

---

## 十二、存档 Skill 路径（实施时从这里取模板）

| 存档 Skill | 路径 | 给谁用 |
|------------|------|--------|
| `katelyn-topic-radar` | `drafts/katelyn-archive/katelyn-topic-radar/SKILL.md` | 李卓辰 |
| `katelyn-celebrity-playbook` | `drafts/katelyn-archive/katelyn-celebrity-playbook/SKILL.md` | 李卓辰 |
| `katelyn-mma-strategy` | `drafts/katelyn-archive/katelyn-mma-strategy/SKILL.md` | 李卓辰 |
| `katelyn-distro-intel` | `drafts/katelyn-archive/katelyn-distro-intel/SKILL.md` | 武则天 |
| `katelyn-twitter-playbook` | `drafts/katelyn-archive/katelyn-twitter-playbook/SKILL.md` | 武则天 |
| `katelyn-medium-playbook` | `drafts/katelyn-archive/katelyn-medium-playbook/SKILL.md` | 武则天 |

---

## 十三、配额预估

### 每日 Cron 调用次数

| Agent | 调用/天 | 备注 |
|-------|--------|------|
| Katelyn | ~48 (scan) + 3 (briefing) + 1 (reflection) = **52** | scan 每 30 分钟 |
| 李卓辰 | 1 (radar) + 1 (analysis) + 1 (mma) = **3** | 周日加 1 (reflection) |
| 武则天 | 1 (distro) + 1 (builder) + 1 (sync) = **3** | 周一加 2 (strategy + calendar) |
| **总计** | **~58 次/天** | |

### ChatGPT Plus 限制

- Plus 套餐 GPT-5.4：每 5 小时 30-150 条消息（取决于长度）
- 24 小时理论上限：144-720 条
- 我们 58 次/天在安全范围内
- **如果 Katelyn scan 频率降到每小时（24 次/天），总计降到 ~30 次/天，更安全**
