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
        "description": "Discover apps running ads and inspect Meta/Google creatives.",
        "arguments": [
            {"name": "category_or_search", "description": "Category or search term", "required": True},
            {"name": "ad_platform", "description": "meta, google, apple, or all", "required": False},
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
    args = {arg["name"]: arg.get("value", "") for arg in (arguments or [])}

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
        platform = (args.get("ad_platform", "all") or "all").lower()
        meta_filter = platform in ("meta", "all", "both")
        apple_filter = platform in ("apple", "all", "both")
        creative_sources = []
        if platform in ("meta", "all", "both"):
            creative_sources.append("meta")
        if platform in ("google", "all", "both"):
            creative_sources.append("google")
        if not creative_sources:
            creative_sources = ["meta", "google"]
        creative_source_text = " and ".join(f"adSource: '{source}'" for source in creative_sources)
        return [_user_message(
            f"Discover which apps are running ads for '{target}'.\n\n"
            f"1. Use search_apps with search: '{target}'{', hasMetaAds: true' if meta_filter else ''}, sortBy: 'revenue', limit: 20.\n"
            f"2. Use search_apps with search: '{target}'{', hasAppleAds: true' if apple_filter else ''}, sortBy: 'revenue', limit: 20 when relevant.\n"
            f"3. For top advertisers, use search_ads with appSlug and {creative_source_text}, sortBy: 'start_date', sortOrder: 'desc', limit: 10.\n"
            "4. Use get_ad_detail on standout ad_doc_id values.\n"
            "5. Analyze platforms, creative angles, copy, and opportunities."
        )]

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

