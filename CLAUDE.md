# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Documentation site for Databricks AI Dev Kit — built with Astro Starlight, deployed to GitHub Pages at `robkisk.github.io/aidevkit.github.io`. Content is a mix of auto-generated pages (synced from ai-dev-kit source) and manually curated "Guided Journey" editorial pages.

## Commands

```bash
npm run dev          # Dev server at localhost:4321/aidevkit.github.io
npm run build        # Production build (catches MDX/frontmatter errors)
npm run preview      # Preview built output

# Content pipeline (Python, run with uv)
uv run scripts/sync_content.py              # Dry run — report what's new
uv run scripts/sync_content.py --write      # Write new skeleton pages
uv run scripts/sync_content.py --skill <name> --write --force  # Force-overwrite a specific skill
```

## Content Pipeline

Three Claude Code skills compose the workflow: `/sync-content` → `/curate-content` → `/deploy-site`.

**Source:** Skill definitions live in `/Users/robby.kiskanyan/dev/aitools/gold-ctx/ai-dev-kit/databricks-skills/`. Each skill directory has a `SKILL.md` (becomes the index page) and optional companion `.md` files (become child pages).

**sync_content.py** reads the source repo and generates `.mdx` skeleton pages. Key config:
- `SKILL_MAP` (line ~40) maps source skill names to `(category-slug, site-slug)` pairs
- `SINGLE_PAGE_SKILLS` set controls which skills render as a single `.mdx` vs directory with children
- New skills that aren't in `SKILL_MAP` trigger a `WARN: unmapped skills` message — the `/sync-content` skill auto-registers these

**Sync is add-only by default.** Without `--force`, existing pages are never overwritten. This protects curated content.

## Editorial Format: Guided Journey

Child pages follow the "Guided Journey" template (see `.claude/skills/curate-content/guided-journey-template.md`):

1. `**Skill:** \`skill-name\`` reference line
2. **What You Can Build** — outcome opener, not feature definition
3. **In Action** — realistic prompt → flagship code → key decisions (3-5 bullets)
4. **More Patterns** — 2-4 additional prompt → code → explanation sets
5. **Watch Out For** — 2-4 gotchas drawn from real patterns

Voice: senior engineer peer. Tool-agnostic ("your AI coding assistant", never "Claude"). Opinionated, no hedging, no filler. Target 100-250 lines, 3-6 code blocks per page.

## Frontmatter Conventions

```yaml
---
curated: true              # Page follows Guided Journey format (added by /curate-content)
title: Outcome-Focused Title
description: Under 160 chars, outcome-focused
sidebar:
  order: 1                 # 0 = index page, 1+ = child pages
  badge:
    text: New
    variant: tip           # User-facing "new skill" indicator
---
```

- **`curated: true`** = already curated, don't touch. Missing = needs curation.
- **`badge: New`** = user-facing indicator; removed manually when skill is no longer new.
- Index pages stay synced from source and are not curated.

## MDX Escaping

In prose (outside code fences and inline backticks), these must be escaped:
- `<` → `&lt;`, `>` → `&gt;` (MDX treats as JSX tags)
- `{` → `\{`, `}` → `\}` (MDX treats as expressions)

Code fences and inline code need no escaping. The sync script handles this automatically via `escape_mdx_angles()`.

## Sidebar

Configured in `astro.config.mjs`. Skills use `autogenerate: { directory: '...' }` per skill group — Starlight auto-discovers all `.mdx` files and sorts by `sidebar.order`. Single-page skills use `{ slug: '...' }` instead.

When adding a new skill: add an `autogenerate` entry under the right category group, and add the `SKILL_MAP` entry in `sync_content.py`.

## Architecture

```
src/content/docs/skills/    # 6 categories → N skill groups → child pages
src/content/docs/mcp-tools/ # Auto-generated MCP tool reference (8 pages)
src/content/docs/reference/ # Auto-generated indexes (all-skills, all-mcp-tools)
src/content/docs/guides/    # Manually written end-to-end walkthroughs
src/pages/index.astro       # Landing page (stats updated by sync script)
scripts/sync_content.py     # Content pipeline script
.claude/skills/             # 3 project skills (sync, curate, deploy)
```

Custom components: `Hero.astro` overrides Starlight default. Brand styling in `src/styles/databricks.css` (DM Sans font, Databricks color palette).

## Deployment

Push to `main` triggers GitHub Actions → builds Astro → deploys to GitHub Pages. Verify with `gh run list --limit 1 --repo robkisk/aidevkit.github.io`.
