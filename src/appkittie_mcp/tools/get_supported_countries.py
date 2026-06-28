import json

from ..constants import APP_STORE_COUNTRY_CODES
from ..rpc import tool_result


TOOL = {
    "name": "get_supported_countries",
    "description": (
        "Get the list of supported App Store country codes for keyword research. "
        "Free - no credit cost."
    ),
    "inputSchema": {"type": "object", "properties": {}},
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(_args, _api_key):
    countries = [{"code": code} for code in APP_STORE_COUNTRY_CODES]
    return tool_result(json.dumps({"data": countries}, indent=2))

