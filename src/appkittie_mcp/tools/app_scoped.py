import json

from ..api import api_get
from ..identifiers import as_str
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

# Query param keys forwarded verbatim to the API. The API resolves any
# identifier form (slug, store ID, package name, or store URL) server-side.
IDENTIFIER_KEYS = ["app_slug", "appSlug", "appId", "appStoreId", "appStoreUrl"]

MISSING_SCOPE_ERROR = (
    "Error: provide an app identifier ('appSlug', 'appId', 'appStoreId', or "
    "'appStoreUrl') or a 'category' for cross-app discovery."
)


async def handle_app_scoped_list(args, api_key, endpoint, extra_keys=(), allow_category=False):
    params = {}

    for key in IDENTIFIER_KEYS:
        value = as_str(args.get(key))
        if value:
            params[key] = value
            break

    category = as_str(args.get("category")) if allow_category else ""
    if category:
        params["category"] = category

    if not params:
        return tool_result(MISSING_SCOPE_ERROR, is_error=True)

    if "count" in args:
        params["count"] = args["count"]
    elif "limit" in args:
        params["count"] = args["limit"]
    if "cursor" in args:
        params["cursor"] = args["cursor"]

    for key in extra_keys:
        if key in args:
            params[key] = args[key]

    data, err = await api_get(endpoint, params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))
