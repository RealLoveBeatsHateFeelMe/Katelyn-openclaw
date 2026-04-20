---
name: x-reply-context
description: For each candidate tweet, fetch existing replies via twitterapi.io get_tweet_replies, analyze them by likeCount and author engagement, and surface white-space angles. Used by x-reply-briefing before generating reply drafts.
---

# X Reply Context Analysis

## 目的

在生成 reply 草稿前，先看帖子下面已经有什么回复。让草稿能：
1. **避免重复**（别说大家都说过的）
2. **找白空间**（没人聊的角度）
3. **学作者品味**（看作者亲自点赞/回复了什么样的 reply）

## API

```
GET https://api.twitterapi.io/twitter/tweet/replies?tweetId={tweet_id}
Header: x-api-key: new1_2c8f68c420a748aeb68cca497306f4d8
```

返回 JSON：
- `tweets[]` — 第一页 reply（默认 ~20 条）
- 每条 reply 字段：`id`, `text`, `likeCount`, `replyCount`, `inReplyToId`, `author.userName`, `createdAt`
- `has_next_page`, `next_cursor` — 翻页（一般不用，第一页够用）

## 分支处理（按候选推文的 reply_count）

### Case A：reply_count == 0
**跳过 API 调用**（省钱）。直接返回：
```json
{
  "context_type": "first_mover",
  "note": "你是第一个回的，先发优势",
  "patterns_to_avoid": [],
  "white_space_angles": [],
  "author_engaged_examples": []
}
```

### Case B：1 ≤ reply_count ≤ 4
调 API 一次（拿全部 1-4 条 reply）。**不做白空间分析**（4 条推不出模式）。返回：
```json
{
  "context_type": "early_window",
  "note": "已有 N 条 reply，但太少看不出模式。直接生成草稿。",
  "existing_replies_summary": "简短列出每条 reply 在说什么",
  "patterns_to_avoid": [],
  "white_space_angles": [],
  "author_engaged_examples": []
}
```

### Case C：reply_count ≥ 5
调 API 拿第一页（~20 条），完整分析：

**Step 1：客户端按 likeCount 降序排列**

**Step 2：检测作者engaged**
- 找所有 `author.userName == 原推作者` 的 reply
- 这些是作者自己回的
- 看他们的 `inReplyToId` → 指向哪条 top-level reply
- 那条 top-level reply 就是"作者亲自engaged"的

**Step 3：分析模式**
- 把 top 10 高赞 reply 的 text 分组：
  - "agree, [data]" 模式
  - "lol/joke" 模式
  - "question" 模式
  - "personal experience" 模式
  - 等
- 数每个模式有几条
- 识别"大家都在说 X"的高频模式 → 加入 `patterns_to_avoid`

**Step 4：找白空间**
- 看推文涉及的角度：地理/时间/技术细节/受众/经济
- 对比已有 reply 覆盖了哪些
- 没覆盖的 → 加入 `white_space_angles`

**Step 5：返回**
```json
{
  "context_type": "crowded",
  "note": "47 条 reply，分析完毕",
  "patterns_to_avoid": [
    "23 条都在说 'agree, X is the bottleneck'",
    "8 条幽默向（'my 2018 GPU is now an asset'）"
  ],
  "white_space_angles": [
    "二手 GPU 的地理差异（HK / SG / 印度市场）",
    "租用 vs 购买的临界点变化"
  ],
  "author_engaged_examples": [
    {
      "type": "liked",
      "reply_author": "@xyz",
      "reply_text": "fwiw I tracked 3090 prices, up 40% in 6mo",
      "why_works": "数据具体 + 短 + fwiw 的口气"
    },
    {
      "type": "replied",
      "reply_author": "@abc",
      "reply_text": "wait, even RTX 4060? checked yesterday no movement",
      "author_response": "yeah 4060 is the exception, but...",
      "why_works": "具体反观察 + 短"
    }
  ]
}
```

## 工作流（被 x-reply-briefing 调用）

```python
def get_reply_context(tweet_id, reply_count):
    if reply_count == 0:
        return {"context_type": "first_mover", ...}

    # 调 API
    sleep(6)  # rate limit
    resp = curl_api(tweet_id)
    replies = resp["tweets"]

    if 1 <= reply_count <= 4:
        return {"context_type": "early_window", ...}

    # reply_count >= 5
    sorted_replies = sorted(replies, key=lambda r: r["likeCount"], reverse=True)

    # 检测作者engaged
    original_author = get_original_author(tweet_id)
    author_replies = [r for r in replies if r["author"]["userName"] == original_author]
    engaged_ids = [r["inReplyToId"] for r in author_replies]
    engaged_replies = [r for r in replies if r["id"] in engaged_ids]

    # LLM 分析模式 + 找白空间
    return llm_analyze(sorted_replies[:10], engaged_replies)
```

## 成本控制

- 每次扫 5 候选
- 平均：1 个 0reply（跳过）+ 2 个 1-4reply（$0.0003 each）+ 2 个 5+reply（$0.003 each）
- 单次 briefing：~$0.0066
- 3 次/天 × 30 = ~$0.6/月

## Rate limit

twitterapi.io 免费/低额每 5 秒 1 个请求。
**每次 curl 之间 sleep 6**。

## 错误处理

- API 返回 `Credits is not enough` → 整批分析跳过，标记 `context_type: "api_error"`，仍生成草稿（无白空间分析）
- API 超时 → 同上
- JSON 解析失败 → 同上

## 不做

- 不翻页（第一页 20 条够用，热门帖子已被 scan 过滤掉了）
- 不 fetch 子回复（reply 的 reply 不重要）
- 不分析作者本人的全部历史（那是 x-kol-scan 的事）

## 更新记录

- 2026-04-20 v1：首版，配合 x-reply-briefing v5 使用
