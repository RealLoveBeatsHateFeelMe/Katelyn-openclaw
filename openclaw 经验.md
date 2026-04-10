# OpenClaw 实战经验

> 记录在 OpenClaw v2026.4.2 上搭建 Katelyn 分发研究 agent 过程中学到的真实教训。所有结论都有 GitHub / 源码 / 文档证据，不是推论。
>
> 最后更新：2026-04-09

---

## 一、最重要的三条教训

### 1. 不要凭推论下结论。先去搜，再动手。

**教训**：OpenClaw 是新生态（2026 发布），Claude 的训练数据对它一无所知。每次我根据"这应该是这样"下结论，都出错。

**例子**：
- **错**：我以为 MiniMax M2.7 tool calling 能力弱 → 错。真相是 OpenClaw v2026.4.2 有 `stripMinimaxToolCallXml` bug（Issue #41839），把 MiniMax 的 XML tool call 格式剥掉但从不 dispatch
- **错**：我以为升级到 v2026.4.9 能修 → 错。PR #46405 还是 open，4.9 changelog 没有 MiniMax 修复
- **错**：我以为 `minimax-portal` OAuth 会绕过 bug → 错。源码显示 portal 和 API key 路径走同一个后端，都撞同一个 bug

**正确做法**：遇到问题先 `WebSearch` + `WebFetch` GitHub issues / 源码 / 社区讨论。验证事实再动手。

### 2. SOUL.md 必须极简。架构靠 skills，不靠堆文件。

**事实**（来自官方源码 + 文档）：
- **官方模板 SOUL.md = 45 行**（`docs/reference/templates/SOUL.md`）
- **社区标杆**（seedprod / thedaviddias）都是 40-100 行
- **硬上限**：`agents.defaults.bootstrapMaxChars: 20000`（每文件，超过截断）
- **关键原理**（`docs/concepts/system-prompt.md`）：*"All of these files are injected into the context window on every turn, which means they consume tokens. Keep them concise."*

**Katelyn v3 的错误**：
- SOUL.md 482 行（10 倍超标）
- BRAND-VOICE.md 277 + PRODUCT.md 197 + GOALS.md 100 + DECISIONS.md 67 + references/ 1254 行
- **总 workspace 2377 行** ≈ 60k-80k tokens 每轮 bootstrap
- 症状：LLM 请求超时、tool call 失败、输出质量下降

**Skills 的真相**（`docs/tools/skills.md`）：
- 每个 skill 在系统 prompt 里**只占 ~24 tokens**（name + description + location）
- Skill body **FREE**，只在 agent 决定 `read` 时才加载
- **证据**：`gh-issues` skill 是 865 行纯 markdown，零代码，运行时零成本
- Skill 可以是纯 markdown reference，不需要任何脚本

**正确做法**：
- SOUL.md ≤80 行，**只写人格**（Who I Am / My Nature / How I Communicate / Never Do）
- AGENTS.md ≤100 行，**高层工作流概述**（不含细节模板）
- 所有模板、示例、playbook、规则 → **塞进 `skills/<name>/SKILL.md`** 懒加载
- 每个 skill 的 `description` 必须写清楚**什么时候该读它**

### 3. Cron message 不要堆规则。让 agent 去读 skill。

**错误做法**（v4 的 farm-ops cron message）：

```
"生成 1 条养号清单。按 SOUL.md 情报线 1 的 v5 模板。工作流：(1) 读 state/processed-posts.json...(2) 读 config/community-rules.md 看 karma...(3) 挑出 1 条...(4) 输出格式严格按 SOUL.md v5：标题行 + 帖子元数据 + 英文回复代码块（**2-3 句口语化真人腔，不是 5 句完整论证**，带 imo/tbh/kinda/小写 i 等口语标记）..."
```

问题：
- message 500+ 字符
- 重复 skill 里已有的规则
- agent 凭记忆执行，格式容易跑偏

**正确做法**（v6）：

```
"运行 farm-ops 工作流。第一步：读 skill katelyn-farm-ops（这是权威模板，包含输出结构+真人腔规则+示例）。第二步：按 skill 说的做。严禁凭记忆写输出格式。"
```

