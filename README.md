# AI Dev Kit Documentation Site

Documentation site for [AI Dev Kit](https://github.com/databricks-solutions/ai-dev-kit) — skills, MCP tools, and a prompt library that give AI coding assistants deep knowledge of the Databricks platform.

**Live site:** https://robkisk.github.io/aidevkit.github.io

## Development

```bash
npm install
npm run dev        # Local dev server at localhost:4321
npm run build      # Production build to ./dist/
```

## Content Refresh

Sync new content from the ai-dev-kit source repo, curate new pages, and deploy:

```bash
# 1. Sync — dry run first, then write
uv run scripts/sync_content.py
uv run scripts/sync_content.py --write --force

# 2. Find uncurated pages
grep -rL "curated: true" src/content/docs/skills/*/*/index.mdx

# 3. Build and deploy
npm run build
git add <files> && git commit && git push
```

The sync script auto-clears stale "New" badges, protects curated pages from overwrites, and updates landing page stats. See `CLAUDE.md` for the full workflow and config details.

## Content Structure

```
src/content/docs/
├── getting-started/       # Quick start, installation, configuration
├── skills/                # 6 categories → skill groups → child pages
│   ├── data-engineering/  # SDP, Structured Streaming, Custom Sources, Zerobus
│   ├── sql-analytics/     # AI Functions, DBSQL, Genie Spaces, Metric Views, Dashboards
│   ├── ai-ml/             # Vector Search, Agent Bricks, MLflow, Model Serving, Synthetic Data
│   ├── apps-databases/    # Databricks Apps (Python & AppKit), Lakebase
│   ├── governance-catalog/ # Iceberg Tables, Unity Catalog
│   └── devops-config/     # Asset Bundles, Jobs, Workspace Config, Execution & Compute
├── mcp-tools/             # Auto-generated MCP tool reference pages
├── guides/                # End-to-end walkthroughs
├── prompt-library/        # Copy-paste prompt templates
└── reference/             # All skills list, all tools list, changelog
```

## Guided Journey Format

All skill pages follow the "Guided Journey" editorial template:

1. **What You Can Build** — Outcome-focused framing
2. **In Action** — Realistic prompt + generated code + key decisions
3. **More Patterns** — Additional prompt/code pairs
4. **Watch Out For** — Gotchas with root cause and fix

## Tech Stack

- [Astro](https://astro.build) + [Starlight](https://starlight.astro.build) — static site framework
- DM Sans + JetBrains Mono — typography
- GitHub Pages — hosting via GitHub Actions
