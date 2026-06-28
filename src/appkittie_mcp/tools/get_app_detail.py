import json

from ..identifiers import api_get_app_resource, resolve_app_path_identifier
from ..rpc import tool_result


TOOL = {
    "name": "get_app_detail",
    "description": (
        "Get detailed information about a specific mobile app by its ID. "
        "Returns metadata, screenshots, growth summary fields, in-app purchases, "
        "decision-makers, and social links. Use get_app_historicals for raw "
        "time-series metrics, list_creators/list_organic_content for creator "
        "data, and search_ads/get_ad_detail for ad creatives. Costs 1 credit per request."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "appId": {
                "type": "string",
                "description": (
                    "AppKittie document ID, app slug, store ID, package name, "
                    "or App Store / Google Play URL."
                ),
            },
        },
        "required": ["appId"],
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    app_identifier, err = await resolve_app_path_identifier(args, api_key)
    if err:
        return tool_result(err, is_error=True)

    data, err = await api_get_app_resource(app_identifier, "", {}, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))

