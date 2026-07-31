# Traceability Matrix — INC-2026-0730-CHECKOUT

> **Illustrative example generated for this synthetic scenario.** This
> matrix is the human-reviewed view of the traceability property the
> framework requires: claims in `examples/orchestrator_analysis.md`,
> `examples/challenge_review.md`, `examples/decision_matrix.md`, and
> `examples/automation_blueprint.md` traces back to a real entry in
> `dataset/evidence_manifest.yaml`. `scripts/validate_examples.py`
> automatically checks citation resolution and manifest coverage; it does
> not judge whether a cited source semantically entails the adjacent claim.
> All 45 evidence IDs in the manifest are cited
> at least once across the example documents; the reverse-index table
> below was generated directly from the example files (not hand-typed)
> and can be regenerated with the snippet in the appendix.

## By hypothesis

### H1 — ProviderAlpha latency/timeout degradation

| Claim | Evidence |
|---|---|
| 17.1% timeout rate for ProviderAlpha NA/EU, 10:00–16:00 UTC | `PAY-METRIC-001` |
| 0% timeout rate for ProviderBeta in the same period (control) | `PAY-METRIC-002`, corroborated by `LOG-APP-003` |
| Concentrated TIMEOUT/NETWORK_ERROR log entries, NA/EU, 11:05–14:43 UTC | `LOG-APP-002` |
| Vendor acknowledgment of elevated processing times (weak, non-specific) | `VENDOR-001` |
| Historical precedent: 2 of 3 prior related incidents were provider-side | `HIST-001` |
| Timeout rate recedes to 1.5% in the post-16:00 tail (does not explain EU persistence) | `PAY-METRIC-003` |

### H2 — checkout-api 3.12.0 release regression

| Claim | Evidence |
|---|---|
| checkout-api 3.12.0 deployed 08:00–09:00 UTC, retry-policy change | `REL-001` |
| Elevated CHECKOUT_RETRY_EXCEEDED on 3.12.0 vs. 3.11.4 control | `LOG-APP-007` vs. `LOG-APP-008` |
| Regional pattern doesn't match (APAC carries same release, smallest decline) | `KPI-HOURLY-004` |

### H3 — EU fraud-rule false declines

| Claim | Evidence |
|---|---|
| FR-2026-118 deployed to EU only, 09:30 UTC | `FRAUD-001` |
| Elevated DECLINE_FRAUD entries in EU post-09:30 | `LOG-APP-004` |
| 13.3% EU fraud-decline rate, isolated post-16:00 window | `PAY-METRIC-003` |
| Baseline fraud-decline control (EU pre-09:30, NA/APAC all day) | `LOG-APP-005` |
| NA equivalent tail shows no comparable fraud elevation (EU-specificity check) | `PAY-METRIC-004` |
| Pre-event same-day EU buckets already within normal range (rules out pre-existing EU pattern) | `PAY-METRIC-005` |
| Fraud Operations' working (unconfirmed) assessment: mostly intended suppression | `dataset/fraud_rule_change.md` |
| Internal claim disputing this hypothesis's magnitude, later contradicted by data | `CHAT-002` |

### H4 — Stale CDN configuration

| Claim | Evidence |
|---|---|
| CDN cache TTL change applied 07:15 UTC, staged rollout | `CDN-001` |
| STALE cache responses, APAC (3 edges) and NA (1 edge) | `GW-API-002`, `GW-API-003` |
| No STALE responses in EU sample (control) | `GW-API-004` |
| CONFIG_MISMATCH errors concentrated in APAC/NA | `LOG-APP-006` |
| APAC customer reports concentrate on page/config symptoms | `CS-FEEDBACK-003` |

## Cross-cutting claims

| Claim | Evidence |
|---|---|
| Baseline (pre-incident) authorization rate ~97.1% all regions | `KPI-HOURLY-001`, `GW-API-001` |
| Regional incident-day KPI figures (NA/EU/APAC) | `KPI-HOURLY-002`, `KPI-HOURLY-003`, `KPI-HOURLY-004` |
| Global aggregate masks EU-specific severity | `KPI-HOURLY-005` |
| Campaign traffic increase, 10:00–16:00 UTC, NA/EU | `CAMPAIGN-001`, `KPI-HOURLY-006` |
| Campaign volume corroborated at raw-log level | `LOG-APP-009`, `GW-API-005` |
| Pre-campaign baseline window within the incident day | `GW-API-006` |
| Transaction-count shortfall estimate (~3,046), explicitly not a revenue figure | `KPI-HOURLY-001`–`004` |
| Premature request for a revenue figure, correctly declined | `CHAT-003` |
| Overconfident internal attribution of sole cause to the release | `CHAT-001` |
| Customer feedback spans all symptom categories, roughly even by region | `CS-FEEDBACK-001`–`006` |
| APAC log-coverage gap, 13:00–14:00 UTC | `LOG-APP-010` |
| Severity, escalation, roles, retention, and closure criteria | `PROC-001` |

