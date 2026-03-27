# AppKittie — App Store Intelligence Skills & MCP Server

AI agent skills for **App Store intelligence**, **ASO**, and **competitive analysis**. Built for indie developers, app marketers, and growth teams who want **Cursor**, **Claude Code**, or any Agent Skills-compatible AI assistant to help with app discovery, keyword research, revenue analysis, ad intelligence, and competitor tracking.

Powered by real App Store data via the [AppKittie API](https://appkittie.com).

## Why This Exists

App Store intelligence is fragmented across expensive tools, manual research, and scattered blog posts. We packaged expert-level analysis into skills that any AI agent can use — so you get actionable insights directly in your IDE.

Each skill contains battle-tested frameworks, scoring rubrics, and output templates. The agent reads the skill, pulls real data from the App Store (via AppKittie), and gives you actionable recommendations — not generic advice.

## Quick Start

**Cursor** — Settings (Cmd+Shift+J) → Rules → Add Rule → Remote Rule (Github) → paste `https://github.com/appkittie/mcp`

**Claude Code** — `npx skills add appkittie/mcp`

**Manual** — `git clone https://github.com/appkittie/mcp.git && cp -r mcp/skills/* .cursor/skills/`

Then ask your agent:

```
"Find the most profitable apps in the Health & Fitness category"
"Research keywords for a meditation app targeting the US market"
"Analyze my competitors — my app ID is 1234567890"
"Which apps are running Meta ads in the productivity category?"
"What apps are growing fastest this week?"
"Optimize my App Store title and subtitle for these keywords"
"Set up my app marketing context for ongoing analysis"
"What's the revenue potential in the education category?"
```

Or invoke directly: `/app-discovery`, `/keyword-research`, `/metadata-optimization`, `/competitor-analysis`, `/growth-analysis`, `/ad-intelligence`, `/revenue-analysis`

## Skills

### Core Intelligence

| Skill | What it does |
|-------|-------------|
| [app-discovery](skills/app-discovery) | Search and filter iOS apps by category, revenue, downloads, growth, ratings, ads, and more |
| [keyword-research](skills/keyword-research) | Evaluate keywords by popularity, difficulty, traffic score, and top-ranking apps — build a prioritized keyword strategy |
| [metadata-optimization](skills/metadata-optimization) | Write optimized title, subtitle, keyword field, and description — with 3 variants and character counts |
| [competitor-analysis](skills/competitor-analysis) | Keyword gaps, revenue comparison, ad strategy teardown, and positioning map |

### Growth & Revenue

| Skill | What it does |
|-------|-------------|
| [growth-analysis](skills/growth-analysis) | Find fastest-growing apps, analyze growth drivers, spot market movers and emerging trends |
| [revenue-analysis](skills/revenue-analysis) | Revenue benchmarking, monetization model analysis, in-app purchase patterns, and pricing strategy |
| [ad-intelligence](skills/ad-intelligence) | Discover which apps run Meta ads and Apple Search Ads, analyze creative strategies, find UA opportunities |

### Foundation

| Skill | What it does |
|-------|-------------|
| [app-marketing-context](skills/app-marketing-context) | Create a context document (app, audience, competitors, goals) that all other skills reference |

## How It Works

```
You: "Find the most profitable fitness apps"

Agent:
  1. Reads app-discovery/SKILL.md (framework, output template)
  2. Calls AppKittie API → search_apps(categories: ["health-fitness"],
     sortBy: "revenue", limit: 20)
  3. Analyzes results: revenue distribution, growth patterns, pricing models
  4. Returns: Top Apps Table + Revenue Insights + Niche Opportunities

You: "Now research keywords for a meditation app"

Agent:
  1. Reads keyword-research/SKILL.md
  2. Calls batch_keyword_difficulty(keywords: ["meditation", "mindfulness", ...])
  3. Deep dives with get_keyword_difficulty on top opportunities
  4. Returns: Keyword Report + Opportunity Scores + Strategy Recommendation
```

Skills reference each other — `competitor-analysis` suggests running `keyword-research` for gaps found, which feeds into `metadata-optimization` for implementation.

## MCP Server

The MCP server runs on Cloudflare Workers and proxies the AppKittie API, making it accessible to any MCP-compatible AI agent.

### MCP Tools

| Tool | What it does | Cost |
|------|-------------|------|
| `search_apps` | Search and filter iOS apps with 30+ filter parameters | 1 credit/hit |
| `get_app_detail` | Full app data: metadata, revenue, ads, IAPs, creators, historical data | 1 credit |
| `get_keyword_difficulty` | Single keyword analysis with top-ranking apps | 10 credits |
| `batch_keyword_difficulty` | Analyze up to 10 keywords at once, sorted by opportunity | 10 credits/keyword |
| `get_supported_countries` | List valid App Store country codes | FREE |

### MCP Prompts

| Prompt | What it does |
|--------|-------------|
| `discover_niche` | Guided workflow to find profitable niches in a category |
| `competitor_analysis` | Step-by-step competitive intelligence gathering |
| `keyword_research` | Structured keyword research and prioritization |
| `app_growth_report` | Growth trend analysis with gainers and losers |
| `ad_intelligence` | Ad landscape analysis for a category or niche |

### Setup — MCP Config

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "appkittie": {
      "url": "https://mcp.appkittie.com",
      "headers": {
        "Authorization": "Bearer appkittie_your_key_here"
      }
    }
  }
}
```

Get your API key at [appkittie.com/settings](https://appkittie.com/settings).

### Deploy Your Own

```bash
cd mcp
npm install
npm run dev      # Local development
npm run deploy   # Deploy to Cloudflare Workers
```

## Installation

### Cursor

| Method | Command |
|--------|---------|
| GitHub Import | Settings → Rules → Add Rule → Remote Rule → `https://github.com/appkittie/mcp` |
| Project-level | `cp -r mcp/skills/* .cursor/skills/` |
| Global | `cp -r mcp/skills/* ~/.cursor/skills/` |

