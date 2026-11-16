import json

from ..api import api_get
from ..rpc import tool_result


TOOL = {
    "name": "search_developers",
    "description": (
        "Search mobile app developers and studios across the App Store and Google Play. "
        "Filter by portfolio size, estimated monthly revenue/downloads, categories, "
        "store presence, website, and latest launch. Costs 1 credit per developer returned. "
        "Pass a returned developer name to get_developer_detail for its portfolio."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "search": {"type": "string", "maxLength": 200, "description": "Developer search query."},
            "stores": {
                "type": "string",
                "enum": ["all", "both", "apple", "google"],
                "description": "Default all. apple/google require that store and also include developers on both stores.",
            },
            "categories": {"type": "array", "items": {"type": "string"}, "description": "Include developers with apps in these categories."},
            "excludedCategories": {"type": "array", "items": {"type": "string"}, "description": "Exclude developers with apps in these categories."},
            "minApps": {"type": "integer", "minimum": 0, "description": "Minimum portfolio app count."},
            "maxApps": {"type": "integer", "minimum": 0, "description": "Maximum portfolio app count."},
            "minMrr": {"type": "number", "minimum": 0, "description": "Minimum estimated monthly portfolio revenue in USD."},
            "maxMrr": {"type": "number", "minimum": 0, "description": "Maximum estimated monthly portfolio revenue in USD."},
            "minDownloads": {"type": "number", "minimum": 0, "description": "Minimum estimated monthly portfolio downloads."},
            "maxDownloads": {"type": "number", "minimum": 0, "description": "Maximum estimated monthly portfolio downloads."},
            "hasWebsite": {"type": "boolean", "description": "True for a known website; false for none. Omit for both."},
            "latestReleasedAfter": {"type": "integer", "minimum": 0, "description": "Most recent app launch on/after this Unix timestamp in seconds."},
            "latestReleasedBefore": {"type": "integer", "minimum": 0, "description": "Most recent app launch on/before this Unix timestamp in seconds."},
            "sortBy": {"type": "string", "enum": ["total_mrr", "total_downloads", "app_count", "latest_released"], "description": "Default total_mrr."},
            "sortOrder": {"type": "string", "enum": ["asc", "desc"], "description": "Default desc."},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "description": "Developers per page. Default 50; capped by remaining credits."},
            "cursor": {"type": "integer", "minimum": 0, "description": "Offset from pagination.nextCursor. Default 0."},
        },
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    params = {key: args[key] for key in TOOL["inputSchema"]["properties"] if key in args}
    data, err = await api_get("/api/v1/developers", params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))
