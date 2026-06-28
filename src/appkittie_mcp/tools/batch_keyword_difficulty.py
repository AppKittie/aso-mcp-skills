import json

from ..api import api_post
from ..constants import STORE_SOURCES
from ..rpc import tool_result


TOOL = {
    "name": "batch_keyword_difficulty",
    "description": (
        "Analyze multiple Apple App Store or Google Play keywords at once (up to 10). "
        "Returns popularity, difficulty, app count, and traffic score for each keyword. "
        "Costs 10 credits per successfully analyzed keyword."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Keywords to analyze (1-10).",
            },
            "country": {"type": "string", "description": "App Store country code. Default: US."},
            "source": {
                "type": "string",
                "enum": STORE_SOURCES,
                "description": "Store source: apple_mobile or google_mobile. Default: apple_mobile.",
            },
        },
        "required": ["keywords"],
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    keywords = args.get("keywords")
    if not keywords or not isinstance(keywords, list):
        return tool_result(
            "Error: 'keywords' is required and must be a non-empty array of strings.",
            is_error=True,
        )
    if len(keywords) > 10:
        return tool_result("Error: Maximum 10 keywords per request.", is_error=True)

    body = {"keywords": keywords}
    if "country" in args:
        body["country"] = args["country"]
    if "source" in args:
        body["source"] = args["source"]

    data, err = await api_post("/api/v1/keywords/difficulty", body, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))

