import json

from ..api import api_get
from ..constants import STORE_SOURCES
from ..identifiers import as_str
from ..rpc import tool_result


# Compact default keeps tool output small for agent context windows.
DEFAULT_TOP_APPS_LIMIT = 10

TOOL = {
    "name": "get_keyword_difficulty",
    "description": (
        "Analyze a single Apple App Store or Google Play keyword's competitiveness. "
        "Returns popularity, difficulty, app count, traffic score, and top-ranking apps. "
        f"Returns the top {DEFAULT_TOP_APPS_LIMIT} ranked apps by default; "
        "set topAppsLimit (0-50) for more or fewer, or includeTopApps=false for metrics only. "
        "Costs 10 credits per request."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "keyword": {"type": "string", "description": "Keyword to analyze."},
            "country": {
                "type": "string",
                "description": "App Store country code (e.g. US, GB, DE). Default: US.",
            },
            "source": {
                "type": "string",
                "enum": STORE_SOURCES,
                "description": "Store source: apple_mobile or google_mobile. Default: apple_mobile.",
            },
            "topAppsLimit": {
                "type": "integer",
                "description": (
                    "Number of top-ranking apps to include (0-50). "
                    f"Default: {DEFAULT_TOP_APPS_LIMIT}."
                ),
            },
            "includeTopApps": {
                "type": "boolean",
                "description": "Set false for a metrics-only response (no topApps).",
            },
        },
        "required": ["keyword"],
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    keyword = as_str(args.get("keyword"))
    if not keyword:
        return tool_result("Error: 'keyword' is required.", is_error=True)

    params = {"keyword": keyword}
    if "country" in args:
        params["country"] = args["country"]
    if "source" in args:
        params["source"] = args["source"]
    if args.get("includeTopApps") is False:
        params["includeTopApps"] = "false"
    else:
        params["topAppsLimit"] = args.get("topAppsLimit", DEFAULT_TOP_APPS_LIMIT)

    data, err = await api_get("/api/v1/keywords/difficulty", params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))

