"""
_manifest.py — Minimal, stdlib-only reader for dataset/evidence_manifest.yaml.

The manifest uses a deliberately restricted YAML subset (see the header
comment in the manifest itself): a flat list of records under the
top-level `evidence:` key, where every record is a flat mapping of
scalars and single-line inline lists (`[NA, EU, APAC]` or `[]`). This
module is not a general YAML parser — it understands exactly that subset,
which is all this repository's tooling needs, and avoids a PyYAML
dependency.

Shared by scripts/validate_dataset.py, scripts/validate_examples.py,
scripts/generate_dataset_summary.py, and the tests/ suite.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "dataset" / "evidence_manifest.yaml"


def _parse_scalar(raw: str):
    val = raw.strip()
    if val == "" or val == "null":
        return None
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [v.strip() for v in inner.split(",")]
    if val.startswith('"') and val.endswith('"') and len(val) >= 2:
        return val[1:-1]
    if val in ("true", "false"):
        return val == "true"
    try:
        return int(val)
    except ValueError:
        pass
    return val


def load_evidence_records(path: Path = MANIFEST_PATH) -> list[dict]:
    """Parse the `evidence:` list from the manifest into a list of dicts."""
    records: list[dict] = []
    current: dict | None = None
    in_evidence = False

    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            stripped = line.strip()

            if not in_evidence:
                if stripped == "evidence:":
                    in_evidence = True
                continue

            if not stripped or stripped.startswith("#"):
                continue

            if stripped.startswith("- "):
                if current is not None:
                    records.append(current)
                current = {}
                rest = stripped[2:]
                if ":" not in rest:
                    continue
                key, val = rest.split(":", 1)
                current[key.strip()] = _parse_scalar(val)
            else:
                if ":" not in stripped or current is None:
                    continue
                key, val = stripped.split(":", 1)
                current[key.strip()] = _parse_scalar(val)

    if current is not None:
        records.append(current)

    return records


def load_manifest_header(path: Path = MANIFEST_PATH) -> dict:
    """Parse the flat top-level scalar keys that appear before `evidence:`."""
    header: dict = {}
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            stripped = raw_line.strip()
            if stripped == "evidence:":
                break
            if not stripped or stripped.startswith("#"):
                continue
            if ":" not in stripped:
                continue
            key, val = stripped.split(":", 1)
            header[key.strip()] = _parse_scalar(val)
    return header


EVIDENCE_ID_RE = re.compile(r"^[A-Z]+(?:-[A-Z]+)*-[0-9]{3,4}$")


def known_prefixes(records: list[dict]) -> set[str]:
    """Return the set of ID prefixes actually used in the manifest, e.g.
    {'LOG-APP', 'GW-API', 'KPI-HOURLY', 'PAY-METRIC', 'CS-FEEDBACK',
    'REL', 'CDN', 'FRAUD', 'VENDOR', 'CHAT', 'CAMPAIGN', 'HIST', 'PROC'}.
    Used to restrict citation-scanning in examples/*.md to real evidence
    ID shapes, so lookalikes (DEC-001, INC-2026-...) are not mistaken for
    evidence citations.
    """
    prefixes = set()
    for rec in records:
        eid = rec.get("id", "")
        m = re.match(r"^(.*)-[0-9]{3,4}$", eid)
        if m:
            prefixes.add(m.group(1))
    return prefixes
