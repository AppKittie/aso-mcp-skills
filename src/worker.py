"""
AppKittie MCP Server — Cloudflare Workers (Python)

An MCP (Model Context Protocol) server that proxies the AppKittie API,
enabling AI agents to discover Apple App Store and Google Play apps, analyze
competitors, research keywords, and access mobile app intelligence data.

Authentication: Clients pass their AppKittie API key as a Bearer token
in the Authorization header. The server forwards it to the AppKittie API.
"""

from js import Response, Headers, fetch
import js
from pyodide.ffi import to_js
import json
from urllib.parse import urlencode


# ═══════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════

API_BASE = "https://appkittie.com"
PROTOCOL_VERSION = "2025-03-26"
SERVER_NAME = "appkittie"
SERVER_VERSION = "1.0.0"

SORT_BY_OPTIONS = [
    "growth", "rating", "reviews", "updated", "released",
    "app_updated", "downloads", "revenue", "trending", "newest",
    "historical_counts.revenue_last_30d",
]

SORT_ORDERS = ["asc", "desc"]

GROWTH_PERIODS = ["7d", "14d", "30d", "60d", "90d"]
GROWTH_TYPES = ["all", "positive", "negative"]
GROWTH_METRICS = ["reviews", "downloads", "revenue"]

CONTENT_RATINGS = ["all", "4+", "9+", "12+", "17+"]
PRICE_TYPES = ["all", "free", "paid"]
STORE_SOURCES = ["apple_mobile", "google_mobile"]

APP_STORE_COUNTRY_CODES = [
    "US", "GB", "CA", "AU", "NZ", "IE",
    "DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH", "PT", "LU",
    "SE", "NO", "DK", "FI", "IS",
    "JP", "KR", "CN", "TW", "HK", "SG",
    "BR", "MX", "IN", "ID", "TH", "MY", "PH", "VN",
    "TR", "SA", "AE", "IL", "EG", "NG", "ZA",
    "PL", "CZ", "RO", "HU", "UA", "RU",
    "AR", "CL", "CO", "PE",
    "GR", "BG", "HR", "SK", "SI", "LT", "LV", "EE",
    "RS", "BA", "MK", "AL", "ME",
    "QA", "KW", "BH", "OM", "JO", "LB",
    "KZ", "UZ", "PK", "BD", "LK",
    "KH", "MM", "LA", "NP",
]


# ═══════════════════════════════════════════════════════════════════════════
# Tool definitions
# ═══════════════════════════════════════════════════════════════════════════

