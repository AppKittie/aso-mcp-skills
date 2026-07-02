from .app_scoped import APP_SCOPED_ANY_OF, APP_SCOPED_PROPERTIES, handle_app_scoped_list


TOOL = {
    "name": "list_organic_content",
    "description": (
        "Fetch organic creator videos with hosted media for a single app or across "
        "a category. Accepts app slug, AppKittie app ID, store ID, package name, or "
        "store URL — or 'category' for cross-app discovery. Filter by platform. "
        "Costs 1 credit per organic content item returned."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            **APP_SCOPED_PROPERTIES,
            "category": {
                "type": "string",
                "description": (
                    "App Store category (e.g. 'Health & Fitness') to discover organic "
                    "content across the category's top apps. Alternative to an app identifier."
                ),
            },
            "platform": {
                "type": "string",
                "description": "Creator platform filter: tiktok, instagram, or youtube.",
            },
        },
        "anyOf": [*APP_SCOPED_ANY_OF, {"required": ["category"]}],
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    return await handle_app_scoped_list(
        args,
        api_key,
        "/api/v1/organic",
        extra_keys=["platform"],
        allow_category=True,
    )
