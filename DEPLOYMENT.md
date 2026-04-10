# OpenClaw 部署文档

## 架构概览

双轨架构：ClaudeClaw 插件（主力，本地编码）+ OpenClaw Docker（备用，消息/工具）。

### 主力架构：ClaudeClaw 插件（本地 Claude Code）

```
Windows 11 Host
└── Claude Code CLI (本地运行)
    └── ClaudeClaw 插件 v1.0.0
        └── Olivia (Claude Sonnet 4.6) — 编码 + Discord 消息
            ├── 内置 Discord WebSocket
            ├── 内置 Cron + 心跳
            └── 直接访问本地文件系统
```

详见 [CLAUDE-CODE-INTEGRATION.md](CLAUDE-CODE-INTEGRATION.md)。

### 备用架构：OpenClaw Docker（原方案）

单实例多 Agent 架构，运行在 WSL2 Ubuntu + Docker Compose 上。

```
Windows 11 Host
└── WSL2 Ubuntu 24.04
    └── Docker Engine 29.3.1
        └── openclaw-unified (1 container)
            └── Olivia  (Claude Sonnet 4.6) — 万能个人助手
```

---

## 连接信息

| 项目 | 值 |
|------|-----|
| Gateway WebSocket | `ws://localhost:18789` |
| Gateway HTTP | `http://localhost:18789` |
| Bridge | `http://localhost:18790` |
| Health Check | `http://localhost:18789/healthz` |
| Gateway Token | `见 SECRETS.md` |
| Dashboard URL | `http://localhost:18789/#token=见 SECRETS.md` |

---

## WSL2 环境

| 项目 | 值 |
|------|-----|
| OS | Ubuntu 24.04.3 LTS (Noble Numbat) |
| WSL2 用户 | `xzwz778` |
| Docker | 29.3.1 |
| Docker Compose | v5.1.1 |
| systemd | 已启用 |
| sudo | 免密码 (NOPASSWD) |

---

## 文件路径 (WSL2 侧)

```
/home/xzwz778/openclaw-unified/          # Docker Compose 项目目录
├── .env                                  # 环境变量 (Token, API Key, 端口等)
└── docker-compose.yml                    # Compose 配置 (从源项目复制)

/home/xzwz778/.openclaw-unified/          # OpenClaw 运行时配置
├── openclaw.json                         # 主配置 (agents, gateway, identity)
├── devices/
│   ├── paired.json                       # 已配对设备
│   └── pending.json                      # 待配对设备
├── workspace/                            # Agent 工作空间
├── canvas/                               # Canvas UI
└── logs/                                 # 日志

/home/xzwz778/openclaw/                   # 源项目 (部署用文件)
├── docker-compose.yml
├── .env.example
└── scripts/
```

Windows 侧源码:
```
C:\Users\32247\Desktop\openclaw\          # 完整源码 repo
```

---

## Agent 配置

| Agent | ID | 模型 | 角色 |
|-------|-----|------|------|
| Olivia | `main` | `anthropic/claude-sonnet-4-6` | 万能个人助手（日常/翻译/编程/写作） |

聊天中可用 `/model` 临时切换模型。

### Hooks 配置

| 项目 | 值 |
|------|-----|
| 状态 | 已启用 |
| Hooks Token | `见 SECRETS.md` |
| Wake 端点 | `POST http://localhost:18789/hooks/wake` |
| Agent 端点 | `POST http://localhost:18789/hooks/agent` |

**配置位置:** `openclaw.json` → `hooks`

### Inner Life Skills

