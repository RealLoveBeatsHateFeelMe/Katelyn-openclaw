# Katelyn — Likely You 分发 Agent 实施计划

## 当前状态

- [x] OpenClaw 多 agent 框架已搭好（`openclaw.json` 有 main + katelyn）
- [x] Katelyn Telegram Bot 已创建并启动（token: `见 SECRETS.md`）
- [x] Workspace 目录已建（`/home/xzwz778/.openclaw/workspace-katelyn/`）
- [x] 占位 SOUL.md / IDENTITY.md / USER.md / AGENTS.md 已写入
- [x] SOUL.md 已重写 — 完整人格 + 品牌声音规则 + 分发逻辑
- [x] 状态文件结构已建（config/ + state/ + drafts/ + reports/）

---

## 架构

全部走 OpenClaw Docker（WSL2 容器内），推送走 Telegram（Katelyn 自己的 bot）。

---

## 实施步骤

### Step 1: 重写 SOUL.md ✅

把 Olivia 的性格 + Katelyn 的全部工作逻辑写进 SOUL.md：
- Olivia 的性格基底（温暖、直接、有观点）
- Likely You 品牌声音规则（数据语言、禁词、自推比例）
- 扫描目标和评估维度
- 安全边界

**文件：** `/home/xzwz778/.openclaw/workspace-katelyn/SOUL.md`

---

### Step 2: 创建状态文件结构 ✅

在 workspace-katelyn 下建立持久化存储：

```
workspace-katelyn/
├── SOUL.md                    # 人格 + 品牌声音 + 工作逻辑
├── IDENTITY.md                # 身份
├── USER.md                    # 献之信息
├── AGENTS.md                  # agent 描述
├── config/
│   ├── scan-targets.md        # Phase 1 扫描目标 + 关键词（可调）
│   └── community-rules.md     # 每个社区的 karma 阈值、频率限制
├── state/
│   ├── processed-posts.json   # 已处理帖子 ID 去重
│   ├── promo-ratio.json       # value_count / promo_count
│   ├── community-status.json  # 每社区 karma、冷却状态、日/周计数
│   └── interaction-log.json   # 发布后的互动记录
├── drafts/
│   └── (每轮扫描生成的草稿，按日期命名)
└── reports/
    └── (月度复盘报告)
```

---

### Step 3: 创建 Cron Jobs ✅

通过 OpenClaw 内置 cron 设置定时任务：

| Job | Schedule | 做什么 |
|-----|----------|--------|
| `katelyn-scan` | 每 30 分钟 | 扫描社区 → 评估 → 写草稿 → 存入 drafts/ |
| `katelyn-briefing` | 每 6 小时 (`0 4,10,16,22 * * *`) | 汇总 drafts/ → 通过 Telegram 推送 briefing 给献之 |
| `katelyn-monthly` | 每月 1 号 (`0 10 1 * *`) | 读 interaction-log → 生成月度复盘 → Telegram 推送 |

**已验证：** OpenClaw cron 完全支持 `--agent katelyn`，三个 job 已创建并绑定到 katelyn agent。

---

### Step 4: 实现扫描逻辑

Katelyn 用 WebSearch 搜索各目标社区，按 scan-targets.md 的配置执行：

1. 读 `config/scan-targets.md` 获取当前 phase 的社区和关键词
2. 逐个社区执行 WebSearch
3. 对每个结果检查 `state/processed-posts.json` 去重
4. 用评估维度打分（相关性、回复空间、互动窗口、品牌安全）
5. 高分帖子调用 WebFetch 读全文 + 评论
6. 生成草稿，存入 `drafts/`
7. 更新 `state/processed-posts.json`

**已验证：** WebSearch（Brave）和 WebFetch 已内置并配置。Reddit 有 Cloudflare 拦截，需要 Reddit API 或浏览器自动化解决。

---

### Step 5: 实现草稿生成

草稿生成逻辑写进 SOUL.md 的 system prompt：
- 品牌声音规则（数据语言、禁词列表）
- 读 `state/promo-ratio.json` 判断是否允许提产品
- 读 `state/community-status.json` 检查 karma 阈值和频率限制
- 生成后自检：版主会不会当成广告？
- 标记 `value` 或 `promo`

---

### Step 6: 实现 Briefing 推送

每 6 小时通过 Telegram（Katelyn 自己的 bot）推送给献之：
1. 读 `drafts/` 里未推送的草稿
2. 读 `state/promo-ratio.json` 获取当前比例
3. 格式化为 briefing 报告（扫描统计 + 草稿列表 + 跳过列表）
4. 通过 Telegram 发给献之
5. 标记已推送的草稿

---

### Step 7: 内容适配器（手动触发）

献之在 Telegram 对 Katelyn 说 "帮我把 Taylor Swift 分析转成三个平台格式" 时触发：
- 读输入的名人分析数据
- 输出 3 份草稿：X (280字)、Reddit (500-800字)、Medium (2000+字)
- 等献之审核

---

### Step 8: 互动记录 + 月度复盘

献之发布内容后通过 Telegram 告诉 Katelyn 效果：
- Katelyn 记录到 `state/interaction-log.json`
- 月底读全部记录生成复盘报告，通过 Telegram 推送

---

## 需要确认的问题

1. **OpenClaw cron 能力** — 容器内 Katelyn 能不能跑 cron？需要验证 `openclaw cron add` 是否支持指定 agent
2. **WebSearch/WebFetch** — OpenClaw agent 有没有这些内置工具？需不需要额外 skill/MCP？
3. **持久化** — workspace 文件在容器重启后保留（volume mount 已确认）

---

## 执行优先级

- ~~**Step 1-4**~~ ✅ 全部完成
- ~~**Reddit 阻塞**~~ ✅ 解决 — 用 `old.reddit.com/.json` 端点 + `web_fetch`，2026 年仍然可用
- ~~**端到端测试**~~ ✅ 通过 — Katelyn 成功扫描 3 社区 12 帖子，生成完整 briefing 报告
- **后面：** Step 5-8 逐步迭代（草稿生成 / briefing 推送 / 适配器 / 复盘）
