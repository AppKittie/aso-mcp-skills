import json

from ..api import api_get
from ..identifiers import resolve_app_slug
from ..rpc import tool_result


APP_SCOPED_PROPERTIES = {
    "appSlug": {"type": "string", "description": "AppKittie app_slug."},
    "app_slug": {"type": "string", "description": "Alias for appSlug."},
    "appId": {
        "type": "string",
        "description": "AppKittie app ID, app slug, store ID, package name, or store URL.",
    },
    "appStoreId": {"type": "string", "description": "Numeric App Store ID or Google Play package name."},
    "appStoreUrl": {"type": "string", "description": "Apple App Store or Google Play URL."},
    "count": {"type": "integer", "description": "Items to return (1-100, default: 50)."},
    "limit": {"type": "integer", "description": "Alias for count."},
    "cursor": {"type": "integer", "description": "Pagination cursor from previous response."},
}

APP_SCOPED_ANY_OF = [
    {"required": ["appSlug"]},
    {"required": ["app_slug"]},
    {"required": ["appId"]},
    {"required": ["appStoreId"]},
    {"required": ["appStoreUrl"]},
]


async def handle_app_scoped_list(args, api_key, endpoint):
    app_slug, err = await resolve_app_slug(args, api_key, required=True)
    if err:
        return tool_result(err, is_error=True)

    params = {"app_slug": app_slug}
    if "count" in args:
        params["count"] = args["count"]
    elif "limit" in args:
        params["count"] = args["limit"]
    if "cursor" in args:
        params["cursor"] = args["cursor"]

    data, err = await api_get(endpoint, params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))