Olivia 装有 [openclaw-inner-life](https://github.com/DKistenev/openclaw-inner-life) 全套 6 模块，提供情绪延续、自我反思和成长能力。

| 模块 | 功能 |
|------|------|
| `inner-life-core` | 6 种情绪 + 半衰期衰减 + 9 步 Brain Loop 协议 |
| `inner-life-reflect` | 自我反思，观察行为模式，更新 SELF.md |
| `inner-life-memory` | 记忆延续，带置信度评分和好奇心追踪 |
| `inner-life-dream` | 安静时段"做梦"，自由联想和创意探索 |
| `inner-life-chronicle` | 每日日记（基于对话、情绪状态、驱动写反思日记） |
| `inner-life-evolve` | 自我进化提案（需人工审批） |

**安装方式:** 从 GitHub 手动复制到容器 `/home/node/.openclaw/workspace/skills/`（ClawHub rate limit 严格）

**状态文件 (容器内 workspace/):**
- `memory/inner-state.json` — 6 种情绪状态
- `memory/drive.json` — 驱动/期待/回避
- `memory/habits.json` — 习惯和用户模式
- `memory/relationship.json` — 信任等级和教训
- `BRAIN.md` — 9 步 Brain Loop 协议
- `SELF.md` — 自我观察空间
- `memory/diary/` — 日记
- `memory/dreams/` — 梦境记录
- `memory/questions.md` — 好奇心积压
- `tasks/QUEUE.md` — 任务队列

---

## 定时提醒 (Windows 侧)

通过 Windows Task Scheduler + PowerShell 脚本实现，使用 Win32 `GetLastInputInfo` API 检测用户是否活跃。

### 护眼提醒 (EyeRestReminder)

| 项目 | 值 |
|------|-----|
| 脚本路径 | `C:\Users\32247\Scripts\EyeRestReminder.ps1` |
| 计划任务名 | `EyeRestReminder` |
| 间隔 | 每 20 分钟 |
| 空闲阈值 | 5 分钟 (空闲超过 5 分钟不提醒) |
| 时间范围 | 全天 |
| 投递方式 | `/hooks/agent` → Olivia → Discord DM |
| 模型 | `anthropic/claude-haiku-4-5` |

### 深夜陪伴 (NightCompanion)

| 项目 | 值 |
|------|-----|
| 脚本路径 | `C:\Users\32247\Scripts\NightCompanion.ps1` |
| 计划任务名 | `NightCompanion` |
| 间隔 | 每 30 分钟 |
| 空闲阈值 | 10 分钟 (深夜宽松) |
| 时间范围 | 0:00 - 6:00 (脚本内判断) |
| 投递方式 | `/hooks/agent` → Olivia → Discord DM |
| 模型 | `anthropic/claude-haiku-4-5` |
| 特殊逻辑 | 交替称呼"我的王"/"我的CEO"，关心+笑话/冷知识 |

### 管理命令

```powershell
# 查看任务状态
Get-ScheduledTask -TaskName "EyeRestReminder" | Get-ScheduledTaskInfo
Get-ScheduledTask -TaskName "NightCompanion" | Get-ScheduledTaskInfo

# 暂停/恢复
Disable-ScheduledTask -TaskName "EyeRestReminder"
Enable-ScheduledTask -TaskName "EyeRestReminder"

# 手动测试
powershell -File C:\Users\32247\Scripts\EyeRestReminder.ps1
powershell -File C:\Users\32247\Scripts\NightCompanion.ps1

# 删除任务
Unregister-ScheduledTask -TaskName "EyeRestReminder" -Confirm:$false
```

---

## 聊天渠道

### Discord

| 项目 | 值 |
|------|-----|
| Bot 名称 | Clawdbot (可在 Developer Portal 改名) |
| Application ID | `1465647492505931921` |
| Discord 用户 | `xianzhi778` (ID: `1420636197604167783`) |
| DM 模式 | `open` (任何人可 DM) |
| 服务器模式 | `allowlist` — 只有 xianzhi778 说话时回复，无需 @mention |
| OAuth2 URL | `https://discord.com/oauth2/authorize?client_id=1465647492505931921&permissions=8&integration_type=0&scope=applications.commands+bot` |

**必须开启的 Intent:** Discord Developer Portal → Bot → Privileged Gateway Intents → **Message Content Intent**

**配置位置:** `openclaw.json` → `channels.discord`

### Telegram

尚未接入。接入时需要：
1. @BotFather 创建 Bot → 拿 Token
2. `.env` 添加 `TELEGRAM_BOT_TOKEN`
3. `docker-compose.yml` environment 添加 `TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:-}`
4. `openclaw.json` 添加 `channels.telegram` 配置

---

## Google OAuth 凭据 (gog skill)

### 学校邮箱通道 (xianzhh2@uci.edu)
| 项目 | 值 |
|------|-----|
| 用途 | 个人/学校邮件管理 |
| 客户端 ID | 见 SECRETS.md |
| 客户端密钥 | 见 SECRETS.md |
| 创建日期 | 2026-03-26 |

### 产品通道 (Likely You 对外)
| 项目 | 值 |
|------|-----|
| 用途 | 产品相关邮件、对外沟通 |
| 客户端 ID | 见 SECRETS.md |
| 客户端密钥 | 见 SECRETS.md |
| 创建日期 | 2026-03-26 |

**gog CLI 配置:**
- WSL2 本地: `~/.config/gogcli/` (credentials.json + keyring/)
- 容器内: `/home/node/.config/gogcli/` (从 WSL2 复制)
- Keyring password: `123123` (环境变量 `GOG_KEYRING_PASSWORD`)
- 容器重建后需要重新: 1) 安装 gog binary 2) 复制 gogcli 目录 3) `gog auth credentials set`

