import json

from ..identifiers import api_get_app_resource, resolve_app_path_identifier
from ..rpc import tool_result


TOOL = {
    "name": "get_app_countries",
    "description": (
        "Fetch the estimated split of a mobile app's users by country, as a percentage per "
        "country, largest first. Requires an app identifier: an app slug or store ID (numeric "
        "App Store ID or Google Play package name), an AppKittie app ID, or an App Store / "
        "Google Play URL. Costs 1 credit per request; an app without country data returns an "
        "empty list for free."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "appSlug": {"type": "string", "description": "AppKittie app_slug."},
            "app_slug": {"type": "string", "description": "Alias for appSlug."},
            "storeId": {"type": "string", "description": "Numeric App Store ID or Google Play package name."},
            "store_id": {"type": "string", "description": "Alias for storeId."},
            "appStoreId": {"type": "string", "description": "Alias for storeId."},
            "appId": {
                "type": "string",
                "description": "AppKittie app ID, slug, store ID, package name, or store URL.",
            },
            "appStoreUrl": {"type": "string", "description": "Apple App Store or Google Play URL."},
        },
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    app_identifier, err = await resolve_app_path_identifier(args, api_key)
    if err:
        return tool_result(err, is_error=True)

    data, err = await api_get_app_resource(app_identifier, "/countries", {}, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))