message 短，明确说"去读 skill"。agent 每次都读 skill → 规则永远是最新的（改 skill 不用改 cron）。

---

## 二、关键配置陷阱

### 2.1 火山方舟（Volcengine）接入

**正确配置**：
- 环境变量名：**`VOLCANO_ENGINE_API_KEY`**（3 个单词，不是 `VOLCENGINE_API_KEY`）
- Provider ID：
  - `volcengine`（通用，`/api/v3` 端点，按量计费）
  - **`volcengine-plan`**（Coding Plan，`/api/coding/v3` 端点，走套餐额度）
- 模型 ID：`volcengine-plan/doubao-seed-code` / `volcengine-plan/ark-code-latest` / `volcengine-plan/kimi-k2.5` / `volcengine-plan/glm-4.7`
- API mode：`openai-completions`

**不要手写 `models.providers.volcengine-plan` 块** — OpenClaw 的 volcengine 插件会自动注册。只需要设置 `agents.defaults.model.primary` + env var。

**关键坑：`~/.openclaw/agents/<agent>/agent/models.json` 优先级高于 `openclaw.json`**

- 这是上游 OpenClaw 行为：agent 私有 `models.json` 会覆盖全局配置
- 如果你改了 `openclaw.json` 但不删 `models.json`，你的改动**不会生效**
- **必须做**：`rm ~/.openclaw/agents/main/agent/models.json ~/.openclaw/agents/<other-agent>/agent/models.json`（备份后删）
- OpenClaw 重启后会根据新的 `openclaw.json` 重新生成

### 2.2 Doubao-Seed-Code 的 thinking 模式

- Doubao 默认启用 thinking（reasoning_content + reasoning_tokens）
- **简单任务**：`agents.defaults.thinkingDefault: "off"` — 更快，够用
- **复杂推理**（topic-radar 的 ENGINE vs REALITY 对照）：`"medium"` 或 `"high"` — 质量更好但慢 2-3 倍
- **必须配合** `agents.defaults.timeoutSeconds: 600` — 默认 timeout 对深度 reasoning 不够

### 2.3 cron `timeoutSeconds` 和 LLM 超时是两层

- Cron 级别：`cron.timeoutSeconds`（payload 级别，默认 30）
- Agent 级别：`agents.defaults.timeoutSeconds`（默认 48 小时）
- LLM 请求级别：provider 自己的 HTTP timeout（约 60-100s per request）

**真相**：farm-ops 之前超时的原因是 **cron 预算 180s 太紧**，不是 LLM 或 context bomb。把 cron `timeoutSeconds` 提到 360s 就解决了。

**调试方法**：看 `/home/xzwz778/.openclaw/cron/runs/<job-id>.jsonl` 的 `durationMs` vs 预算，一眼看清是 cron 杀的还是 LLM 杀的。

### 2.4 `lightContext: true` cron flag

**官方 `docs/automation/cron-jobs.md` 第 253-257 行**：
```
lightContext: true → bootstrapContextMode: 'lightweight'
→ cron bootstrap context empty on purpose
```

对工具密集 agent 的意义：**每次 cron 跑时完全跳过 workspace 注入**。SOUL.md / AGENTS.md 都不注入，只留系统 prompt + cron message + tools list + skills list。

**要求**：
- `sessionTarget: "isolated"` +  `payload.kind: "agentTurn"`
- 不能用 main session cron
- cron message 必须自包含（因为没有 workspace 人格），所以要明确说"读 skill katelyn-X"

### 2.5 `docker exec` 和 env var

**坑**：`docker exec <c> sh -c "... $VAR"` 里的 `$VAR` 是**宿主机 shell 展开的**，不是容器内。

```bash
# 错：宿主机 $MINIMAX_API_KEY 通常为空，变成空字符串传进去
docker exec <c> sh -c "curl -H 'Authorization: Bearer $MINIMAX_API_KEY' ..."

# 对：单引号不展开，让容器内 shell 展开
docker exec <c> sh -c 'curl -H "Authorization: Bearer $MINIMAX_API_KEY" ..."
```