TOOLS = [
    {
        "name": "search_apps",
        "description": (
            "Search and filter mobile apps from the Apple App Store and Google Play. "
            "Discover apps by category, revenue, downloads, growth, ratings, "
            "and more. Supports full-text search, advanced filtering, sorting, "
            "and cursor-based pagination. Returns app metadata including title, "
            "icon, developer, genre, rating, reviews, downloads, and revenue. "
            "Costs 1 credit per app returned."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "search": {
                    "type": "string",
                    "description": "Full-text search query (e.g. 'fitness tracker', 'meditation app')",
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "App Store categories to filter by "
                        "(e.g. ['games', 'productivity', 'health-fitness'])"
                    ),
                },
                "excludedCategories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Categories to exclude from results",
                },
                "source": {
                    "type": "string",
                    "enum": STORE_SOURCES,
                    "description": "Store source to include: apple_mobile or google_mobile",
                },
                "excludedSource": {
                    "type": "string",
                    "enum": STORE_SOURCES,
                    "description": "Store source to exclude: apple_mobile or google_mobile",
                },
                "sortBy": {
                    "type": "string",
                    "enum": SORT_BY_OPTIONS,
                    "description": (
                        "Sort results by: growth, rating, reviews, updated, released, "
                        "downloads, revenue, trending, newest. Default: growth"
                    ),
                },
                "sortOrder": {
                    "type": "string",
                    "enum": SORT_ORDERS,
                    "description": "Sort direction (default: desc)",
                },
                "priceType": {
                    "type": "string",
                    "enum": PRICE_TYPES,
                    "description": "Filter by pricing: all, free, or paid (default: all)",
                },
                "minPrice": {
                    "type": "number",
                    "description": "Minimum app price in USD",
                },
                "maxPrice": {
                    "type": "number",
                    "description": "Maximum app price in USD",
                },
                "minRating": {
                    "type": "number",
                    "description": "Minimum star rating (0–5)",
                },
                "maxRating": {
                    "type": "number",
                    "description": "Maximum star rating (0–5)",
                },
                "minReviews": {
                    "type": "integer",
                    "description": "Minimum number of reviews",
                },
                "maxReviews": {
                    "type": "integer",
                    "description": "Maximum number of reviews",
                },
                "minDownloads": {
                    "type": "integer",
                    "description": "Minimum estimated monthly downloads",
                },
                "maxDownloads": {
                    "type": "integer",
                    "description": "Maximum estimated monthly downloads",
                },
                "minRevenue": {
                    "type": "integer",
                    "description": "Minimum estimated monthly revenue (USD)",
                },
                "maxRevenue": {
                    "type": "integer",
                    "description": "Maximum estimated monthly revenue (USD)",
                },
                "minLifetimeDownloads": {
                    "type": "integer",
                    "description": "Minimum estimated lifetime downloads",
                },
                "maxLifetimeDownloads": {
                    "type": "integer",
                    "description": "Maximum estimated lifetime downloads",
                },
                "minLifetimeRevenue": {
                    "type": "integer",
                    "description": "Minimum estimated lifetime revenue (USD)",
                },
                "maxLifetimeRevenue": {
                    "type": "integer",
                    "description": "Maximum estimated lifetime revenue (USD)",
                },
                "growthMetric": {
                    "type": "string",
                    "enum": GROWTH_METRICS,
                    "description": "Which metric to measure growth on: reviews, downloads, or revenue (default: reviews)",
                },
                "growthPeriod": {
                    "type": "string",
                    "enum": GROWTH_PERIODS,
                    "description": "Growth period window: 7d, 14d, 30d, 60d, 90d (default: 7d)",
                },
                "growthType": {
                    "type": "string",
                    "enum": GROWTH_TYPES,
                    "description": "Growth direction: all, positive, or negative (default: all)",
                },
                "minGrowth": {
                    "type": "number",
                    "description": "Minimum growth value",
                },
                "maxGrowth": {
                    "type": "number",
                    "description": "Maximum growth value",
                },
                "contentRating": {
                    "type": "string",
                    "enum": CONTENT_RATINGS,
                    "description": "Content rating filter: all, 4+, 9+, 12+, 17+ (default: all)",
                },
                "languages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by supported languages",
                },
                "developer": {
                    "type": "string",
                    "description": "Filter by developer name",
                },
                "releasedAfter": {
                    "type": "integer",
                    "description": "Only apps released after this Unix timestamp",
                },
                "updatedAfter": {
                    "type": "integer",
                    "description": "Only apps updated after this Unix timestamp",
                },
                "hasWebsite": {
                    "type": "boolean",
                    "description": "Only apps with a developer website",
                },
                "hasCreators": {
                    "type": "boolean",
                    "description": "Only apps with known creator/influencer partnerships",
                },
                "hasMetaAds": {
                    "type": "boolean",
                    "description": "Only apps running Meta (Facebook/Instagram) ads",
                },
                "hasAppleAds": {
                    "type": "boolean",
                    "description": "Only apps running Apple Search Ads",
                },
                "hasEmails": {
                    "type": "boolean",
                    "description": "Only apps with contact emails available",
                },
                "limit": {
                    "type": "integer",
                    "description": "Results per page (1–100, default: 50)",
                    "default": 50,
                },
                "cursor": {
                    "type": "integer",
                    "description": "Pagination cursor (offset). Use nextCursor from previous response.",
                },
            },
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": True},
    },
    {
        "name": "get_app_detail",
        "description": (
            "Get detailed information about a specific mobile app by its ID. "
            "Returns comprehensive data including metadata, description, "
            "screenshots, historical download/revenue data, Meta ads, "
            "Apple Search Ads, in-app purchases, decision-makers, "
            "social links, and creator partnerships. "
            "Costs 1 credit per request."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "appId": {
                    "type": "string",
                    "description": (
                        "The app's unique identifier. Can be the Meilisearch document ID "
                        "or the app's store ID / slug."
                    ),
                },
            },
            "required": ["appId"],
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": True},
    },
    {
        "name": "get_keyword_difficulty",
        "description": (
            "Analyze a single Apple App Store or Google Play keyword's competitiveness. Returns "
            "popularity score (search volume proxy), difficulty score, "
            "number of competing apps, traffic score, and the top-ranking "
            "apps for that keyword. Use this for deep-dive analysis of "
            "individual keywords. Costs 10 credits per request."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "The keyword to analyze (e.g. 'fitness tracker', 'meditation')",
                },
                "country": {
                    "type": "string",
                    "description": (
                        "App Store country code (e.g. 'US', 'GB', 'DE'). "
                        "Default: US. Use get_supported_countries to see all valid codes."
                    ),
                },
                "source": {
                    "type": "string",
                    "enum": STORE_SOURCES,
                    "description": "Store source to analyze: apple_mobile or google_mobile. Default: apple_mobile.",
                },
            },
            "required": ["keyword"],
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": True},
    },
    {
        "name": "batch_keyword_difficulty",
        "description": (
            "Analyze multiple Apple App Store or Google Play keywords at once (up to 10). Returns "
            "popularity, difficulty, app count, and traffic score for each keyword, "
            "sorted by opportunity (best keywords first). More efficient than "
            "individual lookups when researching multiple keywords. "
            "Costs 10 credits per successfully analyzed keyword."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Keywords to analyze (1–10). Duplicates are removed. "
                        "e.g. ['fitness', 'workout', 'exercise tracker']"
                    ),
                },
                "country": {
                    "type": "string",
                    "description": (
                        "App Store country code (e.g. 'US', 'GB', 'DE'). Default: US."
                    ),
                },
                "source": {
                    "type": "string",
                    "enum": STORE_SOURCES,
                    "description": "Store source to analyze: apple_mobile or google_mobile. Default: apple_mobile.",
                },
            },
            "required": ["keywords"],
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": True},
    },
    {
        "name": "get_supported_countries",
        "description": (
            "Get the list of supported App Store country codes for keyword "
            "research. Use this to validate country codes before calling "
            "get_keyword_difficulty or batch_keyword_difficulty. Free — no credit cost."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": True},
    },
    {
        "name": "get_app_reviews",
        "description": (
            "Fetch user reviews for a specific Apple App Store or Google Play app. "
            "Returns reviews with star ratings, titles, body text, reviewer "
            "nicknames, and dates. Supports pagination via offset for iterating "
            "through all available reviews. Use this to understand user sentiment, "
            "common complaints, feature requests, and overall app reception. "
            "Costs 1 credit per review returned."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "appId": {
                    "type": "string",
                    "description": (
                        "The store-specific app ID. Use numeric App Store IDs for Apple apps "
                        "or package names for Google Play apps."
                    ),
                },
                "source": {
                    "type": "string",
                    "enum": STORE_SOURCES,
                    "description": (
                        "Store source: apple_mobile or google_mobile. If omitted, AppKittie "
                        "infers Apple for numeric IDs and Google Play for package names."
                    ),
                },
                "country": {
                    "type": "string",
                    "description": (
                        "App Store country code (e.g. 'US', 'GB', 'DE'). "
                        "Default: US. Reviews are country-specific."
                    ),
                },
                "maxReviews": {
                    "type": "integer",
                    "description": "Maximum reviews to fetch (1–300, default: 100)",
                },
                "offset": {
                    "type": "integer",
                    "description": (
                        "Pagination offset. Use nextOffset from previous response "
                        "to fetch the next page of reviews."
                    ),
                },
            },
            "required": ["appId"],
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": True},
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# JSON-RPC helpers
# ═══════════════════════════════════════════════════════════════════════════

def rpc_success(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def rpc_error(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def tool_result(text, is_error=False):
    return {
        "content": [{"type": "text", "text": text}],
        **({"isError": True} if is_error else {}),
    }


# ═══════════════════════════════════════════════════════════════════════════
# Instructions for AI agents
# ═══════════════════════════════════════════════════════════════════════════

INSTRUCTIONS = """# AppKittie MCP — Agent Guide

You have access to the AppKittie API through this MCP server. It lets you discover **mobile apps** across the Apple App Store and Google Play, analyze **competitors**, research **store keywords**, read **user reviews**, and access **download/revenue intelligence**.

## 1. Discovering & Searching Apps

Use `search_apps` to find and filter apps across the Apple App Store and Google Play.

**Key filters:**
- `search` — full-text search query (e.g. "meditation app", "calorie tracker")
- `source` — store source: `apple_mobile` or `google_mobile`
- `categories` — App Store categories (e.g. ["games", "health-fitness", "productivity"])
- `sortBy` — sort by: `growth`, `rating`, `reviews`, `downloads`, `revenue`, `trending`, `newest`, `updated`, `released`
- `sortOrder` — "desc" (default) or "asc"
- `growthMetric` — what to measure growth by: `reviews`, `downloads`, or `revenue`
- `growthPeriod` — time window: `7d`, `14d`, `30d`, `60d`, `90d`

**Revenue/download filters:**
- `minDownloads` / `maxDownloads` — estimated monthly downloads
- `minRevenue` / `maxRevenue` — estimated monthly revenue (USD)
- `minLifetimeDownloads` / `maxLifetimeDownloads` — total estimated downloads
- `minLifetimeRevenue` / `maxLifetimeRevenue` — total estimated revenue (USD)

**Marketing intelligence:**
- `hasMetaAds: true` — only apps running Meta (Facebook/Instagram) ads
- `hasAppleAds: true` — only apps running Apple Search Ads
- `hasCreators: true` — only apps with known creator/influencer partnerships
- `hasEmails: true` — only apps with contact emails available

**Cost:** 1 credit per app returned. Control costs with `limit` (default 50, max 100).

**Pagination:** Use `cursor` from the `pagination.nextCursor` field in the response.

## 2. Getting App Details

Use `get_app_detail` with an app ID to get comprehensive data about a single app.

**Returns:**
- Full metadata (title, description, icon, screenshots, genres, languages)
- Pricing info (price, currency, in-app purchases)
- Ratings and reviews (overall + current version)
- Developer info (name, website, socials, decision-makers, hiring status)
- **Historical data** — time series of downloads, revenue, reviews, and ratings
- **Meta ads** — Facebook/Instagram ad creatives the app is running
- **Apple ads** — Apple Search Ads transparency data
- **Creator partnerships** — influencers promoting the app (via TopYappers)

**Cost:** 1 credit per request.

## 3. Keyword Research

Two tools for Apple App Store and Google Play keyword analysis:

### Single Keyword — `get_keyword_difficulty`
Deep analysis of one keyword. Returns:
- **Popularity** — search volume proxy (higher = more searches)
- **Difficulty** — competition score (higher = harder to rank)
- **Apps Count** — number of apps competing for this keyword
- **Traffic Score** — estimated traffic potential
- **Top Apps** — the apps currently ranking for this keyword (with title, icon, source, reviews, score, rank)

**Cost:** 10 credits per request.

### Batch Keywords — `batch_keyword_difficulty`
Analyze up to 10 keywords at once. Results are sorted by opportunity (best first). Returns the same metrics per keyword except top apps.

**Cost:** 10 credits per successfully analyzed keyword.

### Country Codes
Use `get_supported_countries` (free) to see valid country codes. Keywords are country-specific — "fitness" may have very different metrics in US vs DE.
Use `source: "google_mobile"` to analyze Google Play instead of the default `apple_mobile`.

## 4. App Reviews

Use `get_app_reviews` to fetch user reviews for Apple App Store or Google Play apps.

**Parameters:**
- `appId` (required) — numeric App Store ID or Google Play package name
- `source` — `apple_mobile` or `google_mobile`; omitted values are inferred from `appId`
- `country` — country code (default: US). Reviews are country-specific
- `maxReviews` — number of reviews to fetch (1–300, default: 100)
- `offset` — pagination offset. Use `nextOffset` from previous response

**Returns:**
- Individual reviews with `rating` (1–5), `title`, `body`, `reviewerNickname`, `date`
- `nextOffset` for pagination (`null` when no more reviews)
- `totalFetched` — number of reviews in this response

**Cost:** 1 credit per review returned.

**Use cases:**
- **Sentiment analysis** — understand what users love and hate about an app
- **Feature request mining** — find the most requested features in reviews
- **Competitor weakness detection** — read competitor reviews for complaints you can address
- **Rating trend context** — understand why ratings changed by reading recent reviews
- **Cross-country comparison** — compare reviews across different markets

**Pagination:** Fetch all reviews by starting with `offset: 0`, then using `nextOffset` from each response until it returns `null`.

## Credit Costs Summary

| Tool | Cost |
|------|------|
| search_apps | 1 credit per app returned |
| get_app_detail | 1 credit per request |
| get_keyword_difficulty | 10 credits per request |
| batch_keyword_difficulty | 10 credits per keyword (only charged for successful scrapes) |
| get_app_reviews | 1 credit per review returned |
| get_supported_countries | FREE |

## Tips for Agents

- **Start broad, then narrow:** Use `search_apps` with minimal filters first to understand the landscape, then add filters to zero in.
- **Growth is powerful:** Sort by `growth` with `growthMetric=downloads` and `growthPeriod=7d` to find apps gaining traction right now.
- **Find competitors:** Search for apps in the same category with similar download/revenue ranges.
- **Revenue intelligence:** Use `minRevenue` / `maxRevenue` to find apps in specific revenue brackets. Combine with categories to find profitable niches.
- **Ad intelligence:** `hasMetaAds=true` reveals which apps are actively spending on user acquisition — great for competitive analysis.
- **Keyword research workflow:** Start with `batch_keyword_difficulty` to evaluate multiple keyword ideas, then use `get_keyword_difficulty` for deep dives on the most promising ones.
- **Be credit-efficient:** Use smaller `limit` values when exploring. Default is 50, but 10–20 is often enough for initial discovery.
- **Country matters:** Keyword and review data vary significantly by country. Always specify the target market.
- **Review analysis workflow:** Use `get_app_reviews` to understand user sentiment, then combine with `get_app_detail` for the full picture. Compare competitor reviews to find positioning opportunities.
"""


# ═══════════════════════════════════════════════════════════════════════════
# MCP Prompts — reusable workflow templates for agents
# ═══════════════════════════════════════════════════════════════════════════

PROMPTS = [
    {
        "name": "discover_niche",
        "description": (
            "Discover a profitable App Store or Google Play niche. Analyzes categories, "
            "revenue ranges, and growth patterns to find opportunities."
        ),
        "arguments": [
            {
                "name": "category",
                "description": "App Store category to explore (e.g. 'health-fitness', 'productivity')",
                "required": True,
            },
            {
                "name": "revenue_range",
                "description": "Target monthly revenue range (e.g. '1000-10000')",
                "required": False,
            },
            {
                "name": "source",
                "description": "Store source: apple_mobile or google_mobile. Default: apple_mobile.",
                "required": False,
            },
        ],
    },
    {
        "name": "competitor_analysis",
        "description": (
            "Analyze competitors for a specific app or keyword. "
            "Finds similar apps, compares metrics, and identifies gaps."
        ),
        "arguments": [
            {
                "name": "app_or_keyword",
                "description": "App ID to analyze, or a keyword describing the niche",
                "required": True,
            },
        ],
    },
    {
        "name": "keyword_research",
        "description": (
            "Research and prioritize App Store or Google Play keywords for an app. "
            "Evaluates search volume, difficulty, and opportunity."
        ),
        "arguments": [
            {
                "name": "seed_keywords",
                "description": "Comma-separated seed keywords (e.g. 'fitness,workout,exercise')",
                "required": True,
            },
            {
                "name": "country",
                "description": "Target country code (e.g. 'US', 'GB'). Default: US",
                "required": False,
            },
            {
                "name": "source",
                "description": "Store source: apple_mobile or google_mobile. Default: apple_mobile.",
                "required": False,
            },
        ],
    },
    {
        "name": "app_growth_report",
        "description": (
            "Generate a growth report — find the fastest-growing apps "
            "in a category or across the entire App Store."
        ),
        "arguments": [
            {
                "name": "category",
                "description": "Category to analyze (optional, omit for all categories)",
                "required": False,
            },
            {
                "name": "growth_metric",
                "description": "Metric to track: reviews, downloads, or revenue (default: downloads)",
                "required": False,
            },
            {
                "name": "period",
                "description": "Time period: 7d, 14d, 30d, 60d, 90d (default: 7d)",
                "required": False,
            },
        ],
    },
    {
        "name": "ad_intelligence",
        "description": (
            "Discover which apps are running ads (Meta and Apple Search Ads) "
            "in a specific category or niche."
        ),
        "arguments": [
            {
                "name": "category_or_search",
                "description": "Category or search term to filter (e.g. 'games', 'meditation app')",
                "required": True,
            },
            {
                "name": "ad_platform",
                "description": "Ad platform: 'meta', 'apple', or 'both' (default: both)",
                "required": False,
            },
        ],
    },
    {
        "name": "review_analysis",
        "description": (
            "Analyze user reviews for an App Store or Google Play app. Identifies sentiment patterns, "
            "common complaints, feature requests, and competitive review insights."
        ),
        "arguments": [
            {
                "name": "app_id",
                "description": "App Store numeric ID or Google Play package name to analyze reviews for",
                "required": True,
            },
            {
                "name": "source",
                "description": "Store source: apple_mobile or google_mobile. Inferred from app_id if omitted.",
                "required": False,
            },
            {
                "name": "country",
                "description": "Country code for reviews (e.g. 'US', 'GB'). Default: US",
                "required": False,
            },
        ],
    },
]


def _render_prompt(name, arguments):
    """Generate the messages for a prompt invocation."""
    args = {a["name"]: a.get("value", "") for a in (arguments or [])}

    if name == "discover_niche":
        category = args.get("category", "")
        revenue = args.get("revenue_range", "")
        source = args.get("source", "apple_mobile") or "apple_mobile"
        revenue_filters = ""
        if revenue and "-" in revenue:
            parts = revenue.split("-")
            revenue_filters = f", minRevenue: {parts[0]}, maxRevenue: {parts[1]}"
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Help me discover profitable opportunities in the '{category}' "
                        f"category for source '{source}'.\n\n"
                        f"1. Use search_apps with categories: ['{category}'], sortBy: 'revenue', "
                        f"sortOrder: 'desc'{revenue_filters}, source: '{source}', limit: 20 to see the top revenue apps.\n"
                        f"2. Then search_apps with categories: ['{category}'], sortBy: 'growth', "
                        f"growthMetric: 'downloads', growthPeriod: '7d', source: '{source}', limit: 20 for fastest growers.\n"
                        f"3. Analyze the results:\n"
                        f"   - What revenue range do apps in this category typically fall in?\n"
                        f"   - Which apps are growing fastest and why?\n"
                        f"   - Are there gaps — underserved niches within this category?\n"
                        f"   - What pricing models dominate (free, paid, subscription)?\n"
                        f"4. Get detail on the top 3 most interesting apps using get_app_detail.\n"
                        f"5. Summarize findings with specific, actionable niche opportunities."
                    ),
                },
            }
        ]

    if name == "competitor_analysis":
        target = args.get("app_or_keyword", "")
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Run a competitive analysis for '{target}'.\n\n"
                        f"1. If '{target}' looks like an app ID, use get_app_detail to get its data. "
                        f"Otherwise, use search_apps with search: '{target}', limit: 10.\n"
                        f"2. Identify the top 5 competitors in the same space.\n"
                        f"3. For each competitor, note: downloads, revenue, ratings, reviews, "
                        f"whether they run Meta ads or Apple ads.\n"
                        f"4. Use batch_keyword_difficulty with keywords related to '{target}' "
                        f"to find keyword opportunities.\n"
                        f"5. Create a comparison table and identify:\n"
                        f"   - Strengths and weaknesses of each competitor\n"
                        f"   - Keyword gaps you could exploit\n"
                        f"   - Ad strategies being used\n"
                        f"   - Revenue/download benchmarks for the niche"
                    ),
                },
            }
        ]

    if name == "keyword_research":
        seeds = args.get("seed_keywords", "")
        country = args.get("country", "US") or "US"
        source = args.get("source", "apple_mobile") or "apple_mobile"
        keyword_list = [k.strip() for k in seeds.split(",") if k.strip()]
        keywords_json = json.dumps(keyword_list[:10])
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Research keywords for source '{source}' in country '{country}' "
                        f"starting with these seeds: {seeds}\n\n"
                        f"1. Use batch_keyword_difficulty with keywords: {keywords_json}, "
                        f"country: '{country}', source: '{source}' to get initial metrics.\n"
                        f"2. For the top 3 keywords by opportunity, use get_keyword_difficulty "
                        f"with source: '{source}' to see which apps currently rank for them.\n"
                        f"3. Analyze the results:\n"
                        f"   - Which keywords have the best volume-to-difficulty ratio?\n"
                        f"   - Are the top-ranking apps beatable (low reviews, low ratings)?\n"
                        f"   - What long-tail variations could work?\n"
                        f"4. Provide a keyword strategy:\n"
                        f"   - Primary keywords (for title/subtitle)\n"
                        f"   - Secondary keywords (for keyword field)\n"
                        f"   - Long-tail opportunities\n"
                        f"   - Keywords to avoid (too competitive or low relevance)"
                    ),
                },
            }
        ]

    if name == "app_growth_report":
        category = args.get("category", "")
        metric = args.get("growth_metric", "downloads") or "downloads"
        period = args.get("period", "7d") or "7d"
        cat_filter = f", categories: ['{category}']" if category else ""
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Generate an app growth report"
                        f"{f' for the {category} category' if category else ' across all categories'}.\n\n"
                        f"1. Use search_apps with sortBy: 'growth', growthMetric: '{metric}', "
                        f"growthPeriod: '{period}', growthType: 'positive'"
                        f"{cat_filter}, limit: 20 for top gainers.\n"
                        f"2. Use search_apps with same filters but growthType: 'negative', "
                        f"sortOrder: 'asc', limit: 10 for top losers.\n"
                        f"3. Get detail on the top 3 fastest-growing apps.\n"
                        f"4. Compile a report:\n"
                        f"   - Top gainers with growth rates and likely causes\n"
                        f"   - Notable decliners and possible reasons\n"
                        f"   - Trends and patterns (seasonal? new feature? viral?)\n"
                        f"   - Opportunities for new entrants"
                    ),
                },
            }
        ]

    if name == "ad_intelligence":
        target = args.get("category_or_search", "")
        platform = args.get("ad_platform", "both") or "both"
        meta_filter = platform in ("meta", "both")
        apple_filter = platform in ("apple", "both")
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Discover which apps are running ads for '{target}'.\n\n"
                        f"1. Use search_apps with search: '{target}'"
                        f"{', hasMetaAds: true' if meta_filter else ''}"
                        f", sortBy: 'revenue', limit: 20 to find apps with Meta ads.\n"
                        f"2. Use search_apps with search: '{target}'"
                        f"{', hasAppleAds: true' if apple_filter else ''}"
                        f", sortBy: 'revenue', limit: 20 for Apple Search Ads.\n"
                        f"3. Get detail on the top 5 advertisers to see their ad creatives.\n"
                        f"4. Analyze:\n"
                        f"   - Which apps are spending on ads and on which platforms?\n"
                        f"   - What do their Meta ad creatives look like?\n"
                        f"   - What's the relationship between ad spend and revenue?\n"
                        f"   - Are there well-performing apps NOT running ads (opportunity)?\n"
                        f"5. Provide actionable ad strategy recommendations."
                    ),
                },
            }
        ]

    if name == "review_analysis":
        app_id = args.get("app_id", "")
        country = args.get("country", "US") or "US"
        source = args.get("source", "")
        source_fragment = f", source: '{source}'" if source else ""
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Analyze user reviews for app ID '{app_id}' in country '{country}'.\n\n"
                        f"1. Use get_app_detail with appId: '{app_id}' to understand the app.\n"
                        f"2. Use get_app_reviews with appId: '{app_id}', country: '{country}'{source_fragment}, "
                        f"maxReviews: 100 to fetch recent reviews.\n"
                        f"3. If more context is needed, fetch another page with the nextOffset.\n"
                        f"4. Analyze the reviews:\n"
                        f"   - **Overall sentiment** — what's the balance of positive vs negative?\n"
                        f"   - **Common praise** — what do users love most?\n"
                        f"   - **Top complaints** — recurring issues and frustrations\n"
                        f"   - **Feature requests** — what users want added or improved\n"
                        f"   - **Rating distribution** — are most reviews 5-star or mixed?\n"
                        f"5. Provide a summary with:\n"
                        f"   - Sentiment breakdown (positive/neutral/negative percentages)\n"
                        f"   - Top 5 themes from reviews\n"
                        f"   - Actionable recommendations based on user feedback\n"
                        f"   - Competitive opportunities (weaknesses competitors could exploit)"
                    ),
                },
            }
        ]

    return [
        {
            "role": "user",
            "content": {"type": "text", "text": f"Unknown prompt: {name}"},
        }
    ]


