---
description: Olivia 稳定连接完整指南。当 Olivia 掉线、容器被杀、Discord 断连时，按此文档逐步排查和修复。任何涉及容器/Docker/WSL 操作必须先计划再执行。
---

# Olivia 稳定连接指南

## 问题本质

**WSL2 不是生产服务器。** Microsoft 官方（GitHub Issue #9667, #8763）明确说明：WSL2 轻量级 Hyper-V VM 在没有"用户手动打开的终端窗口"且没有"显式用户启动的后台进程"时，会被 idle-terminate。systemd 服务（包括 Docker）不算"用户启动"。

所有 WSL2 内部防护（mask poweroff、vmIdleTimeout、set-sparse）都只能部分缓解，无法完全阻止主机层面的终止。

### 三层问题叠加

| 层 | 问题 | 触发条件 |
|----|------|---------|
| **Windows 层** | Modern Standby (S0) 挂起/杀死 Hyper-V VM | 合盖、空闲、内存压力 |
| **WSL2 层** | VM 被 idle-terminate，systemd 走 poweroff.target | 无用户前台进程时 Windows 认为空闲 |
| **OpenClaw 层** | Discord health-monitor 崩溃 + config clobber 雪崩 | WSL2 网络抖动、DNS 不稳、版本 bug |

---

## 解决方案（按优先级排序）

### 🔴 第一优先：禁用 Connected Standby（PlatformAoAcOverride=0）

**这是目前社区验证最有效的单一方案。** 把 S0 (Modern Standby) 切成传统 S3 睡眠，WSL2 存活率大幅提升。

```powershell
# 管理员 PowerShell
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power" /v PlatformAoAcOverride /t REG_DWORD /d 0 /f
```

**需要重启电脑。**

**需要重启电脑。** 已于 2026-03-26 执行并重启。

验证：
```powershell
powercfg /a
# 联想 X1 结果：S0 和 S3 都显示 "not available"（固件不支持 S3）
# 这意味着电脑完全无法进入任何睡眠状态 = 合盖只关屏幕 = 最理想结果
```

**实际效果（2026-03-26 验证）：** 容器连续 5 分钟 healthy，之前同一时段内必定被杀 2-3 次。

回滚：
```powershell
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Power" /v PlatformAoAcOverride /f
```

### 🔴 第二优先：WSL2 Keep-Alive 后台进程

WSL2 在检测到"有用户后台进程"时不会被 idle-terminate。tmux 后台会话 + Windows 定期 ping 能骗过 idle 检测。

**WSL2 内部：**
```bash
sudo apt install -y tmux
tmux new -d -s keepalive "while true; do sleep 300; done"
```

**Windows Task Scheduler（每 5 分钟执行）：**
```powershell
wsl -d Ubuntu -e tmux send-keys -t keepalive "date" Enter
```

也可以创建 systemd service：
```bash
# /etc/systemd/system/wsl-keepalive.service
[Unit]
Description=WSL2 Keep-Alive
After=multi-user.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'while true; do sleep 300; done'
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable --now wsl-keepalive.service
```

### 🟡 第三优先：已配置的防护（保持）

这些已经配好，确保不被重置：

| 防护 | 配置 | 状态 |
|------|------|------|
| **禁用 Connected Standby** | `PlatformAoAcOverride=0`（注册表） | ✅ 最关键 |
| **tmux keep-alive** | WSL2 内 `tmux new -d -s keepalive` | ✅ 每次 VM 重启后需重做 |
| **WSL2KeepAlive 定时任务** | Windows Task Scheduler 每 5 分钟 ping | ✅ |
| 合盖不休眠 | `powercfg LIDACTION 0` (AC+DC) | ✅ |
| 永不睡眠 | `powercfg standby-timeout-ac 0` | ✅ |
| 禁用 Hibernate | `powercfg /h off` | ✅ |
| WSL2 不空闲关机 | `.wslconfig vmIdleTimeout=999999999` | ✅ |
| Hyper-V 不回收内存 | `wsl --manage Ubuntu --set-sparse false` | ✅ |
| WSL2 拒绝关机 | `systemctl mask poweroff.target halt.target suspend.target hibernate.target` | ✅ 每次 VM 重启后需重做 |
| 自动恢复脚本 | OliviaWatchdog.ps1 每 30 分钟检查 | ✅ |
| OpenClaw 降级 | v2026.3.13-1（避开 v2026.3.24 Discord 崩溃 bug） | ✅ |

### 🟡 第四优先：OpenClaw 层面稳定措施

