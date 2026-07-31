"""
tests/test_linkedin_assets.py — unit + integration tests for the LinkedIn
carousel assets under assets/linkedin/.

Run: python3 -m unittest tests.test_linkedin_assets -v
"""
from __future__ import annotations

import contextlib
import io
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import export_linkedin_assets  # noqa: E402
import validate_linkedin_assets  # noqa: E402

SOURCE_DIR = REPO_ROOT / "assets" / "linkedin" / "source"
RENDERED_DIR = REPO_ROOT / "assets" / "linkedin" / "rendered"

# Phrases each slide must retain, so the "no autonomous decision-making"
# and "human is always accountable" requirements stay checkable, not
# just eyeballed once and forgotten.
REQUIRED_NO_AUTONOMY_PHRASES = {
    "01_evidence-to-decision.svg": ["Recommends only", "Never decides"],
    "02_human-in-the-loop-workflow.svg": ["Nothing executes without it", "Never auto-approves"],
    "03_raci-accountability.svg": ["NEVER THE ACCOUNTABLE OWNER", "Never the model"],
}


class TestLinkedInAssetStructure(unittest.TestCase):
    def test_exactly_three_source_files(self):
        files = sorted(SOURCE_DIR.glob("*.svg"))
        self.assertEqual(len(files), 3, [f.name for f in files])

    def test_source_and_rendered_filenames_match(self):
        source_names = {p.name for p in SOURCE_DIR.glob("*.svg")}
        rendered_names = {p.name for p in RENDERED_DIR.glob("*.svg")}
        self.assertEqual(source_names, rendered_names)

    def test_all_svgs_are_well_formed_xml(self):
        for path in list(SOURCE_DIR.glob("*.svg")) + list(RENDERED_DIR.glob("*.svg")):
            with self.subTest(path=path.name):
                ET.fromstring(path.read_text(encoding="utf-8"))

    def test_all_svgs_are_16_by_9(self):
        for path in SOURCE_DIR.glob("*.svg"):
            root = ET.fromstring(path.read_text(encoding="utf-8"))
            _, _, w, h = (float(p) for p in root.get("viewBox").split())
            with self.subTest(path=path.name):
                self.assertAlmostEqual(w / h, 16 / 9, places=2)

    def test_no_raster_or_embedded_imagery(self):
        for path in SOURCE_DIR.glob("*.svg"):
            text = path.read_text(encoding="utf-8").lower()
            with self.subTest(path=path.name):
                self.assertNotIn("<image", text)
                self.assertNotIn("foreignobject", text)
                self.assertNotIn("base64,", text)

    def test_rendered_matches_stripped_source(self):
        for src in SOURCE_DIR.glob("*.svg"):
            expected = export_linkedin_assets.strip_comments(src.read_text(encoding="utf-8"))
            expected = re.sub(r"\A\n+", "", expected)
            actual = (RENDERED_DIR / src.name).read_text(encoding="utf-8")
            with self.subTest(path=src.name):
                self.assertEqual(actual, expected)


class TestNoAutonomyClaims(unittest.TestCase):
    """Guards the explicit requirement that no slide implies autonomous
    decision-making, and that human accountability is stated, not just
    implied by layout."""

    def test_required_phrases_present(self):
        for filename, phrases in REQUIRED_NO_AUTONOMY_PHRASES.items():
            text = (SOURCE_DIR / filename).read_text(encoding="utf-8")
            for phrase in phrases:
                with self.subTest(file=filename, phrase=phrase):
                    self.assertIn(phrase, text)


class TestFullLinkedInValidatorPasses(unittest.TestCase):
    def test_validate_linkedin_assets_script_passes(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exit_code = validate_linkedin_assets.main()
        self.assertEqual(exit_code, 0, buf.getvalue())


if __name__ == "__main__":
    unittest.main()
