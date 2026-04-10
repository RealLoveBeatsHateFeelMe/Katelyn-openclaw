---
description: 管理 Olivia/OpenClaw 配置、skills、workspace 时自动触发，区分哪些操作在 Claude Code 做，哪些在 Dashboard/CLI 做
---

# OpenClaw 管理分工

## 在 Dashboard / OpenClaw CLI 做（热加载，不需要重启）

- 改模型：Dashboard Config 页 或 `openclaw config set agents.defaults.model.primary <model>`
- 改频道设置（Discord/Telegram）：Dashboard Channels 页
- 改 Agent 路由/绑定：`openclaw agents bind`
- 查状态：`openclaw status` / `openclaw doctor`
- 查日志：`openclaw logs --follow`
- 升级版本：`openclaw update`
- Cron 任务：`openclaw cron add/list/remove`

**这些操作走 OpenClaw 内部热加载，不需要碰 Docker。**

## 在 Claude Code (这里) 做

- **安装/更新 skills**：需要进容器文件系统，复制文件到 `/home/node/.openclaw/workspace/skills/`
- **编辑 workspace 文件**：SOUL.md, AGENTS.md, USER.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md 等（也可以在容器内编辑，但从 Windows 侧通过 WSL2 挂载路径更方便）
- **编辑 .claude/rules**：本 repo 的 rules 文件
- **Docker 基础设施问题**：WSL2 崩溃恢复、容器重建（参考 wsl2-docker-recovery.md）
- **Git 管理**：推送 workspace 文件到 My-love-Olivia repo
- **PowerShell 脚本**：Windows Task Scheduler 任务（护眼提醒、深夜陪伴等）
- **调试复杂问题**：需要读源码、查日志、定位根因时

## 绝对不要做的事

- **不要用 `docker compose restart`** — 会导致双进程，消息管道断裂。必须用 `docker compose down && docker compose up -d openclaw-gateway`
- **不要用 `docker compose run --rm openclaw-cli ...`** — 临时容器会干扰正在运行的 gateway，导致 gateway 被 recreate 或收到 SIGTERM。查状态、改配置、批准设备等操作用 Dashboard 或 `docker exec` 代替
- **不要直接改 openclaw.json 然后手动重启** — 用 Dashboard 或 `docker exec` 进容器内用 `openclaw config set`，让热加载处理
- **不要用 `newgrp docker <<<`** — 会发 SIGTERM 杀容器

## Skills 安装流程（在 Claude Code 做）

Skills 文件需要复制到容器内的 workspace/skills/ 目录：

```bash
# WSL2 侧路径（挂载到容器内）
/home/xzwz778/.openclaw-unified/workspace/skills/

# 从 GitHub 下载 skill 并复制
# 例如 inner-life skills:
wsl -d Ubuntu -- bash -c 'cp -r <source>/inner-life-core /home/xzwz778/.openclaw-unified/workspace/skills/'
```

安装完 skill 后不需要重启，下次对话会自动加载。

## Claude Code CLI 安装（容器重建后需重新执行）

容器里需要装 Claude Code CLI，Olivia 才能通过 ACP 操控它：

```bash
wsl -d Ubuntu -- bash -c 'sudo docker exec -u root openclaw-unified-openclaw-gateway-1 npm install -g @anthropic-ai/claude-code'
```

验证：`sudo docker exec openclaw-unified-openclaw-gateway-1 claude --version`

## Workspace 文件编辑路径

从 Windows/Claude Code 侧编辑：
```
WSL2 路径: /home/xzwz778/.openclaw-unified/workspace/
Windows 访问: wsl -d Ubuntu -- bash -c 'cat/edit ...'
```

编辑后不需要重启，下次对话自动生效。
