import json

from ..api import api_post
from ..constants import STORE_SOURCES
from ..identifiers import as_str
from ..rpc import tool_result


TOOL = {
    "name": "get_app_reviews",
    "description": (
        "Fetch user reviews for a specific Apple App Store or Google Play app. "
        "Supports pagination via offset. Costs 1 credit per review returned."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "appId": {
                "type": "string",
                "description": "Numeric App Store ID or Google Play package name.",
            },
            "source": {
                "type": "string",
                "enum": STORE_SOURCES,
                "description": "Store source. Inferred from appId if omitted.",
            },
            "country": {"type": "string", "description": "Country code. Default: US."},
            "maxReviews": {"type": "integer", "description": "Maximum reviews to fetch (1-300, default: 100)."},
            "offset": {"type": "integer", "description": "Pagination offset."},
        },
        "required": ["appId"],
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    app_id = as_str(args.get("appId"))
    if not app_id:
        return tool_result("Error: 'appId' is required.", is_error=True)

    body = {"appId": app_id}
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

