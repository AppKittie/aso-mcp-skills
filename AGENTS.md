# Agent Guidelines

This repo contains App Store Intelligence skills following the [Agent Skills](https://agentskills.io) open standard, plus an MCP server for real-time data access.

## Structure

```
src/worker.py              — MCP server (Cloudflare Workers, Python)
skills/<name>/SKILL.md     — Skill instructions (required, <500 lines)
skills/<name>/references/  — Detailed docs loaded on demand (optional)
tools/integrations/        — API integration guides (AppKittie)
tools/REGISTRY.md          — Capability matrix: which skill uses which tool
```

Compatible directories: `.cursor/skills/`, `.agents/skills/`, `.claude/skills/`, `.codex/skills/`

## SKILL.md Format

```yaml
---
name: skill-name          # Must match directory, lowercase+hyphens, 1-64 chars
description: ...          # Trigger phrases + scope boundaries, 1-1024 chars
metadata:
  version: 1.0.0
---
```

Description drives discovery — agent reads all descriptions to decide which skill to load. Include "When the user wants to...", trigger keywords, and "For X, see Y skill" boundaries.

## Writing Style

- Direct, actionable, second person
- Tables for comparisons, numbered lists for steps
- Bold for key terms, code blocks for examples
- No filler, no hedging

## App Store Reference

**iOS limits:** Title 30 chars, Subtitle 30 chars, Keyword field 100 chars (comma-separated, no spaces), Description 4000 chars (not indexed for search), Promotional text 170 chars.

**Key rules:** Title has highest keyword weight. Don't repeat keywords across fields. Use singular forms. Don't include "app" or category names in keyword field.

## Commits

`feat(skill-name): ...` / `fix(skill-name): ...` / `docs: ...`

Branches: `feature/skill-name`, `fix/skill-name-desc`, `docs/desc`
