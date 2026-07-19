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

Search and filter Apple App Store and Google Play apps.

**Query Parameters:** See [REGISTRY.md](../REGISTRY.md) for the full filter list.

**Response:**
```json
{
  "data": [
    {
      "app_slug": "headspace-meditation-sleep",
      "source": "apple_mobile",
      "title": "Headspace: Meditation & Sleep",
      "icon": "https://...",
      "developer": "Headspace Health Inc.",
      "primary_genre": "Health & Fitness",
      "score": 4.9,
      "reviews": 750000,
      "downloads": 500000,
      "revenue": 2500000
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

## App Identifiers

App-scoped endpoints accept any of these identifier forms and resolve them automatically: AppKittie app slug, numeric App Store ID, Google Play package name, or store URL. Pass the identifier as `app_slug`/`appSlug`, `appId`, `appStoreId`, or `appStoreUrl`.

### GET /apps/:appId

Get detailed data for a single app. The path segment accepts any identifier form (app slug recommended).

**Response:**
```json
{
  "data": {
    "title": "Headspace: Meditation & Sleep",
    "description": "...",
    "in_app_purchases": [{ "name": "Annual", "price": "$69.99" }],
    "historical_data": [{ "date": "2026-01-01", "downloads": 15000 }],
    ...
  }
}
```

Ad creatives are not embedded in app detail responses. Fetch them separately with `/ads` and `/ads/:adId`.

### GET /apps/:appId/historicals

Historical metric time series (reviews, score, downloads, revenue, MAU, DAU, size, price) for a single app. Query with `period` (`30d`, `90d`, `300d`, `all`) and an optional comma-separated `metrics` list.

### GET /ads

Search and filter Meta and Google ad creatives.

**Query Parameters:** See [REGISTRY.md](../REGISTRY.md) for the full ad filter list. Use `view=compact` for trimmed payloads (identity, status, key copy, and app metrics only) in automated workflows.

**Response:**
```json
{
  "data": [
    {
      "ad_doc_id": "meta_ad_123",
      "ad_source": "meta",
      "type": "video",
      "src": "https://...",
      "poster": "https://...",
      "title": "Sleep better tonight",
      "body": "Try guided meditations for deep sleep.",
      "cta_text": "Install Now",
      "is_active": true,
      "start_date": 1751328000,
      "app_slug": "headspace-meditation-sleep",
      "app_title": "Headspace: Meditation & Sleep",
      "developer": "Headspace Health Inc."
    }
  ],
  "pagination": {
    "nextCursor": 20,
    "totalCount": 250
  }
}
```

### GET /ads/:adId

Get detailed data for a single ad creative.

**Response:**
```json
{
  "data": {
    "ad_doc_id": "meta_ad_123",
    "ad_source": "meta",
    "type": "video",
    "src": "https://...",
    "poster": "https://...",
    "title": "Sleep better tonight",
    "body": "Try guided meditations for deep sleep.",
    "app_slug": "headspace-meditation-sleep",
    "app": {
      "app_slug": "headspace-meditation-sleep",
      "title": "Headspace: Meditation & Sleep",
      "developer": "Headspace Health Inc."
    }
  }
}
```

### GET /creators

Creator profiles for one app or across a category.

**Query Parameters:**
- any app identifier, or `category` for cross-app discovery
- `platform`, `country`, `minFollowers` / `maxFollowers` — creator filters
- `sortBy` (`relevance` | `followers`), `sortOrder`, `count`, `cursor`

**Response:** each creator includes `user_id`, `handle`, `source`, `country`, `followers`, `avatar_url`, plus `app_slug` and `app_title`.

### GET /organic

Organic creator videos with hosted media for one app or across a category. Supports the same scope parameters plus `platform`, `count`, and `cursor`.

### GET /keywords/difficulty

Single keyword analysis.

**Query Parameters:**
- `keyword` (required) — keyword to analyze
- `country` (optional) — App Store country code (default: US)
- `source` (optional) — `apple_mobile` or `google_mobile` (default: `apple_mobile`)
- `topAppsLimit` (optional) — number of top-ranking apps to include, 0–50 (default: 50)
- `includeTopApps` (optional) — set `false` for a metrics-only response

**Response:**
```json
{
  "data": {
    "keyword": "meditation",
    "country": "US",
    "source": "apple_mobile",
    "popularity": 65,
    "difficulty": 78,
    "appsCount": 1200,
    "trafficScore": 42,
    "topApps": [
      {
        "appStoreId": "1573759751",
        "source": "apple_mobile",
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
  "country": "US",
  "source": "apple_mobile"
}
```

**Response:**
```json
{
  "data": [
    {
      "keyword": "sleep sounds",
      "country": "US",
      "source": "apple_mobile",
      "popularity": 55,
      "difficulty": 45,
      "appsCount": 800,
      "trafficScore": 38
    }
  ]
}
```

Results are sorted by opportunity (best first). Only successfully analyzed keywords are returned.

### POST /reviews

Fetch current user reviews in real time directly from the Apple App Store or
Google Play. Each request retrieves current store data; it does not read from
or write to AppKittie's review-monitor database. Also available as `GET /reviews`
with the same fields as query parameters.

**Body:**
```json
{
  "appId": "284882215",
  "source": "apple_mobile",
  "country": "US",
  "maxReviews": 100,
  "offset": 0
}
```

**Body Parameters:**
- `appId` (required) — any app identifier: numeric App Store ID, Google Play package name, AppKittie app slug, or store URL (`appSlug` and `appStoreUrl` accepted as aliases)
- `source` (optional) — `apple_mobile` or `google_mobile`; inferred from the identifier if omitted
- `country` (optional) — App Store country code (default: US)
- `maxReviews` (optional) — max reviews to return, 1–300 (default: 100)
- `offset` (optional) — pagination offset (default: 0)

**Response:**
```json
{
  "data": {
    "appId": 284882215,
    "source": "apple_mobile",
    "country": "us",
    "retrievalMode": "realtime",
    "fetchedAt": "2026-07-18T10:30:00.000Z",
    "reviews": [
      {
        "id": "10458723456",
        "rating": 5,
        "title": "Great app!",
        "body": "Love the new features.",
        "reviewerNickname": "AppFan2024",
        "date": "2025-12-15T10:30:00Z",
        "country": "us"
      }
    ],
    "nextOffset": 100,
    "totalFetched": 100
  }
}
```

Paginate by passing the `nextOffset` value as `offset` in the next request. When `nextOffset` is `null`, there are no more reviews.

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
| App historicals | 1 credit |
| Search ads (per ad returned) | 1 credit |
| Ad detail | 1 credit |
| Creators (per creator returned) | 1 credit |
| Organic content (per item returned) | 1 credit |
| Keyword difficulty (single) | 10 credits |
| Keyword difficulty (batch, per keyword) | 10 credits |
| App reviews (per review returned) | 1 credit |
