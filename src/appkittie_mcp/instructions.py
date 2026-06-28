INSTRUCTIONS = """# AppKittie MCP - Agent Guide

You have access to the AppKittie API through this MCP server. It lets you discover mobile apps across the Apple App Store and Google Play, analyze competitors, research store keywords, inspect ads, fetch creators and organic content, read user reviews, and access download/revenue intelligence.

## Discovering Apps

Use `search_apps` to find and filter apps.

Key filters:
- `search` - full-text search query
- `source` - `apple_mobile` or `google_mobile`
- `categories` - App Store categories
- `sortBy` - `growth`, `rating`, `reviews`, `downloads`, `revenue`, `trending`, `newest`, `updated`, `released`
- `growthMetric` - currently `reviews`
- `growthPeriod` - `7d`, `14d`, `30d`, `60d`, `90d`
- `hasMetaAds`, `hasAppleAds`, `hasCreators`, `hasEmails`, `hasWebsite` - marketing/contact signals

Cost: 1 credit per app returned. Use smaller `limit` values while exploring.

## App Details and Historicals

Use `get_app_detail` for metadata, screenshots, IAPs, contacts, and growth summaries.
Use `get_app_historicals` for raw time-series metrics such as reviews, score, downloads, revenue, MAU, DAU, size, and price.

App-scoped tools accept `appSlug`, `app_slug`, `appId`, `appStoreId`, or `appStoreUrl` where noted. Prefer `appSlug` when you already have it. Use store URLs or store IDs when the user provides those directly.

## Ads

Use `search_ads` and `get_ad_detail` for Meta and Google creatives. App detail responses do not embed ad payloads.

`search_ads` can filter by `appSlug`, `app_slug`, `appId`, `appStoreId`, or `appStoreUrl`. Use this when a user gives an App Store URL and asks for ads for that app.

## Creators and Organic Content

Use `list_creators` for TopYappers creator profiles associated with an app.
Use `list_organic_content` for organic creator videos with hosted media.

Both tools support `count` / `limit` and `cursor` pagination.

## Keywords

Use `batch_keyword_difficulty` for up to 10 seed keywords, then use `get_keyword_difficulty` for deep dives on the strongest opportunities. Keyword metrics are country-specific, so pass `country` when the target market is known.

## Reviews

Use `get_app_reviews` with a numeric App Store ID or Google Play package name. Paginate with `offset` and `nextOffset`.

## Costs

| Tool | Cost |
|------|------|
| search_apps | 1 credit per app returned |
| get_app_detail | 1 credit per request |
| get_app_historicals | 1 credit per request |
| search_ads | 1 credit per ad returned |
| get_ad_detail | 1 credit per request |
| list_creators | 1 credit per creator returned |
| list_organic_content | 1 credit per organic content item returned |
| get_keyword_difficulty | 10 credits per request |
| batch_keyword_difficulty | 10 credits per keyword |
| get_app_reviews | 1 credit per review returned |
| get_supported_countries | Free |
"""

