import json
from urllib.parse import quote

from ..api import api_get
from ..identifiers import as_str
from ..rpc import tool_result


TOOL = {
    "name": "get_ad_detail",
    "description": (
        "Get detailed information for a single ad creative by ad_doc_id. "
        "Returns hosted creative assets, copy, delivery metadata, advertised app fields, "
        "and compact app summary when available. Costs 1 credit per request."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "adId": {"type": "string", "description": "The ad_doc_id returned by search_ads"},
        },
        "required": ["adId"],
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    ad_id = as_str(args.get("adId"))
    if not ad_id:
        return tool_result("Error: 'adId' is required.", is_error=True)

    data, err = await api_get(f"/api/v1/ads/{quote(ad_id, safe='')}", {}, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))

