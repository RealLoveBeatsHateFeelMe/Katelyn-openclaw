# Olivia 接入本地 Claude Code

## 背景

Olivia 原来运行在 WSL2 Docker 容器内的 OpenClaw gateway 中。要操控本地 Claude Code 写代码，经过调研有两条路：

1. **正向集成**：OpenClaw 容器内通过 HTTP bridge/SSH 调用宿主机的 `claude -p` — 三层网络调用，社区反馈可靠性差（session 3-10 分钟 SIGTERM、大输入空输出等）
2. **反向集成（采用）**：用 ClaudeClaw 插件把 OpenClaw 核心能力直接装进本地 Claude Code — 零基础设施，单进程运行

## 方案：ClaudeClaw 插件（反向集成）

**核心思路：不在 OpenClaw 里调用 CC，而是在 CC 里运行 OpenClaw 能力。**

```
之前：Discord → Docker(OpenClaw) → HTTP Bridge → WSL2 → claude -p → 写代码
现在：Discord → ClaudeClaw(本地 CC 插件) → 直接写代码
```

完全避免 OpenClaw 自身庞大的代码和 token 浪费。直接复用 Claude Code 的内存系统、CLAUDE.md、session 管理。

---

## 安装

```bash
# 添加 marketplace
claude plugin marketplace add moazbuilds/claudeclaw

# 安装插件
claude plugin install claudeclaw

# 验证
claude plugin list
# 应显示: claudeclaw@claudeclaw v1.0.0 enabled
```

## 启动与配置

在 Claude Code 会话中运行：

```
/claudeclaw:start
```

跟着向导配置：
- **模型**：Claude Sonnet 4.6（主力）+ GLM 兜底
- **Discord 通道**：复用现有 Clawdbot token（Application ID: `1465647492505931921`）
- **心跳间隔**：15 分钟（可选 5/15/30/60）
- **安静时段**：根据作息设置
- **安全级别**：moderate（项目目录内完全访问）

---

## 插件能力

| 功能 | 说明 |
|------|------|
| 后台 Daemon | PID 管理 + 状态跟踪，永不睡觉 |
| 定时心跳 | 可配间隔 + 安静时段 + 时区感知 |
| Cron 任务 | 完整 cron 表达式，`.claude/claudeclaw/jobs/*.md` |
| Telegram | 文字/图片/语音，Bot API 直连 |
| Discord | DM/服务器/slash 命令，WebSocket Gateway |
| Web Dashboard | `http://127.0.0.1:4632`，实时状态/聊天/设置 |
| 安全级别 | locked(只读) / strict(可编辑) / moderate(项目内完全) / unrestricted |
| 模型切换 | 主模型 + GLM 兜底，agentic 模式自动路由 |
| 语音转写 | whisper.cpp 或 OpenAI 兼容 API |
| 热重载 | 配置和 cron 每 30 秒自动重载，无需重启 |
| Session 共享 | 心跳/cron/Telegram/Discord 共享同一个 Claude session |

## 文件结构

```
.claude/claudeclaw/
├── settings.json      # 主配置（模型、心跳、telegram、discord、安全）
├── session.json       # 共享 Claude session ID
├── daemon.pid         # 进程 PID
├── state.json         # 运行状态（下次执行时间等）
├── jobs/              # Cron 任务定义 (*.md，带 frontmatter)
├── logs/              # 执行日志
│   └── daemon.log
└── prompts/           # 项目级 prompt 覆盖
```

## 可用命令

| 命令 | 用途 |
|------|------|
| `/claudeclaw:start` | 初始化并启动 daemon |
| `/claudeclaw:stop` | 停止 daemon |
| `/claudeclaw:status` | 查看状态和倒计时 |
| `/claudeclaw:config` | 查看/修改设置 |
| `/claudeclaw:jobs` | 管理 cron 任务（创建/列表/编辑/删除） |
| `/claudeclaw:logs` | 查看执行日志 |
| `/claudeclaw:clear` | 重置 session |
| `/claudeclaw:help` | 帮助 |

---

## 架构对比

