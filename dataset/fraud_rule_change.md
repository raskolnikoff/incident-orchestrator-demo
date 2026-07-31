# Fraud Rule Change Record — FR-2026-118 (`FRAUD-001`)

> Synthetic data. Fictional fraud rule set for the OIOF demo dataset.

| Field | Value |
|---|---|
| Rule set ID | FR-2026-118 |
| Scope | Europe (EU) only |
| Deployed | 2026-07-30T09:30:00Z |
| Change owner | Fraud Operations |
| Approval | Fraud Operations Lead, per standing change authority for velocity-threshold tuning (does not require Risk & Governance sign-off below the defined blast-radius threshold — see `PROC-001`) |
| Related incident/ticket | Preceded by a pattern of suspected card-testing traffic observed in EU over the prior 72 hours (not included in this dataset) |

## Summary of change

FR-2026-118 tightens the velocity-based fraud check for EU transactions:
the maximum number of checkout attempts permitted from a single
device/session fingerprint within a rolling 10-minute window was reduced
from 8 to 4, and the fingerprint-similarity threshold used to correlate
related sessions was tightened.

This is a targeted response to a suspected card-testing pattern and was
not intended to affect legitimate repeat-purchase behavior.

## Fraud Operations assessment at time of writing

Post-deployment monitoring shows an increase in `DECLINE_FRAUD` outcomes
in EU (see `LOG-APP-004`, `PAY-METRIC-003`). Fraud Operations' working
assessment is that this increase is expected and largely attributable to
the intended suppression of card-testing traffic, but this has **not**
been separated from a possible false-positive rate increase against
legitimate customers (e.g. customers on shared networks, corporate VPNs,
or making rapid legitimate repeat purchases during the concurrent flash
sale). A false-positive analysis has not yet been performed.

## Explicitly not yet known

- What fraction of the EU `DECLINE_FRAUD` increase is card-testing
  suppression versus false positives against legitimate customers.
- Whether the concurrent EU marketing campaign (`CAMPAIGN-001`), which
  independently increases rapid repeat-checkout attempts from legitimate
  customers, interacts with the new velocity threshold to produce more
  false positives than would occur outside a campaign window.
- Whether reverting the rule change would meaningfully change the
  authorization-success trend in the post-16:00 UTC window
  (`PAY-METRIC-003`), where the provider-timeout signal has receded but the
  fraud-decline elevation persists.
