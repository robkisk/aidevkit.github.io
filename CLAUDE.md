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
uv run scripts/sync_content.py --write --force  # Force-refresh (safe — protects curated pages)
uv run scripts/sync_content.py --skill <name> --write --force  # Force-overwrite a specific skill
```

## Content Refresh Workflow

Three steps to update the site with new content from ai-dev-kit:

### 1. Sync

```bash
uv run scripts/sync_content.py                # Dry run — see what's new/unmapped
uv run scripts/detect_drift.py                # Surface curated pages with stale upstream source
uv run scripts/sync_content.py --write --force  # Write changes (curated pages protected)
```

If the dry run shows **unmapped skills**, add entries to `SKILL_MAP` in `sync_content.py`. New MCP tool files need entries in both `MCP_FILE_TO_PAGE` and `MCP_PAGE_INTROS`. New skills need an entry in `SKILL_INDEX_INTROS`.

The `--force` flag is safe to use because `is_curated()` checks for `curated: true` in existing frontmatter and skips those pages. The sync also auto-clears all "New" sidebar badges before writing, so only genuinely new pages get the badge.

`detect_drift.py` is informational — it flags skills where source git commit time is newer than the max mtime of any curated page in that directory. A flagged skill may not need re-curation if the source diff is agent-instruction-only (not user-facing). Read the source diff before re-curating. After triaging a flagged skill as no-site-impact, `touch` its curated pages to acknowledge the flag — otherwise it reappears on every run.

`detect_drift.py` also validates every MCP tool name across the whole site — backticked in prose, bare inside code fences — (including hand-maintained pages with no upstream source dir: `prompt-library/`, `guides/`, `mcp-tools/index.mdx`) against the current upstream tool surface. It parses every tool name that ever existed in upstream git history and flags site references to tools since removed or renamed — each flag includes the source file's current tools as replacement candidates. Upstream is canonical: a reference to a removed tool must be rewritten to the current tool or deleted, never kept.

### 2. Curate new pages

Find uncurated pages:
```bash
grep -rL "curated: true" src/content/docs/skills/*/*/index.mdx
```

Then curate them into Guided Journey format (see Editorial Format below). Curate in parallel by dispatching agents per category.

### 3. Deploy

```bash
npm run build    # Catch MDX errors
git add <files> && git commit && git push
gh run list --limit 1 --repo robkisk/aidevkit.github.io
```

## Content Pipeline Details

**Source:** Skill definitions live in `/Users/robby.kiskanyan/dev/aitools/gold-ctx/ai-dev-kit/databricks-skills/`. Each skill directory has a `SKILL.md` and optional companion `.md` files (become child pages). MCP tools live in `databricks-mcp-server/databricks_mcp_server/tools/`.

**sync_content.py** reads the source repo and generates `.mdx` pages. Key config sections:
- `SKILL_MAP` (~line 40) — maps source skill names to `(category-slug, site-slug)` pairs. **The key must exactly match the source directory name under `databricks-skills/`** — a typo (singular vs plural, missing prefix) silently produces an "unmapped skills" warning even when the site directory already exists.
- `SINGLE_PAGE_SKILLS` — skills rendered as a single `.mdx` vs directory with children
- `MCP_FILE_TO_PAGE` — maps MCP tool source files to site page slugs
- `MCP_PAGE_INTROS` — intro overview + example prompts for each MCP reference page
- `SKILL_INDEX_INTROS` — intro overview + example prompts for each skill index page
- `MCP_PAGE_TITLES` — display titles for MCP pages

**Curated page protection:** `is_curated()` checks for `curated: true` in existing frontmatter. Pages with this flag are never overwritten, even with `--force`. This is the primary safeguard for hand-edited Guided Journey content.

**`--force` rewrites blindly.** The summary line "N updated" reports files written, not files where content changed. After running with `--force`, use `git diff` to confirm which auto-generated pages actually drifted vs. were rewritten with identical bytes. Curated pages are protected from `--force` overwrites; auto-generated pages (MCP refs, indexes) are not.

**Index page content:** When a `SKILL_INDEX_INTROS` entry exists, the index page shows only the intro (no SKILL.md body). The SKILL.md content is agent instructions that render poorly as user-facing docs. Curated child pages provide the detailed content.

**Badge lifecycle:** `clear_new_badges()` runs at the start of every full sync, stripping all "New" badges. Only pages created in that run get the badge. No manual badge management needed.

**MDX escaping:** Three functions handle escaping:
- `escape_mdx_angles()` — skill page bodies (tracks code fences)
- `escape_mdx_inline()` — MCP tool descriptions and reference table cells
- Both escape `<` → `&lt;`, `>` → `&gt;`, `{` → `\{`, `}` → `\}` outside backticks

**New skeleton pages are not editable drafts.** When sync creates a page from a source `.md` file (e.g., `connections.md` → `connections.mdx`), the MDX escaping strips structure — inline code lands on its own lines with no prose. Curate by rewriting from the original source `.md`, not by editing the skeleton.

## Editorial Format: Guided Journey

All skill pages (index and child) follow the "Guided Journey" template (see `.claude/skills/curate-content/guided-journey-template.md`):

1. `**Skill:** \`skill-name\`` reference line
2. **What You Can Build** — outcome opener, not feature definition
3. **In Action** — realistic prompt → flagship code → key decisions (3-5 bullets)
4. **More Patterns** — 2-4 additional prompt → code → explanation sets
5. **Watch Out For** — 2-4 gotchas drawn from real patterns