# ═══════════════════════════════════════════════════════════════════════════
# MCP protocol handlers
# ═══════════════════════════════════════════════════════════════════════════

def handle_initialize(req_id):
    return rpc_success(req_id, {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {"tools": {}, "prompts": {}},
        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        "instructions": INSTRUCTIONS,
    })


def handle_tools_list(req_id):
    return rpc_success(req_id, {"tools": TOOLS})


def handle_prompts_list(req_id):
    return rpc_success(req_id, {"prompts": PROMPTS})


def handle_prompts_get(req_id, params):
    name = params.get("name", "")
    arguments = params.get("arguments", [])
    prompt = next((p for p in PROMPTS if p["name"] == name), None)
    if not prompt:
        return rpc_error(req_id, -32602, f"Unknown prompt: {name}")
    messages = _render_prompt(name, arguments)
    return rpc_success(req_id, {"messages": messages})


# ═══════════════════════════════════════════════════════════════════════════
# AppKittie API client
# ═══════════════════════════════════════════════════════════════════════════

def _clean_params(params):
    """Prepare params for URL encoding: drop None, stringify booleans and lists."""
    cleaned = {}
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, bool):
            cleaned[k] = "true" if v else "false"
        elif isinstance(v, list):
            cleaned[k] = ",".join(str(item) for item in v)
        else:
            cleaned[k] = v
    return cleaned


