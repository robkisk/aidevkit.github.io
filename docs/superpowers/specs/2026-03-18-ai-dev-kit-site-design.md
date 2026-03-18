# AI Dev Kit Documentation Site — Design Spec

## Overview

A public documentation site for the Databricks AI Dev Kit, deployed to GitHub Pages. Built with **Astro + Starlight**, themed with full **Databricks branding**, targeting **external customers** evaluating or using the AI Dev Kit.

**Repository:** [robkisk/aidevkit.github.io](https://github.com/robkisk/aidevkit.github.io)

**Hosting:** The repo name `aidevkit.github.io` is a **project site** (not a user site, which requires `robkisk/robkisk.github.io`). Two options:
- **Option A (recommended):** Configure a custom domain (e.g., `aidevkit.dev`) via CNAME record and GitHub Pages settings. Set `site: 'https://aidevkit.dev'` in `astro.config.mjs`. Base path stays `/`.
- **Option B:** Accept the project site URL `https://robkisk.github.io/aidevkit.github.io/`. Set `base: '/aidevkit.github.io'` in `astro.config.mjs`. All internal links and asset paths resolve through Astro's base path handling.

**Decision needed before implementation:** Which hosting option to use. The spec assumes Option A with a custom domain for clean URLs.

**Site type:** Hybrid — custom marketing landing page as the front door, with Starlight-powered documentation as the inner pages covering all 28 skills, 99 MCP tools, tutorials, and a prompt library.

---

## 1. Project Structure

```
aidevkit.github.io/
├── astro.config.mjs          # Starlight + site config
├── package.json
├── public/
│   ├── favicon.svg            # Databricks-style icon
│   └── fonts/
│       ├── DMSans-*.woff2     # Self-hosted DM Sans (400, 500, 700)
│       └── JetBrainsMono-*.woff2  # Self-hosted JetBrains Mono (400, 700)
├── src/
│   ├── assets/
│   │   ├── logo-dark.svg      # AI Dev Kit logo (for dark bg)
│   │   └── logo-light.svg     # AI Dev Kit logo (for light bg)
│   ├── components/
│   │   ├── Hero.astro         # Starlight Hero override (global, brand-styled)
│   │   ├── LandingHeader.astro  # Landing page only — standalone header
│   │   ├── LandingFooter.astro  # Landing page only — standalone footer
│   │   └── PromptCard.astro     # Reusable prompt display component
│   ├── content/
│   │   └── docs/              # All documentation lives here
│   │       ├── getting-started/
│   │       ├── skills/        # 30+ skill pages (converted from SKILL.md)
│   │       ├── mcp-tools/     # MCP tool catalog pages
│   │       ├── guides/        # Tutorials and how-tos
│   │       └── reference/     # API reference, config reference
│   ├── pages/
│   │   └── index.astro        # Custom landing page (not in docs/)
│   └── styles/
│       └── databricks.css     # Brand token overrides
├── .github/
│   └── workflows/
│       └── deploy.yml         # GitHub Actions → Pages deployment
└── .gitignore
```

### Key decisions

- **Self-hosted fonts** via `public/fonts/` — DM Sans (brand typeface) and JetBrains Mono (code blocks). Avoids Google Fonts latency. Both loaded via `@font-face` in `databricks.css`.
- **Custom landing page** in `src/pages/index.astro` — full creative control, no sidebar. Does **not** use `<StarlightPage>` wrapper — built as a standalone Astro page with its own header/footer components to avoid Starlight layout constraints.
- **Docs in `src/content/docs/`** — Starlight auto-generates sidebar, Pagefind search, mobile navigation, and pagination.
- **Starlight component overrides** for `Hero` only — applied globally via `components` config, customized to use Databricks branding on doc pages that use the `hero` frontmatter. Header and Footer are **not** global overrides; the landing page uses its own standalone components, while doc pages use Starlight's default header/footer styled via CSS tokens.
- **GitHub Actions deploy** — build Astro, upload artifact, deploy to Pages on every push to `main`.

---

## 2. Databricks Brand Theming

Custom CSS file `src/styles/databricks.css` maps the Databricks palette onto Starlight's CSS custom properties.

### Color Tokens

| Starlight Variable | Databricks Mapping | Hex | Usage |
|---|---|---|---|
| `--sl-color-accent-low` | Lava 300 (derived) | `#FFB8AB` | Accent backgrounds |
| `--sl-color-accent` | Lava 600 | `#FF3621` | Links, CTAs, active nav |
| `--sl-color-accent-high` | Lava 800 | `#801C17` | Hover states |
| `--sl-color-white` | Oat Light | `#F9F7F4` | Light page backgrounds |
| `--sl-color-gray-1` | Navy 300 | `#A3B0B5` | Borders, dividers |
| `--sl-color-gray-5` | Navy 700 | `#1B3139` | Secondary text |
| `--sl-color-gray-6` | Navy 800 | `#0F1F25` | Primary text |
| `--sl-color-black` | Navy 900 | `#0B2026` | Headings, code blocks |

> **Note:** All hex values should be verified against the official Databricks brand portal at https://brand.databricks.com before shipping. Values marked "(derived)" are interpolated from the nearest official tints and may need adjustment.

### Dark Mode Tokens

Starlight scopes dark mode under `[data-theme='dark']`. Full dark palette:

| Starlight Variable | Dark Mode Value | Hex |
|---|---|---|
| `--sl-color-accent-low` | Lava 800 | `#801C17` |
| `--sl-color-accent` | Lava 500 | `#FF5F46` |
| `--sl-color-accent-high` | Lava 300 (derived) | `#FFB8AB` |
| `--sl-color-white` | Navy 900 | `#0B2026` |
| `--sl-color-gray-1` | Navy 800 | `#0F1F25` |
| `--sl-color-gray-5` | Navy 400 | `#6B7D83` |
| `--sl-color-gray-6` | Oat Light | `#F9F7F4` |
| `--sl-color-black` | Oat White | `#FFFFFF` |

> **Note:** Same caveat — verify extended tints against official brand portal before shipping.

### Light Mode

Oat Light (`#F9F7F4`) backgrounds, Navy 800 body text — matching the brand guide's warm cream base.

### Typography

```css
:root {
  --sl-font: 'DM Sans', sans-serif;
  --sl-font-mono: 'JetBrains Mono', monospace;
}
```

- **Headings:** DM Sans, 500 weight (per brand spec)
- **Body:** DM Sans, 400 weight, 1.5 line-height
- **Code blocks:** JetBrains Mono for readability in skill/tool reference pages

### Buttons & Interactive Elements

- **Primary CTA:** Lava 600 background, white text, `font-size: 13px`, `letter-spacing: 1.5px` (brand button spec)
- **Secondary CTA:** Transparent with Navy 900 border, hover fills Navy 900 with white text
- **Body text links:** Lava 800 (`#801C17`) for WCAG AA compliance at normal text sizes (Lava 600 against Oat Light is ~3.5:1, below the 4.5:1 threshold). Lava 600 reserved for large CTAs where 3:1 is sufficient.
- **Transitions:** `all 0.25s ease-in-out` (per brand guide)

---

## 3. Landing Page

Custom `src/pages/index.astro` — no sidebar, full-width, marketing-style.

### Hero Section

- **Background:** Navy 900 (`#0B2026`) full-bleed
- **Headline:** "AI Dev Kit for Databricks"
- **Subheadline:** "Skills, MCP tools, and an interactive builder to accelerate AI development on Databricks"
- **CTAs:**
  - `Get Started` — Lava 600 solid button → `/docs/getting-started/`
  - `View on GitHub` — outline button → `https://github.com/databricks-solutions/ai-dev-kit` (the AI Dev Kit project repo, not the site repo)
- **Optional:** Animated terminal showing a sample prompt/response or install command

### What's Inside (4-column feature grid)

Navy 800 background, four cards:

| Card | Description |
|---|---|
| **28+ Skills** | Pre-built knowledge for pipelines, jobs, apps, ML, and more — drop into any Claude Code session |
| **99 MCP Tools** | Direct API access to your Databricks workspace — execute SQL, manage pipelines, deploy apps |
| **Interactive Builder** | React + FastAPI app for browsing, customizing, and installing skills |
| **Prompt Library** | 130+ ready-to-use prompts covering the full Databricks platform |

### How It Works (3-step flow)

Oat Light background, horizontal numbered steps:

1. **Install** — `claude skill install ...` or add MCP server config
2. **Prompt** — ask Claude to build pipelines, deploy jobs, query data
3. **Ship** — production code, deployed resources, working infrastructure

### Skill Categories (icon grid)

Visual grid showing major categories with icons, linking to their doc sections:
- Data Engineering
- SQL & Analytics
- AI/ML
- Apps & Databases
- Governance
- DevOps

**Icons:** Use inline SVGs from the [databricks-icons](https://github.com/databricks/databricks-icons) repository, served via jsDelivr CDN. Each category gets a representative Databricks product icon (e.g., Pipelines icon for Data Engineering, SQL Warehouse icon for SQL & Analytics). Fall back to [Astro Icon](https://github.com/natemoo-re/astro-icon) with Lucide icons for any gaps.

### Responsive Behavior

The landing page is fully custom (not Starlight) and requires explicit responsive handling:
- **4-column feature grid:** collapses to 2-column at `<768px`, single column at `<480px`
- **3-step flow:** stacks vertically at `<768px`
- **Hero CTAs:** stack vertically at `<480px`
- **Icon grid:** 3-column at `<768px`, 2-column at `<480px`

### Footer

- Links: GitHub, Docs, Getting Started, Prompt Guide
- "Built by Databricks Solutions Architects"
- Databricks brand mark

---

## 4. Documentation Structure

### Sidebar Navigation

```
Getting Started
  ├── Installation
  ├── Quick Start
  └── Configuration

Skills
  ├── Data Engineering
  │   ├── Spark Declarative Pipelines
  │   ├── Spark Structured Streaming
  │   ├── Zerobus Ingest
  │   └── Custom Spark Data Sources
  ├── SQL & Analytics
  │   ├── Databricks SQL
  │   ├── AI Functions
  │   ├── AI/BI Dashboards
  │   ├── Genie Spaces
  │   └── Metric Views
  ├── AI & ML
  │   ├── Model Serving
  │   ├── Vector Search & RAG
  │   ├── MLflow Evaluation
  │   ├── Agent Bricks
  │   └── Synthetic Data Generation
  ├── Apps & Databases
  │   ├── Databricks Apps (Python)
  │   ├── Databricks Apps (AppKit)
  │   ├── Lakebase Autoscale
  │   └── Lakebase Provisioned
  ├── Governance & Catalog
  │   ├── Unity Catalog
  │   ├── Iceberg Tables
  │   └── Volumes & Sharing
  └── DevOps & Config
      ├── Asset Bundles
      ├── Jobs & Orchestration
      ├── Python SDK
      └── Workspace Config

MCP Tools
  ├── Overview
  ├── SQL & Execution
  ├── Pipelines & Jobs
  ├── Unity Catalog & Governance
  ├── Dashboards & Genie
  ├── Vector Search
  ├── Apps & Lakebase
  ├── Serving & Models
  └── Compute & Workspace

Guides
  ├── End-to-End RAG Application
  ├── Medallion Pipeline with CI/CD
  ├── Multi-Agent System
  ├── Real-Time Analytics
  └── ML Ops Pipeline

Prompt Library
  ├── Data Engineering
  ├── SQL & Analytics
  ├── AI & ML
  ├── Apps & Databases
  ├── Governance & Catalog
  └── DevOps & Config

Reference
  ├── All MCP Tools (alphabetical)
  ├── All Skills (alphabetical)
  └── Changelog
```

### Skill Page Template

Each skill page follows a consistent format:

1. **Title & description** — what it does, when to use it
2. **Capabilities** — bullet list of what the skill covers
3. **Related MCP Tools** — links to tool reference pages that pair with this skill
4. **Example Prompts** — 5-10 ready-to-use prompts (from the prompt guide)
5. **Key Concepts** — brief explanation of Databricks features the skill works with
6. **References** — links to official Databricks documentation

### MCP Tool Page Template

1. **Tool name & description**
2. **Parameters** — table of parameter names, types, required/optional, description
3. **Example usage** — sample prompt that would invoke this tool
4. **Related skills** — cross-links back to skill pages

### Content rules

- Skills with 3+ reference files (e.g., `databricks-spark-declarative-pipelines` with 10 numbered files) → each reference becomes a **child page** under the skill's sidebar group
- Skills with 1-2 reference files → **inline as sections** within the main skill page
- Code examples from `examples/` directories → embedded as fenced code blocks in their parent skill page
- The `AI_DEV_KIT_PROMPT_GUIDE.md` → Prompt Library section with minimal reformatting

---

## 5. GitHub Actions Deployment

### Workflow: `.github/workflows/deploy.yml`

```
push to main → install deps → astro build → upload artifact → deploy to Pages
```

- **Trigger:** push to `main` branch
- **Node version:** 22 (LTS)
- **Package manager:** npm
- **Build output:** `dist/` (fully static HTML/CSS/JS)
- **Deploy action:** `actions/deploy-pages@v4`
- **Base path:** `/` with custom domain (Option A) or `/aidevkit.github.io` for project site (Option B). See Overview section for decision.
- **Site URL in config:** set in `astro.config.mjs` `site` property based on hosting option chosen

### GitHub repo settings

- **Pages source:** set to "GitHub Actions" (not "Deploy from a branch")
- **Custom domain** (if Option A): add CNAME record pointing to `robkisk.github.io`, configure in repo Settings → Pages → Custom domain
- Enable "Enforce HTTPS"

### Rebuild trigger

Any push to `main` — whether editing a skill page, updating the landing page, or adding a new guide. Expected build time: **45-90 seconds** (Starlight + Pagefind indexing ~97 pages + self-hosted fonts).

### Search Configuration

Starlight's built-in Pagefind search is enabled by default. Additional configuration:
- **Exclude landing page** from search index — marketing copy should not pollute doc search results. Use `pagefind: false` in the landing page or Pagefind's `data-pagefind-ignore` attribute.
- **Enable `lastUpdated`** in Starlight config — shows "Last updated: <date>" on every doc page, derived from git commit timestamps. Helps external customers trust content currency.
- No additional search weighting needed at launch; Pagefind's default relevance scoring handles structured content well.

---

## 6. Content Migration Strategy

### Source locations

- **Full skill set (30 directories):** `/Users/robby.kiskanyan/dev/devx/dbx-devx-workshop/.claude/skills/` — the skill markdown files exist on disk as untracked files (visible in `git status`). They are not yet committed to `main`. This is the location with the complete set of 30 skill directories.
- **Partial mirror (2 skills only):** `/Users/robby.kiskanyan/dev/aitools/ai-dev-kit/.claude/skills/` — currently contains only `databricks-python-sdk` and `python-dev`. Not yet populated with the full set.
- **Prompt guide:** `AI_DEV_KIT_PROMPT_GUIDE.md` in the workshop repo root (also untracked)

**Prerequisite:** Before migration can begin, the skill files and prompt guide must be accessible — either committed to a branch, or copied directly from their on-disk location into the site repo during the content conversion step.

### Per-skill directory structure (typical)

```
skill-name/
├── SKILL.md                  # Main skill definition
├── 1-topic.md                # Numbered reference files
├── 2-topic.md
├── examples/                 # Code samples
│   └── example.py
└── references/               # Detailed API docs
    └── api-reference.md
```

### Conversion rules

| Source | Target | Treatment |
|---|---|---|
| `SKILL.md` | Skill overview page | Strip agent metadata (triggers, system instructions), keep human-readable content, add Starlight frontmatter |
| Numbered reference files | Child pages or sections | 3+ files → child pages; 1-2 files → inline sections |
| `examples/*.py` | Fenced code blocks | Embed in parent skill page with syntax highlighting |
| `AI_DEV_KIT_PROMPT_GUIDE.md` | Prompt Library page | Minimal reformatting for Starlight compatibility |

### Exclusions

- Agent-facing trigger patterns and system prompt instructions
- Internal Databricks references (logfood, org lookups, internal jargon skills)
- `databricks-docs` — this is a documentation lookup skill (wraps llms.txt), not a user-facing feature to document
- `databricks-unstructured-pdf-generation` — internal synthetic PDF generation for testing; not customer-relevant
- Duplicate content across skills (normalize to single source with cross-links)

### Directory-to-sidebar mapping (non-obvious names)

| Skill Directory | Sidebar Entry |
|---|---|
| `databricks-agent-skill-databricks` | DevOps & Config > Workspace Config |
| `databricks-agent-skill-databricks-apps` | Apps & Databases > Databricks Apps (AppKit) |
| `databricks-agent-skill-databricks-jobs` | DevOps & Config > Jobs & Orchestration |
| `databricks-agent-skill-databricks-lakebase` | Apps & Databases > Lakebase Autoscale |
| `databricks-agent-skill-databricks-pipelines` | Data Engineering > Spark Declarative Pipelines (child pages) |

### Consolidation for large skill directories

`databricks-agent-skill-databricks-pipelines` has 34 reference files. Many are language-specific variants (e.g., `auto-cdc-python.md` + `auto-cdc-sql.md`, `streaming-table-python.md` + `streaming-table-sql.md`). These pairs should be consolidated into single pages with tabbed Python/SQL code blocks rather than separate child pages. This reduces ~34 files to ~15 pages.

### Estimated page count

| Section | Pages |
|---|---|
| Getting Started | 3 |
| Skills (28 skills + child pages) | ~75 |
| MCP Tools (grouped by category) | ~15 |
| Guides (cross-cutting tutorials) | 5 |
| Prompt Library (split by category) | 6 |
| Reference (alphabetical indexes) | 3 |
| **Total** | **~110-120 pages** |

**Note:** The skills page count may exceed 75 — directories like `databricks-spark-declarative-pipelines` (10 files) and `databricks-agent-skill-databricks-pipelines` (20+ reference files) each generate many child pages. MCP tools bumped to ~15 to avoid overly long grouped pages. Prompt Library split by skill category (Data Engineering, SQL, AI/ML, Apps, Governance, DevOps) rather than a single unwieldy page.
