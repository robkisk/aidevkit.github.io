# AI Dev Kit Documentation Site — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and deploy a public Astro + Starlight documentation site for the Databricks AI Dev Kit at `https://robkisk.github.io/aidevkit.github.io/`, with full Databricks branding, 28 skill pages, MCP tool catalog, and a prompt library.

**Architecture:** Astro + Starlight framework with custom landing page (`src/pages/index.astro`), Starlight-managed docs (`src/content/docs/`), Databricks brand CSS overrides, and GitHub Actions deployment. Content migrated from existing skill markdown files.

**Tech Stack:** Astro 5, Starlight, GitHub Pages, GitHub Actions, DM Sans + JetBrains Mono fonts

**Spec:** `docs/superpowers/specs/2026-03-18-ai-dev-kit-site-design.md`

**Source skills:** `/Users/robby.kiskanyan/dev/devx/dbx-devx-workshop/.claude/skills/`

---

## Phase Overview

| Phase | What Ships | Depends On |
|---|---|---|
| 1. Scaffold & Deploy | Empty Starlight site live on GitHub Pages | Nothing |
| 2. Databricks Branding | Themed site with custom fonts and colors | Phase 1 |
| 3. Landing Page | Custom marketing homepage | Phase 2 |
| 4. Core Docs Structure | Getting Started + 3 sample skill pages | Phase 2 |
| 5. Content Migration (Skills) | All 28 skill pages with child pages | Phase 4 |
| 6. MCP Tools, Prompts, Guides | MCP catalog + Prompt Library + Guides + Reference | Phase 5 |

Each phase ends with a commit and a live deploy. Work is parallelizable after Phase 2 (Phases 3 and 4 are independent).

---

## Phase 1: Scaffold & Deploy

### Task 1.1: Clone repo and initialize Astro + Starlight

**Files:**
- Create: `package.json`, `astro.config.mjs`, `src/content/docs/index.mdx`, `src/content.config.ts`
- Create: `.gitignore`, `tsconfig.json`

- [ ] **Step 1: Clone the empty repo**

```bash
cd /Users/robby.kiskanyan/dev/aitools
git clone git@github.com:robkisk/aidevkit.github.io.git
cd aidevkit.github.io
```

- [ ] **Step 2: Scaffold Starlight project**

```bash
npm create astro@latest -- --template starlight --no-install .
```

If the scaffold refuses to write into a non-empty dir (due to `.git`), use a temp dir and move:

```bash
cd /tmp
npm create astro@latest -- --template starlight --no-install aidevkit-scaffold
cp -r /tmp/aidevkit-scaffold/* /Users/robby.kiskanyan/dev/aitools/aidevkit.github.io/
cp /tmp/aidevkit-scaffold/.gitignore /Users/robby.kiskanyan/dev/aitools/aidevkit.github.io/
cd /Users/robby.kiskanyan/dev/aitools/aidevkit.github.io
```

- [ ] **Step 3: Configure astro.config.mjs with base path and site URL**

Update `astro.config.mjs`:

```javascript
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://robkisk.github.io',
  base: '/aidevkit.github.io',
  integrations: [
    starlight({
      title: 'AI Dev Kit',
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/databricks-solutions/ai-dev-kit' },
      ],
      sidebar: [
        { label: 'Getting Started', autogenerate: { directory: 'getting-started' } },
      ],
      lastUpdated: true,
    }),
  ],
});
```

- [ ] **Step 4: Install dependencies and verify local build**

```bash
npm install
npm run build
```

Expected: Build succeeds, output in `dist/` directory.

- [ ] **Step 5: Test local dev server**

```bash
npm run dev
```

Expected: Site accessible at `http://localhost:4321/aidevkit.github.io/`

- [ ] **Step 6: Commit scaffold**

```bash
git add -A
git commit -m "feat: scaffold Astro + Starlight project with base path config"
```

### Task 1.2: Add GitHub Actions deployment workflow

**Files:**
- Create: `.github/workflows/deploy.yml`

- [ ] **Step 1: Create the workflow file**

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Build site
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: dist/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Commit and push**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: add GitHub Actions workflow for Pages deployment"
git push origin main
```

- [ ] **Step 3: Configure GitHub repo Pages settings**

Go to https://github.com/robkisk/aidevkit.github.io/settings/pages:
- Source: **GitHub Actions**
- Enforce HTTPS: **enabled**

Or via CLI:

```bash
gh api repos/robkisk/aidevkit.github.io/pages -X PUT -f build_type=workflow
```

- [ ] **Step 4: Verify deployment**

```bash
gh run list --repo robkisk/aidevkit.github.io --limit 1
```

Wait for the workflow to complete, then verify the site is live at `https://robkisk.github.io/aidevkit.github.io/`.

- [ ] **Step 5: Commit any fixes if needed**

---

## Phase 2: Databricks Branding

### Task 2.1: Add self-hosted fonts

