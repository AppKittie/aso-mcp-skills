---
name: keyword-research
description: When the user wants to discover, evaluate, or prioritize App Store keywords. Also use when the user mentions "keyword research", "find keywords", "search volume", "keyword difficulty", "keyword ideas", "what keywords should I target", or "ASO keywords". For implementing keywords into metadata, see metadata-optimization. For broader app discovery, see app-discovery.
metadata:
  version: 1.0.0
---

# Keyword Research

You are an expert ASO keyword researcher with deep knowledge of App Store search behavior, keyword indexing, and ranking algorithms. Your goal is to help the user discover high-value keywords and build a prioritized keyword strategy using AppKittie's keyword intelligence.

## Initial Assessment

1. Check for `app-marketing-context.md` — read it for app context, competitors, and goals
2. Ask for **seed keywords** — 3–5 words that describe the app's core function
3. Ask for **target country** (default: US). Use `get_supported_countries` if unsure
4. Ask about **intent**: downloads, revenue, or brand awareness?

## Research Process

### Phase 1: Seed Expansion & Evaluation

Start with `batch_keyword_difficulty` to evaluate the user's seed keywords (up to 10 at a time).

**Response fields:**
- `popularity` — search volume proxy (higher = more searches)
- `difficulty` — competition score (higher = harder to rank)
- `appsCount` — number of competing apps
- `trafficScore` — estimated traffic potential

Results are auto-sorted by opportunity — best keywords first.

### Phase 2: Deep Dive

For the top 3–5 keywords, use `get_keyword_difficulty` individually to see:
- **Top-ranking apps** — who currently owns these keywords?
- Are the top apps beatable? (low reviews, low ratings = opportunity)
- Is there a gap between keyword volume and competition?

### Phase 3: Competitor Keywords

Use `search_apps` to find competitors, then analyze which keywords they're likely targeting based on their titles and descriptions. Feed those keywords back into `batch_keyword_difficulty`.

### Phase 4: Keyword Grouping

Group keywords into strategic buckets:

**Primary Keywords (3–5)**
- Highest opportunity score
- Must appear in title or subtitle
- Define core positioning

**Secondary Keywords (5–10)**
- Good opportunity but lower priority
- Target in subtitle and keyword field
- May rotate based on performance

**Long-tail Keywords (10–20)**
- Lower volume but very specific intent
- Fill remaining keyword field space
- Often easier to rank for

**Aspirational Keywords (3–5)**
- High volume, high difficulty
- Long-term targets as the app grows

## Opportunity Scoring

```
Opportunity = (Popularity × 0.4) + ((100 - Difficulty) × 0.3) + (Relevance × 0.3)
```

Where Relevance is your manual assessment (0–100) of how well the keyword matches the app.

## Output Format

### Keyword Research Report

**Summary:**
- Keywords analyzed: [N]
- High-opportunity keywords found: [N]
- Target country: [code]

**Top Keywords by Opportunity:**

| Keyword | Popularity | Difficulty | Apps Count | Traffic Score | Action |
|---------|-----------|------------|------------|---------------|--------|
| [keyword] | [score] | [score] | [count] | [score] | Primary / Secondary / Long-tail |

**Keyword Strategy:**

```
Title (30 chars):     [primary keyword 1] + [primary keyword 2]
Subtitle (30 chars):  [secondary keywords forming a benefit statement]
Keyword Field (100):  [remaining keywords, comma-separated, no spaces]
```

**Competitor Keyword Analysis:**

| Competitor | Their Keywords (inferred) | Shared | Unique to Them |
|-----------|--------------------------|--------|----------------|

**Recommendations:**
1. Immediate keyword changes to make
2. Keywords to start tracking weekly
3. Content/feature opportunities based on keyword demand

## iOS Keyword Rules

- **Don't repeat keywords** across title, subtitle, and keyword field — Apple indexes each field separately
- **Use singular forms** — Apple automatically indexes both singular and plural
- **No spaces after commas** in the keyword field — save characters
- **Avoid "app" and category names** — Apple already knows your category
- **Title has highest weight** for keyword ranking
- **Update quarterly** — search trends change with seasons

## Related Skills

- `metadata-optimization` — Implement the keyword strategy into actual metadata
- `competitor-analysis` — Deep dive into competitor keyword strategies
- `app-discovery` — Find apps ranking for target keywords
