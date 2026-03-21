#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
sync_content.py — Sync ai-dev-kit content to the Astro documentation site.

Reads skills and MCP tool definitions from the local ai-dev-kit repo and
generates .mdx pages for the aidevkit.github.io Starlight site.

Usage:
    uv run scripts/sync_content.py                     # Report mode (dry run)
    uv run scripts/sync_content.py --write             # Write new files only
    uv run scripts/sync_content.py --write --force     # Overwrite existing files
    uv run scripts/sync_content.py --only skills       # Skills only
    uv run scripts/sync_content.py --only mcp-tools    # MCP tools only
    uv run scripts/sync_content.py --only reference     # Reference pages only
    uv run scripts/sync_content.py --skill databricks-vector-search --write --force
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

SOURCE_ROOT = Path("/Users/robby.kiskanyan/dev/aitools/ai-dev-kit")
SITE_ROOT = Path(__file__).resolve().parent.parent  # aidevkit.github.io/
SKILLS_SOURCE = SOURCE_ROOT / "databricks-skills"
MCP_TOOLS_SOURCE = SOURCE_ROOT / "databricks-mcp-server/databricks_mcp_server/tools"
CONTENT_DIR = SITE_ROOT / "src/content/docs"

# Skill name → (site_category, site_slug)
SKILL_MAP: dict[str, tuple[str, str]] = {
    # Data Engineering
    "databricks-spark-declarative-pipelines": ("data-engineering", "spark-declarative-pipelines"),
    "spark-python-data-source":               ("data-engineering", "custom-spark-data-sources"),
    "databricks-spark-structured-streaming":   ("data-engineering", "spark-structured-streaming"),
    "databricks-zerobus-ingest":               ("data-engineering", "zerobus-ingest"),
    # SQL & Analytics
    "databricks-ai-functions":    ("sql-analytics", "ai-functions"),
    "databricks-dbsql":           ("sql-analytics", "databricks-sql"),
    "databricks-genie":           ("sql-analytics", "genie-spaces"),
    "databricks-metric-views":    ("sql-analytics", "metric-views"),
    "databricks-aibi-dashboards": ("sql-analytics", "aibi-dashboards"),
    # AI & ML
    "databricks-vector-search":      ("ai-ml", "vector-search"),
    "databricks-agent-bricks":       ("ai-ml", "agent-bricks"),
    "databricks-mlflow-evaluation":  ("ai-ml", "mlflow-evaluation"),
    "databricks-model-serving":      ("ai-ml", "model-serving"),
    "databricks-synthetic-data-gen": ("ai-ml", "synthetic-data"),
    # Apps & Databases
    "databricks-app-python":           ("apps-databases", "databricks-apps-python"),
    "databricks-lakebase-autoscale":   ("apps-databases", "lakebase-autoscale"),
    "databricks-lakebase-provisioned": ("apps-databases", "lakebase-provisioned"),
    # Governance & Catalog
    "databricks-iceberg":       ("governance-catalog", "iceberg-tables"),
    "databricks-unity-catalog": ("governance-catalog", "unity-catalog"),
    # DevOps & Config
    "databricks-bundles":    ("devops-config", "asset-bundles"),
    "databricks-jobs":       ("devops-config", "jobs-orchestration"),
    "databricks-config":     ("devops-config", "workspace-config"),
    "databricks-python-sdk": ("devops-config", "python-sdk"),
}

# Skills rendered as a single .mdx (not a directory with index + children)
SINGLE_PAGE_SKILLS: set[str] = {
    "databricks-aibi-dashboards",
    "databricks-python-sdk",
}

# Source child filename stem → override site slug (for renamed files)
CHILD_SLUG_OVERRIDES: dict[str, str] = {
    "6-change-data-capture": "auto-cdc",
}

# Source subdirectories to skip when scanning for child pages
SKIP_CHILD_DIRS: set[str] = {"examples", "scripts"}