async def api_get(path, params, api_key):
    clean = _clean_params(params)
    url = f"{API_BASE}{path}"
    if clean:
        url += "?" + urlencode(clean)

    headers = Headers.new()
    headers.set("Authorization", f"Bearer {api_key}")
    headers.set("Accept", "application/json")

    resp = await fetch(
        url,
        to_js({"method": "GET", "headers": headers}, dict_converter=js.Object.fromEntries),
    )
    text = await resp.text()

    if resp.status != 200:
        return None, f"AppKittie API error (HTTP {resp.status}): {text}"
    try:
        return json.loads(text), None
    except json.JSONDecodeError:
        return None, f"Invalid JSON from API: {text[:500]}"


async def api_post(path, body, api_key):
    url = f"{API_BASE}{path}"

    headers = Headers.new()
    headers.set("Authorization", f"Bearer {api_key}")
    headers.set("Content-Type", "application/json")
    headers.set("Accept", "application/json")

    resp = await fetch(
        url,
        to_js(
            {"method": "POST", "headers": headers, "body": json.dumps(body)},
            dict_converter=js.Object.fromEntries,
        ),
    )
    text = await resp.text()

    if resp.status != 200:
        return None, f"AppKittie API error (HTTP {resp.status}): {text}"
    try:
        return json.loads(text), None
    except json.JSONDecodeError:
        return None, f"Invalid JSON from API: {text[:500]}"


