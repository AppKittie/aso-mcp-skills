import json
from urllib.parse import quote

from ..api import api_get
from ..identifiers import as_str
from ..rpc import tool_result


TOOL = {
    "name": "get_store_ranking_history",
    "description": (
        "Fetch daily store-chart positions for one app slug in a specific "
        "collection, country, and category. Costs 10 credits per request. "
        "Use list_store_rankings first to obtain an exact app slug and chart filters."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "appSlug": {
                "type": "string",
                "description": "Exact AppKittie app slug from list_store_rankings.",
            },
            "app_slug": {
                "type": "string",
                "description": "Alias for appSlug.",
            },
            "source": {
                "type": "string",
                "enum": ["apple_mobile", "google_mobile"],
                "description": "Store source. Default: apple_mobile.",
            },
            "collection": {
                "type": "string",
                "enum": ["TOP_FREE", "TOP_PAID", "TOP_GROSSING"],
                "description": "Chart collection. Default: TOP_FREE.",
            },
            "country": {
                "type": "string",
                "description": "Two-letter country code. Default: US.",
            },
            "category": {
                "type": "string",
                "description": "Store category key used by list_store_rankings.",
            },
            "days": {
                "type": "integer",
                "minimum": 1,
                "maximum": 365,
                "description": "Optional number of recent daily observations.",
            },
        },
        "required": ["category"],
        "anyOf": [{"required": ["appSlug"]}, {"required": ["app_slug"]}],
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    app_slug = as_str(args.get("appSlug")) or as_str(args.get("app_slug"))
    if not app_slug:
        return tool_result(
            "Error: 'appSlug' or 'app_slug' is required.",
            is_error=True,
        )

    params = {
        key: args[key]
        for key in ["source", "collection", "country", "category", "days"]
        if key in args
    }
    data, err = await api_get(
        f"/api/v1/trending/{quote(app_slug, safe='')}/history",
        params,
        api_key,
    )
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))
