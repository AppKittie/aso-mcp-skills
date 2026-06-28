import json

from ..constants import HISTORICAL_METRICS, HISTORICAL_PERIODS
from ..identifiers import api_get_app_resource, resolve_app_path_identifier
from ..rpc import tool_result


TOOL = {
    "name": "get_app_historicals",
    "description": (
        "Fetch historical metric time series for a specific mobile app. "
        "Accepts an AppKittie app ID, app slug, store ID, package name, "
        "or App Store / Google Play URL. Costs 1 credit per request."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "appSlug": {"type": "string", "description": "AppKittie app_slug."},
            "app_slug": {"type": "string", "description": "Alias for appSlug."},
            "appId": {
                "type": "string",
                "description": "AppKittie app ID, slug, store ID, package name, or store URL.",
            },
            "appStoreId": {"type": "string", "description": "Numeric App Store ID or Google Play package name."},
            "appStoreUrl": {"type": "string", "description": "Apple App Store or Google Play URL."},
            "period": {
                "type": "string",
                "enum": HISTORICAL_PERIODS,
                "description": "Historical range: 30d, 90d, 300d, or all. Default: 30d.",
            },
            "metrics": {
                "type": "array",
                "items": {"type": "string", "enum": HISTORICAL_METRICS},
                "description": "Optional metrics to include. If omitted, all metrics are returned.",
            },
        },
        "anyOf": [
            {"required": ["appSlug"]},
            {"required": ["app_slug"]},
            {"required": ["appId"]},
            {"required": ["appStoreId"]},
            {"required": ["appStoreUrl"]},
        ],
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    app_identifier, err = await resolve_app_path_identifier(args, api_key)
    if err:
        return tool_result(err, is_error=True)

    params = {}
    if "period" in args:
        params["period"] = args["period"]
    if "metrics" in args:
        params["metrics"] = args["metrics"]

    data, err = await api_get_app_resource(app_identifier, "/historicals", params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))