# MCP tool source file stem → site page slug
MCP_FILE_TO_PAGE: dict[str, str] = {
    "unity_catalog":   "unity-catalog",
    "sql":             "sql-execution",
    "compute":         "compute-workspace",
    "pipelines":       "pipelines-jobs",
    "jobs":            "pipelines-jobs",
    "serving":         "serving-models",
    "vector_search":   "vector-search",
    "aibi_dashboards": "dashboards-genie",
    "genie":           "dashboards-genie",
    "apps":            "apps-lakebase",
    "lakebase":        "apps-lakebase",
    "agent_bricks":    "apps-lakebase",
    "file":            "compute-workspace",
    "volume_files":    "unity-catalog",
    "workspace":       "compute-workspace",
}

MCP_SKIP_FILES: set[str] = {"__init__", "manifest", "user"}

MCP_PAGE_TITLES: dict[str, str] = {
    "unity-catalog":     "Unity Catalog",
    "sql-execution":     "SQL Execution",
    "compute-workspace": "Compute & Workspace",
    "pipelines-jobs":    "Pipelines & Jobs",
    "serving-models":    "Serving & Models",
    "vector-search":     "Vector Search",
    "dashboards-genie":  "Dashboards & Genie",
    "apps-lakebase":     "Apps & Lakebase",
}

CATEGORY_TITLES: dict[str, str] = {
    "data-engineering":   "Data Engineering",
    "sql-analytics":      "SQL & Analytics",
    "ai-ml":              "AI & ML",
    "apps-databases":     "Apps & Databases",
    "governance-catalog": "Governance & Catalog",
    "devops-config":      "DevOps & Config",
}


# ═══════════════════════════════════════════════════════════════════════════
# Data types
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ChildPage:
    slug: str
    title: str
    body: str
    source_path: Path
    order: int


@dataclass
class Skill:
    name: str
    description: str
    body: str
    source_path: Path
    children: list[ChildPage] = field(default_factory=list)


@dataclass
class MCPTool:
    name: str
    description: str
    params: list[dict]
    source_file: str


# ═══════════════════════════════════════════════════════════════════════════
# Parsing helpers
# ═══════════════════════════════════════════════════════════════════════════

def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Extract YAML frontmatter from markdown. Returns (metadata, body)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    for line in m.group(1).split("\n"):
        key, _, val = line.partition(":")
        if val:
            fm[key.strip()] = val.strip().strip("\"'")
    return fm, text[m.end() :]


def slugify_source(stem: str) -> str:
    """Convert source filename stem to site slug.

    Strips numeric prefix, lowercases, and converts underscores to hyphens.
    """
    if stem in CHILD_SLUG_OVERRIDES:
        return CHILD_SLUG_OVERRIDES[stem]
    slug = re.sub(r"^\d+-", "", stem)
    return slug.replace("_", "-").lower()


def extract_order(stem: str) -> int:
    """Extract numeric order from filename stem, or 99 for unnumbered."""
    m = re.match(r"^(\d+)-", stem)
    return int(m.group(1)) if m else 99


def title_from_slug(slug: str) -> str:
    """Convert slug to display title."""
    # Handle known acronyms
    acronyms = {"ml", "ai", "sdk", "sql", "rag", "cdc", "sdp", "vs", "uc", "pdf"}
    words = slug.split("-")
    return " ".join(w.upper() if w.lower() in acronyms else w.title() for w in words)


def extract_heading(text: str) -> str | None:
    """Extract the first h1 heading from markdown text."""
    m = re.match(r"^#\s+(.+)", text.strip())
    return m.group(1).strip() if m else None


def strip_heading(text: str) -> str:
    """Remove the first h1 heading line from markdown text."""
    return re.sub(r"^#\s+.+\n*", "", text.strip(), count=1).strip()


def first_sentence(text: str) -> str:
    """Extract first prose sentence from markdown body."""
    body = strip_heading(text)
    for line in body.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Skip non-prose lines: headings, tables, lists, code fences, blockquotes,
        # numbered lists, links-only lines, HTML tags
        if line.startswith(("#", "|", "-", "```", ">", "!", "[", "<")):
            continue
        if re.match(r"^\d+\.", line):
            continue
        m = re.match(r"([^.!?]+[.!?])", line)
        return m.group(1).strip() if m else line[:120]
    return ""


