import json

from ..api import api_get
from ..constants import (
    CONTENT_RATINGS,
    GROWTH_METRICS,
    GROWTH_PERIODS,
    PRICE_TYPES,
    SORT_BY_OPTIONS,
    SORT_ORDERS,
    STORE_SOURCES,
)
from ..rpc import tool_result


TOOL = {
    "name": "search_apps",
    "description": (
        "Search and filter mobile apps from the Apple App Store and Google Play. "
        "Discover apps by category, revenue, downloads, traction, ratings, "
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
                "description": "App Store categories to filter by (e.g. ['games', 'productivity'])",
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
                "description": "Sort results by growth, rating, reviews, updated, released, downloads, revenue, trending, or newest.",
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
            "minPrice": {"type": "number", "description": "Minimum app price in USD"},
            "maxPrice": {"type": "number", "description": "Maximum app price in USD"},
            "minRating": {"type": "number", "description": "Minimum star rating (0-5)"},
            "maxRating": {"type": "number", "description": "Maximum star rating (0-5)"},
            "minReviews": {"type": "integer", "description": "Minimum number of reviews"},
            "maxReviews": {"type": "integer", "description": "Maximum number of reviews"},
            "minDownloads": {"type": "integer", "description": "Minimum estimated monthly downloads"},
            "maxDownloads": {"type": "integer", "description": "Maximum estimated monthly downloads"},
            "minRevenue": {"type": "integer", "description": "Minimum estimated monthly revenue (USD)"},
            "maxRevenue": {"type": "integer", "description": "Maximum estimated monthly revenue (USD)"},
            "minLifetimeDownloads": {"type": "integer", "description": "Minimum estimated lifetime downloads"},
            "maxLifetimeDownloads": {"type": "integer", "description": "Maximum estimated lifetime downloads"},
            "minLifetimeRevenue": {"type": "integer", "description": "Minimum estimated lifetime revenue (USD)"},
            "maxLifetimeRevenue": {"type": "integer", "description": "Maximum estimated lifetime revenue (USD)"},
            "growthMetric": {
                "type": "string",
                "enum": GROWTH_METRICS,
                "description": "Which metric to sort growth on: reviews (default: reviews)",
            },
            "growthPeriod": {
                "type": "string",
                "enum": GROWTH_PERIODS,
                "description": "Growth sort period window: 7d, 14d, 30d, 60d, 90d",
            },
            "contentRating": {
                "type": "string",
                "enum": CONTENT_RATINGS,
                "description": "Content rating filter: all, 4+, 9+, 12+, 17+",
            },
            "languages": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by supported languages",
            },
            "developer": {"type": "string", "description": "Filter by developer name"},
            "releasedAfter": {"type": "integer", "description": "Only apps released after this Unix timestamp"},
            "updatedAfter": {"type": "integer", "description": "Only apps updated after this Unix timestamp"},
            "hasWebsite": {"type": "boolean", "description": "Only apps with a developer website"},
            "hasCreators": {"type": "boolean", "description": "Only apps with known creator/influencer partnerships"},
            "hasMetaAds": {"type": "boolean", "description": "Only apps running Meta ads"},
            "hasAppleAds": {"type": "boolean", "description": "Only apps running Apple Search Ads"},
            "hasEmails": {"type": "boolean", "description": "Only apps with contact emails available"},
            "limit": {
                "type": "integer",
                "description": "Results per page (1-100, default: 50)",
                "default": 50,
            },
            "cursor": {
                "type": "integer",
                "description": "Pagination cursor (offset). Use nextCursor from previous response.",
            },
        },
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


SEARCH_APPS_KEYS = [
    "search", "categories", "excludedCategories", "source", "excludedSource",
    "sortBy", "sortOrder", "priceType", "minPrice", "maxPrice",
    "minRating", "maxRating", "minReviews", "maxReviews", "minDownloads",
    "maxDownloads", "minRevenue", "maxRevenue", "minLifetimeDownloads",
    "maxLifetimeDownloads", "minLifetimeRevenue", "maxLifetimeRevenue",
    "growthMetric", "growthPeriod", "contentRating", "languages",
    "developer", "releasedAfter", "updatedAfter", "hasWebsite", "hasCreators",
    "hasMetaAds", "hasAppleAds", "hasEmails", "limit", "cursor",
]


def _pick(args, keys):
    return {key: args[key] for key in keys if key in args}


async def handle(args, api_key):
    params = _pick(args, SEARCH_APPS_KEYS)
    data, err = await api_get("/api/v1/apps", params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))

