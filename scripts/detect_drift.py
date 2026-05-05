#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
detect_drift.py — Surface curated pages where upstream source has changed.

The sync_content.py script protects pages with `curated: true` from overwrites,
which is intentional — but it means upstream edits to existing skills never
reach the site without manual re-curation. This script compares the last
git-commit time of each source skill directory against the file mtime of the
corresponding curated site page, and reports skills where source has been
committed AFTER the site page was last touched.

Output is purely informational: it suggests skills that may need re-curation
agents, but does not write or modify any files.

Usage:
    uv run scripts/detect_drift.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
SOURCE_REPO = Path("/Users/robby.kiskanyan/dev/aitools/gold-ctx/ai-dev-kit")
SKILLS_SOURCE = SOURCE_REPO / "databricks-skills"
SITE_SKILLS = SITE_ROOT / "src/content/docs/skills"


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
        return 0

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
