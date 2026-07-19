# Tool Registry

Tools and integrations that AppKittie skills can use for real-time App Store data.

## AppKittie — Primary Integration

[AppKittie](https://appkittie.com) provides Apple App Store and Google Play intelligence via REST API and MCP Server.

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
| `/api/v1/apps/:appId/historicals` | GET | Historical metric time series | 1 credit |
| `/api/v1/ads` | GET | Search and filter ad creatives | 1 credit/hit |
| `/api/v1/ads/:adId` | GET | Get ad detail | 1 credit |
| `/api/v1/creators` | GET | Creator discovery (per app or per category) | 1 credit/creator |
| `/api/v1/organic` | GET | Organic creator videos (per app or per category) | 1 credit/item |
| `/api/v1/keywords/difficulty` | GET | Single keyword analysis | 10 credits |
| `/api/v1/keywords/difficulty` | POST | Batch keyword analysis (up to 10) | 10 credits/keyword |
| `/api/v1/reviews` | GET / POST | Fetch current app reviews in real time | 1 credit/review |

App-scoped endpoints accept any identifier form: app slug, AppKittie app ID, numeric App Store ID, Google Play package name, or store URL.

### MCP Tool ↔ API Mapping

| MCP Tool | API Endpoint | Method |
|----------|-------------|--------|
| `search_apps` | `/api/v1/apps` | GET |
| `get_app_detail` | `/api/v1/apps/:appId` | GET |
| `get_app_historicals` | `/api/v1/apps/:appId/historicals` | GET |
| `search_ads` | `/api/v1/ads` | GET |
| `get_ad_detail` | `/api/v1/ads/:adId` | GET |
| `list_creators` | `/api/v1/creators` | GET |
| `list_organic_content` | `/api/v1/organic` | GET |
| `get_keyword_difficulty` | `/api/v1/keywords/difficulty` | GET |
| `batch_keyword_difficulty` | `/api/v1/keywords/difficulty` | POST |
| `get_app_reviews` | `/api/v1/reviews` | POST |
| `get_supported_countries` | (local, no API call) | — |

### Skill → Tool Mapping

| Skill | Primary Tools Used |
|-------|-------------------|
| `app-discovery` | `search_apps`, `get_app_detail` |
| `keyword-research` | `batch_keyword_difficulty`, `get_keyword_difficulty`, `search_apps` |
| `metadata-optimization` | `batch_keyword_difficulty`, `get_keyword_difficulty` |
| `competitor-analysis` | `search_apps`, `get_app_detail`, `search_ads`, `get_ad_detail`, `batch_keyword_difficulty` |
| `growth-analysis` | `search_apps`, `get_app_detail`, `search_ads` |
| `ad-intelligence` | `search_apps`, `search_ads`, `get_ad_detail`, `get_app_detail` |
| `creator-discovery` | `list_creators`, `list_organic_content`, `search_apps` |
| `revenue-analysis` | `search_apps`, `get_app_detail` |
| `review-analysis` | `get_app_reviews`, `get_app_detail`, `search_apps` |
| `app-marketing-context` | `get_app_detail`, `search_apps`, `search_ads` |

### App Data Fields

**List response** (from `search_apps`):
`app_slug`, `source`, `icon`, `title`, `developer`, `primary_genre`, `score`, `reviews`, `url`, `downloads`, `revenue`, `app_released_date_timestamp`, `app_updated_date_timestamp`, `date_updated_timestamp`, `historical_counts.reviews_growth_7d`

**Detail response** (from `get_app_detail`):
All list fields plus: `description`, `genres`, `languages`, `size`, `version`, `released`, `updated`, `release_notes`, `price`, `currency`, `free`, `developer_url`, `historical_counts`, `historical_data`, `screenshots`, `in_app_purchases`, `decision_makers`, `socials`, `hiring`, `emails`, `websites`, `topyappers_creators`

Ad creatives are fetched separately with `search_ads` and `get_ad_detail`.

### Ad Data Fields

**List response** (from `search_ads`):
`ad_doc_id`, `ad_source`, `ad_network`, `page_name`, `type`, `src`, `poster`, `preview_url`, `title`, `body`, `caption`, `description`, `label`, `cta_text`, `cta_type`, `link_url`, `is_active`, `publisher_platform`, `countries`, `surfaces`, `start_date`, `end_date`, `creative_text`, `app_slug`, `app_title`, `app_url`, `app_icon`, `category`, `ad_language`, `app_downloads`, `app_revenue`, `developer`

**Detail response** (from `get_ad_detail`):
All ad list fields plus deeper delivery/transparency fields such as `transparency_by_location`, `region_stats`, `content`, and compact `app` summary when available.

### Search Filters

| Filter | Type | Description |
|--------|------|-------------|
| `search` | string | Full-text search |
| `source` | enum | `apple_mobile` or `google_mobile` |
| `excludedSource` | enum | `apple_mobile` or `google_mobile` |
| `categories` | string[] | App Store categories |
| `sortBy` | enum | growth, rating, reviews, downloads, revenue, trending, newest, updated, released |
| `sortOrder` | enum | asc, desc |
| `growthMetric` | enum | reviews |
| `growthPeriod` | enum | 7d, 14d, 30d, 60d, 90d |
| `priceType` | enum | all, free, paid |
| `minPrice` / `maxPrice` | number | Price range (USD) |
| `minRating` / `maxRating` | number | Star rating (0–5) |
| `minReviews` / `maxReviews` | integer | Review count |
| `minDownloads` / `maxDownloads` | integer | Est. monthly downloads |
| `minRevenue` / `maxRevenue` | integer | Est. monthly revenue (USD) |
| `minLifetimeDownloads` / `maxLifetimeDownloads` | integer | Est. total downloads |
| `minLifetimeRevenue` / `maxLifetimeRevenue` | integer | Est. total revenue (USD) |
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

### Ad Search Filters

| Filter | Type | Description |
|--------|------|-------------|
| `search` | string | Full-text search across creative text and app metadata |
| `textSearchFields` | string[] | Search fields such as `creative_text`, `title`, `body`, `cta_text`, `page_name`, `developer`, `app_title`, `category` |
| `adSource` | enum | `all`, `meta`, `google` |
| `mediaType` | enum | `all`, `image`, `video` |
| `status` | enum | `all`, `active`, `inactive` |
| `appSlug` / `appId` / `appStoreId` / `appStoreUrl` | string | Ads for one app (any identifier form) |
| `view` | enum | `full`, `compact` — compact returns identity, status, key copy, and app metrics only |
| `categories` / `excludedCategories` | string[] | Advertised app categories |
| `adLanguages` / `excludedAdLanguages` | string[] | Representative country codes mapped to ad language |
| `countries` / `excludedCountries` | string[] | Countries where ads were observed |
| `surfaces` / `excludedSurfaces` | string[] | Ad surfaces or placements |
| `developer` | string | Advertised app developer |
| `startedAfter` / `startedBefore` | integer | Ad start date Unix timestamp bounds |
| `endedAfter` / `endedBefore` | integer | Ad end date Unix timestamp bounds |
| `minAppDownloads` / `maxAppDownloads` | integer | Advertised app estimated monthly downloads |
| `minAppRevenue` / `maxAppRevenue` | integer | Advertised app estimated monthly revenue |
| `sortBy` | enum | `start_date`, `end_date`, `app_downloads`, `app_revenue`, `app_released_timestamp`, `app_updated_timestamp` |
| `sortOrder` | enum | `asc`, `desc` |
| `limit` | integer | Results per page (1–100) |
| `cursor` | integer | Pagination offset |

### Creator Search Filters

| Filter | Type | Description |
|--------|------|-------------|
| any app identifier | string | Scope to one app (`app_slug`, `appId`, `appStoreId`, or `appStoreUrl`) |
| `category` | string | Cross-app discovery across the category's top apps |
| `platform` | string | `tiktok`, `instagram`, or `youtube` |
| `country` | string | Creator country code |
| `minFollowers` / `maxFollowers` | integer | Follower range |
| `sortBy` | enum | `relevance`, `followers` |
| `sortOrder` | enum | `asc`, `desc` |
| `count` / `limit` | integer | Results per page (1–100) |
| `cursor` | integer | Pagination offset |

`list_organic_content` supports the same scope parameters plus `platform`.