| | 旧方案 (OpenClaw Docker) | 新方案 (ClaudeClaw) |
|---|---|---|
| 运行位置 | WSL2 Docker 容器 | Windows 本地 Claude Code |
| 代码访问 | 需要 bridge/挂载 | 直接本地文件系统 |
| Discord | OpenClaw gateway 转发 | 插件内置 WebSocket |
| 定时任务 | Windows Task Scheduler + /hooks/agent | 内置 cron + 心跳 |
| Session/Memory | OpenClaw 独立系统 | 复用 CC 的 session/CLAUDE.md |
| 资源占用 | Docker 容器常驻 (~200MB+) | CC 进程内运行 |
| 维护成本 | Docker/WSL2/网络三层 | 单进程，零基础设施 |
| 人格配置 | workspace/SOUL.md + IDENTITY.md | CLAUDE.md + prompts/ |
| 护眼提醒 | PowerShell + Task Scheduler | ClaudeClaw cron job |
| 深夜陪伴 | PowerShell + Task Scheduler | ClaudeClaw 心跳 |

---

## 两种操控 Claude Code 的底层方法（参考）

### 方法 1：CLI subprocess (`claude -p`)

```bash
claude -p "你的任务" --output-format json --permission-mode bypassPermissions
```

- 非交互式，返回 JSON 结果
- 适合一次性短任务、CI/CD
- 可用 `--session-id` 恢复会话
- 支持 `--allowedTools "Bash,Read,Edit"` 预批准工具
- 支持 `--append-system-prompt` 注入系统提示

### 方法 2：Claude Agent SDK

```python
# Python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="你的任务",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Bash"],
    ),
):
    # 处理流式事件
    pass
```

```typescript
// TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "你的任务",
  options: {
    allowedTools: ["Read", "Edit", "Bash"],
  },
})) {
  // 处理流式事件
}
```

- 进程内 async iterable
- 流式事件（text_delta, tool_call 等）
- 支持 programmatic hooks 拦截工具执行
- 更精细的权限控制

**ClaudeClaw 本质上用方法 1（内部调 `claude -p`），封装成完整的 daemon + 消息桥接。**

---

## 社区反馈：为什么不用正向集成

社区（GitHub issues、Reddit）对 `claude -p` 作为远程 daemon 的反馈：

- Session 3-10 分钟后 SIGTERM 死掉（[#29642](https://github.com/anthropics/claude-code/issues/29642)）
- 大输入 headless 模式返回空输出（[#7263](https://github.com/anthropics/claude-code/issues/7263)）
- 长时间异步流挂死
- 子进程僵尸、文件描述符泄漏
- CC 的权限系统为交互式人类设计，不适合无人值守 agent

**结论：CC 适合短任务一次性调用，不适合当永在线 daemon。ClaudeClaw 通过短任务循环 + 心跳机制绕过了这些限制。**

---

## 迁移清单

从 OpenClaw Docker 迁移到 ClaudeClaw 时需要处理：

- [ ] SOUL.md → CLAUDE.md 或 `.claude/claudeclaw/prompts/`
- [ ] HEARTBEAT.md 定时任务 → ClaudeClaw cron jobs
- [ ] 护眼提醒（EyeRestReminder）→ ClaudeClaw cron
- [ ] 深夜陪伴（NightCompanion）→ ClaudeClaw 心跳
- [ ] Discord Clawdbot token → ClaudeClaw Discord 配置
- [ ] Google OAuth（gog skill）→ 评估是否需要迁移
- [ ] Inner Life skills → 评估 ClaudeClaw 兼容性
- [ ] 旧 Docker 架构保留为备用

---

## 备用方案：HTTP Bridge（如果 ClaudeClaw 不满足需求）

如果需要保留 OpenClaw Docker 架构并让 Olivia 操控本地 CC：

1. WSL2 上运行 Node.js HTTP bridge（监听 18791 端口）
2. Docker 容器通过 `host.docker.internal` 访问
3. Bridge 接受 POST 请求，执行 `claude -p`，返回 JSON
4. 需要 systemd service + docker-compose extra_hosts 配置

详见 `.claude/plans/` 中的原始 bridge 方案。