## Full reverse index (evidence ID → citing document)

| Evidence ID | Cited in |
|---|---|
| `LOG-APP-001` | `orchestrator_analysis.md` |
| `LOG-APP-002` | `challenge_review.md`, `decision_matrix.md`, `orchestrator_analysis.md` |
| `LOG-APP-003` | `orchestrator_analysis.md` |
| `LOG-APP-004` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `LOG-APP-005` | `orchestrator_analysis.md` |
| `LOG-APP-006` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `LOG-APP-007` | `challenge_review.md`, `decision_matrix.md`, `orchestrator_analysis.md` |
| `LOG-APP-008` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `LOG-APP-009` | `orchestrator_analysis.md` |
| `LOG-APP-010` | `challenge_review.md`, `orchestrator_analysis.md` |
| `GW-API-001` | `orchestrator_analysis.md` |
| `GW-API-002` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `GW-API-003` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `GW-API-004` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `GW-API-005` | `orchestrator_analysis.md` |
| `GW-API-006` | `orchestrator_analysis.md` |
| `KPI-HOURLY-001` | `orchestrator_analysis.md` |
| `KPI-HOURLY-002` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `KPI-HOURLY-003` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `KPI-HOURLY-004` | `orchestrator_analysis.md` |
| `KPI-HOURLY-005` | `orchestrator_analysis.md` |
| `KPI-HOURLY-006` | `orchestrator_analysis.md` |
| `PAY-METRIC-001` | `challenge_review.md`, `decision_matrix.md`, `orchestrator_analysis.md` |
| `PAY-METRIC-002` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `PAY-METRIC-003` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `PAY-METRIC-004` | `orchestrator_analysis.md` |
| `PAY-METRIC-005` | `orchestrator_analysis.md` |
| `PAY-METRIC-006` | `orchestrator_analysis.md` |
| `PAY-METRIC-008` | `orchestrator_analysis.md` |
| `CS-FEEDBACK-001` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `CS-FEEDBACK-002` | `orchestrator_analysis.md` |
| `CS-FEEDBACK-003` | `challenge_review.md`, `orchestrator_analysis.md` |
| `CS-FEEDBACK-004` | `orchestrator_analysis.md` |
| `CS-FEEDBACK-005` | `orchestrator_analysis.md` |
| `CS-FEEDBACK-006` | `orchestrator_analysis.md` |
| `REL-001` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `CDN-001` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `FRAUD-001` | `decision_matrix.md`, `orchestrator_analysis.md` |
| `VENDOR-001` | `challenge_review.md`, `decision_matrix.md`, `orchestrator_analysis.md` |
| `CHAT-001` | `orchestrator_analysis.md` |
| `CHAT-002` | `orchestrator_analysis.md` |
| `CHAT-003` | `orchestrator_analysis.md` |
| `CAMPAIGN-001` | `orchestrator_analysis.md` |
| `HIST-001` | `orchestrator_analysis.md` |
| `PROC-001` | `decision_matrix.md`, `orchestrator_analysis.md` |

**Coverage: 45 / 45 manifest evidence IDs cited at least once.**

## Appendix — how this was generated

```python
import re, glob
from collections import defaultdict

pattern = re.compile(r'\b([A-Z]+(?:-[A-Z]+)*-[0-9]{3,4})\b')
citations = defaultdict(set)
for f in sorted(glob.glob("examples/*.md")):
    for m in pattern.findall(open(f).read()):
        citations[m].add(f)
```

`scripts/validate_examples.py` runs an equivalent extraction restricted
to known evidence-ID prefixes (to avoid false positives like decision
IDs `DEC-*` or the incident ID `INC-2026-0730-CHECKOUT`, which share the
same dash-number shape but are not evidence citations) and fails the
build if any citation does not resolve to `dataset/evidence_manifest.yaml`.
