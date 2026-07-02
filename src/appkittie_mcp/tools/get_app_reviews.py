import json

from ..api import api_post
from ..constants import STORE_SOURCES
from ..identifiers import as_str
from ..rpc import tool_result


IDENTIFIER_KEYS = ["appId", "appSlug", "app_slug", "appStoreId", "appStoreUrl", "url"]

TOOL = {
    "name": "get_app_reviews",
    "description": (
        "Fetch user reviews for a specific Apple App Store or Google Play app. "
        "Accepts a numeric App Store ID, Google Play package name, AppKittie app "
        "slug, or store URL. Supports pagination via offset. "
        "Costs 1 credit per review returned."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "appId": {
                "type": "string",
                "description": (
                    "App identifier: numeric App Store ID, Google Play package name, "
                    "AppKittie app slug, or store URL."
                ),
            },
            "appSlug": {"type": "string", "description": "AppKittie app_slug."},
            "appStoreId": {"type": "string", "description": "Numeric App Store ID or Google Play package name."},
            "appStoreUrl": {"type": "string", "description": "Apple App Store or Google Play URL."},
            "source": {
                "type": "string",
                "enum": STORE_SOURCES,
                "description": "Store source. Inferred from the identifier if omitted.",
            },
            "country": {"type": "string", "description": "Country code. Default: US."},
            "maxReviews": {"type": "integer", "description": "Maximum reviews to fetch (1-300, default: 100)."},
            "offset": {"type": "integer", "description": "Pagination offset."},
        },
        "anyOf": [
            {"required": ["appId"]},
            {"required": ["appSlug"]},
            {"required": ["appStoreId"]},
            {"required": ["appStoreUrl"]},
        ],
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    identifier = ""
    for key in IDENTIFIER_KEYS:
        identifier = as_str(args.get(key))
        if identifier:
            break

    if not identifier:
        return tool_result(
            "Error: provide 'appId' (numeric App Store ID, Google Play package "
            "name, app slug, or store URL), 'appSlug', 'appStoreId', or 'appStoreUrl'.",
            is_error=True,
        )

    body = {"appId": identifier}
    if "source" in args:
        body["source"] = args["source"]
    if "country" in args:
        body["country"] = args["country"]
    if "maxReviews" in args:
        body["maxReviews"] = args["maxReviews"]
    if "offset" in args:
        body["offset"] = args["offset"]

    data, err = await api_post("/api/v1/reviews", body, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))