或者：
```bash
docker exec <c> printenv MINIMAX_API_KEY  # 直接读，最可靠
```

---

## 三、Bug 档案

### 3.1 MiniMax XML tool call bug（Issue #41839）

- **状态**：open，PR #46405 卡在 XML entity decoding + attribute ordering 两个 review 问题上
- **症状**：`read tool called without path: argsType=object`（工具参数是空对象）
- **根因**：`stripMinimaxToolCallXml()` 在 `src/agents/pi-embedded-utils.ts` 把 MiniMax 的 `<minimax:tool_call>` XML 剥掉但从不解析和 dispatch
- **影响版本**：2026.4.2（截至 2026-04-09 的所有 4.x 版本都受影响）
- **workaround**：换模型到 Doubao-Seed-Code / Anthropic Claude 等走标准 tool_use 的模型

### 3.2 Kimi tool calling 长期 regression

- **相关 issues**：#9413 #39603 #39882 #39907 #40552 #40787 #41297 #42481 #44549 #55942（10+ 个）
- **症状**：每个版本都会坏一次，社区 workaround 是"降级到 v2026.3.2"
- **结论**：**不要在 OpenClaw 上用 Kimi 跑工具密集 agent**

### 3.3 Browser tool 不在 allowlist 但还能调用

- **症状**：cron `toolsAllow: ["web_search","web_fetch","read","write"]`，但 `browser` 工具还是被调用了
- **可能**：allowlist 只过滤给 LLM 展示的 schema，不过滤实际执行
- **影响**：container 里没 Chromium 时 browser 工具每次失败 ~2 秒，不致命但浪费时间
- **workaround**：在 cron message 明确说"不要用 browser 工具，只用 web_fetch"

---

## 四、Workspace 架构的黄金准则

```
workspace-<agent>/
  # Always-injected (官方 bootstrap 列表)
  SOUL.md        ≤80 lines   纯人格（Who I Am / Nature / Communicate / Never Do）
  AGENTS.md      ≤100 lines  高层工作流概述 + 铁律 + skill 索引
  IDENTITY.md    ≤15 lines   名字 / emoji / 一句话角色
  USER.md        ≤25 lines   用户信息
  TOOLS.md       ≤50 lines   工具表面笔记
  HEARTBEAT.md   ≤20 lines   心跳 checklist

  # Lazy-loaded skills（~24 tokens/skill 成本）
  skills/
    <agent>-workflow-A/SKILL.md    # 情报线 A 的完整模板 + 示例 + 规则
    <agent>-workflow-B/SKILL.md    # 情报线 B
    <agent>-brand-voice/SKILL.md   # 品牌声音规则
    <agent>-playbook-1/SKILL.md    # 平台 playbook
    ...
```

**规则**：
1. 任何超过 100 行的内容 → **塞进 skill**
2. 任何"如果献之问 X 就做 Y"的模板 → **塞进 skill**
3. 任何好/坏示例对照 → **塞进 skill**
4. 任何 playbook / reference / 规则表 → **塞进 skill**
5. SOUL.md 只留"我是谁 + 怎么说话 + 绝不做什么"

**Skill description 的写法**：必须明确告诉 agent **什么时候该读它**：

```markdown
---
name: katelyn-farm-ops
description: Load at the start of every farm-ops cron run. This is the complete farm-ops workflow — how Katelyn picks 1 Reddit post per hour and generates a 2-3 sentence real-person-tone English reply. Contains the exact output template, the real-person vs AI-tone rules, the good/bad examples, and the hard rules. Read this skill BEFORE reading any other skill in farm-ops workflow.
---
```

description 里必须包含：
- **触发场景**（"at the start of every farm-ops cron run"）
- **内容清单**（"output template, real-person tone rules, examples"）
- **读取时机**（"BEFORE reading any other skill"）

---

## 五、真人腔文本生成

**教训**：LLM 默认写"AI 腔" — 完整论证、句号收束、每句都在解释。**真人 Reddit 评论不是这样**。

**对照**：