| 措施 | 说明 |
|------|------|
| 使用 v2026.3.13-1 | 避开 v2026.3.24 的 Discord health-monitor 崩溃 bug (#54729) |
| `restart: unless-stopped` | docker-compose.yml 已有 |
| 不用 `docker compose restart` | 用 `down && up` 代替，避免双进程 |
| 不用 `docker compose run --rm openclaw-cli` | 用 Dashboard 或 `docker exec` 代替 |
| 定期备份 openclaw.json | 防止 clobber 雪崩 |
| acpx queueOwnerTtlSeconds=120 | 避免 ACP session 秒死 |
| npm cache 权限 | 容器重建后需 `chown -R 1000:1000 /home/node/.npm` |

---

## 如果以上都不够（备选方案）

| 方案 | 可靠性 | 成本 | 说明 |
|------|--------|------|------|
| Docker Desktop | 高 | 免费 | 对 Windows 电源事件有专门处理，容器存活率更高 |
| 完整 Hyper-V VM | 很高 | 免费 | 安装 Ubuntu 24.04 VM，不会被 Windows 随意杀 |
| 云服务器 | 最高 | $5-20/月 | AWS/GCP/Oracle Cloud 免费层可能够用 |
| Mini PC / Raspberry Pi 5 | 最高 | $50-100 一次性 | 24/7 在线无压力 |

---

## 一键恢复命令

掉线后执行（不需要 plan approval，这是恢复操作）：

```bash
wsl --shutdown && timeout 8 && wsl -d Ubuntu -- bash -c 'sleep 30 && sudo systemctl mask systemd-poweroff.service poweroff.target halt.target suspend.target hibernate.target 2>/dev/null && tmux new -d -s keepalive "while true; do sleep 300; done" 2>/dev/null; rm -f /home/xzwz778/.openclaw-unified/openclaw.json.clobbered.* && cd /home/xzwz778/openclaw-unified && sudo docker compose down 2>/dev/null; sudo docker compose up -d openclaw-gateway && sudo docker exec -u root openclaw-unified-openclaw-gateway-1 bash -c "chown -R 1000:1000 /home/node/.npm" 2>/dev/null'
```

---

## 诊断命令速查

```bash
# WSL2 VM 存活检查
wsl -d Ubuntu -- bash -c 'uptime'

# Docker 是否在被反复杀
wsl -d Ubuntu -- bash -c 'sudo journalctl -u docker --no-pager | grep -c "Stopping docker"'

# 容器状态
wsl -d Ubuntu -- bash -c 'sudo docker ps --format "table {{.Names}}\t{{.Status}}"'

# 健康检查
curl -s http://localhost:18789/healthz

# Discord 连接状态
wsl -d Ubuntu -- bash -c 'sudo docker logs --tail 20 openclaw-unified-openclaw-gateway-1 2>&1 | grep -i "discord\|SIGTERM\|uncaught\|error"'

# systemd 是否在做关机
wsl -d Ubuntu -- bash -c 'sudo journalctl --no-pager | grep -E "poweroff|shutdown|Stopping docker" | tail -10'

# 检查 clobbered 文件数量
wsl -d Ubuntu -- bash -c 'ls /home/xzwz778/.openclaw-unified/openclaw.json.clobbered.* 2>/dev/null | wc -l'

# 检查 Windows 电源状态
powercfg /a
```

---

## 2026-03-26 完整事件时间线

| 时间 | 事件 | 根因 | 修复 |
|------|------|------|------|
| 昨晚 | 合盖睡觉，期望 Olivia 继续在线 | — | — |
| ~06:19 | 478 个 .clobbered 文件，配置栈溢出 | 容器反复崩溃触发配置保护机制雪崩 | 删除垃圾文件 |
| ~06:29 | SIGTERM 循环，Docker 被 systemd 反复杀 | WSL2 VM 被 Windows poweroff | `wsl --shutdown` 重启 |
| ~06:32 | Docker Engine 10 分钟重启 5 次 | systemd 走 poweroff.target 完整关机流程 | 发现是 Windows 给 VM 发关机信号 |
| ~06:34 | 尝试 vmIdleTimeout=-1 | WSL2 空闲超时 | `.wslconfig` 创建 |
| ~06:37 | 尝试 mask poweroff.target | systemd 内部关机 | 部分有效，但 Windows 可绕过 |
| ~06:50 | 改模型后用 `docker compose restart` | 双进程，消息管道断裂 | 改用 `down && up` |
| ~07:05 | 用 `docker compose run --rm openclaw-cli` | 临时容器干扰 gateway | 禁止使用 `run` |
| ~07:19 | set-sparse false + 多重防护 | — | 容器首次撑 40 分钟 |
| ~07:51 | ACP queueOwnerTtlSeconds=0.1s | Claude Code 来不及启动 | 改为 120s |
| ~07:55 | acpx EACCES 错误 | root 装 npm 包坏了权限 | chown 修复 |
| ~08:46 | 合盖 40 分钟后掉线 | Windows Hibernate 杀 VM | `powercfg /h off` |
| ~15:33 | 又被杀，反复重启 | WSL2 VM 层面未解决 | — |
| ~15:58 | 降级到 v2026.3.13-1 | v2026.3.24 Discord 崩溃 bug | 降级 |
| ~16:04 | Discord logged in 但容器又被重启 | WSL2 VM 仍被 Windows 杀 | 需要 PlatformAoAcOverride=0 |
| ~16:20 | 执行 PlatformAoAcOverride=0 + tmux keepalive | — | 注册表 + 重启电脑 |
| ~16:35 | **重启后容器连续 5 分钟 healthy，0 SIGTERM** | PlatformAoAcOverride=0 生效 | 所有睡眠状态已禁用 |

---

## 关键认知

1. **WSL2 是开发工具，不是 24/7 服务器** — Microsoft 官方反复强调
2. **所有 WSL2 内部防护都挡不住 Windows 主机层面的 VM 终止**
3. **Modern Standby (S0) 是笔记本场景的最大敌人** — 禁用它（PlatformAoAcOverride=0）是社区共识最有效方案
4. **OpenClaw v2026.3.24 有 Discord 崩溃 bug** — 用 v2026.3.13-1 避开
5. **彻底解决需要离开 WSL2** — Docker Desktop / Hyper-V VM / 云 / Mini PC