### Claude Code

| Method | Command |
|--------|---------|
| CLI | `npx skills add appkittie/mcp` |
| Specific skills | `npx skills add appkittie/mcp --skill keyword-research competitor-analysis` |
| Manual | `cp -r mcp/skills/* .claude/skills/` |

### Any Agent

```bash
git submodule add https://github.com/appkittie/mcp.git .agents/appkittie
```

Works with any tool that supports the Agent Skills standard (`.agents/skills/`, `.cursor/skills/`, `.claude/skills/`, `.codex/skills/`).

## API Reference

### Authentication

All API requests require a Bearer token:

```
Authorization: Bearer appkittie_your_key_here
```

### Endpoints

| Endpoint | Method | Purpose | Cost |
|----------|--------|---------|------|
| `/api/v1/apps` | GET | Search and filter apps | 1 credit/hit |
| `/api/v1/apps/:appId` | GET | Get app detail | 1 credit |
| `/api/v1/keywords/difficulty` | GET | Single keyword analysis | 10 credits |
| `/api/v1/keywords/difficulty` | POST | Batch keywords (up to 10) | 10 credits/keyword |

### Search Filters

The `search_apps` tool / `GET /api/v1/apps` endpoint supports 30+ filters:

**Discovery:** `search`, `categories`, `excludedCategories`, `developer`

**Metrics:** `minDownloads`/`maxDownloads`, `minRevenue`/`maxRevenue`, `minRating`/`maxRating`, `minReviews`/`maxReviews`

**Growth:** `growthMetric` (reviews/downloads/revenue), `growthPeriod` (7d–90d), `growthType` (all/positive/negative), `minGrowth`/`maxGrowth`

**Intelligence:** `hasMetaAds`, `hasAppleAds`, `hasCreators`, `hasEmails`, `hasWebsite`

**Sorting:** `sortBy` (growth/rating/reviews/downloads/revenue/trending/newest), `sortOrder` (asc/desc)

See [tools/REGISTRY.md](tools/REGISTRY.md) for the full filter reference.

## Data Available

### App List Fields
Title, icon, developer, category, rating, reviews, downloads estimate, revenue estimate, growth metrics, release/update dates

### App Detail Fields
Everything above plus: full description, screenshots, version history, in-app purchases, Meta ad creatives, Apple Search Ads data, creator partnerships, decision-maker contacts, social links, hiring status, historical time series

### Keyword Fields
Popularity (search volume proxy), difficulty (competition), app count, traffic score, top-ranking apps with title/icon/reviews/score/rank

## Contributing

PRs welcome — fix an inaccuracy, improve a framework, or add a new skill. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
