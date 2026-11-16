import json
from urllib.parse import quote

from ..api import api_get
from ..rpc import tool_result


TOOL = {
    "name": "get_developer_detail",
    "description": (
        "Get a developer's cross-store portfolio, estimated monthly revenue/download totals, "
        "store and top-earner breakdowns, websites, and compact app rows. "
        "Requires the exact developer name from search_developers, not developer_slug. "
        "Returns up to the 1,000 highest-revenue apps; revenue/download totals cover those apps. "
        "Costs 1 credit per request. Use get_app_detail for full app metadata."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 1024,
                "description": "Exact developer name, including capitalization and punctuation.",
            },
        },
        "required": ["name"],
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    name = args.get("name")
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 1024:
        return tool_result("Error: 'name' must be a non-empty developer name of at most 1024 characters.", is_error=True)
    data, err = await api_get(f"/api/v1/developers/{quote(name.strip(), safe='')}", {}, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))
