# Tool Registry

Tools and integrations that AppKittie skills can use for real-time App Store data.

## AppKittie — Primary Integration

[AppKittie](https://appkittie.com) provides App Store intelligence via REST API and MCP Server.

### Connection Methods

| Method | Best For | Setup |
|--------|----------|-------|
| **MCP Server** | Cursor, Claude Code, AI agents | Add to MCP config (see README) |
| **REST API** | Scripts, dashboards, custom tools | HTTP requests with API key |

### API Endpoints

| Endpoint | Method | Purpose | Cost |
|----------|--------|---------|------|
| `/api/v1/apps` | GET | Search and filter apps | 1 credit/hit |
| `/api/v1/apps/:appId` | GET | Get app detail | 1 credit |
| `/api/v1/keywords/difficulty` | GET | Single keyword analysis | 10 credits |
| `/api/v1/keywords/difficulty` | POST | Batch keyword analysis (up to 10) | 10 credits/keyword |

### MCP Tool ↔ API Mapping

| MCP Tool | API Endpoint | Method |
|----------|-------------|--------|
| `search_apps` | `/api/v1/apps` | GET |
| `get_app_detail` | `/api/v1/apps/:appId` | GET |
| `get_keyword_difficulty` | `/api/v1/keywords/difficulty` | GET |
| `batch_keyword_difficulty` | `/api/v1/keywords/difficulty` | POST |
| `get_supported_countries` | (local, no API call) | — |

### Skill → Tool Mapping

| Skill | Primary Tools Used |
|-------|-------------------|
| `app-discovery` | `search_apps`, `get_app_detail` |
| `keyword-research` | `batch_keyword_difficulty`, `get_keyword_difficulty`, `search_apps` |
| `metadata-optimization` | `batch_keyword_difficulty`, `get_keyword_difficulty` |
| `competitor-analysis` | `search_apps`, `get_app_detail`, `batch_keyword_difficulty` |
| `growth-analysis` | `search_apps`, `get_app_detail` |
| `ad-intelligence` | `search_apps`, `get_app_detail` |
| `revenue-analysis` | `search_apps`, `get_app_detail` |
| `app-marketing-context` | `get_app_detail`, `search_apps` |

### App Data Fields

**List response** (from `search_apps`):
`app_slug`, `icon`, `title`, `developer`, `primary_genre`, `score`, `reviews`, `url`, `downloads`, `historical_counts.revenue_last_30d`, `app_released_date_timestamp`, `app_updated_date_timestamp`, `date_updated_timestamp`, `historical_counts.reviews_growth_7d`

**Detail response** (from `get_app_detail`):
All list fields plus: `description`, `genres`, `languages`, `size`, `version`, `released`, `updated`, `release_notes`, `price`, `currency`, `free`, `developer_url`, `historical_counts`, `historical_data`, `screenshots`, `meta_ads`, `apple_ads`, `in_app_purchases`, `decision_makers`, `socials`, `hiring`, `emails`, `websites`, `topyappers_creators`

### Search Filters

| Filter | Type | Description |
|--------|------|-------------|
| `search` | string | Full-text search |
| `categories` | string[] | App Store categories |
| `sortBy` | enum | growth, rating, reviews, downloads, revenue, trending, newest, updated, released |
| `sortOrder` | enum | asc, desc |
| `priceType` | enum | all, free, paid |
| `minPrice` / `maxPrice` | number | Price range (USD) |
| `minRating` / `maxRating` | number | Star rating (0–5) |
| `minReviews` / `maxReviews` | integer | Review count |
| `minDownloads` / `maxDownloads` | integer | Est. monthly downloads |
| `minRevenue` / `maxRevenue` | integer | Est. monthly revenue (USD) |
| `minLifetimeDownloads` / `maxLifetimeDownloads` | integer | Est. total downloads |
| `minLifetimeRevenue` / `maxLifetimeRevenue` | integer | Est. total revenue (USD) |
| `growthMetric` | enum | reviews, downloads, revenue |
| `growthPeriod` | enum | 7d, 14d, 30d, 60d, 90d |
| `growthType` | enum | all, positive, negative |
| `contentRating` | enum | all, 4+, 9+, 12+, 17+ |
| `languages` | string[] | Supported languages |
| `developer` | string | Developer name |
| `hasWebsite` | boolean | Has developer website |
| `hasCreators` | boolean | Has creator partnerships |
| `hasMetaAds` | boolean | Running Meta ads |
| `hasAppleAds` | boolean | Running Apple Search Ads |
| `hasEmails` | boolean | Has contact emails |
| `limit` | integer | Results per page (1–100) |
| `cursor` | integer | Pagination offset |