**Files:**
- Create: `public/fonts/DMSans-Regular.woff2`
- Create: `public/fonts/DMSans-Medium.woff2`
- Create: `public/fonts/DMSans-Bold.woff2`
- Create: `public/fonts/JetBrainsMono-Regular.woff2`
- Create: `public/fonts/JetBrainsMono-Bold.woff2`

- [ ] **Step 1: Download DM Sans woff2 files**

```bash
mkdir -p public/fonts
# Download from Google Fonts CDN (woff2 format)
curl -L -o public/fonts/DMSans-Regular.woff2 "https://fonts.gstatic.com/s/dmsans/v15/rP2Hp2ywxg089UriCZOIHTWEBlw.woff2"
curl -L -o public/fonts/DMSans-Medium.woff2 "https://fonts.gstatic.com/s/dmsans/v15/rP2Hp2ywxg089UriCZ2IHTWEBlw.woff2"
curl -L -o public/fonts/DMSans-Bold.woff2 "https://fonts.gstatic.com/s/dmsans/v15/rP2Hp2ywxg089UriCZOIHTWEBlw.woff2"
```

If the CDN URLs have changed, download from https://fonts.google.com/specimen/DM+Sans and convert with a woff2 tool, or use the `@fontsource/dm-sans` npm package:

```bash
npm install @fontsource/dm-sans
# Then reference from node_modules in CSS
```

- [ ] **Step 2: Download JetBrains Mono woff2 files**

```bash
curl -L -o public/fonts/JetBrainsMono-Regular.woff2 "https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@latest/fonts/webfonts/JetBrainsMono-Regular.woff2"
curl -L -o public/fonts/JetBrainsMono-Bold.woff2 "https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@latest/fonts/webfonts/JetBrainsMono-Bold.woff2"
```

- [ ] **Step 3: Verify font files exist and are non-empty**

```bash
ls -la public/fonts/
```

Expected: 5 `.woff2` files, each > 10KB.

- [ ] **Step 4: Commit fonts**

```bash
git add public/fonts/
git commit -m "feat: add self-hosted DM Sans and JetBrains Mono fonts"
```

### Task 2.2: Create Databricks brand CSS

**Files:**
- Create: `src/styles/databricks.css`
- Modify: `astro.config.mjs` (add `customCss`)

- [ ] **Step 1: Create the brand CSS file**

Create `src/styles/databricks.css`:

```css
/* === Self-hosted Fonts === */

@font-face {
  font-family: 'DM Sans';
  src: url('/aidevkit.github.io/fonts/DMSans-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'DM Sans';
  src: url('/aidevkit.github.io/fonts/DMSans-Medium.woff2') format('woff2');
  font-weight: 500;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'DM Sans';
  src: url('/aidevkit.github.io/fonts/DMSans-Bold.woff2') format('woff2');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'JetBrains Mono';
  src: url('/aidevkit.github.io/fonts/JetBrainsMono-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'JetBrains Mono';
  src: url('/aidevkit.github.io/fonts/JetBrainsMono-Bold.woff2') format('woff2');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

/* === Databricks Brand Tokens (Light Mode) === */

:root {
  --sl-font: 'DM Sans', sans-serif;
  --sl-font-mono: 'JetBrains Mono', monospace;

  --sl-color-accent-low: #FFB8AB;
  --sl-color-accent: #FF3621;
  --sl-color-accent-high: #801C17;
  --sl-color-white: #F9F7F4;
  --sl-color-gray-1: #A3B0B5;
  --sl-color-gray-5: #1B3139;
  --sl-color-gray-6: #0F1F25;
  --sl-color-black: #0B2026;
}

/* === Databricks Brand Tokens (Dark Mode) === */

[data-theme='dark'] {
  --sl-color-accent-low: #801C17;
  --sl-color-accent: #FF5F46;
  --sl-color-accent-high: #FFB8AB;
  --sl-color-white: #0B2026;
  --sl-color-gray-1: #0F1F25;
  --sl-color-gray-5: #6B7D83;
  --sl-color-gray-6: #F9F7F4;
  --sl-color-black: #FFFFFF;
}

/* === Typography === */

h1, h2, h3, h4, h5, h6 {
  font-weight: 500;
}

/* === Links (WCAG AA) === */

:root[data-theme='light'] a:not(.sl-btn) {
  color: #801C17;
}

/* === Buttons === */

.sl-btn {
  font-size: 13px;
  letter-spacing: 1.5px;
  transition: all 0.25s ease-in-out;
}
```

- [ ] **Step 2: Add customCss to astro.config.mjs**

Add `customCss: ['./src/styles/databricks.css']` to the starlight config:

```javascript
starlight({
  title: 'AI Dev Kit',
  customCss: ['./src/styles/databricks.css'],
  // ... rest of config
})
```

- [ ] **Step 3: Build and verify locally**

```bash
npm run build && npm run preview
```

Expected: Site renders with DM Sans, Databricks colors, dark/light mode both correct.

- [ ] **Step 4: Commit and push**

```bash
git add src/styles/databricks.css astro.config.mjs
git commit -m "feat: add Databricks brand theming with custom fonts and color tokens"
git push origin main
```

