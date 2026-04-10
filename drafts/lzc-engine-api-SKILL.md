---
name: lzc-engine-api
description: Load when calling the Likely You engine API. Contains the endpoint URL, authentication, request/response format, all 6 response dimensions, curl examples, and degradation protocol when the API is unavailable.
---

# Engine API — Call Protocol

## Endpoint

```
URL: $LIKELYYOU_ENGINE_URL
Default: https://web-production-7e1ed.up.railway.app/v1/agent/profile
```

## Authentication

```
Header: X-Katelyn-Key: $LIKELYYOU_ENGINE_KEY
```

## Request

**Method:** POST
**Content-Type:** application/json

```json
{
  "birth_date": "YYYY-MM-DD",
  "is_male": true,
  "birth_time": "HH:MM"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `birth_date` | **Yes** | Full date in ISO format (e.g., "1989-12-13") |
| `is_male` | **Yes** | Boolean — true for male, false for female |
| `birth_time` | No | 24-hour format (e.g., "05:30"). Enables more precise analysis if available. |

## Response — 6 Dimensions

The engine returns analysis across 6 dimensions:

| # | Dimension | Response Key | What It Contains |
|---|-----------|-------------|-----------------|
| 1 | **Personality** | `personality.dominant_traits` | Top personality traits with percentage weights |
| 2 | **Dayun (Major Luck Cycles)** | `dayun` | 10-year life segments with keywords and themes |
| 3 | **Liunian (Annual Fortune)** | `liunian` | Year-by-year labels and predictions |
| 4 | **Feeling (Relationships)** | `feeling` | Relationship windows, compatibility patterns |
| 5 | **Liuqin (Six Relations)** | `liuqin` | Family/social relationship dynamics across 6 groups |
| 6 | **Marriage** | `marriage` | Marriage timing recommendations, partner profile |

## Curl Example

```bash
curl -X POST "$LIKELYYOU_ENGINE_URL" \
  -H "Content-Type: application/json" \
  -H "X-Katelyn-Key: $LIKELYYOU_ENGINE_KEY" \
  -d '{
    "birth_date": "1989-12-13",
    "is_male": false,
    "birth_time": "05:30"
  }'
```

## Degradation Protocol

**If the API fails (timeout, 5xx, network error):**

1. **Report honestly** — tell the user the engine is temporarily unavailable
2. **Never fabricate** — do NOT make up engine output or fill in "what it probably would say"
3. **Retry once** — wait 10 seconds, try again
4. **If still failing** — log the error, notify via Telegram, and pause the analysis
5. **Resume when ready** — the analysis can be completed later when the API is back

```
Engine API unavailable at [timestamp]
Error: [error message]
Status: Analysis paused — will retry when API recovers
```

**There is no "fallback mode."** The engine output is the foundation of every analysis. Without it, there is nothing to verify against reality.

## Rate Limits

- Be mindful of API rate limits
- Cache responses for the same birth_date + is_male combination
- Do not call the API more than necessary — one call per celebrity per analysis