# ═══════════════════════════════════════════════════════════════════════════
# Tool handlers
# ═══════════════════════════════════════════════════════════════════════════

_SEARCH_APPS_KEYS = [
    "search", "categories", "excludedCategories", "source", "excludedSource", "sortBy", "sortOrder",
    "priceType", "minPrice", "maxPrice", "minRating", "maxRating",
    "minReviews", "maxReviews", "minDownloads", "maxDownloads",
    "minRevenue", "maxRevenue", "minLifetimeDownloads", "maxLifetimeDownloads",
    "minLifetimeRevenue", "maxLifetimeRevenue", "growthMetric", "growthPeriod",
    "growthType", "minGrowth", "maxGrowth", "contentRating", "languages",
    "developer", "releasedAfter", "updatedAfter", "hasWebsite", "hasCreators",
    "hasMetaAds", "hasAppleAds", "hasEmails", "limit", "cursor",
]


def _pick(args, keys):
    return {k: args[k] for k in keys if k in args}


async def handle_search_apps(args, api_key):
    params = _pick(args, _SEARCH_APPS_KEYS)
    data, err = await api_get("/api/v1/apps", params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))


async def handle_get_app_detail(args, api_key):
    app_id = args.get("appId", "").strip()
    if not app_id:
        return tool_result("Error: 'appId' is required.", is_error=True)
    data, err = await api_get(f"/api/v1/apps/{app_id}", {}, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))