def escape_mdx_angles(body: str) -> str:
    """Escape all < in prose to prevent MDX JSX parse errors.

    Leaves code fences and inline code untouched. MDX treats any < in
    prose as a JSX tag start, so we must escape them to &lt;.

    Properly tracks fenced code blocks per CommonMark: an opening fence
    (``` or ~~~, optionally with info string) is closed only by a line
    with at least as many backticks/tildes and NO info string.
    """
    result: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in body.split("\n"):
        stripped = line.strip()

        if in_fence:
            # Check for closing fence: same char, >= length, no info string
            m = re.match(r"^(`{3,}|~{3,})\s*$", stripped)
            if m and m.group(1)[0] == fence_char and len(m.group(1)) >= fence_len:
                in_fence = False
            result.append(line)
            continue

        # Check for opening fence
        m = re.match(r"^(`{3,}|~{3,})", stripped)
        if m:
            in_fence = True
            fence_char = m.group(1)[0]
            fence_len = len(m.group(1))
            result.append(line)
            continue

        # Outside code fence: escape MDX-sensitive chars in prose, not inline code
        parts = re.split(r"(`[^`]*`)", line)
        escaped: list[str] = []
        for part in parts:
            if part.startswith("`") and part.endswith("`") and len(part) > 1:
                escaped.append(part)
            else:
                part = part.replace("<", "&lt;").replace(">", "&gt;")
                part = part.replace("{", "\\{").replace("}", "\\}")
        result.append("".join(escaped))

    return "\n".join(result)


def sanitize_yaml(value: str) -> str:
    """Make a string safe for unquoted YAML frontmatter values.

    Strips markdown formatting (bold, italic, code) and wraps in quotes
    if the value contains YAML-special characters.
    """
    # Strip markdown bold/italic
    s = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", value)
    # Strip inline code
    s = re.sub(r"`(.+?)`", r"\1", s)
    # Collapse whitespace
    s = " ".join(s.split())
    # Truncate long descriptions
    if len(s) > 160:
        s = s[:157] + "..."
    # Quote if it contains YAML-unsafe chars or could be parsed as non-string
    needs_quoting = (
        re.search(r"[:{}\[\]&*!|>%@`#]", s)
        or s.startswith(("'", '"'))
        or re.match(r"^[\d.]+$", s)  # pure number like "1." or "3.0"
        or s.lower() in ("true", "false", "yes", "no", "null", "~", "")
    )
    if needs_quoting:
        s = s.replace('"', '\\"')
        return f'"{s}"'
    return s


# ═══════════════════════════════════════════════════════════════════════════
# Source reading
# ═══════════════════════════════════════════════════════════════════════════

