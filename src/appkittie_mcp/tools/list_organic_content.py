from .app_scoped import APP_SCOPED_PROPERTIES, handle_app_scoped_list


ORGANIC_SORT_FIELDS = [
    "date_created_timestamp",
    "followers_count",
    "view_count",
    "likes_count",
    "app_downloads",
    "app_revenue",
    "app_released_timestamp",
    "app_updated_timestamp",
]

ORGANIC_TEXT_SEARCH_FIELDS = [
    "video_description",
    "search_text",
    "handle",
    "user_id",
    "content_id",
    "content_language",
    "source",
    "app_title",
    "developer",
    "category",
    "title",
    "description",
]

ORGANIC_FILTER_PROPERTIES = {
    "search": {
        "type": "string",
        "description": "Search organic captions, handles, apps, developers, and categories.",
    },
    "textSearchFields": {
        "type": "array",
        "items": {"type": "string", "enum": ORGANIC_TEXT_SEARCH_FIELDS},
        "description": "Fields searched by 'search'.",
    },
    "category": {
        "type": "string",
        "description": "Single app category alias (for example, 'Health & Fitness').",
    },
    "categories": {
        "type": "array",
        "items": {"type": "string"},
        "description": "App categories to include.",
    },
    "excludedCategories": {
        "type": "array",
        "items": {"type": "string"},
        "description": "App categories to exclude.",
    },
    "platform": {
        "type": "string",
        "description": "Single creator platform alias: tiktok, instagram, or youtube.",
    },
    "contentSources": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Creator platforms to include.",
    },
    "excludedContentSources": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Creator platforms to exclude.",
    },
    "contentLanguages": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Content language codes to include, such as EN or DE.",
    },
    "excludedContentLanguages": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Content language codes to exclude.",
    },
    "handles": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Creator handles to include.",
    },
    "excludedHandles": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Creator handles to exclude.",
    },
    "developer": {"type": "string", "description": "Exact app developer filter."},
    "createdAfter": {
        "type": "number",
        "description": "Minimum content creation Unix timestamp.",
    },
    "createdBefore": {
        "type": "number",
        "description": "Maximum content creation Unix timestamp.",
    },
    "minFollowers": {"type": "number", "description": "Minimum creator followers."},
    "maxFollowers": {"type": "number", "description": "Maximum creator followers."},
    "minViews": {"type": "number", "description": "Minimum content views."},
    "maxViews": {"type": "number", "description": "Maximum content views."},
    "minLikes": {"type": "number", "description": "Minimum content likes."},
    "maxLikes": {"type": "number", "description": "Maximum content likes."},
    "minAppDownloads": {
        "type": "number",
        "description": "Minimum estimated monthly app downloads.",
    },
    "maxAppDownloads": {
        "type": "number",
        "description": "Maximum estimated monthly app downloads.",
    },
    "minAppRevenue": {
        "type": "number",
        "description": "Minimum estimated monthly app revenue.",
    },
    "maxAppRevenue": {
        "type": "number",
        "description": "Maximum estimated monthly app revenue.",
    },
    "sortBy": {
        "type": "string",
        "enum": ORGANIC_SORT_FIELDS,
        "description": "Organic or app metric used to sort results.",
    },
    "sortOrder": {
        "type": "string",
        "enum": ["asc", "desc"],
        "description": "Sort direction. Default: desc.",
    },
}

ORGANIC_FILTER_KEYS = tuple(ORGANIC_FILTER_PROPERTIES)

TOOL = {
    "name": "list_organic_content",
    "description": (
        "Search organic creator content with hosted media globally or by app, "
        "category, platform, language, creator reach, views, and app "
        "performance. Accepts any AppKittie or store app identifier. "
        "Costs 1 credit per organic content item returned."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            **APP_SCOPED_PROPERTIES,
            **ORGANIC_FILTER_PROPERTIES,
        },
    },
    "annotations": {"readOnlyHint": True, "openWorldHint": True},
}


async def handle(args, api_key):
    return await handle_app_scoped_list(
        args,
        api_key,
        "/api/v1/organic",
        extra_keys=ORGANIC_FILTER_KEYS,
        allow_category=True,
        allow_global=True,
    )
