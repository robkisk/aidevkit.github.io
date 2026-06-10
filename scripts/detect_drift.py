#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
detect_drift.py — Surface site content that has drifted from upstream source.

Two checks:

1. Curated page drift. The sync_content.py script protects pages with
   `curated: true` from overwrites, which is intentional — but it means
   upstream edits to existing skills never reach the site without manual
   re-curation. This check compares the last git-commit time of each source
   skill directory against the file mtime of the corresponding curated site
   page, and reports skills where source has been committed AFTER the site
   page was last touched.

2. Stale MCP tool references. Hand-maintained pages (prompt-library/, guides/,
   mcp-tools/index.mdx) have no upstream source directory, so check 1 never
   flags them. This check parses every MCP tool name that has EVER existed in
   upstream git history (deduped by blob SHA, so each file version is parsed
   once), subtracts the current tool surface, and scans all site pages for
   references to removed tools — backticked names in prose, bare names inside
   code fences. High precision: only tokens that were once registered
   `@mcp.tool` functions are ever flagged (a backticked SDK method that
   happens to share a name with a removed tool can still false-positive).

Output is purely informational: it suggests pages that may need re-curation,
but does not write or modify any files.

Usage:
    uv run scripts/detect_drift.py
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
SOURCE_REPO = Path("/Users/robby.kiskanyan/dev/aitools/gold-ctx/ai-dev-kit")
SKILLS_SOURCE = SOURCE_REPO / "databricks-skills"
SITE_SKILLS = SITE_ROOT / "src/content/docs/skills"
MCP_TOOLS_REL = "databricks-mcp-server/databricks_mcp_server/tools"
SITE_DOCS = SITE_ROOT / "src/content/docs"
BACKTICK_TOKEN = re.compile(r"`([a-z][a-z0-9_]+)`")
WORD_TOKEN = re.compile(r"[a-z][a-z0-9_]{3,}")


def parse_skill_map(sync_script: Path) -> tuple[dict[str, tuple[str, str]], set[str]]:
    text = sync_script.read_text()
    skill_map_match = re.search(r"SKILL_MAP[^=]*=\s*\{(.*?)\n\}", text, re.S)
    single_match = re.search(r"SINGLE_PAGE_SKILLS[^=]*=\s*\{(.*?)\}", text, re.S)
    if not skill_map_match:
        sys.exit("ERROR: could not parse SKILL_MAP from sync_content.py")

    skill_map: dict[str, tuple[str, str]] = {}
    for line in skill_map_match.group(1).split("\n"):
        m = re.match(r'\s*"([^"]+)":\s*\("([^"]+)",\s*"([^"]+)"\)', line)
        if m:
            skill_map[m.group(1)] = (m.group(2), m.group(3))

    single = set(re.findall(r'"([^"]+)"', single_match.group(1))) if single_match else set()
    return skill_map, single


def last_commit_epoch(path: Path, repo: Path) -> int:
    rel = path.relative_to(repo)
    out = subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--format=%ct", "--", str(rel)],
        capture_output=True, text=True
    ).stdout.strip()
    return int(out) if out else 0


def recent_commit_subjects(path: Path, repo: Path, limit: int = 3) -> list[str]:
    rel = path.relative_to(repo)
    out = subprocess.run(
        ["git", "-C", str(repo), "log", "--since=180 days", f"-{limit}", "--format=%h %s", "--", str(rel)],
        capture_output=True, text=True
    ).stdout.strip()
    return [line for line in out.split("\n") if line]


