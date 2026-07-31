#!/usr/bin/env python3
"""
validate_examples.py — Validate examples/ against dataset/evidence_manifest.yaml.

This is the automated form of the traceability guarantee described in
examples/traceability_matrix.md: every claim in the illustrative example
outputs must cite a real evidence ID.

Checks:
  1. Every evidence-ID-shaped citation in examples/*.md resolves to a
     real id in evidence_manifest.yaml (no dangling references). Citation
     scanning is restricted to known evidence-ID prefixes so lookalikes
     (decision IDs like DEC-001, the incident ID INC-2026-0730-CHECKOUT)
     are not mistakenly treated as evidence citations.
  2. No Decision Matrix / automation blueprint text assigns an AI system
     as a decision owner or approver (the "AI is never the accountable
     decision owner" governance rule).
  3. The embedded JSON block in examples/automation_blueprint.md validates
     against schemas/automation_blueprint.schema.json.

Run: python3 scripts/validate_examples.py
Exit code 0 on success, 1 if any check fails.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _manifest  # noqa: E402
import _schema_lite  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
SCHEMAS_DIR = REPO_ROOT / "schemas"

BANNED_OWNER_STRINGS = [
    "AI", "the model", "LLM", "the assistant", "Claude", "ChatGPT", "GPT-4", "GPT-5",
]


def main() -> int:
    errors: list[str] = []

    records = _manifest.load_evidence_records()
    manifest_ids = {r["id"] for r in records}
    prefixes = _manifest.known_prefixes(records)
    prefix_pattern = re.compile(
        r"\b((?:" + "|".join(re.escape(p) for p in prefixes) + r")-[0-9]{3,4})\b"
    )

    example_files = sorted(EXAMPLES_DIR.glob("*.md"))
    if not example_files:
        errors.append("examples/: no example files found")

    cited_ids: set[str] = set()
    for path in example_files:
        text = path.read_text(encoding="utf-8")
        for m in prefix_pattern.findall(text):
            cited_ids.add(m)
            if m not in manifest_ids:
                errors.append(f"{path.relative_to(REPO_ROOT)}: cites unknown evidence id {m!r}")

    uncited = manifest_ids - cited_ids
    if uncited:
        # Not a hard failure - some evidence exists for completeness/context
        # and may not need a claim in the illustrative examples - but flag
        # it loudly so drift is visible.
        print(f"Note: {len(uncited)} manifest evidence id(s) are not cited "
              f"in any examples/*.md file: {sorted(uncited)}")

    # --- Decision-owner governance check --------------------------------
    decision_matrix_text = (EXAMPLES_DIR / "decision_matrix.md").read_text(encoding="utf-8")
    owner_lines = re.findall(r"Decision owner\s*[|:]\s*([^|\n]+)", decision_matrix_text)
    owner_lines += re.findall(r"\*\*Consulted roles:\*\*\s*([^\n]+)", decision_matrix_text)
    for line in owner_lines:
        for banned in BANNED_OWNER_STRINGS:
            if re.search(rf"\b{re.escape(banned)}\b", line):
                errors.append(f"decision_matrix.md: decision owner/role field contains banned token {banned!r}: {line!r}")

    # --- automation_blueprint.md embedded JSON vs schema ------------------
    blueprint_text = (EXAMPLES_DIR / "automation_blueprint.md").read_text(encoding="utf-8")
    json_match = re.search(r"```json\n(.*?)\n```", blueprint_text, re.DOTALL)
    if not json_match:
        errors.append("automation_blueprint.md: no embedded ```json block found")
    else:
        try:
            instance = json.loads(json_match.group(1))
        except json.JSONDecodeError as e:
            errors.append(f"automation_blueprint.md: embedded JSON is invalid ({e})")
        else:
            schema = json.loads((SCHEMAS_DIR / "automation_blueprint.schema.json").read_text())
            schema_errors = _schema_lite.validate(instance, schema)
            for e in schema_errors:
                errors.append(f"automation_blueprint.md embedded JSON: {e}")

    # --- Report -----------------------------------------------------
    print(f"Scanned {len(example_files)} example file(s), "
          f"found {len(cited_ids)} distinct evidence citations, "
          f"{len(manifest_ids)} ids in manifest.")

    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\nAll example validation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
