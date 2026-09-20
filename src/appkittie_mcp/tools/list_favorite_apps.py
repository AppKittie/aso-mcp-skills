import json

from ..api import api_get
from ..rpc import tool_result


TOOL = {
    "name": "list_favorite_apps",
    "description": (
        "List the API team's owner's saved app favorites, including slugs, folders, "
        "and save dates. Shares favorites with the owner's dashboard. Costs no credits. "
        "Use get_app_detail with a returned slug for app metadata."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "folder": {
                "type": "string",
                "maxLength": 128,
                "description": "Filter by folder; empty string selects unfiled favorites. Omit for all folders.",
            },
            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 50},
            "cursor": {"type": "integer", "minimum": 0, "description": "Offset from pagination.nextCursor."},
        },
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    params = {key: args[key] for key in TOOL["inputSchema"]["properties"] if key in args}
    data, err = await api_get("/api/v1/favorites/apps", params, api_key)
    if err:
        return tool_result(err, is_error=True)
    return tool_result(json.dumps(data, indent=2))