def read_skill(skill_dir: Path) -> Skill | None:
    """Read a skill directory and extract metadata + child files."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None

    text = skill_md.read_text()
    fm, body = parse_frontmatter(text)

    children: list[ChildPage] = []
    for f in sorted(skill_dir.rglob("*.md")):
        if f.name == "SKILL.md":
            continue
        rel = f.relative_to(skill_dir)
        if any(part in SKIP_CHILD_DIRS for part in rel.parts[:-1]):
            continue

        child_text = f.read_text()
        _, child_body = parse_frontmatter(child_text)
        slug = slugify_source(f.stem)
        title = extract_heading(child_body) or title_from_slug(slug)
        order = extract_order(f.stem)
        children.append(
            ChildPage(
                slug=slug,
                title=title,
                body=child_body,
                source_path=f,
                order=order,
            )
        )

    children.sort(key=lambda c: (c.order, c.slug))

    return Skill(
        name=fm.get("name", skill_dir.name),
        description=fm.get("description", ""),
        body=body,
        source_path=skill_dir,
        children=children,
    )


def read_all_skills() -> dict[str, Skill]:
    """Read all skills from the ai-dev-kit repo."""
    skills: dict[str, Skill] = {}
    if not SKILLS_SOURCE.exists():
        print(f"  ERROR: Skills source not found: {SKILLS_SOURCE}", file=sys.stderr)
        return skills

    for d in sorted(SKILLS_SOURCE.iterdir()):
        if not d.is_dir() or d.name in ("TEMPLATE", "__pycache__"):
            continue
        skill = read_skill(d)
        if skill:
            skills[skill.name] = skill
    return skills


def parse_mcp_tools(filepath: Path) -> list[MCPTool]:
    """Parse @mcp.tool decorated functions from a Python file using AST."""
    try:
        source = filepath.read_text()
        tree = ast.parse(source)
    except (SyntaxError, OSError) as e:
        print(f"  WARN: Could not parse {filepath.name}: {e}", file=sys.stderr)
        return []

    tools: list[MCPTool] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        # Check for @mcp.tool decorator
        has_tool_decorator = False
        for d in node.decorator_list:
            if isinstance(d, ast.Attribute) and d.attr == "tool":
                has_tool_decorator = True
            elif isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute):
                if d.func.attr == "tool":
                    has_tool_decorator = True
        if not has_tool_decorator:
            continue

        # Extract docstring
        docstring = ast.get_docstring(node) or ""
        desc_parts = docstring.split("\n\n")
        desc = desc_parts[0].replace("\n", " ").strip() if desc_parts else ""

        # Parse param descriptions from docstring Args: section
        param_descs: dict[str, str] = {}
        in_args = False
        current_param = ""
        for line in docstring.split("\n"):
            stripped = line.strip()
            if stripped.lower().startswith("args:"):
                in_args = True
                continue
            if in_args:
                if stripped.lower().startswith(
                    ("returns:", "raises:", "example:", "note:", "examples:")
                ):
                    in_args = False
                    continue
                pm = re.match(r"(\w+)\s*(?:\(.*?\))?\s*:\s*(.+)", stripped)
                if pm:
                    current_param = pm.group(1)
                    param_descs[current_param] = pm.group(2).strip()
                elif current_param and stripped:
                    param_descs[current_param] += " " + stripped

        # Extract parameters from function signature
        params: list[dict] = []
        fn_args = node.args
        n_defaults = len(fn_args.defaults)
        n_args = len(fn_args.args)

        for i, arg in enumerate(fn_args.args):
            if arg.arg in ("self", "cls"):
                continue
            type_str = "str"
            if arg.annotation:
                try:
                    type_str = ast.unparse(arg.annotation)
                except Exception:
                    type_str = "Any"
            default_idx = i - (n_args - n_defaults)
            required = default_idx < 0

            params.append(
                {
                    "name": arg.arg,
                    "type": type_str,
                    "required": required,
                    "description": param_descs.get(arg.arg, ""),
                }
            )

        tools.append(
            MCPTool(
                name=node.name,
                description=desc,
                params=params,
                source_file=filepath.stem,
            )
        )

    return tools


def read_all_mcp_tools() -> dict[str, list[MCPTool]]:
    """Read all MCP tool files and group by page slug."""
    pages: dict[str, list[MCPTool]] = {}
    if not MCP_TOOLS_SOURCE.exists():
        print(
            f"  ERROR: MCP tools source not found: {MCP_TOOLS_SOURCE}", file=sys.stderr
        )
        return pages

    for f in sorted(MCP_TOOLS_SOURCE.glob("*.py")):
        stem = f.stem
        if stem in MCP_SKIP_FILES:
            continue
        if stem not in MCP_FILE_TO_PAGE:
            print(f"  WARN: Unmapped MCP tool file: {f.name}")
            continue

        page_slug = MCP_FILE_TO_PAGE[stem]
        tools = parse_mcp_tools(f)
        if tools:
            pages.setdefault(page_slug, []).extend(tools)

    return pages


# ═══════════════════════════════════════════════════════════════════════════
# Content generation
# ═══════════════════════════════════════════════════════════════════════════

def gen_skill_index(skill: Skill, slug: str) -> str:
    """Generate index.mdx content from a skill's SKILL.md."""
    title = title_from_slug(slug)
    desc = sanitize_yaml(skill.description)
    body = escape_mdx_angles(strip_heading(skill.body))

    return (
        f"---\n"
        f"title: {title}\n"
        f"description: {desc}\n"
        f"sidebar:\n"
        f"  label: {title}\n"
        f"  order: 0\n"
        f"---\n\n"
        f"{body}\n"
    )