Voice: senior engineer peer. Tool-agnostic ("your AI coding assistant", never "Claude"). Opinionated, no hedging, no filler. Target 100-250 lines, 3-6 code blocks per page.

## Frontmatter Conventions

```yaml
---
curated: true              # Page follows Guided Journey format (protected from sync overwrites)
title: Outcome-Focused Title
description: Under 160 chars, outcome-focused
sidebar:
  order: 1                 # 0 = index page, 1+ = child pages
  badge:
    text: New
    variant: tip           # Auto-managed: cleared on sync, added only to new pages
---
```

- **`curated: true`** = already curated, protected from sync overwrites. Missing = needs curation.
- **`badge: New`** = auto-managed by sync. Cleared at start of each sync, only applied to newly created pages.

**Watch for orphan curated pages.** `curated: true` protects pages from sync overwrites, including ones from deprecated topic structures. To find orphans, compare site directory contents against `ls /Users/robby.kiskanyan/dev/aitools/gold-ctx/ai-dev-kit/databricks-skills/<skill>/` (and `references/`, `references/python/`, `references/sql/` subdirs). Pages with no source-file backing should be deleted — they're not regenerated by sync and may carry stale syntax.

## Counts and Stats

**Only the landing page (`src/pages/index.astro`) shows skill/tool counts.** These are auto-updated by `sync_landing()` in sync_content.py. Do NOT hardcode counts in any other page (Quick Start, Installation, MCP index, etc.) — they go stale.

## MDX Escaping

In prose (outside code fences and inline backticks), these must be escaped:
- `<` → `&lt;`, `>` → `&gt;` (MDX treats as JSX tags)
- `{` → `\{`, `}` → `\}` (MDX treats as expressions)

Code fences and inline code need no escaping. The sync script handles this automatically.

## Sidebar

Configured in `astro.config.mjs`. Skills use `autogenerate: { directory: '...' }` per skill group — Starlight auto-discovers all `.mdx` files and sorts by `sidebar.order`. Single-page skills use `{ slug: '...' }` instead.

When adding a new skill: add an `autogenerate` entry under the right category group in `astro.config.mjs`, and add entries in `sync_content.py` for `SKILL_MAP`, `SKILL_INDEX_INTROS`.

When adding a new MCP tool file: add entries in `sync_content.py` for `MCP_FILE_TO_PAGE`, `MCP_PAGE_TITLES`, and `MCP_PAGE_INTROS`.

## Architecture

```
src/content/docs/skills/    # 6 categories → N skill groups → child pages
src/content/docs/mcp-tools/ # Auto-generated MCP tool reference (9 pages)
src/content/docs/reference/ # Auto-generated indexes (all-skills, all-mcp-tools)
src/content/docs/guides/    # Manually written end-to-end walkthroughs
src/pages/index.astro       # Landing page (stats updated by sync script)
scripts/sync_content.py     # Content pipeline script
.claude/skills/             # 3 project skills (sync, curate, deploy)
```

Category index pages (`src/content/docs/skills/*/index.mdx`) use `sidebar: hidden: true` — they serve as landing pages from the homepage, not sidebar navigation items.

Custom components: `Hero.astro` overrides Starlight default. Brand styling in `src/styles/databricks.css` (DM Sans font, Databricks color palette).

**AppKit pages are manually maintained.** `src/content/docs/skills/apps-databases/databricks-apps-appkit/` has no source skill in `databricks-skills/` — these pages are hand-curated and live outside the sync pipeline. Don't try to add them to `SKILL_MAP`.

## Deployment

Push to `main` triggers GitHub Actions → builds Astro → deploys to GitHub Pages. Verify with `gh run list --limit 1 --repo robkisk/aidevkit.github.io`.
