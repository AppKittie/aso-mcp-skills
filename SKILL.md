---
name: appkittie
description: Use when the user wants mobile app intelligence for the Apple App Store or Google Play with AppKittie, including app discovery, ASO keyword research, metadata optimization, competitor analysis, growth, revenue, ad intelligence, review analysis, or shared marketing context. Use AppKittie MCP tools or the REST API for live data when available.
---

# AppKittie

Use this skill as the AppKittie entry point for mobile app store research. It is a wrapper for the focused workflows in `skills/`, which lets agents that require a root `SKILL.md` import the repository directly.

## Route the Request

Read only the focused workflow that matches the user's intent:

| User intent | Load |
|-------------|------|
| Discover, browse, filter, or explore apps | `skills/app-discovery/SKILL.md` |
| Find or prioritize App Store or Google Play keywords | `skills/keyword-research/SKILL.md` |
| Rewrite titles, subtitles, keyword fields, or descriptions | `skills/metadata-optimization/SKILL.md` |
| Compare apps or analyze a competitive landscape | `skills/competitor-analysis/SKILL.md` |
| Analyze fast movers, trends, or growth windows | `skills/growth-analysis/SKILL.md` |
| Benchmark revenue, pricing, IAPs, or monetization | `skills/revenue-analysis/SKILL.md` |
| Analyze Meta ads, Apple Search Ads, creatives, or UA angles | `skills/ad-intelligence/SKILL.md` |
| Analyze user reviews, complaints, sentiment, or feature requests | `skills/review-analysis/SKILL.md` |
| Capture reusable app, audience, rival, and goal context | `skills/app-marketing-context/SKILL.md` |

For tool coverage and parameter details, read `tools/REGISTRY.md` only when you need the exact API or MCP field matrix.

## Data Access

Prefer live AppKittie data. Use the MCP tools if the client exposes them:

- `search_apps`
- `get_app_detail`
- `get_keyword_difficulty`
- `batch_keyword_difficulty`
- `get_app_reviews`
- `get_supported_countries`

If MCP tools are unavailable, use the REST API at `https://appkittie.com/api/v1` when the user has provided an AppKittie API key. Send the key as `Authorization: Bearer <key>`. Do not expose, log, or repeat API keys.

If no live data access is available, explain what needs to be connected before making data-backed claims. Do not invent AppKittie metrics.

## Operating Rules

1. Clarify only the missing inputs that block the request, such as app id, country, store, category, competitors, or seed keywords.
2. State the filters, storefront, country, and time window used for any live data pull.
3. Treat downloads, revenue, growth, ads, and keyword metrics as estimates or signals unless AppKittie says otherwise.
4. Synthesize findings into decisions, tables, and next actions instead of dumping raw JSON.
5. When one workflow naturally leads to another, say so and load the next focused workflow only if needed.