def gen_skill_single(skill: Skill, slug: str) -> str:
    """Generate a single-page .mdx from SKILL.md + child content concatenated."""
    title = title_from_slug(slug)
    desc = sanitize_yaml(skill.description)
    parts = [strip_heading(skill.body)]
    for child in skill.children:
        parts.append(f"\n---\n\n{child.body.strip()}")
    body = escape_mdx_angles("\n".join(parts))

    return (
        f"---\n"
        f"title: {title}\n"
        f"description: {desc}\n"
        f"sidebar:\n"
        f"  label: {title}\n"
        f"---\n\n"
        f"{body}\n"
    )


def gen_child_page(child: ChildPage) -> str:
    """Generate a child .mdx page from source content."""
    body = escape_mdx_angles(strip_heading(child.body))
    desc = sanitize_yaml(first_sentence(child.body) or child.title)
    title = sanitize_yaml(child.title)

    return (
        f"---\n"
        f"title: {title}\n"
        f"description: {desc}\n"
        f"sidebar:\n"
        f"  order: {child.order}\n"
        f"---\n\n"
        f"{body}\n"
    )


def gen_mcp_page(page_slug: str, tools: list[MCPTool]) -> str:
    """Generate an MCP tools reference page."""
    title = MCP_PAGE_TITLES.get(page_slug, title_from_slug(page_slug))
    sections: list[str] = []

    for tool in sorted(tools, key=lambda t: t.name):
        param_table = ""
        if tool.params:
            rows: list[str] = []
            for p in tool.params:
                req = "Yes" if p["required"] else "No"
                desc = p["description"] or "\u2014"
                ptype = p["type"].replace("|", "\\|")
                rows.append(f"| `{p['name']}` | `{ptype}` | {req} | {desc} |")
            param_table = (
                "\n**Parameters:**\n\n"
                "| Parameter | Type | Required | Description |\n"
                "|---|---|---|---|\n"
                + "\n".join(rows)
                + "\n"
            )

        sections.append(f"## {tool.name}\n\n**Description:** {tool.description}\n{param_table}")

    body = "\n".join(sections)

    return (
        f"---\n"
        f"title: {title}\n"
        f"description: MCP tools for {title.lower()} operations.\n"
        f"sidebar:\n"
        f"  label: {title}\n"
        f"---\n\n"
        f"{body}\n"
    )


def gen_all_skills_ref(skills: dict[str, Skill]) -> str:
    """Generate the all-skills.mdx reference page."""
    rows: list[str] = []
    for name, skill in sorted(skills.items()):
        if name not in SKILL_MAP:
            continue
        category, slug = SKILL_MAP[name]
        cat_title = CATEGORY_TITLES.get(category, category)
        link = f"/aidevkit.github.io/skills/{category}/{slug}/"
        rows.append(
            f"| [{title_from_slug(slug)}]({link}) | {cat_title} | {skill.description} |"
        )

    table = "\n".join(rows)

    return (
        f"---\n"
        f"title: All Skills\n"
        f"description: Complete reference of all AI Dev Kit skills organized by category.\n"
        f"---\n\n"
        f"## Skills Reference\n\n"
        f"| Skill | Category | Description |\n"
        f"|---|---|---|\n"
        f"{table}\n"
    )


