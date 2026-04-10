---
description: 当 Olivia/Gateway 容器无法启动、反复重启、Discord 掉线、或日志出现 SIGTERM/clobbered/Maximum call stack size exceeded 时自动触发
---

# WSL2 Docker 稳定运行指南

## 前置条件（已配置，确保不被重置）

### 1. WSL2 VM 不自动关闭（根本原因修复）

文件 `C:\Users\32247\.wslconfig`：
```ini
[wsl2]
vmIdleTimeout=-1
```

**这是最关键的一条。** 没有这个，WSL2 VM 会在空闲时自动关闭，导致 Docker Engine 每 1-2 分钟被 systemd 杀一次，容器永远起不来。

### 2. Windows 电源设置

```powershell
# 合盖不休眠
powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0
powercfg /setdcvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0
powercfg /setactive SCHEME_CURRENT

# 永不睡眠，屏幕5分钟关
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 5

# 彻底禁用 Hibernate（需要管理员权限）
powercfg /h off
powercfg /change hibernate-timeout-ac 0
powercfg /change hibernate-timeout-dc 0
```

### 3. Hyper-V 内存回收

```bash
wsl --manage Ubuntu --set-sparse false
```

### 4. WSL2 内部防护（每次 WSL 重启后需重做）

```bash
wsl -d Ubuntu -- bash -c 'sudo systemctl mask systemd-poweroff.service poweroff.target'
```

**全部配好后，合上联想 X1 盖子 = 只关屏幕，WSL2/Docker/Olivia 应持续在线。**

---

## 症状识别

以下任一症状出现时，按修复步骤处理：

- 容器反复重启（`docker ps` 显示 Up 几秒就重启）
- 日志中出现 `signal SIGTERM received` 循环
- 日志中出现 `Config observe anomaly: openclaw.json (missing-meta-vs-last-good)` 刷屏
- 日志中出现 `RangeError: Maximum call stack size exceeded`
- `.openclaw-unified/` 目录下出现大量 `openclaw.json.clobbered.*` 文件
- Olivia 在 Discord 上线后很快掉线，或只能回第一条消息

## 诊断步骤

先判断是哪一层的问题：

```bash
# 1. 检查 WSL2 VM 是否在被反复关闭
wsl -d Ubuntu -- bash -c 'sudo journalctl -u docker --no-pager | grep -c "Stopping docker"'

# 2. 检查 Docker Engine 是否稳定（等30秒看PID是否变化）
wsl -d Ubuntu -- bash -c 'pidof dockerd && sleep 30 && pidof dockerd'

# 3. 检查容器日志
wsl -d Ubuntu -- bash -c 'sudo docker logs --tail 20 openclaw-unified-openclaw-gateway-1 2>&1'
```

## 修复步骤（按顺序执行）

### 第 1 步：确认 .wslconfig 存在

```bash
cat C:\Users\32247\.wslconfig
```

如果没有 `vmIdleTimeout=-1`，加上它。这是根因。

### 第 2 步：一键恢复命令

```bash
wsl --shutdown && timeout 8 && wsl -d Ubuntu -- bash -c 'sleep 30 && sudo systemctl mask systemd-poweroff.service poweroff.target 2>/dev/null && rm -f /home/xzwz778/.openclaw-unified/openclaw.json.clobbered.* && cd /home/xzwz778/openclaw-unified && sudo docker compose down 2>/dev/null; sudo docker compose up -d openclaw-gateway && sudo docker exec -u root openclaw-unified-openclaw-gateway-1 bash -c "chown -R 1000:1000 /home/node/.npm" 2>/dev/null'
```

### 第 3 步：验证（等 60 秒）

```bash
wsl -d Ubuntu -- bash -c 'sleep 60 && sudo docker ps --format "table {{.Names}}\t{{.Status}}" && curl -s http://localhost:18789/healthz'
```

预期结果：容器 `(healthy)`，healthz 返回 `{"ok":true,"status":"live"}`

---

## 操作纪律

- **任何涉及容器重启、Docker 操作、WSL 重启的改动，必须先写计划，等用户 approve plan 后才能执行**
- **每次恢复后必须做稳定性检查**：等 3-5 分钟确认容器持续 healthy，不能恢复完就说"好了"
- **需要写一个 30 分钟自动检查脚本，全天监控 Olivia 在线状态**

## 绝对不要做的事

- **不要用 `docker compose restart`** — 会导致内部双进程，消息管道断裂
- **不要用 `docker compose run --rm openclaw-cli ...`** — 临时容器会干扰 gateway，导致 gateway 被 recreate 或 SIGTERM
- **不要用 `newgrp docker <<<`** — 会发 SIGTERM 杀容器
- **不要在 Docker 不稳定时反复重启容器** — 先确认 Docker Engine 自身稳定（PID 不变），再启动容器

## 历史教训（2026-03-26）

| 问题 | 根因 | 解决 |
|------|------|------|
| 容器每 1-2 分钟被 SIGTERM 杀 | WSL2 `vmIdleTimeout` 默认值导致 VM 空闲自动关闭 | `.wslconfig` 加 `vmIdleTimeout=-1` |
| 478 个 .clobbered 垃圾文件 | 容器反复崩溃时配置系统的防护机制，积累后导致栈溢出 | 删除垃圾文件 + 修复根因 |
| 改模型后 Olivia 不回消息 | 用了 `docker compose restart` 导致双进程 | 用 `down + up` 代替 |
| CLI 命令后 gateway 崩溃 | `docker compose run --rm openclaw-cli` 干扰了 gateway | 不用 `run`，用 Dashboard 或 `docker exec` |
| 合盖后一切崩溃 | Windows 休眠 + WSL2 空闲超时双重打击 | 合盖不休眠 + vmIdleTimeout=-1 |
| 合盖 40 分钟后掉线 | Windows Hibernate 硬杀 Hyper-V VM | `powercfg /h off` 禁用 Hibernate |
| WSL2 内部 systemd 周期性关机 | Windows 给 VM 发 poweroff 信号 | `systemctl mask poweroff.target`（每次 WSL 重启后需重做） |
| acpx session 立刻死（queue owner unavailable） | `queueOwnerTtlSeconds` 默认 0.1 秒太短 | 改为 120 秒 |
| acpx spawn 失败（EACCES） | 用 root 装 npm 包导致 cache 权限坏 | `chown -R 1000:1000 /home/node/.npm` |
| acpx spawn 的不是 claude CLI 而是 @zed-industries/claude-agent-acp | acpx 有自己的 agent spawner | 这是正确行为，不需要手动装 claude CLI |
