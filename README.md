# AI Dev Kit Documentation Site

Documentation site for [AI Dev Kit](https://github.com/databricks-solutions/ai-dev-kit) — skills, MCP tools, and a prompt library that give AI coding assistants deep knowledge of the Databricks platform.

**Live site:** https://robkisk.github.io/aidevkit.github.io

## What's in the Docs

- **28 Skills** — Pre-built knowledge covering data engineering, SQL analytics, AI/ML, app development, governance, and DevOps on Databricks
- **99 MCP Tools** — Direct workspace interaction (run SQL, manage pipelines, deploy apps, query vector indexes)
- **Prompt Library** — Tested prompt templates for common tasks
- **Guides** — End-to-end walkthroughs (RAG applications, medallion pipelines, multi-agent systems)

## Development

```bash
npm install
npm run dev        # Local dev server at localhost:4321
npm run build      # Production build to ./dist/
```

## Content Structure

All documentation lives in `src/content/docs/` as `.mdx` files. The directory structure maps directly to the site URL structure.

```
src/content/docs/
├── getting-started/       # Quick start, installation, configuration
├── skills/
│   ├── data-engineering/  # SDP, Structured Streaming, Custom Sources, Zerobus
│   ├── sql-analytics/     # AI Functions, DBSQL, Genie Spaces, Metric Views
│   ├── ai-ml/             # Vector Search, Agent Bricks, MLflow, Model Serving
│   ├── apps-databases/    # Databricks Apps, Lakebase
│   ├── governance-catalog/ # Iceberg Tables, Unity Catalog
│   └── devops-config/     # Asset Bundles, Jobs, Workspace Config
├── mcp-tools/             # MCP tool reference pages
├── guides/                # End-to-end tutorials
├── prompt-library/        # Copy-paste prompt templates
└── reference/             # All skills list, all tools list, changelog
```

## Content Template

Child pages follow the "Guided Journey" template:

1. **What You Can Build** — Outcome-focused framing (2-3 sentences)
2. **In Action** — Realistic prompt + generated code + key decisions
3. **More Patterns** — Additional prompt/code pairs (2-4 scenarios)
4. **Watch Out For** — Gotchas with mistake, cause, and fix

See `docs/superpowers/specs/2026-03-19-child-page-content-rewrite-design.md` for the full content spec.

## Content Sourcing

Docs pages are manually maintained. Skill source files in [`ai-dev-kit/databricks-skills/`](https://github.com/databricks-solutions/ai-dev-kit) provide the authoritative patterns — when sources disagree, skill files take precedence.

## Tech Stack

- [Astro](https://astro.build) + [Starlight](https://starlight.astro.build) — static site framework
- [Catppuccin Mocha/Latte](https://catppuccin.com) — syntax highlighting theme
- DM Sans + JetBrains Mono — typography
- GitHub Pages — hosting
