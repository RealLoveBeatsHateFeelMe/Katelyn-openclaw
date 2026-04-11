---
name: x-kol-scan
description: Load at the start of every x-kol-scan cron run. Uses twitterapi.io to fetch recent tweets from builder accounts. Filters by reply count (<100), originality. Scores using x-scoring. Stores in state/x-processed-posts.json.
---

# X KOL Scan — 扫描工作流（v3 twitterapi.io）

## 核心任务

每轮扫描 10-12 个 builder 的最新推文，评分后存入 state。

## 触发

Cron：`*/45 * * * *`

## API 配置

```
API: twitterapi.io
Key: new1_2c8f68c420a748aeb68cca497306f4d8
Header: x-api-key
Endpoint: https://api.twitterapi.io/twitter/user/last_tweets
```

## 工作流

### Step 1：读配置

- 本 skill + `x-scoring`
- `config/x-kol-list.json` — builder 列表
- `state/x-processed-posts.json` — 已处理帖子（去重）

### Step 2：选本轮扫描目标

从 x-kol-list.json 选 10-12 个 builder（轮换，优先 high priority + 上轮没扫的）

### Step 3：调 API 拿推文

对每个 builder 执行：

```bash
curl -s -H "x-api-key: new1_2c8f68c420a748aeb68cca497306f4d8" \
n**重要：每次 curl 调用之间必须等 6 秒（sleep 6），否则会触发 rate limit。** 免费用户 QPS 限制是每 5 秒 1 个请求。
  "https://api.twitterapi.io/twitter/user/last_tweets?userName={handle}&count=5"
```

返回 JSON，每条推文包含：
- `text` — 推文内容
- `replyCount` — 回复数
- `likeCount` — 点赞数
- `retweetCount` — 转发数
- `viewCount` — 浏览数
- `isReply` — 是否是回复
- `createdAt` — 发布时间
- `author.followers` — 粉丝数
- `url` — 推文链接

### Step 4：过滤

对 API 返回的每条推文：

- `isReply == true` → 跳过（是回复不是原创）
- `type != "tweet"` → 跳过（转发等）
- `replyCount > 100` → 跳过（太拥挤）
- 发布时间 > 7 天前 → 跳过
- 内容和 building/AI/shipping 完全无关的日常帖 → 跳过

### Step 5：去重

检查 tweet ID 是否已在 x-processed-posts.json 中。已有 → 跳过。

### Step 6：评分

用 x-scoring 公式。从 API 数据直接读取精确数值：

```
topic_relevance (0-5) — 帖子内容和 AI/building/shipping 的相关度
author_size (0-3) — author.followers
reply_window (0-5) — replyCount 越少越好
recency (0-3) — createdAt 越新越好
```

### Step 7：存储

写入 state/x-processed-posts.json。格式：

```json
{
  "last_scan": "ISO timestamp",
  "scanned_handles": ["handle1", "handle2"],
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
      "posted_at": "ISO timestamp",
      "is_original": true,
      "x_opportunity_score": 12,
      "status": "candidate"
    }
  ]
}
```

### Step 8：紧急推送

score >= 12 且 reply_count <= 5 且 age < 1h → 立即推送 Telegram

### Step 9：清理

删除 7 天以上记录。更新 scanned_handles。

## 注意

- 不要用 web_search，直接用 exec/curl 调 twitterapi.io
- 每个 builder 只拿 5 条最新推文（count=5），省 API credits
- 每轮 10-12 个 builder = 10-12 次 API 调用 = 50-60 条推文待评分

## 更新记录

- 2026-04-11：v3 — 切换到 twitterapi.io，替代 Brave Search