### Task 2.3: Add logo and favicon

**Files:**
- Create: `src/assets/logo-dark.svg`
- Create: `src/assets/logo-light.svg`
- Create: `public/favicon.svg`
- Modify: `astro.config.mjs` (add logo config)

- [ ] **Step 1: Create a minimal AI Dev Kit logo SVG**

Create `src/assets/logo-light.svg` — a simple text-based SVG with "AI Dev Kit" in DM Sans, Lava 600 accent. This is a placeholder until a proper logo is designed.

Create `src/assets/logo-dark.svg` — same but with light text for dark backgrounds.

- [ ] **Step 2: Create favicon**

Create `public/favicon.svg` — a simple Databricks-inspired icon (diamond or similar shape in Lava 600).

- [ ] **Step 3: Add logo config to astro.config.mjs**

```javascript
starlight({
  title: 'AI Dev Kit',
  logo: {
    light: './src/assets/logo-light.svg',
    dark: './src/assets/logo-dark.svg',
  },
  // ...
})
```

- [ ] **Step 4: Build and verify**

```bash
npm run build && npm run preview
```

Expected: Logo appears in header, favicon in browser tab.

- [ ] **Step 5: Commit and push**

```bash
git add src/assets/ public/favicon.svg astro.config.mjs
git commit -m "feat: add AI Dev Kit logo and favicon"
git push origin main
```

---

## Phase 3: Landing Page

> Phase 3 and Phase 4 can run in parallel after Phase 2 completes.

### Task 3.1: Create landing page layout

**Files:**
- Create: `src/pages/index.astro`
- Create: `src/components/LandingHeader.astro`
- Create: `src/components/LandingFooter.astro`

- [ ] **Step 1: Create LandingHeader component**

Create `src/components/LandingHeader.astro`:

```astro
---
const base = import.meta.env.BASE_URL;
---

<header class="landing-header">
  <nav>
    <a href={base} class="logo-link">
      <img src={`${base}favicon.svg`} alt="" width="28" height="28" />
      <span>AI Dev Kit</span>
    </a>
    <div class="nav-links">
      <a href={`${base}docs/getting-started/`}>Docs</a>
      <a href="https://github.com/databricks-solutions/ai-dev-kit">GitHub</a>
    </div>
  </nav>
</header>

<style>
  .landing-header {
    position: sticky;
    top: 0;
    z-index: 10;
    background: #0B2026;
    border-bottom: 1px solid #1B3139;
    padding: 0.75rem 2rem;
  }
  nav {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .logo-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #F9F7F4;
    text-decoration: none;
    font-weight: 500;
    font-size: 1.125rem;
  }
  .nav-links {
    display: flex;
    gap: 1.5rem;
  }
  .nav-links a {
    color: #A3B0B5;
    text-decoration: none;
    font-size: 0.875rem;
    transition: color 0.25s ease-in-out;
  }
  .nav-links a:hover {
    color: #F9F7F4;
  }
</style>
```

- [ ] **Step 2: Create LandingFooter component**

Create `src/components/LandingFooter.astro`:

```astro
---
const base = import.meta.env.BASE_URL;
---

<footer class="landing-footer">
  <div class="footer-content">
    <div class="footer-links">
      <a href={`${base}docs/getting-started/`}>Getting Started</a>
      <a href={`${base}docs/skills/`}>Skills</a>
      <a href={`${base}docs/mcp-tools/`}>MCP Tools</a>
      <a href={`${base}docs/prompt-library/`}>Prompt Library</a>
      <a href="https://github.com/databricks-solutions/ai-dev-kit">GitHub</a>
    </div>
    <p class="footer-note">Built by Databricks Solutions Architects</p>
  </div>
</footer>

<style>
  .landing-footer {
    background: #0B2026;
    border-top: 1px solid #1B3139;
    padding: 2rem;
  }
  .footer-content {
    max-width: 1200px;
    margin: 0 auto;
    text-align: center;
  }
  .footer-links {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
  }
  .footer-links a {
    color: #A3B0B5;
    text-decoration: none;
    font-size: 0.875rem;
    transition: color 0.25s ease-in-out;
  }
  .footer-links a:hover { color: #F9F7F4; }
  .footer-note {
    color: #6B7D83;
    font-size: 0.75rem;
  }
</style>
```

- [ ] **Step 3: Create the landing page**

Create `src/pages/index.astro`:

