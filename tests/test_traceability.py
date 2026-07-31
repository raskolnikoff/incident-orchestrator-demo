"""
tests/test_traceability.py — the traceability guarantee, as tests.

This is the automated counterpart to examples/traceability_matrix.md:
every evidence citation in examples/*.md must resolve to a real manifest
entry, and (a stronger property this repository happens to satisfy) every
manifest entry is cited by at least one example.

Run: python3 -m unittest tests.test_traceability -v
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import _manifest  # noqa: E402

EXAMPLES_DIR = REPO_ROOT / "examples"


class TestTraceability(unittest.TestCase):
    def setUp(self):
        self.records = _manifest.load_evidence_records()
        self.manifest_ids = {r["id"] for r in self.records}
        prefixes = _manifest.known_prefixes(self.records)
        self.citation_pattern = re.compile(
            r"\b((?:" + "|".join(re.escape(p) for p in prefixes) + r")-[0-9]{3,4})\b"
        )
        self.cited_ids: set[str] = set()
        for path in EXAMPLES_DIR.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.cited_ids.update(self.citation_pattern.findall(text))

    def test_every_citation_resolves_to_a_manifest_entry(self):
        dangling = self.cited_ids - self.manifest_ids
        self.assertEqual(dangling, set(), f"dangling evidence citations: {sorted(dangling)}")

    def test_every_manifest_entry_is_cited_at_least_once(self):
        """Stronger than strictly required, but true for this dataset and
        worth protecting against regression: full traceability coverage."""
        uncited = self.manifest_ids - self.cited_ids
        self.assertEqual(uncited, set(), f"manifest ids never cited in examples/: {sorted(uncited)}")

    def test_orchestrator_analysis_covers_all_required_sections(self):
        text = (EXAMPLES_DIR / "orchestrator_analysis.md").read_text(encoding="utf-8")
        required_headings = [
            "## 1. Executive incident summary",
            "## 2. Timeline",
            "## 3. Evidence inventory",
            "## 4. Fact / inference / assumption table",
            "## 5. Contradiction register",
            "## 6. Competing hypotheses",
            "## 7. Confidence levels with rationale",
            "## 8. Customer-impact assessment",
            "## 9. Business-impact assessment",
            "## 10. Data-quality limitations",
            "## 11. Investigation workstreams",
            "## 12. Immediate containment options",
            "## 13. Decision Matrix",
            "## 14. Human approval gates",
            "## 15. Communication drafts",
            "## 16. Audit and traceability table",
            "## 17. Self-review for unsupported claims",
            "## 18. Input-integrity review",
        ]
        for heading in required_headings:
            self.assertIn(heading, text, f"missing required section: {heading}")

    def test_no_hypothesis_declared_conclusively_proven(self):
        """Guard against regression toward false certainty: the analysis
        must not claim a single confirmed root cause."""
        text = (EXAMPLES_DIR / "orchestrator_analysis.md").read_text(encoding="utf-8").lower()
        for banned in ["root cause has been confirmed", "is conclusively proven",
                       "definitively caused by", "confirmed root cause is"]:
            self.assertNotIn(banned, text)


if __name__ == "__main__":
    unittest.main()
