"""
tests/test_dataset.py — unit + integration tests for dataset/ integrity.

Run: python3 -m unittest tests.test_dataset -v
(or `make test`, which runs the whole tests/ suite)
"""
from __future__ import annotations

import contextlib
import csv
import io
import json
import hashlib
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import _manifest  # noqa: E402
import validate_dataset  # noqa: E402

DATASET_DIR = REPO_ROOT / "dataset"


class TestApplicationLogs(unittest.TestCase):
    def setUp(self):
        with open(DATASET_DIR / "application_logs.jsonl", encoding="utf-8") as f:
            self.rows = [json.loads(line) for line in f if line.strip()]

    def test_minimum_record_count(self):
        self.assertGreaterEqual(len(self.rows), 250)

    def test_every_row_has_required_fields(self):
        required = {"timestamp", "log_id", "evidence_id", "service", "region",
                    "level", "http_status", "latency_ms", "request_id",
                    "correlation_id", "sampled", "message"}
        for row in self.rows:
            self.assertTrue(required.issubset(row.keys()), row)

    def test_regions_are_valid(self):
        for row in self.rows:
            self.assertIn(row["region"], {"NA", "EU", "APAC"})


class TestCsvFiles(unittest.TestCase):
    def _read(self, filename):
        with open(DATASET_DIR / filename, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_api_gateway_logs_min_rows(self):
        self.assertGreaterEqual(len(self._read("api_gateway_logs.csv")), 150)

    def test_hourly_kpis_min_rows(self):
        self.assertGreaterEqual(len(self._read("hourly_kpis.csv")), 48)

    def test_payment_metrics_min_rows(self):
        self.assertGreaterEqual(len(self._read("payment_metrics.csv")), 100)

    def test_customer_feedback_min_rows(self):
        self.assertGreaterEqual(len(self._read("customer_feedback.csv")), 35)

    def test_hourly_kpis_covers_three_regions(self):
        rows = self._read("hourly_kpis.csv")
        regions = {r["region"] for r in rows}
        self.assertEqual(regions, {"NA", "EU", "APAC"})

    def test_payment_metrics_covers_multiple_methods_and_providers(self):
        rows = self._read("payment_metrics.csv")
        methods = {r["payment_method"] for r in rows}
        providers = {r["provider"] for r in rows}
        self.assertGreaterEqual(len(methods), 4)
        self.assertEqual(providers, {"ProviderAlpha", "ProviderBeta"})


class TestEvidenceManifest(unittest.TestCase):
    def setUp(self):
        self.records = _manifest.load_evidence_records()

    def test_manifest_not_empty(self):
        self.assertGreater(len(self.records), 0)

    def test_ids_unique(self):
        ids = [r["id"] for r in self.records]
        self.assertEqual(len(ids), len(set(ids)), "duplicate evidence IDs found")

    def test_ids_match_expected_shape(self):
        for r in self.records:
            self.assertRegex(r["id"], _manifest.EVIDENCE_ID_RE)

    def test_reliability_is_valid_enum(self):
        for r in self.records:
            self.assertIn(r["reliability"], {"high", "medium", "low"}, r["id"])

    def test_source_file_paths_exist(self):
        for r in self.records:
            src = REPO_ROOT / r["source_file"]
            self.assertTrue(src.exists(), f"{r['id']}: source_file {src} does not exist")

    def test_manifest_sources_match_snapshot_checksums(self):
        checksum_lines = (DATASET_DIR / "source_checksums.sha256").read_text().splitlines()
        expected = {
            source: digest
            for digest, source in (line.split(maxsplit=1) for line in checksum_lines if line.strip())
        }
        sources = {r["source_file"] for r in self.records}
        self.assertEqual(set(expected), sources)
        for source in sources:
            actual = hashlib.sha256((REPO_ROOT / source).read_bytes()).hexdigest()
            self.assertEqual(actual, expected[source], source)


class TestFullValidatorPasses(unittest.TestCase):
    """Integration test: the full validate_dataset.py script (which
    includes cross-checks too expensive to duplicate here, like
    record_count-vs-actual-rows reconciliation and the prohibited-name /
    secret scan) must exit 0 against this repository's real dataset."""

    def test_validate_dataset_script_passes(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exit_code = validate_dataset.main()
        self.assertEqual(exit_code, 0, buf.getvalue())


class TestDeterministicGeneration(unittest.TestCase):
    """Regression guard for the framework's reproducibility claim: the
    README and dataset/README.md both assert regeneration is
    byte-identical (fixed seed=42). If a future edit to
    generate_dataset.py introduces hidden nondeterminism (e.g. relying on
    dict/set iteration order, wall-clock time, or unseeded randomness),
    this test catches it locally instead of only in CI."""

    GENERATED_FILES = [
        "application_logs.jsonl",
        "api_gateway_logs.csv",
        "hourly_kpis.csv",
        "payment_metrics.csv",
        "customer_feedback.csv",
    ]

    def test_regeneration_is_byte_identical(self):
        import importlib.util

        before = {name: (DATASET_DIR / name).read_bytes() for name in self.GENERATED_FILES}

        gen_path = REPO_ROOT / "scripts" / "generate_dataset.py"
        spec = importlib.util.spec_from_file_location("generate_dataset", gen_path)
        module = importlib.util.module_from_spec(spec)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            spec.loader.exec_module(module)
            module.main()

        try:
            for name in self.GENERATED_FILES:
                after = (DATASET_DIR / name).read_bytes()
                self.assertEqual(before[name], after, f"{name} changed after regeneration")
        finally:
            # Restore exactly, regardless of assertion outcome, so this
            # test never leaves the working tree modified.
            for name in self.GENERATED_FILES:
                (DATASET_DIR / name).write_bytes(before[name])


if __name__ == "__main__":
    unittest.main()
