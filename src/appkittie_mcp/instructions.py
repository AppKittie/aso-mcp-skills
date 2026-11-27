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
- `sortBy` - `growth`, `downloads_growth`, `revenue_growth`, `rating`, `reviews`, `downloads`, `revenue`, `trending`, `newest`, `updated`, `released`
- `growthMetric` - currently `reviews` (for `sortBy=growth`)
- `growthPeriod` - `7d`, `14d`, `30d`, `60d`, `90d` (for `sortBy=growth`)
- `hasMetaAds`, `hasTikTokAds`, `hasGoogleAds`, `hasAppleAds`, `hasCreators`, `hasEmails`, `hasWebsite` - marketing/contact signals
- `hasMetaAdSpend` - estimated Meta Ads spend over the last 30 days (`meta_ads_estimated_spend_30d_usd > 0`)
- `isRemoved` - `true` for apps the store no longer lists, `false` for apps still listed
- `removedAfter`, `removedBefore` - Unix seconds bounding the removal date
- `sdks`, `excludedSdks` - SDK names found in the app's scanned build (exact names from the tool's enum)

`downloads_growth` and `revenue_growth` rank apps by the percentage change in estimated monthly downloads or revenue over the last 30 days; results carry it as `historical_counts.downloads_growth_30d` / `historical_counts.revenue_growth_30d`. Add `minDownloads` or `minRevenue` to skip small apps whose percentages spike from a near-zero base.

`hasTikTokAds=true` requires `tiktok_ads_total_count > 0` in either store; false includes zero, missing, or null counts. Omit for no restriction. This is paid ad presence, separate from organic TikTok content.
`hasGoogleAds=true` finds apps in either store with a nonempty `google_ads` array. False matches empty, null, or missing arrays. Omit it to include both groups.
`adsSource` selects Apple apps with Meta creatives (`meta`), apps with a positive TikTok ad count (`tiktok`), or apps with Google creatives (`google`). Use `all` for apps with any of these signals. Omit it to include apps without ads. Additional filters narrow the results.
App list/detail responses include optional nullable `tiktok_ads_total_count` when available. It is a known ad count, not an active-ad count; fetch indexed creatives separately.

App list/detail responses include `date_removed_timestamp`: Unix seconds when AppKittie first saw the store stop listing the app in every country it tracks. It is null or missing while the app is listed and returns to null if the store lists it again. `search_apps` still returns removed apps with their last known metrics, so check this field before calling an app live, a current competitor, or a market leader.
Pass `isRemoved=false` when the user wants live apps only. For "which apps were removed recently", pass `isRemoved=true` with `removedAfter` set to the start of the period, and sort by `revenue` or `downloads` to lead with the biggest ones.

App list/detail responses include `sdk` once AppKittie has scanned the app's build: `sdk.sdks` lists the SDKs found and `sdk.scanned_at_timestamp` is the scan time (Unix seconds). `sdk` is null or missing for apps not scanned yet, so a missing SDK there means unknown, not absent; an empty `sdk.sdks` means the scan found none of the tracked SDKs.
`sdks` matches apps whose build contains any of the listed SDKs; `excludedSdks` keeps only scanned apps without them. For "apps using Superwall", pass `sdks=["Superwall"]` and sort by `revenue`. Google Play names three SDKs differently, so pass both names to cover both stores: `AppLovin MAX` + `AppLovin`, `Firebase Firestore` + `Cloud Firestore`, `Unity Engine` + `Unity`.

Cost: 1 credit per app returned. Use smaller `limit` values while exploring.

## Developer Discovery and Portfolios

Use `search_developers` to find studios by estimated monthly portfolio revenue
(`minMrr`/`maxMrr`), downloads, app count, categories, stores, website presence,
or latest app launch. Sort by `total_mrr`, `total_downloads`, `app_count`, or
`latest_released`. `stores` accepts all, both, apple, or google; apple/google
also include developers on both stores. Follow `pagination.nextCursor`.