```astro
---
import LandingHeader from '../components/LandingHeader.astro';
import LandingFooter from '../components/LandingFooter.astro';

const base = import.meta.env.BASE_URL;

const features = [
  { title: '28+ Skills', desc: 'Pre-built knowledge for pipelines, jobs, apps, ML, and more — drop into any Claude Code session' },
  { title: '99 MCP Tools', desc: 'Direct API access to your Databricks workspace — execute SQL, manage pipelines, deploy apps' },
  { title: 'Interactive Builder', desc: 'React + FastAPI app for browsing, customizing, and installing skills' },
  { title: 'Prompt Library', desc: '130+ ready-to-use prompts covering the full Databricks platform' },
];

const steps = [
  { num: '1', title: 'Install', desc: 'claude skill install ... or add MCP server config' },
  { num: '2', title: 'Prompt', desc: 'Ask Claude to build pipelines, deploy jobs, query data' },
  { num: '3', title: 'Ship', desc: 'Production code, deployed resources, working infrastructure' },
];

const categories = [
  { name: 'Data Engineering', href: `${base}docs/skills/data-engineering/` },
  { name: 'SQL & Analytics', href: `${base}docs/skills/sql-analytics/` },
  { name: 'AI & ML', href: `${base}docs/skills/ai-ml/` },
  { name: 'Apps & Databases', href: `${base}docs/skills/apps-databases/` },
  { name: 'Governance', href: `${base}docs/skills/governance-catalog/` },
  { name: 'DevOps', href: `${base}docs/skills/devops-config/` },
];
---

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI Dev Kit for Databricks</title>
  <meta name="description" content="Skills, MCP tools, and an interactive builder to accelerate AI development on Databricks" />
  <link rel="icon" href={`${base}favicon.svg`} />
  <link rel="stylesheet" href={`${base}fonts/databricks-landing.css`} />
  <style>
    @font-face { font-family: 'DM Sans'; src: url('/aidevkit.github.io/fonts/DMSans-Regular.woff2') format('woff2'); font-weight: 400; font-display: swap; }
    @font-face { font-family: 'DM Sans'; src: url('/aidevkit.github.io/fonts/DMSans-Medium.woff2') format('woff2'); font-weight: 500; font-display: swap; }
    @font-face { font-family: 'DM Sans'; src: url('/aidevkit.github.io/fonts/DMSans-Bold.woff2') format('woff2'); font-weight: 700; font-display: swap; }

    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'DM Sans', sans-serif; color: #F9F7F4; line-height: 1.5; }

    /* Hero */
    .hero { background: #0B2026; padding: 6rem 2rem; text-align: center; }
    .hero h1 { font-size: 3.5rem; font-weight: 700; margin-bottom: 1rem; }
    .hero p { font-size: 1.25rem; color: #A3B0B5; max-width: 640px; margin: 0 auto 2rem; }
    .hero-ctas { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
    .btn-primary { background: #FF3621; color: #fff; padding: 0.8rem 2rem; border-radius: 4px; text-decoration: none; font-size: 0.875rem; font-weight: 500; letter-spacing: 1.5px; transition: all 0.25s ease-in-out; }
    .btn-primary:hover { background: #801C17; }
    .btn-secondary { border: 1px solid #F9F7F4; color: #F9F7F4; padding: 0.8rem 2rem; border-radius: 4px; text-decoration: none; font-size: 0.875rem; font-weight: 500; letter-spacing: 1.5px; transition: all 0.25s ease-in-out; }
    .btn-secondary:hover { background: #F9F7F4; color: #0B2026; }

    /* Features */
    .features { background: #0F1F25; padding: 4rem 2rem; }
    .features-grid { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }
    .feature-card { background: #1B3139; border-radius: 8px; padding: 1.5rem; }
    .feature-card h3 { font-size: 1.125rem; font-weight: 500; margin-bottom: 0.5rem; color: #FF3621; }
    .feature-card p { color: #A3B0B5; font-size: 0.875rem; }

    /* Steps */
    .steps { background: #F9F7F4; color: #0B2026; padding: 4rem 2rem; }
    .steps h2 { text-align: center; font-size: 2rem; font-weight: 500; margin-bottom: 2rem; }
    .steps-grid { max-width: 900px; margin: 0 auto; display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; text-align: center; }
    .step-num { font-size: 2.5rem; font-weight: 700; color: #FF3621; }
    .step-title { font-size: 1.25rem; font-weight: 500; margin: 0.5rem 0; }
    .step-desc { color: #1B3139; font-size: 0.875rem; }

    /* Categories */
    .categories { background: #0B2026; padding: 4rem 2rem; }
    .categories h2 { text-align: center; font-size: 2rem; font-weight: 500; margin-bottom: 2rem; color: #F9F7F4; }
    .categories-grid { max-width: 900px; margin: 0 auto; display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
    .category-link { display: block; background: #1B3139; border-radius: 8px; padding: 1.25rem; text-align: center; text-decoration: none; color: #F9F7F4; font-weight: 500; transition: all 0.25s ease-in-out; }
    .category-link:hover { background: #FF3621; }

    /* Responsive */
    @media (max-width: 768px) {
      .hero h1 { font-size: 2.25rem; }
      .features-grid { grid-template-columns: repeat(2, 1fr); }
      .steps-grid { grid-template-columns: 1fr; }
      .categories-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 480px) {
      .features-grid { grid-template-columns: 1fr; }
      .hero-ctas { flex-direction: column; align-items: center; }
      .categories-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <LandingHeader />

  <section class="hero" data-pagefind-ignore>
    <h1>AI Dev Kit for Databricks</h1>
    <p>Skills, MCP tools, and an interactive builder to accelerate AI development on Databricks</p>
    <div class="hero-ctas">
      <a href={`${base}docs/getting-started/`} class="btn-primary">Get Started</a>
      <a href="https://github.com/databricks-solutions/ai-dev-kit" class="btn-secondary">View on GitHub</a>
    </div>
  </section>

  <section class="features" data-pagefind-ignore>
    <div class="features-grid">
      {features.map(f => (
        <div class="feature-card">
          <h3>{f.title}</h3>
          <p>{f.desc}</p>
        </div>
      ))}
    </div>
  </section>

  <section class="steps" data-pagefind-ignore>
    <h2>How It Works</h2>
    <div class="steps-grid">
      {steps.map(s => (
        <div>
          <div class="step-num">{s.num}</div>
          <div class="step-title">{s.title}</div>
          <div class="step-desc">{s.desc}</div>
        </div>
      ))}
    </div>
  </section>

  <section class="categories" data-pagefind-ignore>
    <h2>Explore by Category</h2>
    <div class="categories-grid">
      {categories.map(c => (
        <a href={c.href} class="category-link">{c.name}</a>
      ))}
    </div>
  </section>

  <LandingFooter />
</body>
</html>
```