def gen_all_mcp_ref(pages: dict[str, list[MCPTool]]) -> str:
    """Generate the all-mcp-tools.mdx reference page."""
    rows: list[str] = []
    for page_slug, tools in sorted(pages.items()):
        title = MCP_PAGE_TITLES.get(page_slug, title_from_slug(page_slug))
        for tool in sorted(tools, key=lambda t: t.name):
            link = f"/aidevkit.github.io/mcp-tools/{page_slug}/"
            desc = tool.description[:120]
            rows.append(f"| [{tool.name}]({link}) | {title} | {desc} |")

    table = "\n".join(rows)

    return (
        f"---\n"
        f"title: All MCP Tools\n"
        f"description: Complete reference of all MCP tools available in the AI Dev Kit.\n"
        f"---\n\n"
        f"## MCP Tools Reference\n\n"
        f"| Tool | Category | Description |\n"
        f"|---|---|---|\n"
        f"{table}\n"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Sync orchestration
# ═══════════════════════════════════════════════════════════════════════════

def write_file(
    path: Path, content: str, *, force: bool, dry_run: bool
) -> tuple[str, str]:
    """Write content to path. Returns (action, display_line)."""
    rel = path.relative_to(SITE_ROOT)
    exists = path.exists()

    if exists and not force:
        return "skip", f"  . skip (exists): {rel}"
    if dry_run:
        action = "would overwrite" if exists else "would create"
        return "dry", f"  ~ {action}: {rel}"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    action_label = "updated" if exists else "created"
    return action_label, f"  + {action_label}: {rel}"


def sync_skills(
    *, force: bool, dry_run: bool, only_skill: str | None = None
) -> list[str]:
    """Sync skill pages. Returns log lines."""
    log: list[str] = []
    skills = read_all_skills()
    log.append(f"\n  Found {len(skills)} skills in source\n")

    counts: dict[str, int] = {"created": 0, "updated": 0, "skip": 0, "dry": 0}
    unmapped: list[str] = []

    for name, skill in sorted(skills.items()):
        if only_skill and name != only_skill:
            continue
        if name not in SKILL_MAP:
            unmapped.append(name)
            continue

        category, slug = SKILL_MAP[name]

        if name in SINGLE_PAGE_SKILLS:
            path = CONTENT_DIR / "skills" / category / f"{slug}.mdx"
            content = gen_skill_single(skill, slug)
            action, line = write_file(path, content, force=force, dry_run=dry_run)
            counts[action] = counts.get(action, 0) + 1
            log.append(line)
        else:
            # Index page
            index_path = CONTENT_DIR / "skills" / category / slug / "index.mdx"
            content = gen_skill_index(skill, slug)
            action, line = write_file(
                index_path, content, force=force, dry_run=dry_run
            )
            counts[action] = counts.get(action, 0) + 1
            log.append(line)

            # Child pages
            for child in skill.children:
                child_path = CONTENT_DIR / "skills" / category / slug / f"{child.slug}.mdx"
                content = gen_child_page(child)
                action, line = write_file(
                    child_path, content, force=force, dry_run=dry_run
                )
                counts[action] = counts.get(action, 0) + 1
                log.append(line)

    if unmapped and not only_skill:
        log.append(f"\n  WARN: {len(unmapped)} unmapped skills (add to SKILL_MAP):")
        for name in unmapped:
            log.append(f"    - {name}")

    log.append(
        f"\n  Summary: {counts.get('created', 0)} created, "
        f"{counts.get('updated', 0)} updated, "
        f"{counts.get('skip', 0)} skipped, "
        f"{counts.get('dry', 0)} dry-run"
    )
    return log


def sync_mcp_tools(*, force: bool, dry_run: bool) -> list[str]:
    """Sync MCP tool reference pages. Returns log lines."""
    log: list[str] = []
    pages = read_all_mcp_tools()
    tool_count = sum(len(t) for t in pages.values())
    log.append(f"\n  Found {tool_count} tools across {len(pages)} pages\n")

    counts: dict[str, int] = {}
    for page_slug, tools in sorted(pages.items()):
        path = CONTENT_DIR / "mcp-tools" / f"{page_slug}.mdx"
        content = gen_mcp_page(page_slug, tools)
        action, line = write_file(path, content, force=force, dry_run=dry_run)
        counts[action] = counts.get(action, 0) + 1
        log.append(line)

    log.append(
        f"\n  Summary: {counts.get('created', 0)} created, "
        f"{counts.get('updated', 0)} updated, "
        f"{counts.get('skip', 0)} skipped"
    )
    return log


def sync_reference(*, force: bool, dry_run: bool) -> list[str]:
    """Sync reference index pages. Returns log lines."""
    log: list[str] = []
    skills = read_all_skills()
    pages = read_all_mcp_tools()

    path = CONTENT_DIR / "reference" / "all-skills.mdx"
    content = gen_all_skills_ref(skills)
    _, line = write_file(path, content, force=force, dry_run=dry_run)
    log.append(line)

    path = CONTENT_DIR / "reference" / "all-mcp-tools.mdx"
    content = gen_all_mcp_ref(pages)
    _, line = write_file(path, content, force=force, dry_run=dry_run)
    log.append(line)

    return log


LANDING_PAGE = SITE_ROOT / "src/pages/index.astro"


def sync_landing(*, dry_run: bool) -> list[str]:
    """Update skill and MCP tool counts on the landing page."""
    log: list[str] = []

    skills = read_all_skills()
    pages = read_all_mcp_tools()

    # Count mapped skills + site-only skills (e.g., AppKit)
    mapped_skills = sum(1 for name in skills if name in SKILL_MAP)
    site_only_dirs = [
        d
        for d in (CONTENT_DIR / "skills").rglob("index.mdx")
        if d.parent.name
        not in {slug for _, slug in SKILL_MAP.values()}
        | {"skills"}
    ]
    skill_count = mapped_skills + len(site_only_dirs)
    tool_count = sum(len(t) for t in pages.values())

    log.append(f"\n  Skills: {skill_count}, MCP Tools: {tool_count}")

    if not LANDING_PAGE.exists():
        log.append(f"  ERROR: Landing page not found: {LANDING_PAGE}")
        return log

    text = LANDING_PAGE.read_text()
    original = text

    # Update skill stat: match `stat: '<anything>',` followed by `title: 'Skills',`
    text = re.sub(
        r"(stat:\s*')[^']*(',\s*\n\s*title:\s*'Skills')",
        rf"\g<1>{skill_count}\2",
        text,
    )
    # Update MCP tool stat
    text = re.sub(
        r"(stat:\s*')[^']*(',\s*\n\s*title:\s*'MCP Tools')",
        rf"\g<1>{tool_count}\2",
        text,
    )

    if text == original:
        log.append("  . no changes needed")
        return log

    if dry_run:
        log.append(f"  ~ would update: {LANDING_PAGE.relative_to(SITE_ROOT)}")
    else:
        LANDING_PAGE.write_text(text)
        log.append(f"  + updated: {LANDING_PAGE.relative_to(SITE_ROOT)}")

    return log


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync ai-dev-kit content to the documentation site.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write files (default: dry-run report only)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files (default: skip existing)",
    )
    parser.add_argument(
        "--only",
        choices=["skills", "mcp-tools", "reference", "landing"],
        help="Sync only the specified section",
    )
    parser.add_argument(
        "--skill",
        type=str,
        help="Sync only the named skill (e.g., databricks-vector-search)",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=SOURCE_ROOT,
        help=f"Path to ai-dev-kit repo (default: {SOURCE_ROOT})",
    )
    args = parser.parse_args()

    # Allow overriding source path
    global SKILLS_SOURCE, MCP_TOOLS_SOURCE
    if args.source != SOURCE_ROOT:
        SKILLS_SOURCE = args.source / "databricks-skills"
        MCP_TOOLS_SOURCE = (
            args.source / "databricks-mcp-server/databricks_mcp_server/tools"
        )

    dry_run = not args.write
    force = args.force

    header = "DRY RUN (use --write to apply)" if dry_run else "WRITING CHANGES"
    if force:
        header += " [force: overwriting existing]"
    print(f"\n{'=' * 56}")
    print(f"  {header}")
    print(f"{'=' * 56}")

    # If --skill is set, only sync that skill
    if args.skill:
        print(f"\n-- skills (filtered: {args.skill}) --")
        for line in sync_skills(
            force=force, dry_run=dry_run, only_skill=args.skill
        ):
            print(line)
        print()
        return

    sections = [args.only] if args.only else ["skills", "mcp-tools", "reference", "landing"]

    for section in sections:
        print(f"\n-- {section} --")
        if section == "skills":
            log = sync_skills(force=force, dry_run=dry_run)
        elif section == "mcp-tools":
            log = sync_mcp_tools(force=force, dry_run=dry_run)
        elif section == "reference":
            log = sync_reference(force=force, dry_run=dry_run)
        elif section == "landing":
            log = sync_landing(dry_run=dry_run)
        else:
            continue

        for line in log:
            print(line)

    print()
    if dry_run:
        print("No files written. Use --write to apply changes.\n")


if __name__ == "__main__":
    main()
