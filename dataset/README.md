# dataset/

Synthetic evidence set for the fictional incident
`INC-2026-0730-CHECKOUT` ("Intermittent Checkout Authorization
Degradation") at the fictional company **Northstar Commerce**.

Everything in this directory — every log line, metric, complaint,
email, chat message, and change record — is fabricated for this demo
repository. No real company, system, incident, or person is represented.
See the repository root [README](../README.md#synthetic-data-disclaimer)
for the full disclaimer.

## Contents

| File | What it is | Rows/records |
|---|---|---|
| `incident_brief.md` | Narrative overview and known caveats | — |
| `data_dictionary.md` | Field-by-field schema reference | — |
| `application_logs.jsonl` | Structured application logs | 300 |
| `api_gateway_logs.csv` | CDN/API gateway access logs | 180 |
| `hourly_kpis.csv` | Regional hourly checkout KPIs | 144 |
| `payment_metrics.csv` | Payment-method/provider metrics | 216 |
| `customer_feedback.csv` | Synthetic customer complaints | 40 |
| `release_notes.md` | Checkout-api release + CDN change record | — |
| `fraud_rule_change.md` | EU fraud-rule change record | — |
| `vendor_email.md` | Third-party payment provider communication | — |
| `internal_chat.md` | Internal chat excerpts (flagged for overconfidence) | — |
| `campaign_schedule.csv` | Marketing campaign schedule | 6 |
| `incident_history.md` | Prior-incident pattern context | — |
| `operating_procedure.md` | Incident management procedure (severity, RACI roles, escalation) | — |
| `evidence_manifest.yaml` | Evidence catalog — every claim traces here | 45 evidence IDs |
| `source_checksums.sha256` | SHA-256 snapshot of every manifest source | 12 files |

## Regenerating the structured files

```bash
python3 scripts/generate_dataset.py
```

This regenerates `application_logs.jsonl`, `api_gateway_logs.csv`,
`hourly_kpis.csv`, `payment_metrics.csv`, and `customer_feedback.csv`
deterministically (fixed seed `42`). The narrative files and
`evidence_manifest.yaml` are hand-authored and are not touched by the
generator; if you change the generator's logic in a way that changes
record counts or time ranges, update `evidence_manifest.yaml` to match —
`make validate` will catch drift between the two.

## Using this data

Every meaningful claim in `prompts/`, `examples/`, and `docs/` should cite
an `id` from `evidence_manifest.yaml`. Run `make validate` to check that:

- every evidence citation in `examples/*.md` resolves to a real manifest
  entry;
- every manifest entry's declared `record_count` matches the actual number
  of rows/records carrying that `evidence_id` in the underlying file;
- no evidence ID is orphaned (defined but never cited) or dangling (cited
  but undefined).
- every manifest source still matches the content-addressed snapshot in
  `source_checksums.sha256`.

See `dataset/incident_brief.md` for the narrative starting point, and
`examples/orchestrator_analysis.md` for a worked example of using this
evidence set the way `prompts/01_incident_orchestrator.md` expects.
