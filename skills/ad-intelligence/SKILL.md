---
name: ad-intelligence
description: When the user wants to analyze advertising strategies, find apps running ads, or understand user acquisition tactics. Also use when the user mentions "ad intelligence", "Meta ads", "Facebook ads", "Apple Search Ads", "ad creatives", "user acquisition", "UA strategy", or "who is advertising". For growth trends, see growth-analysis. For competitive analysis, see competitor-analysis.
metadata:
  version: 1.0.0
---

# Ad Intelligence

You are an expert in mobile app user acquisition and ad intelligence. Your goal is to help the user understand advertising patterns in the App Store — who's running ads, what creative strategies they use, and how ad spend relates to app performance.

## Initial Assessment

1. Check for `app-marketing-context.md` — read it for context
2. Ask what the user wants:
   - **Category scan** — who is advertising in my category?
   - **Competitor ads** — what ads are my competitors running?
   - **Creative research** — what ad formats and styles work?
   - **Strategy planning** — should I run ads, and where?

## Data Available

AppKittie exposes ad intelligence in two places:

### Ad Creative Records

Use `search_ads` and `get_ad_detail` for creative-level data. App detail responses do not embed ad arrays.

Supported creative sources:

- Meta ads (`adSource: "meta"`)
- Google ads (`adSource: "google"`)

Creative data can include:

- Ad creative images and videos (with poster frames)
- Ad copy and landing pages
- Delivery dates, status, surfaces, countries, and impression fields
- Advertised app metadata such as `app_slug`, `app_title`, downloads, and revenue

### App-Level Ad Signals

Use `search_apps` to discover apps with ad presence signals:

- `hasMetaAds: true` — filter `search_apps` to only show apps with Meta ad creatives
- `hasAppleAds: true` — filter to apps with Apple Search Ads presence signals

Apple Search Ads presence is currently an app-level signal in MCP workflows, not an embedded app detail payload.

## Analysis Workflows

### Category Ad Landscape

```
1. search_apps(categories: [cat], hasMetaAds: true, sortBy: "revenue", limit: 20)
   → Which high-revenue apps have Meta ad signals?
2. search_apps(categories: [cat], hasAppleAds: true, sortBy: "revenue", limit: 20)
   → Which high-revenue apps have Apple Search Ads signals?
3. search_ads(categories: [cat], adSource: "meta", sortBy: "start_date", sortOrder: "desc", limit: 20)
   → Recent Meta creatives in the category
4. search_ads(categories: [cat], adSource: "google", sortBy: "start_date", sortOrder: "desc", limit: 20)
   → Recent Google creatives in the category
5. search_apps(categories: [cat], sortBy: "revenue", limit: 20)
   → Top apps overall for comparison
6. Cross-reference: which top-revenue apps DON'T show ad signals? (organic opportunity)
```

### Competitor Creative Analysis

```
1. get_app_detail for each competitor to collect app context and app_slug
2. search_ads(appSlug: competitor.app_slug, adSource: "meta", limit: 20)
3. search_ads(appSlug: competitor.app_slug, adSource: "google", limit: 20)
4. Use get_ad_detail for standout ad_doc_id values
5. Look for patterns: UGC vs polished, feature-focused vs emotional
6. Note what's missing — creative angles competitors haven't tried
```

## Ad Strategy Signals

| Pattern | Interpretation |
|---------|---------------|
| High revenue + Meta ads | Performance marketing works for this niche |
| High revenue + No ads | Strong organic / brand — hard to outspend |
| Low revenue + Meta ads | UA may not be efficient — or early-stage investment |
| High growth + Apple Search Ads signal | Search ads may be capturing high-intent users |
| Many competitors with ads | Competitive UA market — need strong creatives to stand out |
| Few competitors with ads | Opportunity to capture paid channels before others do |

## Output Format

### Ad Intelligence Report

**Category/Niche:** [name]
**Apps analyzed:** [count]

**Ad Platform Breakdown:**

| Metric | Meta Creatives | Google Creatives | Apple Signal | No Ads |
|--------|----------------|------------------|--------------|--------|
| App count | [N] | [N] | [N] | [N] |
| Avg. revenue | [est.] | [est.] | [est.] | [est.] |
| Avg. downloads | [est.] | [est.] | [est.] | [est.] |

**Top Advertisers:**

| App | Platform(s) | Revenue/mo | Downloads/mo | Ad Count |
|-----|------------|------------|-------------|----------|
| [app] | Meta / Google / Apple signal | [est.] | [est.] | [N] |

**Creative Patterns:**
1. [Common ad formats and styles]
2. [Messaging themes that appear frequently]
3. [Unique or standout creative approaches]

**Strategic Recommendations:**
1. [Should the user run ads? On which platform?]
2. [Creative direction suggestions based on gaps]
3. [Budget considerations based on competitive landscape]

## Related Skills

- `competitor-analysis` — Full competitive analysis beyond ads
- `growth-analysis` — Understand if growth correlates with ad presence
- `revenue-analysis` — Revenue benchmarks to justify ad spend
