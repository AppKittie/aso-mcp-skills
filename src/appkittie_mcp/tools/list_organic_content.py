from .app_scoped import APP_SCOPED_ANY_OF, APP_SCOPED_PROPERTIES, handle_app_scoped_list


TOOL = {
    "name": "list_organic_content",
    "description": (
        "Fetch organic creator videos with hosted media for a single app. "
        "Accepts app slug, AppKittie app ID, store ID, package name, or store URL. "
        "Costs 1 credit per organic content item returned."
    ),
    "inputSchema": {
        "type": "object",
        "properties": APP_SCOPED_PROPERTIES,
        "anyOf": APP_SCOPED_ANY_OF,
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    return await handle_app_scoped_list(args, api_key, "/api/v1/organic")

