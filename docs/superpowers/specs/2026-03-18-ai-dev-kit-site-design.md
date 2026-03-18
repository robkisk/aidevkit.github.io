# AI Dev Kit Documentation Site — Design Spec

## Overview

A public documentation site for the Databricks AI Dev Kit, hosted at `https://robkisk.github.io` via GitHub Pages. Built with **Astro + Starlight**, themed with full **Databricks branding**, targeting **external customers** evaluating or using the AI Dev Kit.

**Repository:** [robkisk/aidevkit.github.io](https://github.com/robkisk/aidevkit.github.io)

**Site type:** Hybrid — custom marketing landing page as the front door, with Starlight-powered documentation as the inner pages covering all 30+ skills, 99 MCP tools, tutorials, and a prompt library.

---

## 1. Project Structure

```
aidevkit.github.io/
├── astro.config.mjs          # Starlight + site config
├── package.json
├── public/
│   ├── favicon.svg            # Databricks-style icon
│   └── fonts/
│       └── DMSans-*.woff2     # Self-hosted DM Sans (400, 500, 700)
├── src/
│   ├── assets/
│   │   ├── logo-dark.svg      # AI Dev Kit logo (for dark bg)
│   │   └── logo-light.svg     # AI Dev Kit logo (for light bg)
│   ├── components/
│   │   ├── Hero.astro         # Custom Hero override (landing page)
│   │   ├── Header.astro       # Custom header with Databricks nav style
│   │   └── Footer.astro       # Custom footer with links
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

- **Self-hosted DM Sans** via `public/fonts/` — avoids Google Fonts latency, matches brand spec.
- **Custom landing page** in `src/pages/index.astro` — full creative control, no sidebar, wraps with `<StarlightPage>` for consistent theming.
- **Docs in `src/content/docs/`** — Starlight auto-generates sidebar, Pagefind search, mobile navigation, and pagination.
- **Component overrides** for Hero, Header, Footer — Databricks look without fighting Starlight's internals.
- **GitHub Actions deploy** — build Astro, upload artifact, deploy to Pages on every push to `main`.

---

## 2. Databricks Brand Theming

Custom CSS file `src/styles/databricks.css` maps the Databricks palette onto Starlight's CSS custom properties.

### Color Tokens

| Starlight Variable | Databricks Mapping | Hex | Usage |
|---|---|---|---|
| `--sl-color-accent-low` | Lava 100 | `#FFF0EE` | Accent backgrounds |
| `--sl-color-accent` | Lava 600 | `#FF3621` | Links, CTAs, active nav |
| `--sl-color-accent-high` | Lava 800 | `#B7200F` | Hover states |
| `--sl-color-white` | Oat Light | `#F9F7F4` | Light page backgrounds |
| `--sl-color-gray-1` | Navy 100 | `#E8EBED` | Borders, dividers |
| `--sl-color-gray-5` | Navy 700 | `#1B3139` | Secondary text |
| `--sl-color-gray-6` | Navy 800 | `#0F1F25` | Primary text |
| `--sl-color-black` | Navy 900 | `#0B2026` | Headings, code blocks |

**Dark mode:** Navy 900 backgrounds, Oat Light text.
**Light mode:** Oat Light (`#F9F7F4`) backgrounds, Navy 800 body text — matching the brand guide's warm cream base.

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
- **Links:** Lava 600 color, underline on hover (not default blue)
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
  - `View on GitHub` — outline button → `https://github.com/robkisk/aidevkit.github.io`
- **Optional:** Animated terminal showing a sample prompt/response or install command

### What's Inside (4-column feature grid)

Navy 800 background, four cards:

| Card | Description |
|---|---|
| **30+ Skills** | Pre-built knowledge for pipelines, jobs, apps, ML, and more — drop into any Claude Code session |
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
  └── Full catalog (130+ prompts)

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
- **Base path:** `/` (user site — no subpath)
- **Site URL in config:** `https://robkisk.github.io`

### GitHub repo settings

- **Pages source:** set to "GitHub Actions" (not "Deploy from a branch")
- No other configuration needed

### Rebuild trigger

Any push to `main` — whether editing a skill page, updating the landing page, or adding a new guide. Build time ~30 seconds for a Starlight site of this size.

---

## 6. Content Migration Strategy

### Source locations

- **Primary skills:** `/Users/robby.kiskanyan/dev/devx/dbx-devx-workshop/.claude/skills/`
- **Canonical source:** `/Users/robby.kiskanyan/dev/aitools/ai-dev-kit/`

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
- Duplicate content across skills (normalize to single source with cross-links)

### Estimated page count

| Section | Pages |
|---|---|
| Getting Started | 3 |
| Skills (30 skills + child pages) | ~75 |
| MCP Tools (grouped by category) | ~10 |
| Guides (cross-cutting tutorials) | 5 |
| Prompt Library | 1 |
| Reference (alphabetical indexes) | 3 |
| **Total** | **~97 pages** |
