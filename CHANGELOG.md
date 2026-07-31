# Changelog

All notable changes to this repository are documented here. Format
loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] — 2026-08-01

### Added

- Initial public release of the Operational Incident Orchestration
  Framework (OIOF) demo repository.
- Four model-agnostic prompts: Incident Orchestrator, Independent
  Challenge, Automation Blueprint, Executive Brief
  (`prompts/01`–`04`, plus `prompts/prompt_design_notes.md`).
- Synthetic incident dataset for the fictional "Intermittent Checkout
  Authorization Degradation" incident at the fictional Northstar
  Commerce, generated deterministically (`scripts/generate_dataset.py`,
  seed 42): 300 application log records, 180 API gateway log rows, 144
  hourly KPI rows, 216 payment-metric rows, 40 customer-feedback records,
  plus narrative change/communication records and a 45-entry evidence
  manifest (`dataset/evidence_manifest.yaml`).
- Six illustrative example outputs (`examples/`) demonstrating the
  framework's fact/inference/hypothesis discipline, all evidence-cited
  and cross-checked for traceability.
- Six PlantUML diagrams (`diagrams/source/`), rendered to SVG/PNG
  (`diagrams/rendered/`): framework overview, evidence-to-decision
  pipeline, incident workflow, human approval sequence, escalation state
  machine, and a RACI-inspired responsibility model.
- Four JSON Schemas (`schemas/`) for the evidence manifest, findings,
  decision matrix, and automation blueprint, including a machine-checked
  invariant that an AI system can never be the accountable decision
  owner.
- Python standard-library-only validation scripts and test suite
  (`scripts/validate_dataset.py`, `scripts/validate_examples.py`,
  `tests/`) wired into `make validate` / `make test` and GitHub Actions
  CI (`.github/workflows/`).
- Governance, architecture, methodology, limitations, and walkthrough
  documentation (`docs/`).
