import json

from ..api import api_get
from ..constants import (
    AD_MEDIA_TYPES,
    AD_SORT_BY_OPTIONS,
    AD_SOURCE_OPTIONS,
    AD_STATUSES,
    AD_TEXT_SEARCH_FIELDS,
    SORT_ORDERS,
)
from ..identifiers import resolve_app_slug
from ..rpc import tool_result


TOOL = {
    "name": "search_ads",
    "description": (
        "Search and filter Meta and Google ad creatives for mobile apps. "
        "Supports full-text search, filters, sorting, app-specific lookup, "
        "and cursor-based pagination. Costs 1 credit per ad returned."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "search": {"type": "string", "description": "Full-text search query across ad creative text and app metadata"},
            "textSearchFields": {
                "type": "array",
                "items": {"type": "string", "enum": AD_TEXT_SEARCH_FIELDS},
                "description": "Fields to search. Defaults to all supported ad text fields.",
            },
            "adSource": {
                "type": "string",
                "enum": AD_SOURCE_OPTIONS,
                "description": "Ad source: all, meta, or google.",
            },
            "mediaType": {
                "type": "string",
                "enum": AD_MEDIA_TYPES,
                "description": "Creative media type: all, image, or video.",
            },
            "status": {
                "type": "string",
                "enum": AD_STATUSES,
                "description": "Ad status: all, active, or inactive.",
            },
            "categories": {"type": "array", "items": {"type": "string"}, "description": "Advertised app categories to include"},
            "excludedCategories": {"type": "array", "items": {"type": "string"}, "description": "Advertised app categories to exclude"},
            "adLanguages": {"type": "array", "items": {"type": "string"}, "description": "Representative country codes mapped to ad language codes."},
            "excludedAdLanguages": {"type": "array", "items": {"type": "string"}, "description": "Representative country codes whose ad languages should be excluded."},
            "appSlug": {"type": "string", "description": "Filter ads for a single app slug."},
            "app_slug": {"type": "string", "description": "Alias for appSlug."},
            "appId": {
                "type": "string",
                "description": "App identifier to resolve to appSlug: AppKittie ID, slug, store ID, package, or store URL.",
            },
            "appStoreId": {"type": "string", "description": "Numeric App Store ID or Google Play package name."},
            "appStoreUrl": {"type": "string", "description": "Apple App Store or Google Play URL."},
            "countries": {"type": "array", "items": {"type": "string"}, "description": "Countries where the ad was observed"},
            "excludedCountries": {"type": "array", "items": {"type": "string"}, "description": "Countries to exclude"},
            "surfaces": {"type": "array", "items": {"type": "string"}, "description": "Ad surfaces or placements to include"},
            "excludedSurfaces": {"type": "array", "items": {"type": "string"}, "description": "Ad surfaces or placements to exclude"},
            "developer": {"type": "string", "description": "Exact advertised app developer name"},
            "startedAfter": {"type": "integer", "description": "Only ads that started after this Unix timestamp"},
            "startedBefore": {"type": "integer", "description": "Only ads that started before this Unix timestamp"},
            "endedAfter": {"type": "integer", "description": "Only ads that ended after this Unix timestamp"},
            "endedBefore": {"type": "integer", "description": "Only ads that ended before this Unix timestamp"},
            "minAppDownloads": {"type": "integer", "description": "Minimum advertised app monthly downloads"},
            "maxAppDownloads": {"type": "integer", "description": "Maximum advertised app monthly downloads"},
            "minAppRevenue": {"type": "integer", "description": "Minimum advertised app monthly revenue"},
            "maxAppRevenue": {"type": "integer", "description": "Maximum advertised app monthly revenue"},
            "sortBy": {
                "type": "string",
                "enum": AD_SORT_BY_OPTIONS,
                "description": "Sort field for ad results.",
            },
            "sortOrder": {"type": "string", "enum": SORT_ORDERS, "description": "Sort direction."},
            "limit": {"type": "integer", "description": "Results per page (1-100, default: 50)", "default": 50},
            "cursor": {"type": "integer", "description": "Pagination cursor (offset)."},
        },
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


SEARCH_ADS_KEYS = [
    "search", "textSearchFields", "adSource", "mediaType", "status",
    "categories", "excludedCategories", "adLanguages", "excludedAdLanguages",
    "appSlug", "app_slug", "countries", "excludedCountries", "surfaces",
    "excludedSurfaces", "developer", "startedAfter", "startedBefore",
    "endedAfter", "endedBefore", "minAppDownloads", "maxAppDownloads",
    "minAppRevenue", "maxAppRevenue", "sortBy", "sortOrder", "limit", "cursor",
]


def _pick(args, keys):
    return {key: args[key] for key in keys if key in args}


async def handle(args, api_key):
    params = _pick(args, SEARCH_ADS_KEYS)
    app_slug, err = await resolve_app_slug(args, api_key)
    if err:
        return tool_result(err, is_error=True)
    if app_slug:
        params["appSlug"] = app_slug
        params.pop("app_slug", None)

    data, err = await api_get("/api/v1/ads", params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))

