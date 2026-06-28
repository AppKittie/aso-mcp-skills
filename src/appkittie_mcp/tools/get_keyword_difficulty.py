import json

from ..api import api_get
from ..constants import STORE_SOURCES
from ..identifiers import as_str
from ..rpc import tool_result


TOOL = {
    "name": "get_keyword_difficulty",
    "description": (
        "Analyze a single Apple App Store or Google Play keyword's competitiveness. "
        "Returns popularity, difficulty, app count, traffic score, and top-ranking apps. "
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

    data, err = await api_get("/api/v1/keywords/difficulty", params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))