❌ **AI 腔**（5 句完整论证）：
> Because fighting isn't a "technical" project in most people's heads — it's an identity project. Being bad at basketball is survivable, getting beat up in a fight feels like a verdict on who you are. That's why most people overrate themselves: they've never had real contact with trained people and don't know how much conditioning, distance, and pressure compound the gap. The "if I really went for it" fantasy only survives because it's never been tested.

✅ **真人腔**（2-3 句 + 口语标记）：
> tbh it's because getting beat in a fight feels personal in a way losing at basketball doesn't. most people have never actually gone hard with a trained person so the "if i really tried" fantasy never gets tested.

**规则**：
1. **最多 2-3 句**
2. **必须有口语标记**：`imo` / `tbh` / `kinda` / `yeah` / 破折号 `—` / 省略号 `...` / 小写 `i`
3. **观点明确**（不绕弯子）
4. **1-2 个因果**就够（不写完整论证链）
5. **可以有轻微逻辑残缺**（真人说话本来就不完美）
6. **至少 1 个具体数据点**（名字 / 数字 / 事件）
7. **禁止模板开头**（"Great question!" / "As someone who..."）
8. **禁止放 URL**

**Prompt 里必须有对照示例**：只给规则不够，要放一个错误例子 + 一个正确例子 + 解释为什么。

---

## 六、推送格式（Telegram）

**坑**：把整个 briefing 包进一个大代码块 → 链接不能点击

**正确结构**：
- **元数据是普通文本**（让 URL 被 Telegram 渲染成可点击链接）
- **只有需要用户复制的内容**（英文回复 / 代码片段）放代码块

示例（farm-ops）：

```
🌱 Farm-ops — 2026-04-09 14:00

1. Post title (普通文本)

🔗 https://old.reddit.com/r/MMA/... (可点击)

📍 r/MMA · karma 0 · 🟢

💡 问题型+74评论

(三反引号代码块开始)
tbh it's because... (可一键复制)
(三反引号代码块结束)
```

---

## 七、状态文件的用法

Katelyn 用的状态文件（`workspace-katelyn/state/`）：

| 文件 | 用途 | 写入者 |
|------|------|--------|
| `processed-posts.json` | 帖子去重 | scan cron |
| `rejection-summary.json` | 拒绝原因统计 | scan cron |
| `trend-signals.json` | 话题趋势 + watchlist | topic-radar cron |
| `engagement-history.json` | 发布效果反馈 | 献之手动上报后 Katelyn 写 |
| `promo-ratio.json` | 自推比例计数器 | 所有 intel crons |
| `community-status.json` | 各社区 karma + 冷却 | 献之手动更新 |
| `reflection-pending.json` | 元观察累积池 | scan cron 写，reflection cron 读并清空 |

**规则**：
- 所有状态是 JSON 文件（不要 sqlite / db，简单就好）
- 每次 cron 读必要的 state → 做决策 → 写回
- **不要在 SOUL.md 里暴露文件结构给用户**（不说 "state/X.json 里..."）

---

## 八、调试速查

### 看 cron 真实执行日志
```bash
sudo docker exec <container> cat /home/node/.openclaw/cron/runs/<job-id>.jsonl
```

### 看容器日志里的 agent 错误
```bash
sudo docker logs --tail 50 <container> 2>&1 | grep -iE 'error|timeout|failover'
```

### 看 skills 被识别了没
```bash
sudo docker exec <container> openclaw skills list | grep <prefix>
```

### 测 provider API 本身能不能通（绕过 agent 层）
```bash
sudo docker exec <container> bash -c 'curl -sS <provider-endpoint> -H "Authorization: Bearer $<KEY>" ...'
```

### 手动触发 cron（测试专用，不走 scheduler）
```bash
sudo docker exec <container> openclaw cron run <job-id>
```

**⚠️ 坑**：如果 `nextRunAtMs` 很远，手动 `cron run` 可能被 scheduler 合并或跳过。这种情况**直接用 `openclaw agent --agent <id> --message "..."`** 绕过 cron。

### 看当前 context 有什么文件（在 agent session 里）
```
/context list
/context detail
```

---