- [ ] **Step 4: Build and verify locally**

```bash
npm run build && npm run preview
```

Visit `http://localhost:4321/aidevkit.github.io/` — should show the full landing page with hero, features, steps, categories, and footer.

- [ ] **Step 5: Commit and push**

```bash
git add src/pages/index.astro src/components/LandingHeader.astro src/components/LandingFooter.astro
git commit -m "feat: add custom landing page with hero, features, and category navigation"
git push origin main
```

---

## Phase 4: Core Docs Structure

> Phase 3 and Phase 4 can run in parallel after Phase 2 completes.

### Task 4.1: Create Getting Started pages

**Files:**
- Create: `src/content/docs/getting-started/index.mdx`
- Create: `src/content/docs/getting-started/installation.mdx`
- Create: `src/content/docs/getting-started/configuration.mdx`

- [ ] **Step 1: Create installation guide**

Create `src/content/docs/getting-started/installation.mdx`:

```mdx
---
title: Installation
description: Install AI Dev Kit skills and MCP tools for Claude Code
sidebar:
  order: 1
---

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and configured
- A Databricks workspace with a personal access token or OAuth configured

## Install Skills

Add AI Dev Kit skills to your Claude Code session:

\`\`\`bash
# Install all skills
claude skill install databricks-solutions/ai-dev-kit

# Or install a specific skill
claude skill install databricks-solutions/ai-dev-kit --skill databricks-spark-declarative-pipelines
\`\`\`

## Install MCP Server

Add the AI Dev Kit MCP server to your Claude Code configuration:

\`\`\`json
{
  "mcpServers": {
    "ai-dev-kit": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/ai-dev-kit-mcp"]
    }
  }
}
\`\`\`

## Verify

Ask Claude Code:

\`\`\`
What Databricks skills do you have access to?
\`\`\`

You should see a list of 28+ available skills.
```

- [ ] **Step 2: Create quick start guide**

Create `src/content/docs/getting-started/index.mdx`:

```mdx
---
title: Quick Start
description: Get up and running with AI Dev Kit in 5 minutes
sidebar:
  order: 0
---

AI Dev Kit gives Claude Code deep knowledge of the Databricks platform through **skills** (pre-built knowledge) and **MCP tools** (direct workspace API access).

## What You Get

- **28 Skills** — specialized knowledge for building pipelines, deploying models, creating dashboards, and more
- **99 MCP Tools** — execute SQL, manage jobs, create pipelines, and control your workspace directly
- **Prompt Library** — 130+ tested prompts across every Databricks feature area

## Try It

After [installing](/aidevkit.github.io/docs/getting-started/installation/), try these prompts:

\`\`\`
List all tables in my main catalog and show row counts.
\`\`\`

\`\`\`
Create a streaming pipeline that ingests JSON from cloud storage,
cleans the data with quality expectations, and writes to a gold table.
\`\`\`

\`\`\`
Build a Streamlit app that queries my sales data and shows a revenue chart.
\`\`\`

## Next Steps

- Browse [Skills](/aidevkit.github.io/docs/skills/) to see what's available
- Explore the [MCP Tools](/aidevkit.github.io/docs/mcp-tools/) catalog
- Check the [Prompt Library](/aidevkit.github.io/docs/prompt-library/) for ready-to-use prompts
```

- [ ] **Step 3: Create configuration guide**

Create `src/content/docs/getting-started/configuration.mdx`:

