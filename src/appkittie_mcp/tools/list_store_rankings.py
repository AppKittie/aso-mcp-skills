import json

from ..api import api_get
from ..rpc import tool_result


TOOL = {
    "name": "list_store_rankings",
    "description": (
        "List the current apps in an Apple App Store or Google Play chart by "
        "collection, country, and category. Costs 1 credit per app returned. "
        "Use get_store_ranking_history for one app's daily chart positions."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
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
                "description": "Store category key. Default: BUSINESS.",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Apps to return. Default: 50.",
            },
            "offset": {
                "type": "integer",
                "minimum": 0,
                "description": "Zero-based pagination offset. Default: 0.",
            },
        },
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    params = {
        key: args[key]
        for key in ["source", "collection", "country", "category", "limit", "offset"]
        if key in args
    }
    data, err = await api_get("/api/v1/trending", params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))