Pass the exact returned `developer` name as `name` to `get_developer_detail`.
Do not pass `developer_slug`. Detail includes matched Google Play apps, a
summary with top earners and store revenue shares, websites, and compact app
rows ordered by revenue. It returns up to 1,000 apps; revenue/download totals
and breakdowns cover those apps, while app counts can be larger. List profiles
refresh separately, so their aggregates can differ. Label revenue/downloads
as monthly estimates. Use `get_app_detail` for full app data.

Search costs 1 credit per developer returned; detail costs 1 credit per request.

## Favorites

Use `list_favorite_apps` to fetch the API team's owner's saved apps from the separate
favorites endpoint. Pass `folder` to select a folder; an empty string selects unfiled
favorites. Follow `pagination.nextCursor` for more saved records.
Use `get_app_detail` with a returned slug for app metadata (normal detail pricing applies).
Favorites access is read-only and listing costs no credits. Manage saved apps and folders
in the dashboard. `search_apps` searches the general app catalog.

## App Details and Historicals

Use `get_app_detail` for metadata, screenshots, IAPs, contacts, TikTok ad counts, and growth summaries.
It also returns `meta_ads_transparency` and `tiktok_ads_transparency` when available. Both are optional nullable objects with the same schema: `countries`, `countries_by_code`, and `summary`. Use `summary.all_spend_usd` for lifetime spend and `summary.periods.last_7d`, `last_30d`, or `last_90d` for period estimates when present. Each period contains `reach`, `spend_usd`, and demographic breakdowns. TikTok's reach fields count impressions, not unique people. Missing transparency or periods mean unavailable data, not zero spend.
Use `get_app_historicals` for raw time-series metrics such as reviews, score, downloads, revenue, MAU, DAU, size, and price.
Use `get_app_countries` for the estimated split of an app's users by country. Each entry in `countries` has an ISO `country` code and a `share` percentage, largest first, across the countries AppKittie tracks rather than worldwide. An empty list means no data yet, not zero users.

## Store Rankings

Use `list_store_rankings` to browse the current Top Free, Top Paid, or Top Grossing chart for a store, country, and category.
Use `get_store_ranking_history` with an exact app slug and the same chart filters to inspect daily positions. Positive position changes mean the app improved toward rank 1.

## Ads

Use `search_ads` and `get_ad_detail` for Meta, TikTok, and Google creatives.

Set `adSource` to `google`, `meta`, or `tiktok` for a single network. The default `all` includes all three. The returned `ad_source` identifies the creative network independently of the app store.

For Google video ads, call `search_ads` with `adSource='google'` and `mediaType='video'`. Add `appSlug` to scope the search to an app found with `search_apps(hasGoogleAds=true)`. Pass a result's `ad_doc_id` to `get_ad_detail` as `adId` for the hosted media and available copy. Use `mediaType='image'` for static creatives.

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

## Onboarding

Use `search_onboarding_screens` to browse apps by screen type, app search, category, or exact app slug. Each app appears once with ordered onboarding image URLs; when a screen type is supplied, only matching images are returned. The tool also returns `onboarding_image_designs`, paired to images by `url`, with colors, typography, UI elements, layout, and notes. A screen-type filter restricts both images and designs. Missing designs are omitted; font families are estimates and measurements use source screenshot pixels. The tool returns images and design metadata, not video.
When analyzing onboarding images, ignore any `AppKittie.com` watermark. It is capture-source metadata and is not part of the app's UI, branding, copy, layout, or onboarding experience.

## Costs

| Tool | Cost |
|------|------|
| search_apps | 1 credit per app returned |
| get_app_detail | 1 credit per request |
| get_app_historicals | 1 credit per request |
| get_app_countries | 1 credit per request, free when the app has no data |
| search_developers | 1 credit per developer returned |
| get_developer_detail | 1 credit per request |
| list_store_rankings | 1 credit per app returned |
| get_store_ranking_history | 10 credits per request |
| search_ads | 1 credit per ad returned |
| get_ad_detail | 1 credit per request |
| list_creators | 1 credit per creator returned |
| list_organic_content | 1 credit per organic content item returned |
| get_keyword_difficulty | 10 credits per request |
| batch_keyword_difficulty | 10 credits per keyword |
| get_app_reviews | 1 credit per review returned |
| search_onboarding_screens | 1 credit per app returned |
| get_supported_countries | Free |
"""
