---
name: app-marketing-context
description: When the user wants to create a shared context document for their app that other skills can reference. Also use when the user mentions "set up my app", "configure my app context", "my app details", or before running any other skill for the first time. This skill creates app-marketing-context.md which all other skills read for background.
metadata:
  version: 1.0.0
---

# App Marketing Context

You are setting up a shared context document that all AppKittie skills will reference. This ensures consistent, personalized advice across keyword research, competitor analysis, metadata optimization, and more.

## When to Use

Run this skill:
- **First time** using AppKittie skills for a specific app
- When the app's **strategy changes** (new target market, repositioning)
- When **competitors shift** significantly

## Information to Gather

Ask the user for each section. If they have an App Store ID, use `get_app_detail` to pre-fill what you can.

### 1. App Identity

- **App name** (brand)
- **App Store ID** (numeric) or slug
- **One-sentence description** — what does the app do?
- **Target platform** — iOS only, or also Android?

### 2. Target Audience

- **Primary audience** — who is the main user?
- **Secondary audience** — any secondary segments?
- **User problems** — what pain points does the app solve?
- **User language** — how do users describe their problem? (important for keywords)

### 3. Competitive Landscape

- **Direct competitors** — apps that do the same thing (list 3–5)
- **Indirect competitors** — apps that solve the same problem differently
- **Key differentiators** — what makes this app unique?

### 4. Current Performance

Use `get_app_detail` if available:
- **Downloads/month** (estimated)
- **Revenue/month** (estimated)
- **Rating** and **review count**
- **Current keywords** (if known)
- **Running ads?** (Meta, Apple Search Ads)

### 5. Goals

- **Primary goal** — downloads, revenue, ratings, brand awareness?
- **Target metrics** — specific numbers they're aiming for
- **Timeline** — when do they want to achieve this?
- **Budget** — any ad budget or is it organic only?

## Output Format

Generate an `app-marketing-context.md` file:

```markdown
# App Marketing Context

## App
- **Name:** [name]
- **App Store ID:** [id]
- **Description:** [one-sentence]
- **Category:** [primary genre]
- **Price:** [free/paid/subscription]

## Audience
- **Primary:** [description]
- **Secondary:** [description]
- **Pain points:** [list]
- **Language:** [how users describe the problem]

## Competitors
| App | Strengths | Weaknesses |
|-----|-----------|-----------|
| [comp1] | [strengths] | [weaknesses] |

## Current Performance
- **Downloads/mo:** [est.]
- **Revenue/mo:** [est.]
- **Rating:** [★] ([count] reviews)
- **Known keywords:** [list]

## Goals
- **Primary:** [goal]
- **Target:** [metrics]
- **Timeline:** [timeframe]
- **Budget:** [amount or "organic only"]

## Notes
[Any additional context]
```

## Related Skills

All other skills check for this file:
- `keyword-research` — uses audience language and competitors
- `metadata-optimization` — uses brand, keywords, value prop
- `competitor-analysis` — uses competitor list and differentiators
- `growth-analysis` — uses current performance as baseline
- `ad-intelligence` — uses budget and goals
- `revenue-analysis` — uses revenue targets and pricing model
- `app-discovery` — uses category and competitive context
