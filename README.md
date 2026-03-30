# AppKittie — App Store Intelligence Skills & MCP Server

AI agent skills for **App Store intelligence**, **ASO**, and **competitive analysis**. Built for indie developers, app marketers, and growth teams who want **Cursor**, **Claude Code**, or any Agent Skills-compatible AI assistant to help with app discovery, keyword research, revenue analysis, ad intelligence, and competitor tracking.

Powered by real App Store data via the [AppKittie API](https://appkittie.com). Access a database of **2M+ iOS apps** with downloads, revenue estimates, growth metrics, and ad intelligence.

## Quick Start

**Cursor** — Settings (Cmd+Shift+J) → Rules → Add Rule → Remote Rule (Github) → paste `https://github.com/appkittie/mcp`

**Claude Code** — `npx skills add appkittie/mcp`

**Manual** — `git clone https://github.com/appkittie/mcp.git && cp -r mcp/skills/* .cursor/skills/`

Then ask your agent:

```
"Find the most profitable apps in the Health & Fitness category"
"Research keywords for a meditation app targeting the US market"
"Analyze my competitors — my app ID is 1234567890"
"Which apps are running Meta ads in the productivity category?"
"What apps are growing fastest this week?"
"Optimize my App Store title and subtitle for these keywords"
"Set up my app marketing context for ongoing analysis"
"What's the revenue potential in the education category?"
```

Or invoke directly: `/app-discovery`, `/keyword-research`, `/metadata-optimization`, `/competitor-analysis`, `/growth-analysis`, `/ad-intelligence`, `/revenue-analysis`

## Skills

### Core Intelligence

| Skill | What it does |
|-------|-------------|
| [app-discovery](skills/app-discovery) | Search and filter iOS apps by category, revenue, downloads, growth, ratings, ads, and more |
| [keyword-research](skills/keyword-research) | Evaluate keywords by popularity, difficulty, traffic score, and top-ranking apps — build a prioritized keyword strategy |
| [metadata-optimization](skills/metadata-optimization) | Write optimized title, subtitle, keyword field, and description — with 3 variants and character counts |
| [competitor-analysis](skills/competitor-analysis) | Keyword gaps, revenue comparison, ad strategy teardown, and positioning map |

### Growth & Revenue

| Skill | What it does |
|-------|-------------|
| [growth-analysis](skills/growth-analysis) | Find fastest-growing apps, analyze growth drivers, spot market movers and emerging trends |
| [revenue-analysis](skills/revenue-analysis) | Revenue benchmarking, monetization model analysis, in-app purchase patterns, and pricing strategy |
| [ad-intelligence](skills/ad-intelligence) | Discover which apps run Meta ads and Apple Search Ads, analyze creative strategies, find UA opportunities |

### Foundation

| Skill | What it does |
|-------|-------------|
| [app-marketing-context](skills/app-marketing-context) | Create a context document (app, audience, competitors, goals) that all other skills reference |

## How It Works

```
You: "Find the most profitable fitness apps"

Agent:
  1. Reads app-discovery/SKILL.md (framework, output template)
  2. Calls AppKittie API → search_apps(categories: ["health-fitness"],
     sortBy: "revenue", limit: 20)
  3. Analyzes results: revenue distribution, growth patterns, pricing models
  4. Returns: Top Apps Table + Revenue Insights + Niche Opportunities

You: "Now research keywords for a meditation app"

Agent:
  1. Reads keyword-research/SKILL.md
  2. Calls batch_keyword_difficulty(keywords: ["meditation", "mindfulness", ...])
  3. Deep dives with get_keyword_difficulty on top opportunities
  4. Returns: Keyword Report + Opportunity Scores + Strategy Recommendation
```

Skills reference each other — `competitor-analysis` suggests running `keyword-research` for gaps found, which feeds into `metadata-optimization` for implementation.

## MCP Server

The MCP server runs on Cloudflare Workers and proxies the AppKittie API, making it accessible to any MCP-compatible AI agent.

### Setup

1. Get your API key at [appkittie.com/settings/api-keys](https://appkittie.com/settings/api-keys) — copy it immediately, it's only shown once
2. Add to your MCP configuration:

```json
{
  "mcpServers": {
    "appkittie": {
      "url": "https://mcp.appkittie.com",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### Tools

| Tool | What it does | Credits |
|------|-------------|---------|
| `search_apps` | Search and filter iOS apps with 30+ filter parameters | 1 per app returned |
| `get_app_detail` | Full app data: metadata, revenue, ads, IAPs, creator partnerships, contacts, historical data | 1 per request |
| `get_keyword_difficulty` | Single keyword analysis with popularity, difficulty, traffic score, and top-ranking apps | 10 per request |
| `batch_keyword_difficulty` | Analyze up to 10 keywords at once, sorted by opportunity score | 10 per keyword |
| `get_supported_countries` | List valid App Store country codes | Free |

### Prompts

| Prompt | What it does |
|--------|-------------|
| `discover_niche` | Guided workflow to find profitable niches in a category |
| `competitor_analysis` | Step-by-step competitive intelligence gathering |
| `keyword_research` | Structured keyword research and prioritization |
| `app_growth_report` | Growth trend analysis with gainers and losers |
| `ad_intelligence` | Ad landscape analysis for a category or niche |

## API Reference

**Base URL:** `https://appkittie.com/api/v1`

**Authentication:** Bearer token in the `Authorization` header. Generate keys from your [dashboard](https://appkittie.com/settings/api-keys).

```bash
curl -X GET "https://appkittie.com/api/v1/apps?search=fitness&limit=5" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Endpoints

| Endpoint | Method | Description | Credits |
|----------|--------|-------------|---------|
| `/api/v1/apps` | `GET` | Search and filter apps | 1 per app returned |
| `/api/v1/apps/:appId` | `GET` | Get detailed app data | 1 per request |
| `/api/v1/keywords/difficulty` | `GET` | Single keyword difficulty | 10 per request |
| `/api/v1/keywords/difficulty` | `POST` | Batch keywords (up to 10) | 10 per keyword |

### Response Format

All successful responses wrap data in a `data` field. List endpoints include cursor-based pagination:

```json
{
  "data": [{ "title": "Calm", "score": 4.8, "downloads": 85000, ... }],
  "pagination": { "nextCursor": 50, "totalCount": 12450 }
}
```

Pass `nextCursor` as the `cursor` query parameter to fetch the next page. When `nextCursor` is `null`, there are no more results.

### Search Filters

The `search_apps` tool / `GET /api/v1/apps` endpoint supports 30+ filters. All filters combine with AND logic.

**Search:** `search` — full-text across title, developer, and description

**Categories:** `categories`, `excludedCategories` — comma-separated category names

**Metrics:** `minDownloads`/`maxDownloads`, `minRevenue`/`maxRevenue`, `minRating`/`maxRating`, `minReviews`/`maxReviews`, `minLifetimeDownloads`/`maxLifetimeDownloads`, `minLifetimeRevenue`/`maxLifetimeRevenue`

**Price:** `priceType` (all/free/paid), `minPrice`/`maxPrice`

**Growth:** `growthPeriod` (7d/14d/30d/60d/90d), `growthType` (all/positive/negative), `minGrowth`/`maxGrowth`

**Intelligence:** `hasMetaAds`, `hasAppleAds`, `hasCreators`, `hasEmails`, `hasWebsite`

**Content:** `contentRating` (all/4+/9+/12+/17+), `languages`, `developer`

**Dates:** `releasedAfter`, `updatedAfter` — Unix timestamps

**Sorting:** `sortBy` (growth/rating/reviews/updated/released/downloads/revenue/trending/newest), `sortOrder` (asc/desc)

See [tools/REGISTRY.md](tools/REGISTRY.md) for the full filter reference.

### Example Requests

Search for high-revenue fitness apps:

```bash
curl -X GET "https://appkittie.com/api/v1/apps?search=fitness&categories=Health+%26+Fitness&minRevenue=10000&sortBy=revenue&sortOrder=desc&limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Batch keyword analysis:

```bash
curl -X POST "https://appkittie.com/api/v1/keywords/difficulty" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["meditation", "sleep tracker", "mindfulness", "breathing exercises", "yoga"], "country": "US"}'
```

### Credits

The API uses credit-based billing. Each call consumes credits based on the endpoint and data returned.

- **List Apps** charges 1 credit per app in the response. Requesting `limit=50` with 50 results costs 50 credits. If your balance is lower than the limit, the response is automatically truncated.
- **Batch Keywords** charges 10 credits per keyword that returns data. Duplicates are deduplicated before processing.
- **Keyword Difficulty** charges 10 credits per request.
- **Get App Detail** charges 1 credit per request.

Every response includes `X-Credits-Used` and `X-Credits-Remaining` headers. Check your balance from the [API Keys page](https://appkittie.com/settings/api-keys) or inspect these headers.

### Rate Limiting

Rate limits are enforced per API key with a 60-second sliding window.

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Max requests per 60-second window |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when the window resets |

When exceeded, the API returns `429` with the reset timestamp. Use exponential backoff or wait for the reset.

### Error Handling

Errors return JSON with an `error` field. Validation errors include a `details` object with field-level messages.

| Status | Meaning |
|--------|---------|
| `400` | Invalid parameters — check `details` for specifics |
| `401` | Invalid or missing API key |
| `402` | Insufficient credits — top up or reduce request scope |
| `404` | App not found |
| `429` | Rate limit exceeded — wait for `X-RateLimit-Reset` |
| `500` | Internal server error |
| `503` | Search service temporarily unavailable |

### Data Available

**App list fields:** Title, icon, developer, category, rating, reviews, downloads estimate, revenue estimate (last 30 days), growth metrics across 7/14/30/60/90-day windows, release and update dates

**App detail fields:** Everything above plus: full description, screenshots, version history, in-app purchases (name, price, duration), Meta ad creatives (image/video, headline, CTA, active status, dates), Apple Search Ads data by country (placement, format, audience targeting, creative assets), creator/influencer partnerships (handle, platform, followers, country), decision-maker contacts (name, email, LinkedIn), social links, hiring status, historical time-series data for rank/reviews/revenue/downloads

**Keyword fields:** Popularity (0–100, search volume proxy), difficulty (0–100, competition), app count, traffic score (0–100, combined opportunity metric), top-ranking apps with title/icon/reviews/score/rank

## Installation

### Cursor

| Method | Command |
|--------|---------|
| GitHub Import | Settings → Rules → Add Rule → Remote Rule → `https://github.com/appkittie/mcp` |
| Project-level | `cp -r mcp/skills/* .cursor/skills/` |
| Global | `cp -r mcp/skills/* ~/.cursor/skills/` |

### Claude Code

| Method | Command |
|--------|---------|
| CLI | `npx skills add appkittie/mcp` |
| Specific skills | `npx skills add appkittie/mcp --skill keyword-research competitor-analysis` |
| Manual | `cp -r mcp/skills/* .claude/skills/` |

### Any Agent

```bash
git submodule add https://github.com/appkittie/mcp.git .agents/appkittie
```

Works with any tool that supports the Agent Skills standard (`.agents/skills/`, `.cursor/skills/`, `.claude/skills/`, `.codex/skills/`).

## Full Documentation

For complete API documentation with interactive examples, see [docs.appkittie.com](https://docs.appkittie.com).

## Contributing

PRs welcome — fix an inaccuracy, improve a framework, or add a new skill. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
