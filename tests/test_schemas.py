"""
tests/test_schemas.py — unit tests for schemas/*.json and the
stdlib-only _schema_lite validator, plus integration checks that the
example JSON payloads conform.

Run: python3 -m unittest tests.test_schemas -v
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import _schema_lite  # noqa: E402
import validate_examples  # noqa: E402

SCHEMAS_DIR = REPO_ROOT / "schemas"
EXAMPLES_DIR = REPO_ROOT / "examples"


class TestSchemaFilesAreValidJson(unittest.TestCase):
    def test_all_schema_files_parse(self):
        schema_files = list(SCHEMAS_DIR.glob("*.json"))
        self.assertEqual(len(schema_files), 4)
        for path in schema_files:
            with self.subTest(path=path.name):
                json.loads(path.read_text())


class TestSchemaLiteValidator(unittest.TestCase):
    def test_valid_decision_matrix_row_passes(self):
        schema = json.loads((SCHEMAS_DIR / "decision_matrix.schema.json").read_text())
        instance = {
            "decision_id": "DEC-999",
            "decision_required": "Test decision",
            "trigger": "Test trigger",
            "evidence_ids": ["LOG-APP-001"],
            "confidence": "medium",
            "customer_risk": "low",
            "operational_risk": "low",
            "reversibility": "easily_reversible",
            "options": ["Do nothing", "Take action"],
            "recommended_option": "Do nothing",
            "decision_owner": "SRE Lead",
            "consulted_roles": ["Incident Commander"],
            "approval_deadline": "2026-07-30T15:00:00Z",
            "fallback": "Escalate to Incident Commander",
            "status": "Open",
        }
        errors = _schema_lite.validate(instance, schema)
        self.assertEqual(errors, [])

    def test_ai_as_decision_owner_fails(self):
        """The core governance invariant: an LLM/AI must never be modeled
        as the accountable decision owner."""
        schema = json.loads((SCHEMAS_DIR / "decision_matrix.schema.json").read_text())
        instance = {
            "decision_id": "DEC-999",
            "decision_required": "Test decision",
            "trigger": "Test trigger",
            "evidence_ids": ["LOG-APP-001"],
            "confidence": "medium",
            "customer_risk": "low",
            "operational_risk": "low",
            "reversibility": "easily_reversible",
            "options": ["Do nothing", "Take action"],
            "recommended_option": "Do nothing",
            "decision_owner": "AI",
            "consulted_roles": [],
            "approval_deadline": "2026-07-30T15:00:00Z",
            "fallback": "Escalate to Incident Commander",
            "status": "Open",
        }
        errors = _schema_lite.validate(instance, schema)
        self.assertTrue(
            any("decision_owner" in e for e in errors),
            f"expected a decision_owner violation, got: {errors}",
        )

    def test_ai_owner_variants_fail(self):
        schema = json.loads((SCHEMAS_DIR / "decision_matrix.schema.json").read_text())
        base = {
            "decision_id": "DEC-999", "decision_required": "Test", "trigger": "Test",
            "evidence_ids": ["LOG-APP-001"], "confidence": "medium",
            "customer_risk": "low", "operational_risk": "low",
            "reversibility": "easily_reversible", "options": ["Wait", "Act"],
            "recommended_option": "Wait", "consulted_roles": [],
            "approval_deadline": "2026-07-30T15:00:00Z",
            "fallback": "Escalate to Incident Commander", "status": "Open",
        }
        for owner in ("ai", "AI system", "Language Model", "GPT-5 agent", "ChatGPT"):
            with self.subTest(owner=owner):
                errors = _schema_lite.validate({**base, "decision_owner": owner}, schema)
                self.assertTrue(any("decision_owner" in e for e in errors), errors)

    def test_additional_property_fails_when_schema_is_closed(self):
        schema = json.loads((SCHEMAS_DIR / "decision_matrix.schema.json").read_text())
        errors = _schema_lite.validate({"unexpected": True}, schema)
        self.assertTrue(any("unexpected property" in e for e in errors), errors)

    def test_missing_required_field_fails(self):
        schema = json.loads((SCHEMAS_DIR / "evidence_manifest.schema.json").read_text())
        instance = {"schema_version": "1.0", "incident_id": "INC-TEST"}
        # missing 'evidence'
        errors = _schema_lite.validate(instance, schema)
        self.assertTrue(any("evidence" in e for e in errors))


class TestExampleJsonConformsToSchema(unittest.TestCase):
    def test_automation_blueprint_embedded_json_matches_schema(self):
        text = (EXAMPLES_DIR / "automation_blueprint.md").read_text()
        match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        self.assertIsNotNone(match, "no embedded JSON block found")
        instance = json.loads(match.group(1))
        schema = json.loads((SCHEMAS_DIR / "automation_blueprint.schema.json").read_text())
        errors = _schema_lite.validate(instance, schema)
        self.assertEqual(errors, [], errors)

    def test_validate_examples_script_passes(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exit_code = validate_examples.main()
        self.assertEqual(exit_code, 0, buf.getvalue())


if __name__ == "__main__":
    unittest.main()
