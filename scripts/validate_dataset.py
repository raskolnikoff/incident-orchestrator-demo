#!/usr/bin/env python3
"""
validate_dataset.py — Validate dataset/ for internal consistency.

Checks (see docs/methodology.md for why each matters):
  1. application_logs.jsonl parses as valid JSON, one object per line
  2. Every CSV file has its expected header columns
  3. Timestamp-shaped fields parse as valid ISO 8601 UTC
  4. Every evidence ID in evidence_manifest.yaml is unique
  5. Every evidence_id referenced by a dataset row exists in the manifest
  6. Every manifest entry's declared record_count matches the actual
     number of rows/records carrying that evidence_id (where applicable)
  7. Minimum record-count thresholds are met for each structured file
  8. No prohibited real-company names appear anywhere in the repository
  9. No obvious secrets appear anywhere in the repository

Run: python3 scripts/validate_dataset.py
Exit code 0 on success, 1 if any check fails (errors are printed).
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _manifest  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = REPO_ROOT / "dataset"

MIN_COUNTS = {
    "application_logs.jsonl": 250,
    "api_gateway_logs.csv": 150,
    "hourly_kpis.csv": 48,
    "payment_metrics.csv": 100,
    "customer_feedback.csv": 35,
}

EXPECTED_CSV_COLUMNS = {
    "api_gateway_logs.csv": [
        "timestamp", "request_id", "evidence_id", "region", "edge_node",
        "endpoint", "method", "http_status", "latency_ms", "cache_status",
        "app_version", "correlation_id",
    ],
    "hourly_kpis.csv": [
        "date", "hour_utc", "region", "evidence_id", "sessions",
        "checkout_attempts", "checkout_authorized", "checkout_declined",
        "checkout_errors", "auth_success_rate", "avg_latency_ms", "campaign_active",
    ],
    "payment_metrics.csv": [
        "date", "time_bucket_start_utc", "evidence_id", "region",
        "payment_method", "provider", "attempts", "authorized",
        "declined_fraud", "declined_issuer", "timeouts", "gateway_errors",
        "avg_latency_ms", "auth_rate",
    ],
    "customer_feedback.csv": [
        "feedback_id", "evidence_id", "timestamp_reported", "region",
        "channel", "payment_method", "symptom_category", "sentiment",
        "delay_hours_est", "free_text",
    ],
    "campaign_schedule.csv": [
        "campaign_id", "name", "region", "start_utc", "end_utc", "channel",
        "expected_traffic_uplift_pct", "evidence_id", "notes",
    ],
}

PROHIBITED_NAMES = [
    "LVMH", "Louis Vuitton", "MaIA",
]

# Deliberately conservative secret-shaped patterns. False positives are
# fine (they just get reviewed); false negatives are the risk we're
# guarding against.
SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),                       # AWS access key
    re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),
    re.compile(r"""(?i)\b(api|secret)[_-]?key\b\s*[:=]\s*['"][A-Za-z0-9/+_-]{16,}['"]"""),
    re.compile(r"""(?i)\bpassword\b\s*[:=]\s*['"][^'"]{4,}['"]"""),
]

TEXT_FILE_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".csv", ".jsonl",
                       ".puml", ".sh", ".cff", ".txt", ""}
EXCLUDE_DIRS = {".git", "diagrams/rendered"}
# This validator's own denylist necessarily contains the prohibited
# strings it's checking for, and its own regex source contains
# secret-shaped patterns by definition - exclude it from its own scan.
EXCLUDE_FILES = {"scripts/validate_dataset.py"}


def iter_repo_text_files():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO_ROOT)
        if any(str(rel).startswith(ex) for ex in EXCLUDE_DIRS):
            continue
        if str(rel) in EXCLUDE_FILES:
            continue
        if path.suffix.lower() not in TEXT_FILE_SUFFIXES:
            continue
        yield path