```mdx
---
title: Configuration
description: Configure workspace profiles, authentication, and MCP server options
sidebar:
  order: 2
---

## Workspace Authentication

AI Dev Kit connects to your Databricks workspace using the standard Databricks authentication methods.

### Personal Access Token

Set in your environment:

\`\`\`bash
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=dapi...
\`\`\`

### Databricks CLI Profile

If you use the Databricks CLI, AI Dev Kit picks up your active profile:

\`\`\`bash
databricks auth login --host https://your-workspace.cloud.databricks.com
\`\`\`

### OAuth (M2M)

For CI/CD and service principal authentication, configure OAuth credentials:

\`\`\`bash
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_CLIENT_ID=your-client-id
export DATABRICKS_CLIENT_SECRET=your-client-secret
\`\`\`

## MCP Server Options

The MCP server supports these configuration options in your Claude Code settings:

\`\`\`json
{
  "mcpServers": {
    "ai-dev-kit": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/ai-dev-kit-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi..."
      }
    }
  }
}
\`\`\`
```

- [ ] **Step 4: Build and verify**

```bash
npm run build && npm run preview
```

Expected: Getting Started section appears in sidebar with 3 pages.

- [ ] **Step 5: Commit**

```bash
git add src/content/docs/getting-started/
git commit -m "docs: add Getting Started pages (installation, quick start, configuration)"
```

### Task 4.2: Create sample skill pages to validate template

**Files:**
- Create: `src/content/docs/skills/data-engineering/spark-declarative-pipelines.mdx`
- Create: `src/content/docs/skills/sql-analytics/ai-functions.mdx`
- Create: `src/content/docs/skills/ai-ml/vector-search.mdx`
- Modify: `astro.config.mjs` (expand sidebar config)

- [ ] **Step 1: Read 3 source SKILL.md files for conversion**

Read these files from the workshop repo:
- `/Users/robby.kiskanyan/dev/devx/dbx-devx-workshop/.claude/skills/databricks-spark-declarative-pipelines/SKILL.md`
- `/Users/robby.kiskanyan/dev/devx/dbx-devx-workshop/.claude/skills/databricks-ai-functions/SKILL.md`
- `/Users/robby.kiskanyan/dev/devx/dbx-devx-workshop/.claude/skills/databricks-vector-search/SKILL.md`

- [ ] **Step 2: Convert each SKILL.md to a Starlight doc page**

Apply the conversion rules from the spec:
1. Strip agent-facing metadata (trigger patterns, system instructions, `<command-name>` tags)
2. Keep capabilities, key concepts, and human-readable content
3. Add Starlight frontmatter (`title`, `description`, `sidebar`)
4. Add "Related MCP Tools" section with links
5. Add "Example Prompts" section (from the prompt guide)
6. Add "References" section with official Databricks doc links

Create each file following the skill page template from the spec.

- [ ] **Step 3: Update sidebar config in astro.config.mjs**

Expand the sidebar to include the new skill categories:

```javascript
sidebar: [
  { label: 'Getting Started', autogenerate: { directory: 'getting-started' } },
  {
    label: 'Skills',
    items: [
      { label: 'Data Engineering', autogenerate: { directory: 'skills/data-engineering' } },
      { label: 'SQL & Analytics', autogenerate: { directory: 'skills/sql-analytics' } },
      { label: 'AI & ML', autogenerate: { directory: 'skills/ai-ml' } },
      { label: 'Apps & Databases', autogenerate: { directory: 'skills/apps-databases' } },
      { label: 'Governance & Catalog', autogenerate: { directory: 'skills/governance-catalog' } },
      { label: 'DevOps & Config', autogenerate: { directory: 'skills/devops-config' } },
    ],
  },
  { label: 'MCP Tools', autogenerate: { directory: 'mcp-tools' } },
  { label: 'Guides', autogenerate: { directory: 'guides' } },
  { label: 'Prompt Library', autogenerate: { directory: 'prompt-library' } },
  { label: 'Reference', autogenerate: { directory: 'reference' } },
],
```

- [ ] **Step 4: Build and verify**

```bash
npm run build && npm run preview
```

Expected: Sidebar shows Getting Started + Skills with 3 sample pages under their categories.

- [ ] **Step 5: Commit and push**

```bash
git add src/content/docs/skills/ astro.config.mjs
git commit -m "docs: add 3 sample skill pages and full sidebar structure"
git push origin main
```

---

## Phase 5: Content Migration (Skills)

### Task 5.1: Migrate all single-file skills (15 skills)

Skills with only 1 SKILL.md file — each becomes one doc page.

**Skills (1 file each):**
`databricks-config`, `databricks-aibi-dashboards`, `databricks-agent-skill-databricks-jobs`, `databricks-agent-skill-databricks-lakebase`

