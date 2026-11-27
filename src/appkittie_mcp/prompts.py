import json


PROMPTS = [
    {
        "name": "discover_niche",
        "description": "Discover a profitable App Store or Google Play niche.",
        "arguments": [
            {"name": "category", "description": "Category to explore", "required": True},
            {"name": "revenue_range", "description": "Target monthly revenue range", "required": False},
            {"name": "source", "description": "Store source: apple_mobile or google_mobile", "required": False},
        ],
    },
    {
        "name": "competitor_analysis",
        "description": "Analyze competitors for a specific app or keyword.",
        "arguments": [
            {"name": "app_or_keyword", "description": "App ID, app URL, app slug, or keyword", "required": True},
        ],
    },
    {
        "name": "keyword_research",
        "description": "Research and prioritize App Store or Google Play keywords.",
        "arguments": [
            {"name": "seed_keywords", "description": "Comma-separated seed keywords", "required": True},
            {"name": "country", "description": "Target country code. Default: US", "required": False},
            {"name": "source", "description": "Store source. Default: apple_mobile", "required": False},
        ],
    },
    {
        "name": "app_growth_report",
        "description": "Generate a traction report for a category or the whole catalog.",
        "arguments": [
            {"name": "category", "description": "Category to analyze", "required": False},
            {"name": "period", "description": "Growth period: 7d, 14d, 30d, 60d, 90d", "required": False},
        ],
    },
    {
        "name": "ad_intelligence",
        "description": "Find apps with Google, Meta, TikTok, or Apple Search Ads and inspect available creatives.",
        "arguments": [
            {"name": "category_or_search", "description": "Category or search term", "required": True},
            {"name": "ad_platform", "description": "Choose google, meta, tiktok, apple (app signal), or all (default).", "required": False},
        ],
    },
    {
        "name": "review_analysis",
        "description": "Analyze user reviews for an App Store or Google Play app.",
        "arguments": [
            {"name": "app_id", "description": "App Store ID or Google Play package name", "required": True},
            {"name": "source", "description": "Store source", "required": False},
            {"name": "country", "description": "Country code. Default: US", "required": False},
        ],
    },
]