## 九、已验证可用的组合

截至 2026-04-09 我们 Katelyn 跑的是：

- **OpenClaw**：v2026.4.2（Docker `ghcr.io/openclaw/openclaw:latest`）
- **模型**：`volcengine-plan/doubao-seed-code`（火山方舟 Coding Plan，sk-cp- key）
- **Fallback**：`volcengine-plan/ark-code-latest`
- **Thinking**：`medium`
- **Timeout**：cron 360s，agents.defaults 600s
- **Workspace**：SOUL 65 行 + AGENTS 86 行 + 14 个 skills（`katelyn-*`）
- **Search**：Brave Search API
- **引擎 API**：Likely You `/v1/agent/profile`（Anthropic-style JSON）
- **Telegram**：独立 bot 每个 agent

**工作的能力**：
- ✅ farm-ops 养号清单（每小时 12:00-02:00）
- ✅ distro-intel 分发情报（每日）
- ✅ topic-radar 话题雷达（每日，含引擎 API 调用）
- ✅ reflection 策略感触（每日，空则沉默）
- ✅ Scan 底层扫描（每 30 分钟）

**不要做的**：
- ❌ 不要用 MiniMax M2.7（OpenClaw tool call bug）
- ❌ 不要用 Kimi K2.5（长期 regression）
- ❌ 不要把任何长内容放在 workspace 根目录
- ❌ 不要在 cron message 里堆规则
- ❌ 不要升级 OpenClaw 到未知新版本（v2026.3.24 Discord 崩溃是前车之鉴）

---

## 十、下次遇到问题的 checklist

1. **这是已知 bug 吗？** 先 WebSearch GitHub issues
2. **我的配置对吗？** 对照 `docs/providers/<provider>.md` 和 `extensions/<provider>/openclaw.plugin.json`
3. **env var 进容器了吗？** `docker exec <c> printenv <VAR>`
4. **直接 curl provider endpoint 能通吗？** 绕过 agent 层确认底层
5. **workspace 是不是太大？** `wc -l workspace-*/**.md`，>200 行就考虑搬 skill
6. **cron 预算够吗？** 看 `durationMs` vs `timeoutSeconds`
7. **skill description 写清了"什么时候读"吗？**
8. **SOUL.md 有没有堆规则？** 应该只有人格
9. **模型是不是走了 tool_use 路径？** MiniMax/Kimi 的 XML 格式有兼容问题
10. **有没有 agent-private `models.json` 覆盖？** 必须删

---

## 十一、有用的外部资源

- **官方 docs**: `C:\Users\32247\Desktop\openclaw\docs\` 本地源码
- **社区 SOUL.md 标杆**:
  - [seedprod/openclaw-prompts-and-skills](https://github.com/seedprod/openclaw-prompts-and-skills)
  - [thedaviddias/souls-directory](https://github.com/thedaviddias/souls-directory)
  - [mergisi/awesome-openclaw-agents](https://github.com/mergisi/awesome-openclaw-agents)
- **分发/营销 agent 标杆**:
  - [thomasbln/openclaw-marketing-agent](https://github.com/thomasbln/openclaw-marketing-agent)
  - [hesamsheikh/awesome-openclaw-usecases](https://github.com/hesamsheikh/awesome-openclaw-usecases)
- **Reddit 无 API 访问**:
  - [ajitesh-kuppa-sivakumar/reddit-openclaw](https://github.com/ajitesh-kuppa-sivakumar/reddit-openclaw)（注意路径要改成容器内路径）
- **性能警告**:
  - [dev.to: Why Your OpenClaw Agent Gets Slower and More Expensive Over Time](https://dev.to/studio1hq/why-your-openclaw-agent-gets-slower-and-more-expensive-over-time-5c5e)
  - [Medium: OpenClaw: The AI Agent That Burns Through Your API Budget](https://medium.com/@reza.ra/openclaw-the-ai-agent-that-burns-through-your-api-budget-and-how-to-fix-it-050fc57552c9)

---

## 更新记录

- **2026-04-09**：首次建立。Katelyn v3 → v6 重构过程的完整教训。