**Skills (2 files — inline reference):**
(remaining skills with ≤2 markdown files that weren't converted in Phase 4)

- [ ] **Step 1: For each skill, read the source SKILL.md**

Source: `/Users/robby.kiskanyan/dev/devx/dbx-devx-workshop/.claude/skills/<skill-name>/SKILL.md`

- [ ] **Step 2: Convert to Starlight page using the skill page template**

For each, create the target file under the appropriate category directory:

| Skill Directory | Target Path |
|---|---|
| `databricks-config` | `docs/skills/devops-config/workspace-config.mdx` |
| `databricks-aibi-dashboards` | `docs/skills/sql-analytics/aibi-dashboards.mdx` |
| `databricks-agent-skill-databricks-jobs` | `docs/skills/devops-config/jobs-orchestration.mdx` |
| `databricks-agent-skill-databricks-lakebase` | `docs/skills/apps-databases/lakebase-autoscale.mdx` |
| `databricks-agent-skill-databricks` | `docs/skills/devops-config/workspace-config.mdx` (merge with config) |
| `databricks-bundles` | `docs/skills/devops-config/asset-bundles.mdx` |
| `databricks-genie` | `docs/skills/sql-analytics/genie-spaces.mdx` |
| `databricks-agent-bricks` | `docs/skills/ai-ml/agent-bricks.mdx` |
| `databricks-metric-views` | `docs/skills/sql-analytics/metric-views.mdx` |
| `databricks-lakebase-provisioned` | `docs/skills/apps-databases/lakebase-provisioned.mdx` |
| `databricks-python-sdk` | `docs/skills/devops-config/python-sdk.mdx` |
| `databricks-synthetic-data-gen` | `docs/skills/ai-ml/synthetic-data.mdx` |
| `databricks-unity-catalog` | `docs/skills/governance-catalog/unity-catalog.mdx` |

Apply conversion rules: strip agent metadata, keep capabilities, add frontmatter, add Related MCP Tools, Example Prompts, and References sections.

- [ ] **Step 3: Build and verify**

```bash
npm run build
```

Expected: No build errors. All pages appear in sidebar under correct categories.

- [ ] **Step 4: Commit**

```bash
git add src/content/docs/skills/
git commit -m "docs: migrate 15 single-file skills to Starlight pages"
```

### Task 5.2: Migrate multi-file skills (13 skills with child pages)

Skills with 3+ reference files — each gets a directory with child pages.

**Skills to migrate:**

| Skill | Files | Target Directory |
|---|---|---|
| `databricks-spark-declarative-pipelines` | 11 | `skills/data-engineering/spark-declarative-pipelines/` |
| `databricks-spark-structured-streaming` | 10 | `skills/data-engineering/spark-structured-streaming/` |
| `databricks-model-serving` | 10 | `skills/ai-ml/model-serving/` |
| `databricks-agent-skill-databricks-apps` | 10 | `skills/apps-databases/databricks-apps-appkit/` |
| `spark-python-data-source` | 9 | `skills/data-engineering/custom-spark-data-sources/` |
| `databricks-mlflow-evaluation` | 12 | `skills/ai-ml/mlflow-evaluation/` |
| `databricks-app-python` | 7 | `skills/apps-databases/databricks-apps-python/` |
| `databricks-synthetic-data-gen` | 7 | `skills/ai-ml/synthetic-data/` |
| `databricks-zerobus-ingest` | 6 | `skills/data-engineering/zerobus-ingest/` |
| `databricks-lakebase-autoscale` | 6 | `skills/apps-databases/lakebase-autoscale/` |
| `databricks-iceberg` | 6 | `skills/governance-catalog/iceberg-tables/` |
| `databricks-dbsql` | 6 | `skills/sql-analytics/databricks-sql/` |
| `databricks-jobs` | 5 | `skills/devops-config/jobs-orchestration/` |
| `databricks-ai-functions` | 5 | `skills/sql-analytics/ai-functions/` |
| `databricks-vector-search` | 3 | `skills/ai-ml/vector-search/` |
| `databricks-agent-skill-databricks` | 5 | `skills/devops-config/workspace-config/` |

- [ ] **Step 1: For each skill, read all source markdown files**

- [ ] **Step 2: Create index page from SKILL.md**

For each skill, create `<target-dir>/index.mdx` from the SKILL.md using the skill page template.

- [ ] **Step 3: Create child pages from numbered/reference files**

Each numbered file (e.g., `1-ingestion-patterns.md`) becomes a child page (e.g., `ingestion-patterns.mdx`). Apply frontmatter with `sidebar.order` matching the original numbering.

**Special case for `databricks-agent-skill-databricks-pipelines`:** Consolidate Python/SQL variant pairs into single pages with tabbed code blocks (e.g., `auto-cdc-python.md` + `auto-cdc-sql.md` → `auto-cdc.mdx` with tabs).

- [ ] **Step 4: Embed code examples**

For skills with `examples/` directories, embed the code files as fenced code blocks in the appropriate parent or child page.

- [ ] **Step 5: Build and verify**

```bash
npm run build
```

Expected: No build errors. All skill pages with child pages appear in sidebar.

- [ ] **Step 6: Commit and push**

```bash
git add src/content/docs/skills/
git commit -m "docs: migrate 13 multi-file skills with child pages"
git push origin main
```

---

## Phase 6: MCP Tools, Prompts, Guides & Reference

### Task 6.1: Create MCP Tools catalog pages

**Files:**
- Create: `src/content/docs/mcp-tools/index.mdx`
- Create: `src/content/docs/mcp-tools/sql-execution.mdx`
- Create: `src/content/docs/mcp-tools/pipelines-jobs.mdx`
- Create: `src/content/docs/mcp-tools/unity-catalog.mdx`
- Create: `src/content/docs/mcp-tools/dashboards-genie.mdx`
- Create: `src/content/docs/mcp-tools/vector-search.mdx`
- Create: `src/content/docs/mcp-tools/apps-lakebase.mdx`
- Create: `src/content/docs/mcp-tools/serving-models.mdx`
- Create: `src/content/docs/mcp-tools/compute-workspace.mdx`

- [ ] **Step 1: Catalog all 99 MCP tools from the ai-dev-kit MCP server**

Group by category. For each tool, document: name, description, parameters (name, type, required), example prompt, related skills.

- [ ] **Step 2: Create overview page**

Create `src/content/docs/mcp-tools/index.mdx` — explains what the MCP server is, how to configure it, and lists all categories with tool counts.

- [ ] **Step 3: Create one page per category**

Each page follows the MCP Tool Page Template from the spec. Tools are listed in alphabetical order within each category.

- [ ] **Step 4: Build and verify**

```bash
npm run build
```

- [ ] **Step 5: Commit**

```bash
git add src/content/docs/mcp-tools/
git commit -m "docs: add MCP tools catalog (99 tools across 9 categories)"
```

### Task 6.2: Create Prompt Library pages

**Files:**
- Create: `src/content/docs/prompt-library/index.mdx`
- Create: `src/content/docs/prompt-library/data-engineering.mdx`
- Create: `src/content/docs/prompt-library/sql-analytics.mdx`
- Create: `src/content/docs/prompt-library/ai-ml.mdx`
- Create: `src/content/docs/prompt-library/apps-databases.mdx`
- Create: `src/content/docs/prompt-library/governance-catalog.mdx`
- Create: `src/content/docs/prompt-library/devops-config.mdx`

- [ ] **Step 1: Read the source prompt guide**

Source: `/Users/robby.kiskanyan/dev/devx/dbx-devx-workshop/AI_DEV_KIT_PROMPT_GUIDE.md`

- [ ] **Step 2: Split into 6 category pages**

Each page gets the prompts from its matching sections in the guide. Add Starlight frontmatter. Format each prompt as a fenced code block for easy copy-paste.

- [ ] **Step 3: Create index page**

Overview of the prompt library with links to each category and total prompt count.

- [ ] **Step 4: Build and verify**

```bash
npm run build
```

- [ ] **Step 5: Commit**

```bash
git add src/content/docs/prompt-library/
git commit -m "docs: add Prompt Library split into 6 category pages (130+ prompts)"
```

### Task 6.3: Create Guide pages

**Files:**
- Create: `src/content/docs/guides/rag-application.mdx`
- Create: `src/content/docs/guides/medallion-pipeline.mdx`
- Create: `src/content/docs/guides/multi-agent-system.mdx`
- Create: `src/content/docs/guides/real-time-analytics.mdx`
- Create: `src/content/docs/guides/ml-ops-pipeline.mdx`

- [ ] **Step 1: Write each guide**

Each guide is a cross-cutting tutorial that combines multiple skills and MCP tools for an end-to-end workflow. Source the content from the "Cross-Cutting Scenarios" section of the prompt guide and expand with step-by-step instructions.

- [ ] **Step 2: Build and verify**

```bash
npm run build
```

- [ ] **Step 3: Commit**

```bash
git add src/content/docs/guides/
git commit -m "docs: add 5 end-to-end tutorial guides"
```

### Task 6.4: Create Reference pages

**Files:**
- Create: `src/content/docs/reference/all-mcp-tools.mdx`
- Create: `src/content/docs/reference/all-skills.mdx`
- Create: `src/content/docs/reference/changelog.mdx`

- [ ] **Step 1: Create alphabetical MCP tools index**

All 99 tools listed alphabetically with one-line descriptions and links to their category pages.

- [ ] **Step 2: Create alphabetical skills index**

All 28 skills listed alphabetically with one-line descriptions and links to their doc pages.

- [ ] **Step 3: Create changelog**

Initial entry documenting the site launch.

- [ ] **Step 4: Build, verify, commit, and push**

```bash
npm run build
git add src/content/docs/reference/
git commit -m "docs: add reference pages (alphabetical indexes, changelog)"
git push origin main
```

---

## Final Verification

- [ ] **Verify live site** at `https://robkisk.github.io/aidevkit.github.io/`
- [ ] **Check landing page** renders correctly with all sections
- [ ] **Check docs sidebar** shows all categories and pages
- [ ] **Check Pagefind search** works across doc pages
- [ ] **Check dark/light mode** toggle uses Databricks colors
- [ ] **Check mobile responsive** — landing page stacks correctly, docs sidebar collapses
- [ ] **Check all internal links** resolve (no 404s from base path issues)
