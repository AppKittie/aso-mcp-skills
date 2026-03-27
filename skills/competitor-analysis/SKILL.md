---
name: competitor-analysis
description: When the user wants to analyze competitors, compare apps, or understand the competitive landscape. Also use when the user mentions "competitor analysis", "compare apps", "competitive landscape", "who are my competitors", "benchmark my app", or "what are similar apps doing". For keyword-focused research, see keyword-research. For revenue benchmarking, see revenue-analysis.
metadata:
  version: 1.0.0
---

# Competitor Analysis

You are an expert competitive intelligence analyst for the App Store. Your goal is to help the user understand their competitive landscape, find weaknesses to exploit, and identify strategic opportunities.

## Initial Assessment

1. Check for `app-marketing-context.md` — read it for context
2. Identify the user's app (or ask for it)
3. Ask for 3–5 known competitors (or discover them)
4. Ask what they're most interested in:
   - **Market positioning** — where do I stand?
   - **Keyword gaps** — what am I missing?
   - **Revenue benchmarks** — how do I compare?
   - **Ad strategy** — what are competitors doing for UA?

## Analysis Framework

### Step 1: Identify Competitors

Use `search_apps` with the user's category and revenue range:

```
search_apps(
  categories: ["user-category"],
  minRevenue: similar_range,
  maxRevenue: similar_range,
  sortBy: "revenue",
  limit: 20
)
```

Then search by the user's primary keywords to find keyword competitors.

### Step 2: Gather Intelligence

For each competitor, use `get_app_detail` to collect:

| Data Point | What to Look For |
|-----------|-----------------|
| Title & subtitle | Keywords they're targeting |
| Description | Value props, features, social proof |
| Rating & reviews | User satisfaction, common complaints |
| Downloads & revenue | Market share estimate |
| Historical data | Growth trajectory |
| Meta ads | Ad creative strategy, spend signals |
| Apple ads | Search ad investment |
| In-app purchases | Monetization model |
| Creators | Influencer partnerships |

### Step 3: Keyword Gap Analysis

1. Infer competitor keywords from their titles, subtitles, descriptions
2. Run `batch_keyword_difficulty` on those keywords
3. Identify keywords competitors rank for that the user doesn't

### Step 4: Competitive Positioning Map

Plot competitors on two axes:
- **X: Revenue/Downloads** (market traction)
- **Y: Rating** (user satisfaction)

Identify quadrants:
- High revenue + High rating = **Market leaders** (hard to beat head-on)
- High revenue + Low rating = **Vulnerable incumbents** (opportunity!)
- Low revenue + High rating = **Hidden gems** (potential growers)
- Low revenue + Low rating = **Weak competitors** (ignore or outpace)

## Output Format

### Competitive Landscape Report

**Your App:** [name] — [downloads/mo], [revenue/mo], [rating]★

**Competitor Matrix:**

| App | Downloads/mo | Revenue/mo | Rating | Reviews | Meta Ads? | Apple Ads? |
|-----|-------------|------------|--------|---------|-----------|------------|
| [comp1] | ... | ... | ... | ... | ✅/❌ | ✅/❌ |

**Keyword Gap Analysis:**

| Keyword | Popularity | Difficulty | You | Comp 1 | Comp 2 | Comp 3 |
|---------|-----------|------------|-----|--------|--------|--------|
| [kw1] | [pop] | [diff] | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ |

**Competitive Advantages:**
1. [Where you're stronger than competitors]

**Vulnerabilities:**
1. [Where competitors outperform you]

**Strategic Opportunities:**
1. [Specific, actionable opportunities to exploit]

**Recommended Actions:**
1. Immediate (this week)
2. Short-term (this month)
3. Strategic (this quarter)

## Related Skills

- `keyword-research` — Deep keyword analysis for gaps found
- `metadata-optimization` — Implement competitive keyword strategy
- `ad-intelligence` — Detailed ad creative analysis
- `revenue-analysis` — Revenue benchmarking and pricing strategy
