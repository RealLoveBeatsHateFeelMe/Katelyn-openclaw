---
name: x-kol-scan
description: Two-pass X scan using twitterapi.io. Pass 1 probes each builder with count=1 to detect new posts via statusesCount diff. Pass 2 fetches only the diff. Saves 60%+ API cost compared to always fetching N tweets per builder.
---

# X KOL Scan — 两步扫描法（v4）

## 核心思路

**先看有没有新东西，有再拿。** 不像之前每次都拉 5 条（很多是旧的）。

twitterapi.io 计费按返回的推文数。statusesCount 是这个人的总推文数（包括 reply/quote）。对比上次看到的 statusesCount，知道这段时间发了多少条。

## 触发

Cron: `30 9,14,20 * * *` PT 时区（每天 3 次：9:30 / 14:30 / 20:30）

## API 配置

```
Endpoint: https://api.twitterapi.io/twitter/user/last_tweets
Header: x-api-key: new1_2c8f68c420a748aeb68cca497306f4d8
Params: userName={handle}&count={N}
```

**Rate limit:** 免费/低额用户每 5 秒 1 个请求。**每次 curl 之间 sleep 6**。

## State Schema

`state/x-processed-posts.json`：

```json
{
  "last_scan": "ISO timestamp",
  "scanned_handles": ["..."],
  "builder_state": {
    "elvissun": {
      "last_seen_tweet_id": "2042798244845981697",
      "last_statuses_count": 7520,
      "last_probed_at": "ISO"
    },
    "gabriel1": {...}
  },
  "posts": [
    {
      "id": "tweet_id",
      "url": "https://x.com/handle/status/id",
      "author_handle": "handle",
      "author_followers": 43770,
      "text": "tweet text",
      "reply_count": 2,
      "like_count": 3,
      "view_count": 1984,
      "posted_at": "ISO",
      "is_original": true,
      "x_opportunity_score": 12,
      "status": "candidate"
    }
  ]
}
```

`builder_state` 是新加的字段。每次扫描更新。

## 工作流

### Step 1：读 skill + 配置

- 本 skill + `x-scoring`
- `config/x-kol-list.json` — 38 个 builder
- `state/x-processed-posts.json` — 已处理 + builder_state

### Step 2：第一步扫描 — 探测（probe）

对每个 active builder（最多 38 个），按顺序：

```bash
curl -s -H "x-api-key: $KEY" "https://api.twitterapi.io/twitter/user/last_tweets?userName={handle}&count=1"
sleep 6  # rate limit
```

返回 JSON 里：
- `data.tweets[0].id` → 最新 tweet ID
- `data.tweets[0].author.statusesCount` → 总推文数

**对比 builder_state[handle]：**
- 如果不存在（首次扫该 builder）→ 标记 `is_first_scan: true`，diff 设 5（默认拉 5 条）
- 如果存在：
  - `current_count = data.tweets[0].author.statusesCount`
  - `last_count = builder_state[handle].last_statuses_count`
  - `diff = current_count - last_count`
  - diff <= 0 → 跳过这个 builder（没新东西，省 API）
  - diff > 0 → 进入第二步

**更新 builder_state[handle]**：
- `last_statuses_count = current_count`
- `last_seen_tweet_id = data.tweets[0].id`
- `last_probed_at = now`

### Step 3：第二步扫描 — 精确拉取（fetch）

仅对 diff > 0 的 builder：

```bash
N=$(min(diff, 5))
curl -s -H "x-api-key: $KEY" "https://api.twitterapi.io/twitter/user/last_tweets?userName={handle}&count=N"
sleep 6
```

最多 5 条（防爆发狂发）。

### Step 4：过滤每条新推文

对 fetch 回来的每条推文：
- `isReply == true` → 跳过（reply 不要）
- `type != "tweet"` → 跳过（转发不要）
- `replyCount > 100` → 跳过（太拥挤）
- 发布时间 > 7 天前 → 跳过（API 计费但还是过滤）
- 已在 posts 里（按 tweet ID 去重）→ 跳过

### Step 5：评分

用 `x-scoring` 公式。score >= 5 标 candidate，否则 skipped。

### Step 6：存储

- 新推文加到 posts 数组
- 更新 builder_state
- 更新 last_scan 和 scanned_handles

### Step 7：紧急推送

如果有 candidate score >= 12 且 reply_count <= 5 且 age < 1h → 立即 Telegram 推送：

```
🚨 X 黄金窗口

@{handle} ({followers} followers)
💬 {reply_count} · ⏰ {age}
"{text 前 100 字}"

🔗 {url}
```

### Step 8：清理

- 删除 posts 里 7 天前的记录
- builder_state 全保留

## 成本估算

按当前 38 个 builder：
- 每次扫描：38 个 probe + ~14 个 fetch × 平均 2 条 = ~66 推文
- 3 次/天 = 198 推文
- 30 天 = 5,940 推文
- $0.00015 × 5940 = **$0.89/月**

$5 充值 = 5+ 个月用量。

## 错误处理

- API 返回 `Credits is not enough` → 整轮停止，记录错误，下轮重试
- 单个 curl 超时 → 跳过该 builder，继续下一个
- JSON 解析失败 → 跳过该 builder
- builder 不存在（404）→ 在 builder_state 里标记 `error: "not_found"`，下次跳过

## 绝对不做

- 不每次都拉 5 条（用 diff 判断）
- 不调 web_search（用 curl）
- 不写 reply 草稿（briefing 的事）
- 不推送 briefing（briefing 的事）

## 更新记录

- 2026-04-12 v4：两步扫描，statusesCount diff 决定拉多少
- 2026-04-11 v3：换到 twitterapi.io
- 2026-04-11 v2：用户名搜索为主
- 2026-04-10 v1：首版
