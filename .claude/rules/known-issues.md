---
description: OpenClaw/Olivia 已知问题和解决方案速查表，遇到 bug 时先查这里再行动
---

# OpenClaw 已知问题速查表

## 操作纪律

**任何涉及容器重启、Docker 操作、WSL 重启、配置修改的改动，必须：**
1. 先分析问题
2. 搜索已知 issue
3. 写进计划
4. 等用户 approve plan 后才能执行

---

## 🔴 Critical: Discord 崩溃 Bug (v2026.3.24)

**Issue #54729, #54931** — Discord stale-socket health-monitor 导致 gateway 进程崩溃

**症状：**
- Olivia 上线后几秒到几分钟就掉线
- 容器显示 healthy 但 Discord 不回消息
- 日志出现 `Uncaught exception: Error: Max reconnect attempts (0) reached after code 1005`
- 一天崩溃多次

**根因：** health-monitor 检测到 Discord 连接"stale"后，`onAbort` 设 `maxAttempts: 0` 再断开，WebSocket close handler 触发 max-attempts 错误路径，产生 uncaught exception 杀死整个 gateway。

**解决方案：**
- 等官方修复（关注 Issue #54729）
- 或降级到更稳定的版本（如 v2026.3.13）
- 临时方案：`restart: always` 让容器自动重启

**我们的版本：2026.3.24 — 正中此 bug**

---

## 🟡 WSL2 VM 被 Windows 杀死

### 问题 1: vmIdleTimeout 不生效

**原因：** `-1` 在某些 WSL 版本上不被识别，回退到默认值。

**修复：** 用大正整数代替 `-1`：
```ini
# C:\Users\32247\.wslconfig
[wsl2]
vmIdleTimeout=999999999
```

### 问题 2: Windows 休眠/合盖杀 VM

**已配置的防护：**
```powershell
# 合盖不休眠
powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0
powercfg /setdcvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0
powercfg /setactive SCHEME_CURRENT
# 永不睡眠
powercfg /change standby-timeout-ac 0
# 禁用 Hibernate
powercfg /h off
```

**如果还不够 — 禁用 Connected Standby（核弹选项）：**
```reg
Windows Registry Editor Version 5.00
[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Power]
"PlatformAoAcOverride"=dword:00000000
```
需要管理员权限 + 重启。强制使用 S3 传统睡眠替代 S0ix Modern Standby。

### 问题 3: autoMemoryReclaim 导致 VM 重启

**注意：** 我们的 WSL 版本 (2.6.3.0) 不支持 `autoMemoryReclaim` 参数（报 Unknown key）。这个参数在 `[experimental]` section 下可能有效：
```ini
[experimental]
autoMemoryReclaim=disabled
```

---

## 🟡 OpenClaw 配置文件问题

### 问题: openclaw.json 被覆盖/损坏

**Issue #6028, #6070, #1661, #13058, #25007**

**症状：** 配置文件被清空、覆盖、或出现 `__OPENCLAW_REDACTED__`

**常见触发：**
- 用 Control UI Raw JSON 编辑器
- `openclaw config set` 在配置暂时不可读时执行
- Studio GUI 编辑
- 容器反复崩溃时自动写入 .clobbered 备份文件

**防护：**
- 每次改配置前备份：`cp openclaw.json openclaw.json.manual-backup`
- 用 `openclaw config set` 改单个值，不要整体替换
- 避免用 Raw JSON 编辑器

### 问题: reload.mode="hybrid" 触发重启

改了 port、bind、gateway mode、plugin config 等"不安全"项时，hybrid 模式会触发容器内进程重启。

**防护：** 对于这些改动，预期容器会重启，不是 bug。

---

## 🟡 Docker 操作问题

### 不要用 `docker compose restart`

会导致内部双进程（PID 冲突），Discord 能登录但消息管道断裂。

**正确方式：** `docker compose down && docker compose up -d openclaw-gateway`

### 不要用 `docker compose run --rm openclaw-cli`

临时容器会干扰正在运行的 gateway，导致 gateway 被 recreate 或 SIGTERM。

**正确方式：** 用 Dashboard 或 `docker exec`

### 不要在容器内执行 `openclaw gateway restart/stop`

**Issue #36137** — Docker 容器没有 systemd，这些命令会失败。

**正确方式：** 从宿主机用 `docker compose`

### npm cache 权限问题

用 root 装 npm 包后，`/home/node/.npm` 权限会坏，导致 acpx 无法 spawn 进程。

**修复：** `sudo docker exec -u root <container> chown -R 1000:1000 /home/node/.npm`

---

## 🟢 稳定运行最佳实践

### .wslconfig（最新推荐）

```ini
[wsl2]
vmIdleTimeout=999999999
```

### docker-compose.yml

确保有 `restart: unless-stopped`（已有）。考虑改为 `restart: always`。

### WSL2 内部防护（每次 VM 重启后需重做）

```bash
sudo systemctl mask poweroff.target halt.target suspend.target hibernate.target
```

### Windows 侧自动恢复脚本（待创建）

每 30 分钟检查 Olivia 是否在线，掉了自动恢复。

### 降级版本（如果 Discord 崩溃持续）

```bash
# 在 .env 中指定稳定版本
OPENCLAW_IMAGE=ghcr.io/openclaw/openclaw:v2026.3.13
```

---

## 一键恢复命令

```bash
wsl --shutdown && timeout 8 && wsl -d Ubuntu -- bash -c 'sleep 30 && sudo systemctl mask systemd-poweroff.service poweroff.target halt.target suspend.target hibernate.target 2>/dev/null && rm -f /home/xzwz778/.openclaw-unified/openclaw.json.clobbered.* && cd /home/xzwz778/openclaw-unified && sudo docker compose down 2>/dev/null; sudo docker compose up -d openclaw-gateway && sudo docker exec -u root openclaw-unified-openclaw-gateway-1 bash -c "chown -R 1000:1000 /home/node/.npm" 2>/dev/null'
```

---

## 参考链接

- [Issue #54729: Discord health-monitor crash (v2026.3.24)](https://github.com/openclaw/openclaw/issues/54729)
- [Issue #54931: Discord uncaught exception crash loop](https://github.com/openclaw/openclaw/issues/54931)
- [Issue #6070: config set overwrites entire config](https://github.com/openclaw/openclaw/issues/6070)
- [Issue #25007: Single openclaw.json is single point of failure](https://github.com/openclaw/openclaw/issues/25007)
- [Issue #36137: gateway restart/stop fail in containers](https://github.com/openclaw/openclaw/issues/36137)
- [microsoft/WSL#4189: VM shutdown kills background processes](https://github.com/microsoft/WSL/issues/4189)
- [microsoft/WSL#10292: vmIdleTimeout not respected](https://github.com/microsoft/WSL/issues/10292)
- Microsoft 官方立场：WSL2 是开发工具，不是生产服务器，持续运行服务建议用完整 Hyper-V VM 或云实例
