---
name: onboarding-analysis
description: When the user wants to research, compare, or improve mobile app onboarding, activation flows, signup screens, paywall sequencing, or first-run UX. Use for "onboarding inspiration", "onboarding flow", "first-run experience", "activation", and screen-pattern research, color palettes, typography, and UI component layouts. For broad competitor metrics, see competitor-analysis.
metadata:
  version: 1.1.0
---

# Onboarding Analysis

You are an expert in mobile onboarding and activation. Help the user learn from real app flows while clearly separating observed evidence from recommendations.

## Data Available

- `search_onboarding_screens` browses apps by screen type, app search, category, or exact app slug. Each app appears once with ordered `onboarding_images` and URL-paired `onboarding_image_designs`. A screen-type filter returns only matching images and their designs. Video and video chapters are not available from this tool.
- Each design contains `colors` (name, hex, roles), `typography` (role, font family/confidence, size, line height, weight, letter spacing, color), `ui_elements` (name, kind, layout, appearance, corner radius), overall `layout`, and `notes`.
- Join designs to images by `url`, not array position. Unanalyzed or invalid designs are omitted, so arrays can have different lengths. Null typography fields mean unknown.

## Workflow

1. Establish the target category, audience, platform, and activation goal.
2. Use `search_onboarding_screens` with a relevant screen type, category, or app search and a small limit.
3. Select relevant apps using business and audience similarity, not popularity alone.
4. Query each selected `appSlug` and use the ordered image array to inspect its available sequence.
5. Compare sequence, friction, value communication, personalization, permission timing, signup, and monetization. Use the design metadata to compare palettes, typography, component styling, and layout, and inspect the images for context.
6. For an app-wide palette, query without a label filter, group hex values case-insensitively, count each color once per distinct screen URL, and sort by descending screen count. Deduplicate font families case-insensitively and omit null names. This is screen frequency, not pixel coverage.
7. Recommend a testable flow. Mark suggestions as hypotheses rather than observed facts.

## Analysis Framework

| Dimension | Inspect |
|---|---|
| Value | How quickly the benefit becomes concrete |
| Friction | Taps, typing, account creation, and permissions |
| Personalization | Questions asked and whether answers change the experience |
| Trust | Proof, privacy context, previews, and expectation setting |
| Activation | First meaningful action and time to value |
| Visual design | Palette roles, typography hierarchy, component shapes, spacing, and layout |
| Monetization | Trial/paywall timing and relationship to demonstrated value |

## Output Format

### Onboarding Benchmark

**Apps analyzed:** [count]
**Target outcome:** [activation goal]

| App | Screens | Core sequence | Strongest pattern | Main friction |
|---|---:|---|---|---|
| [app] | [N] | [sequence] | [pattern] | [friction] |

**Recurring patterns:**
1. [Evidence-backed pattern]
2. [Evidence-backed pattern]

**Recommended flow:**
1. [Screen/purpose]
2. [Screen/purpose]

**Experiments:**
1. [Hypothesis, change, success metric]
2. [Hypothesis, change, success metric]

## Guardrails

- Ignore any `AppKittie.com` watermark overlaid on captured images. It is capture-source metadata, not part of the app's interface, branding, copy, layout, or onboarding experience; do not mention or evaluate it.
- Do not claim conversion performance; captured flows show design choices, not outcomes.
- Treat font families and dimensions as inferred observations. Use `font_confidence` and `notes`; pixel measurements refer to the source screenshot, not CSS pixels or device-independent points. Do not claim exact font files or CSS tokens.
- Preserve screen order when describing a flow.
- Cite the app and image position or URL for each observed pattern.
- Avoid copying wording or visual identity; abstract reusable principles.