def render_prompt(name, arguments):
    # MCP sends a name-to-value object. Older clients used a list of named values.
    args = arguments if isinstance(arguments, dict) else {
        arg["name"]: arg.get("value", "") for arg in (arguments or [])
    }

    if name == "discover_niche":
        category = args.get("category", "")
        revenue = args.get("revenue_range", "")
        source = args.get("source", "apple_mobile") or "apple_mobile"
        revenue_filters = ""
        if revenue and "-" in revenue:
            parts = revenue.split("-")
            revenue_filters = f", minRevenue: {parts[0]}, maxRevenue: {parts[1]}"
        return [_user_message(
            f"Discover profitable opportunities in '{category}' for source '{source}'.\n\n"
            f"1. Use search_apps with categories: ['{category}'], sortBy: 'revenue', "
            f"sortOrder: 'desc'{revenue_filters}, source: '{source}', limit: 20.\n"
            f"2. Use search_apps with categories: ['{category}'], sortBy: 'growth', "
            f"growthMetric: 'reviews', growthPeriod: '7d', sortOrder: 'desc', source: '{source}', limit: 20.\n"
            "3. Get detail on the top 3 most interesting apps.\n"
            "4. Summarize revenue ranges, growth patterns, gaps, pricing models, and specific opportunities."
        )]

    if name == "competitor_analysis":
        target = args.get("app_or_keyword", "")
        return [_user_message(
            f"Run a competitive analysis for '{target}'.\n\n"
            "1. If the target looks like an app ID, app slug, or store URL, use get_app_detail. Otherwise search_apps.\n"
            "2. Identify the top 5 competitors.\n"
            "3. Compare downloads, revenue, ratings, reviews, ad signals, positioning, and monetization.\n"
            "4. For apps with ad signals, use search_ads and get_ad_detail.\n"
            "5. Use batch_keyword_difficulty for related keyword opportunities.\n"
            "6. Produce a comparison table and actionable gaps."
        )]

    if name == "keyword_research":
        seeds = args.get("seed_keywords", "")
        country = args.get("country", "US") or "US"
        source = args.get("source", "apple_mobile") or "apple_mobile"
        keyword_list = [keyword.strip() for keyword in seeds.split(",") if keyword.strip()]
        keywords_json = json.dumps(keyword_list[:10])
        return [_user_message(
            f"Research keywords for source '{source}' in country '{country}' from seeds: {seeds}\n\n"
            f"1. Use batch_keyword_difficulty with keywords: {keywords_json}, country: '{country}', source: '{source}'.\n"
            "2. For the top 3 by opportunity, use get_keyword_difficulty.\n"
            "3. Analyze volume-to-difficulty, ranking apps, long-tail variants, and keywords to avoid.\n"
            "4. Provide a prioritized keyword strategy."
        )]

    if name == "app_growth_report":
        category = args.get("category", "")
        period = args.get("period", "7d") or "7d"
        cat_filter = f", categories: ['{category}']" if category else ""
        return [_user_message(
            f"Generate an app growth report{f' for {category}' if category else ''}.\n\n"
            f"1. Use search_apps with sortBy: 'growth', growthMetric: 'reviews', growthPeriod: '{period}', "
            f"sortOrder: 'desc'{cat_filter}, limit: 20.\n"
            "2. Get detail on the top 3 most interesting apps.\n"
            "3. Summarize top movers, likely drivers, trends, and entrant opportunities."
        )]

    if name == "ad_intelligence":
        target = args.get("category_or_search", "")
        platform = (args.get("ad_platform") or "all").strip().lower()
        app_filters = {
            "meta": "adsSource: 'meta'",
            "tiktok": "hasTikTokAds: true",
            "google": "hasGoogleAds: true",
            "apple": "hasAppleAds: true",
            "all": "adsSource: 'all'",
        }
        if platform == "all":
            app_sources, creative_sources = ("all", "apple"), ("meta", "tiktok", "google")
        elif platform == "both":
            # Preserve the original Meta and TikTok comparison and separate Apple signal.
            app_sources, creative_sources = ("meta", "tiktok", "apple"), ("meta", "tiktok")
        elif platform in app_filters:
            app_sources = (platform,)
            creative_sources = () if platform == "apple" else (platform,)
        else:
            return [_user_message("Choose google, meta, tiktok, apple, or all for ad_platform.")]

        steps = [
            f"Use search_apps with search: {target!r}, {app_filters[source]}, sortBy: 'revenue', limit: 20."
            for source in app_sources
        ]
        for source in creative_sources:
            steps.append(
                f"Pass a returned app_slug to search_ads as appSlug with adSource: '{source}', "
                "sortBy: 'start_date', sortOrder: 'desc', limit: 10."
            )
        if creative_sources:
            steps.append("Pass a returned ad_doc_id to get_ad_detail as adId to inspect the media and available copy.")
            steps.append("Summarize the observed creative formats and messaging for the requested networks.")
        else:
            steps.append("Summarize Apple Search Ads presence and the estimated revenue of the matching apps.")
        workflow = "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1))
        return [_user_message(f"Research ads for {target!r}.\n\n{workflow}")]

    if name == "review_analysis":
        app_id = args.get("app_id", "")
        country = args.get("country", "US") or "US"
        source = args.get("source", "")
        source_fragment = f", source: '{source}'" if source else ""
        return [_user_message(
            f"Analyze user reviews for app ID '{app_id}' in country '{country}'.\n\n"
            f"1. Use get_app_detail with appId: '{app_id}'.\n"
            f"2. Use get_app_reviews with appId: '{app_id}', country: '{country}'{source_fragment}, maxReviews: 100.\n"
            "3. Paginate if needed with nextOffset.\n"
            "4. Summarize sentiment, praise, complaints, feature requests, rating distribution, and recommendations."
        )]

    return [_user_message(f"Unknown prompt: {name}")]


def _user_message(text):
    return {"role": "user", "content": {"type": "text", "text": text}}