def is_iso8601(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except (ValueError, AttributeError):
        return False


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    # --- 1. application_logs.jsonl ----------------------------------
    app_log_path = DATASET_DIR / "application_logs.jsonl"
    app_log_evidence_ids: list[str] = []
    app_log_count = 0
    with open(app_log_path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"application_logs.jsonl:{lineno}: invalid JSON ({e})")
                continue
            app_log_count += 1
            if not is_iso8601(rec.get("timestamp", "")):
                errors.append(f"application_logs.jsonl:{lineno}: bad timestamp {rec.get('timestamp')!r}")
            eid = rec.get("evidence_id")
            if eid:
                app_log_evidence_ids.append(eid)
    if app_log_count < MIN_COUNTS["application_logs.jsonl"]:
        errors.append(
            f"application_logs.jsonl: {app_log_count} records, expected >= {MIN_COUNTS['application_logs.jsonl']}"
        )

    # --- 2 & 3. CSV files: headers + timestamps -----------------------
    csv_evidence_ids: dict[str, list[str]] = {}
    csv_counts: dict[str, int] = {}
    for filename, expected_cols in EXPECTED_CSV_COLUMNS.items():
        path = DATASET_DIR / filename
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            actual_cols = reader.fieldnames or []
            if actual_cols != expected_cols:
                errors.append(
                    f"{filename}: header mismatch.\n  expected: {expected_cols}\n  actual:   {actual_cols}"
                )
            rows = list(reader)
        csv_counts[filename] = len(rows)
        eids = []
        for i, row in enumerate(rows, start=2):  # header is line 1
            eid = row.get("evidence_id")
            if eid:
                eids.append(eid)
            for ts_field in ("timestamp", "timestamp_reported", "start_utc", "end_utc"):
                if ts_field in row and row[ts_field]:
                    if not is_iso8601(row[ts_field]):
                        errors.append(f"{filename}:{i}: bad {ts_field} {row[ts_field]!r}")
        csv_evidence_ids[filename] = eids
        if filename in MIN_COUNTS and len(rows) < MIN_COUNTS[filename]:
            errors.append(f"{filename}: {len(rows)} rows, expected >= {MIN_COUNTS[filename]}")

    # --- 4. Evidence ID uniqueness + manifest structure ----------------
    records = _manifest.load_evidence_records()
    ids = [r.get("id") for r in records]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        errors.append(f"evidence_manifest.yaml: duplicate evidence IDs: {sorted(dupes)}")
    for r in records:
        eid = r.get("id", "")
        if not _manifest.EVIDENCE_ID_RE.match(eid):
            errors.append(f"evidence_manifest.yaml: id {eid!r} does not match expected ID shape")

    manifest_ids = set(ids)

    # Content-address every source named by the evidence manifest so a
    # stable evidence ID cannot silently point at changed bytes.
    checksum_path = DATASET_DIR / "source_checksums.sha256"
    expected_hashes: dict[str, str] = {}
    for lineno, line in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            errors.append(f"source_checksums.sha256:{lineno}: malformed checksum record")
            continue
        expected_hashes[parts[1].strip()] = parts[0]

    source_files = {str(r.get("source_file")) for r in records}
    missing_hashes = source_files - set(expected_hashes)
    extra_hashes = set(expected_hashes) - source_files
    if missing_hashes:
        errors.append(f"source_checksums.sha256: missing manifest sources: {sorted(missing_hashes)}")
    if extra_hashes:
        errors.append(f"source_checksums.sha256: unknown sources: {sorted(extra_hashes)}")
    for source_file in sorted(source_files & set(expected_hashes)):
        source_path = REPO_ROOT / source_file
        if not source_path.is_file():
            errors.append(f"{source_file}: manifest source file does not exist")
            continue
        actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if actual_hash != expected_hashes[source_file]:
            errors.append(
                f"{source_file}: content hash differs from source_checksums.sha256; "
                "update the evidence snapshot intentionally"
            )

    # --- 5. Every dataset evidence_id exists in the manifest -----------
    all_dataset_eids: dict[str, set[str]] = {"application_logs.jsonl": set(app_log_evidence_ids)}
    for filename, eids in csv_evidence_ids.items():
        all_dataset_eids[filename] = set(eids)

    for filename, eids in all_dataset_eids.items():
        dangling = eids - manifest_ids
        if dangling:
            errors.append(f"{filename}: evidence_id(s) not found in manifest: {sorted(dangling)}")

    # --- 6. record_count cross-check ------------------------------------
    actual_counts_by_id: dict[str, int] = {}
    for eid in app_log_evidence_ids:
        actual_counts_by_id[eid] = actual_counts_by_id.get(eid, 0) + 1
    for eids in csv_evidence_ids.values():
        for eid in eids:
            actual_counts_by_id[eid] = actual_counts_by_id.get(eid, 0) + 1

    for r in records:
        eid = r.get("id")
        declared = r.get("record_count")
        if declared is None:
            continue  # derived aggregates / narrative docs - not row-countable
        actual = actual_counts_by_id.get(eid, 0)
        if actual != declared:
            errors.append(
                f"evidence_manifest.yaml: {eid} declares record_count={declared} "
                f"but {actual} rows/records reference it in dataset/"
            )

    # --- 7. campaign_schedule.csv is checked above via EXPECTED_CSV_COLUMNS

    # --- 8 & 9. prohibited names + secret scan --------------------------
    for path in iter_repo_text_files():
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        rel = path.relative_to(REPO_ROOT)
        for name in PROHIBITED_NAMES:
            if name.lower() in text.lower():
                errors.append(f"{rel}: contains prohibited name {name!r}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{rel}: matches a secret-shaped pattern ({pattern.pattern})")

    # --- Report -----------------------------------------------------
    print(f"application_logs.jsonl: {app_log_count} records")
    for filename, count in csv_counts.items():
        print(f"{filename}: {count} rows")
    print(f"evidence_manifest.yaml: {len(records)} evidence records")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\nAll dataset validation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
