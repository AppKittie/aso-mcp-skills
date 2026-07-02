INSTRUCTIONS = """# AppKittie MCP - Agent Guide

You have access to the AppKittie API through this MCP server. It lets you discover mobile apps across the Apple App Store and Google Play, analyze competitors, research store keywords, inspect ads, discover creators and organic content, read user reviews, and access download/revenue intelligence.

## App Identifiers

Every app-scoped tool accepts any of these identifier forms and resolves them automatically:

- AppKittie `appSlug` / `app_slug` (preferred when you already have it)
- Numeric App Store ID (e.g. `6480417616`)
- Google Play package name (e.g. `com.example.app`)
- Apple App Store or Google Play URL

Pass whichever the user gives you — no manual conversion needed.

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

## Ads

Use `search_ads` and `get_ad_detail` for Meta and Google creatives. App detail responses do not embed ad payloads.

`search_ads` returns a compact view by default (identity, status, key copy, app metrics) to keep responses small. Pass `view='full'` only when you need complete creative payloads with media URLs. Use `get_ad_detail` for a deep dive on one ad.

## Creators and Organic Content (Influencer Discovery)

Use `list_creators` for TopYappers creator profiles and `list_organic_content` for organic creator videos with hosted media.

Scope results one of two ways:
- Per app: pass any app identifier.
- Across a category: pass `category` (e.g. `Health & Fitness`) to discover creators across the category's top apps. Each result includes `app_slug` and `app_title` context.

Creator filters: `platform` (tiktok/instagram/youtube), `country`, `minFollowers`/`maxFollowers`, and `sortBy='followers'`.

To confirm a creator actually posted about an app (rather than being a loose name association), cross-reference their handle against `list_organic_content` for that app.

Both tools support `count` / `limit` and `cursor` pagination.

## Keywords

Use `batch_keyword_difficulty` for up to 10 seed keywords, then use `get_keyword_difficulty` for deep dives on the strongest opportunities. Keyword metrics are country-specific, so pass `country` when the target market is known.

`get_keyword_difficulty` returns the top 10 ranked apps by default. Set `topAppsLimit` (0-50) for more, or `includeTopApps=false` for metrics only.

## Reviews

Use `get_app_reviews` with any app identifier (numeric App Store ID, Google Play package name, app slug, or store URL). Paginate with `offset` and `nextOffset`.

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
