#!/usr/bin/env python3
"""
validate_linkedin_assets.py — Validate assets/linkedin/{source,rendered}/.

Checks:
  1. Exactly 3 source SVGs, each with a matching rendered SVG (by filename).
  2. Every SVG is well-formed XML.
  3. Every SVG's viewBox is a 16:9 aspect ratio (presentation format).
  4. No raster or embedded imagery: no <image>, no <foreignObject>, no
     base64 data URIs. Every mark must be an authored vector primitive.
  5. Every SVG has a <title> and an aria-label, so the "understandable
     in five seconds" requirement is also machine-checked for the
     accessible text summary, not just eyeballed.
  6. rendered/<name>.svg is exactly source/<name>.svg with XML comments
     stripped, i.e. source and rendered can never silently drift apart.
  7. No prohibited real-company names appear (same denylist discipline
     as scripts/validate_dataset.py).

Run: python3 scripts/validate_linkedin_assets.py
Exit code 0 on success, 1 if any check fails.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_linkedin_assets as exporter  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "assets" / "linkedin" / "source"
RENDERED_DIR = REPO_ROOT / "assets" / "linkedin" / "rendered"

EXPECTED_COUNT = 3
PROHIBITED_NAMES = ["LVMH", "Louis Vuitton", "MaIA"]


def main() -> int:
    errors: list[str] = []

    source_files = sorted(SOURCE_DIR.glob("*.svg"))
    rendered_files = sorted(RENDERED_DIR.glob("*.svg"))

    if len(source_files) != EXPECTED_COUNT:
        errors.append(
            f"expected {EXPECTED_COUNT} source SVGs in {SOURCE_DIR}, found {len(source_files)}"
        )

    source_names = {p.name for p in source_files}
    rendered_names = {p.name for p in rendered_files}
    if source_names != rendered_names:
        errors.append(
            f"source/rendered filename mismatch. "
            f"source-only: {sorted(source_names - rendered_names)}, "
            f"rendered-only: {sorted(rendered_names - source_names)}"
        )

    for src in source_files:
        rel = src.relative_to(REPO_ROOT)
        raw = src.read_text(encoding="utf-8")

        # 2. well-formed XML
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            errors.append(f"{rel}: not well-formed XML ({e})")
            continue

        # 3. 16:9 viewBox
        view_box = root.get("viewBox", "")
        parts = view_box.split()
        if len(parts) != 4:
            errors.append(f"{rel}: missing or malformed viewBox")
        else:
            _, _, w, h = (float(p) for p in parts)
            ratio = w / h if h else 0
            if abs(ratio - 16 / 9) > 0.01:
                errors.append(f"{rel}: viewBox aspect ratio {ratio:.3f} is not 16:9 ({w}x{h})")

        # 4. no raster/embedded imagery
        lower = raw.lower()
        if "<image" in lower:
            errors.append(f"{rel}: contains an <image> element (raster embed not allowed)")
        if "foreignobject" in lower:
            errors.append(f"{rel}: contains a <foreignObject> element (not allowed)")
        if "base64," in lower:
            errors.append(f"{rel}: contains a base64-encoded data URI (raster embed not allowed)")

        # 5. accessible title + aria-label
        ns = {"svg": "http://www.w3.org/2000/svg"}
        title_el = root.find("svg:title", ns)
        if title_el is None or not (title_el.text or "").strip():
            errors.append(f"{rel}: missing a non-empty <title> element")
        if not root.get("aria-label", "").strip():
            errors.append(f"{rel}: missing a non-empty aria-label attribute")

        # 6. source -> rendered parity (no drift)
        rendered_path = RENDERED_DIR / src.name
        if rendered_path.exists():
            expected = exporter.strip_comments(raw)
            expected = re.sub(r"\A\n+", "", expected)
            actual = rendered_path.read_text(encoding="utf-8")
            if actual != expected:
                errors.append(
                    f"{rendered_path.relative_to(REPO_ROOT)}: out of sync with {rel}. "
                    f"Run `python3 scripts/export_linkedin_assets.py` (or `make linkedin-assets`)."
                )

        # 7. prohibited names
        for name in PROHIBITED_NAMES:
            if name.lower() in lower:
                errors.append(f"{rel}: contains prohibited name {name!r}")

    print(f"assets/linkedin/source: {len(source_files)} SVG(s)")
    print(f"assets/linkedin/rendered: {len(rendered_files)} SVG(s)")

    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\nAll LinkedIn asset validation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