async def handle_get_keyword_difficulty(args, api_key):
    keyword = args.get("keyword", "").strip()
    if not keyword:
        return tool_result("Error: 'keyword' is required.", is_error=True)
    params = {"keyword": keyword}
    if "country" in args:
        params["country"] = args["country"]
    if "source" in args:
        params["source"] = args["source"]
    data, err = await api_get("/api/v1/keywords/difficulty", params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))


async def handle_batch_keyword_difficulty(args, api_key):
    keywords = args.get("keywords")
    if not keywords or not isinstance(keywords, list):
        return tool_result(
            "Error: 'keywords' is required and must be a non-empty array of strings.",
            is_error=True,
        )
    if len(keywords) > 10:
        return tool_result(
            "Error: Maximum 10 keywords per request.",
            is_error=True,
        )
    body = {"keywords": keywords}
    if "country" in args:
        body["country"] = args["country"]
    if "source" in args:
        body["source"] = args["source"]
    data, err = await api_post("/api/v1/keywords/difficulty", body, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))


async def handle_get_supported_countries(_args, _api_key):
    countries = [
        {"code": code} for code in APP_STORE_COUNTRY_CODES
    ]
    return tool_result(json.dumps({"data": countries}, indent=2))


async def handle_get_app_reviews(args, api_key):
    app_id = args.get("appId", "").strip()
    if not app_id:
        return tool_result("Error: 'appId' is required.", is_error=True)
    body = {"appId": app_id}
    if "source" in args:
        body["source"] = args["source"]
    if "country" in args:
        body["country"] = args["country"]
    if "maxReviews" in args:
        body["maxReviews"] = args["maxReviews"]
    if "offset" in args:
        body["offset"] = args["offset"]
    data, err = await api_post("/api/v1/reviews", body, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))


