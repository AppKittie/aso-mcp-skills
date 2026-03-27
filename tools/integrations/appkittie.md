# AppKittie API Integration

## Authentication

All API requests require a Bearer token:

```
Authorization: Bearer appkittie_your_key_here
```

API keys are generated from the AppKittie dashboard at [appkittie.com/settings](https://appkittie.com/settings).

## Base URL

```
https://appkittie.com/api/v1
```

## Endpoints

### GET /apps

Search and filter App Store apps.

**Query Parameters:** See [REGISTRY.md](../REGISTRY.md) for the full filter list.

**Response:**
```json
{
  "data": [
    {
      "app_slug": "headspace-meditation-sleep",
      "title": "Headspace: Meditation & Sleep",
      "icon": "https://...",
      "developer": "Headspace Health Inc.",
      "primary_genre": "Health & Fitness",
      "score": 4.9,
      "reviews": 750000,
      "downloads": 500000,
      "historical_counts": { "revenue_last_30d": 2500000 }
    }
  ],
  "pagination": {
    "nextCursor": 50,
    "totalCount": 1234
  }
}
```

**Headers:**
- `X-Credits-Used` — credits consumed
- `X-Credits-Remaining` — remaining balance
- `X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset`

### GET /apps/:appId

Get detailed data for a single app.

**Response:**
```json
{
  "data": {
    "title": "Headspace: Meditation & Sleep",
    "description": "...",
    "meta_ads": [{ "src": "https://...", "poster": "https://..." }],
    "apple_ads": [{ ... }],
    "in_app_purchases": [{ "name": "Annual", "price": "$69.99" }],
    "historical_data": [{ "date": "2026-01-01", "downloads": 15000 }],
    ...
  }
}
```

### GET /keywords/difficulty

Single keyword analysis.

**Query Parameters:**
- `keyword` (required) — keyword to analyze
- `country` (optional) — App Store country code (default: US)

**Response:**
```json
{
  "data": {
    "keyword": "meditation",
    "country": "US",
    "popularity": 65,
    "difficulty": 78,
    "appsCount": 1200,
    "trafficScore": 42,
    "topApps": [
      {
        "appStoreId": "1573759751",
        "title": "Headspace: Meditation & Sleep",
        "icon": "https://...",
        "developer": "Headspace Health Inc.",
        "reviews": 750000,
        "score": 4.9,
        "rank": 1
      }
    ]
  }
}
```

### POST /keywords/difficulty

Batch keyword analysis (up to 10 keywords).

**Body:**
```json
{
  "keywords": ["meditation", "mindfulness", "sleep sounds"],
  "country": "US"
}
```

**Response:**
```json
{
  "data": [
    {
      "keyword": "sleep sounds",
      "country": "US",
      "popularity": 55,
      "difficulty": 45,
      "appsCount": 800,
      "trafficScore": 38
    }
  ]
}
```

Results are sorted by opportunity (best first). Only successfully analyzed keywords are returned.

## Error Codes

| Status | Meaning |
|--------|---------|
| 400 | Invalid parameters |
| 401 | Invalid or missing API key |
| 402 | Insufficient credits |
| 404 | App not found |
| 429 | Rate limit exceeded |
| 503 | Search service unavailable |

## Credit Costs

| Operation | Cost |
|-----------|------|
| Search apps (per hit returned) | 1 credit |
| App detail | 1 credit |
| Keyword difficulty (single) | 10 credits |
| Keyword difficulty (batch, per keyword) | 10 credits |
