#!/usr/bin/env python3
"""
export_linkedin_assets.py — Export assets/linkedin/source/*.svg to
assets/linkedin/rendered/*.svg.

The source files are the editable masters: hand-authored SVG with a
design-rationale header comment explaining which PlantUML diagram's
technical meaning each asset preserves. The rendered files are the
ready-to-download deliverable: the same markup with the authoring
comments stripped, so what you post is a clean, minimal file.

This script is the single source of truth for keeping source and
rendered in sync — scripts/validate_linkedin_assets.py fails the build
if they drift apart. Re-run this script after every edit to a source
file:

    python3 scripts/export_linkedin_assets.py
    # or: make linkedin-assets

Deliberately stdlib-only, matching the rest of this repository's
validation tooling.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "assets" / "linkedin" / "source"
RENDERED_DIR = REPO_ROOT / "assets" / "linkedin" / "rendered"

COMMENT_RE = re.compile(r"<!--.*?-->\n?", re.DOTALL)


def strip_comments(svg_text: str) -> str:
    """Remove XML comment blocks. SVG comments don't nest, so a single
    non-greedy pass is sufficient and exact."""
    return COMMENT_RE.sub("", svg_text)


def main() -> int:
    RENDERED_DIR.mkdir(parents=True, exist_ok=True)

    source_files = sorted(SOURCE_DIR.glob("*.svg"))
    if not source_files:
        print(f"No source SVGs found in {SOURCE_DIR}", file=sys.stderr)
        return 1

    for src in source_files:
        cleaned = strip_comments(src.read_text(encoding="utf-8"))
        # Collapse the blank line(s) left behind where the header
        # comment used to be, so the exported file opens cleanly.
        cleaned = re.sub(r"\A\n+", "", cleaned)
        dest = RENDERED_DIR / src.name
        dest.write_text(cleaned, encoding="utf-8")
        print(f"{src.relative_to(REPO_ROOT)} -> {dest.relative_to(REPO_ROOT)}")

    # Remove any stale rendered files that no longer have a source.
    source_names = {p.name for p in source_files}
    for stale in RENDERED_DIR.glob("*.svg"):
        if stale.name not in source_names:
            stale.unlink()
            print(f"removed stale {stale.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