**已认证的邮箱账号:**
- `tao.for.luv@gmail.com` — 产品邮箱 (Likely You)
- `xianzhh2@uci.edu` — 学校邮箱

**已启用的 Google API (项目 likely-you-stuff):**
- Gmail API
- Google Drive API
- Google Docs API
- Google Sheets API

---

## 日常维护命令

所有命令在 WSL2 中执行 (`wsl -d Ubuntu`)。

### 启动
```bash
cd ~/openclaw-unified && docker compose up -d openclaw-gateway
```

### 停止
```bash
cd ~/openclaw-unified && docker compose down
```

### 重启
```bash
cd ~/openclaw-unified && docker compose restart openclaw-gateway
```

### 查看状态
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### 健康检查
```bash
curl -s http://localhost:18789/healthz
```

### 查看日志
```bash
docker logs -f openclaw-unified-openclaw-gateway-1
```

### 升级镜像
```bash
docker pull ghcr.io/openclaw/openclaw:latest
cd ~/openclaw-unified && docker compose up -d openclaw-gateway
```

### 设备配对
当 Control UI 显示 "pairing required" 时:
```bash
cd ~/openclaw-unified
# 查看待配对设备
docker compose run --rm openclaw-cli devices list
# 批准配对 (替换 REQUEST_ID)
docker compose run --rm openclaw-cli devices approve <REQUEST_ID>
```

### 生成 Dashboard URL
```bash
cd ~/openclaw-unified
docker compose run --rm openclaw-cli dashboard --no-open
```

---

## 模型切换

### 修改 agent 默认模型
编辑 `/home/xzwz778/.openclaw-unified/openclaw.json`，修改对应 agent 的 `model.primary`，然后重启。

### 聊天中临时切换
```
/model list
/model anthropic/claude-opus-4-6
```

### 支持的模型提供商
在 `.env` 中添加对应 Key 即可：

| 提供商 | 环境变量 | 模型示例 |
|--------|----------|---------|
| Anthropic | `ANTHROPIC_API_KEY` | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 |
| OpenAI | `OPENAI_API_KEY` | gpt-4o, gpt-4o-mini |
| Google | `GEMINI_API_KEY` | gemini-2.5-pro |
| OpenRouter | `OPENROUTER_API_KEY` | deepseek-chat, llama-3 |

---

## 故障排除

### 问题: sudo 需要密码
WSL2 已配置免密 sudo: `/etc/sudoers.d/nopasswd-user`

### 问题: 旧 clawdbot 进程占端口
```bash
# 检查
systemctl --user status clawdbot-gateway.service
# 停止并禁用
systemctl --user stop clawdbot-gateway.service
systemctl --user disable clawdbot-gateway.service
```

### 问题: openclaw.json 配置格式错误
- `identity` 已迁移到 `agents.list[].identity`
- `agent.*` 已迁移到 `agents.defaults`
- 必须设置 `gateway.mode = "local"`
- 非 loopback bind 需要 `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback = true`

### 问题: Docker 端口未映射
容器多次重启后端口映射可能丢失，需要 `docker compose down && docker compose up -d`

### 问题: Windows → WSL2 bash 脚本变量丢失
Windows 的 `wsl -d Ubuntu -- bash -c` 会吞掉 `$` 变量。解决方法:
- 用单引号 heredoc (`<<'EOF'`)
- 或先写脚本文件到 WSL2 再执行
- 或用硬编码值替代变量

---

## 关键文档参考 (源码内)

- `docker-compose.yml` — Docker Compose 模板
- `.env.example` — 环境变量参考
- `docs/install/docker.md` — Docker 部署指南
- `docs/concepts/multi-agent.md` — 多 Agent 路由
- `docs/concepts/memory.md` — Agent 记忆系统
- `docs/gateway/configuration-reference.md` — 完整配置参考
- `docs/gateway/configuration-examples.md` — 配置示例