TOOL_HANDLERS = {
    "search_apps": handle_search_apps,
    "get_app_detail": handle_get_app_detail,
    "get_keyword_difficulty": handle_get_keyword_difficulty,
    "batch_keyword_difficulty": handle_batch_keyword_difficulty,
    "get_supported_countries": handle_get_supported_countries,
    "get_app_reviews": handle_get_app_reviews,
}


# ═══════════════════════════════════════════════════════════════════════════
# HTTP layer
# ═══════════════════════════════════════════════════════════════════════════

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, Mcp-Session-Id",
    "Access-Control-Max-Age": "86400",
}


def json_response(body, status=200):
    headers = Headers.new()
    headers.set("Content-Type", "application/json")
    for k, v in CORS_HEADERS.items():
        headers.set(k, v)
    return Response.new(json.dumps(body), status=status, headers=headers)


def empty_response(status=202):
    headers = Headers.new()
    for k, v in CORS_HEADERS.items():
        headers.set(k, v)
    return Response.new("", status=status, headers=headers)


def extract_api_key(request):
    auth = request.headers.get("Authorization") or ""
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


async def handle_rpc(rpc, api_key, env):
    """Process a single JSON-RPC message."""
    method = rpc.get("method", "")
    req_id = rpc.get("id")
    params = rpc.get("params", {})
    is_notification = req_id is None

    if method == "initialize":
        return handle_initialize(req_id)

    if method == "notifications/initialized":
        return None

    if method == "ping":
        return rpc_success(req_id, {})

    if method == "tools/list":
        return handle_tools_list(req_id)

    if method == "prompts/list":
        return handle_prompts_list(req_id)

    if method == "prompts/get":
        return handle_prompts_get(req_id, params)

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            return rpc_error(req_id, -32602, f"Unknown tool: {tool_name}")

        resolved_key = api_key
        if not resolved_key:
            if tool_name == "get_supported_countries":
                try:
                    result = await handler(arguments, "")
                    return rpc_success(req_id, result)
                except Exception as e:
                    return rpc_success(
                        req_id,
                        tool_result(f"Tool execution error: {str(e)}", is_error=True),
                    )

            return rpc_success(
                req_id,
                tool_result(
                    "Authentication required. Pass your AppKittie API key as a "
                    "Bearer token in the Authorization header.",
                    is_error=True,
                ),
            )

        try:
            result = await handler(arguments, resolved_key)
            return rpc_success(req_id, result)
        except Exception as e:
            return rpc_success(
                req_id,
                tool_result(f"Tool execution error: {str(e)}", is_error=True),
            )

    if is_notification:
        return None

    return rpc_error(req_id, -32601, f"Method not found: {method}")


