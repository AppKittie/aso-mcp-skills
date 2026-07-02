from .app_scoped import APP_SCOPED_ANY_OF, APP_SCOPED_PROPERTIES, handle_app_scoped_list


CREATOR_FILTER_KEYS = [
    "platform",
    "country",
    "minFollowers",
    "maxFollowers",
    "sortBy",
    "sortOrder",
]

TOOL = {
    "name": "list_creators",
    "description": (
        "Fetch TopYappers creator profiles for a single app or across a category. "
        "Accepts app slug, AppKittie app ID, store ID, package name, or store URL — "
        "or 'category' for cross-app creator discovery. "
        "Filter by platform, country, and follower range. "
        "Costs 1 credit per creator returned."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            **APP_SCOPED_PROPERTIES,
            "category": {
                "type": "string",
                "description": (
                    "App Store category (e.g. 'Health & Fitness') to discover creators "
                    "across the category's top apps. Alternative to an app identifier."
                ),
            },
            "platform": {
                "type": "string",
                "description": "Creator platform filter: tiktok, instagram, or youtube.",
            },
            "country": {
                "type": "string",
                "description": "Creator country code filter (e.g. US).",
            },
            "minFollowers": {"type": "integer", "description": "Minimum follower count."},
            "maxFollowers": {"type": "integer", "description": "Maximum follower count."},
            "sortBy": {
                "type": "string",
                "enum": ["relevance", "followers"],
                "description": "Sort order. Default: relevance.",
            },
            "sortOrder": {"type": "string", "enum": ["asc", "desc"], "description": "Sort direction. Default: desc."},
        },
        "anyOf": [*APP_SCOPED_ANY_OF, {"required": ["category"]}],
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    return await handle_app_scoped_list(
        args,
        api_key,
        "/api/v1/creators",
        extra_keys=CREATOR_FILTER_KEYS,
        allow_category=True,
    )