def tool_names_from_source(src: str) -> set[str]:
    """Names of @mcp.tool-decorated functions (same logic as sync_content.py)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in node.decorator_list:
            target = d.func if isinstance(d, ast.Call) else d
            if isinstance(target, ast.Attribute) and target.attr == "tool":
                names.add(node.name)
    return names


def git_out(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(SOURCE_REPO), *args], capture_output=True, text=True
    ).stdout


def current_tools() -> tuple[set[str], dict[str, set[str]]]:
    """Current tool surface, plus per-source-file grouping for suggestions."""
    current: set[str] = set()
    by_file: dict[str, set[str]] = {}
    for f in sorted((SOURCE_REPO / MCP_TOOLS_REL).glob("*.py")):
        names = tool_names_from_source(f.read_text())
        current |= names
        if names:
            by_file[f.stem] = names
    return current, by_file


def historical_tools() -> dict[str, str]:
    """Every tool name that ever existed in git history -> source file stem.

    Dedupes by blob SHA so each unique file version is parsed exactly once,
    regardless of how many commits it survived unchanged.
    """
    blob_stems: dict[str, str] = {}
    for rev in git_out("rev-list", "HEAD", "--", MCP_TOOLS_REL).split():
        for line in git_out("ls-tree", rev, MCP_TOOLS_REL + "/").splitlines():
            parts = line.split()
            if len(parts) >= 4 and parts[3].endswith(".py"):
                blob_stems.setdefault(parts[2], Path(parts[3]).stem)

    name_to_stem: dict[str, str] = {}
    for sha, stem in blob_stems.items():
        for name in tool_names_from_source(git_out("cat-file", "blob", sha)):
            name_to_stem.setdefault(name, stem)
    return name_to_stem


def check_stale_tool_refs() -> int:
    """Report site references to MCP tools that no longer exist upstream."""
    print("=" * 56)
    print("  STALE MCP TOOL REFERENCE CHECK")
    print("=" * 56)

    tools_dir = SOURCE_REPO / MCP_TOOLS_REL
    if not tools_dir.exists():
        print(f"\n  WARN: MCP tools source not found: {tools_dir}\n")
        return 0

    current, current_by_file = current_tools()
    name_to_stem = historical_tools()
    if not name_to_stem:
        print("\n  WARN: could not read tool history from upstream git repo —")
        print("  stale-reference check skipped.\n")
        return 0
    removed = set(name_to_stem) - current

    hits: dict[str, list[tuple[str, int]]] = {}
    targets = sorted(SITE_DOCS.rglob("*.mdx"))
    landing = SITE_ROOT / "src/pages/index.astro"
    if landing.exists():
        targets.append(landing)
    for path in targets:
        rel = str(path.relative_to(SITE_ROOT))
        in_fence = False
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                # Inside code fences names appear bare (calls, comments)
                toks = set(WORD_TOKEN.findall(line)) & removed
            else:
                toks = {t for t in BACKTICK_TOKEN.findall(line) if t in removed}
            for tok in sorted(toks):
                hits.setdefault(tok, []).append((rel, i))

    if not hits:
        print(f"\n  No stale references. All MCP tool names on the site exist")
        print(f"  in the current upstream tool surface ({len(current)} tools).\n")
        return 0

    total = sum(len(v) for v in hits.values())
    print(f"\n  {total} reference(s) to {len(hits)} removed tool(s):\n")
    for tok in sorted(hits):
        stem = name_to_stem[tok]
        now = ", ".join(sorted(current_by_file.get(stem, set()))) or "(none)"
        print(f"  `{tok}` (was in {stem}.py — current tools there: {now})")
        for rel, lineno in hits[tok]:
            print(f"      {rel}:{lineno}")
        print()
    return total


def main() -> int:
    skill_map, single_pages = parse_skill_map(SITE_ROOT / "scripts/sync_content.py")

    stale: list[tuple[int, str, Path]] = []
    for skill, (cat, slug) in skill_map.items():
        src = SKILLS_SOURCE / skill
        if not src.exists():
            continue

        if skill in single_pages:
            site_files = [SITE_SKILLS / cat / f"{slug}.mdx"]
        else:
            site_dir = SITE_SKILLS / cat / slug
            site_files = sorted(site_dir.glob("*.mdx")) if site_dir.exists() else []
        site_files = [f for f in site_files if f.exists()]
        if not site_files:
            continue

        src_epoch = last_commit_epoch(src, SOURCE_REPO)
        # Use max mtime across all curated pages — if ANY page was recently
        # updated, treat the skill as fresh (avoids false-positives when child
        # pages were re-curated but the index.mdx was left alone).
        site_mtime = max(int(f.stat().st_mtime) for f in site_files)
        if src_epoch > site_mtime:
            days = (src_epoch - site_mtime) // 86400
            stale.append((days, skill, src))

    stale.sort(reverse=True)

    print("=" * 56)
    print("  CURATED PAGE DRIFT CHECK")
    print("=" * 56)

    if not stale:
        print("\n  No drift detected. All curated pages are newer than their")
        print("  source skill directories' last commit.\n")
    else:
        print(f"\n  {len(stale)} skill(s) have source updates newer than their")
        print(f"  curated site pages. Consider re-curating:\n")
        for days, skill, src in stale:
            print(f"  {days:3d}d stale: {skill}")
            for subject in recent_commit_subjects(src, SOURCE_REPO):
                print(f"           {subject}")
            print()

        print("  Note: drift only flags candidates. The script cannot tell whether")
        print("  source changes are user-facing (API/syntax updates) or agent-only")
        print("  (prompt instructions). A re-curation agent should make that call.\n")

    check_stale_tool_refs()
    return 0


if __name__ == "__main__":
    sys.exit(main())