# ═══════════════════════════════════════════════════════════════════════════
# Cloudflare Workers entry point
# ═══════════════════════════════════════════════════════════════════════════

async def on_fetch(request, env):
    if request.method == "OPTIONS":
        headers = Headers.new()
        for k, v in CORS_HEADERS.items():
            headers.set(k, v)
        return Response.new("", status=204, headers=headers)

    if request.method == "GET":
        return json_response({
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "protocol": "MCP",
            "description": (
                "AppKittie MCP Server — discover App Store and Google Play apps, "
                "research ASO keywords, and access download/revenue intelligence."
            ),
            "tools": len(TOOLS),
            "docs": "https://appkittie.com/docs",
        })

    if request.method == "DELETE":
        return empty_response(200)

    if request.method != "POST":
        return json_response(
            {"error": "Method not allowed. Use POST for MCP messages."},
            status=405,
        )

    try:
        body_text = await request.text()
        rpc = json.loads(body_text)
    except Exception:
        return json_response(rpc_error(None, -32700, "Parse error: invalid JSON"))

    api_key = extract_api_key(request)

    if isinstance(rpc, list):
        results = []
        for msg in rpc:
            result = await handle_rpc(msg, api_key, env)
            if result is not None:
                results.append(result)
        if results:
            return json_response(results)
        return empty_response()

    result = await handle_rpc(rpc, api_key, env)
    if result is None:
        return empty_response()
    return json_response(result)
