# Incident Brief — INC-2026-0730-CHECKOUT

> **Synthetic data notice.** Northstar Commerce, all systems, people,
> incidents, and communications referenced in this repository are entirely
> fictional. This brief was authored for the OIOF demo dataset and does not
> describe a real event.

| Field | Value |
|---|---|
| Incident ID | `INC-2026-0730-CHECKOUT` |
| Title | Intermittent Checkout Authorization Degradation |
| Detected | 2026-07-30T11:40:00Z (automated alert: checkout authorization success rate below threshold) |
| Status at time of writing | Investigating — root cause not established |
| Regions affected | North America (NA), Europe (EU), Asia Pacific (APAC) — severity differs by region |
| Systems in scope | Web storefront, mobile application, Checkout API, Payment Orchestration Service, Fraud Decision Service, Promotion Service, CDN, observability platform, customer-support platform, third-party payment provider(s) |
| Declared severity | SEV-2 (provisional — see `PROC-001`) |

## Summary of observed symptoms

Checkout authorization success rate declined on the incident day
(2026-07-30) relative to the prior-day baseline in every region, but by
different magnitudes and with different accompanying symptoms:

- **North America** — authorization success rate fell from a ~97.1%
  baseline to a low of ~87.9% during 11:00–16:00 UTC. Customer reports
  concentrate on declined-card messages.
- **Europe** — the largest regional decline, from a ~97.1% baseline to a
  low of ~85.4% during the same window, with the drop persisting (in a
  smaller form) well after 16:00 UTC. Customer reports include fraud-like
  decline messaging on cards customers describe as in normal use.
- **Asia Pacific** — a comparatively smaller decline, from ~97.1% to a low
  of ~94.3%. Customer reports concentrate on checkout page/configuration
  errors rather than declined payments.

## Changes active in the relevant window

Four independent changes or events were active in or around the incident
window, any combination of which may be contributing:

1. A checkout-api release (`3.12.0`) was deployed — canary in NA at 08:00
   UTC, full fleet at 09:00 UTC. See `dataset/release_notes.md` (`REL-001`).
2. A CDN cache-policy change for the `/api/checkout/config` endpoint was
   applied at 07:15 UTC to a subset of edge nodes. See
   `dataset/release_notes.md` (`CDN-001`).
3. A fraud rule set update (`FR-2026-118`) was deployed to EU only at 09:30
   UTC. See `dataset/fraud_rule_change.md` (`FRAUD-001`).
4. The "Summer Flash Sale" marketing campaign increased traffic in NA and
   EU from 10:00–16:00 UTC. See `dataset/campaign_schedule.csv`
   (`CAMPAIGN-001`).

The third-party payment provider that handles the majority of NA and
essentially all EU transactions in this dataset (`ProviderAlpha`) has
separately acknowledged, in vague terms, "elevated processing times for a
subset of transactions" — see `dataset/vendor_email.md` (`VENDOR-001`).

## Why this is not a single-cause incident

Every one of the four changes above overlaps in time with at least part of
the observed degradation, and none of them individually explains the full
pattern:

- The provider-timeout signal (`LOG-APP-002`, `PAY-METRIC-001`) is
  concentrated in NA and EU and fades by ~15:00 UTC, but EU's decline
  persists past that point.
- The EU fraud-rule signal (`LOG-APP-004`, `PAY-METRIC-003`) explains part
  of the EU-specific, later-persisting decline, but does not touch NA or
  APAC.
- The CDN staleness signal (`GW-API-002`, `GW-API-003`, `LOG-APP-006`) is
  concentrated in APAC (and a smaller NA subset), where the authorization
  decline is smallest — it looks more related to page/config errors than
  to authorization decline specifically.
- The campaign explains a real increase in traffic volume
  (`KPI-HOURLY-006`) in NA and EU, but volume increase alone does not
  arithmetically account for the authorization **rate** decline — rate and
  volume are different things, and conflating them is a common analysis
  error this dataset is designed to expose.
- Application-version data (`LOG-APP-007` vs `LOG-APP-008`) shows an
  elevated checkout-retry pattern on the new release, independent of
  region, which could itself be amplifying load on `ProviderAlpha` rather
  than being a purely separate cause.

See `dataset/evidence_manifest.yaml` for the full evidence catalog and
`examples/orchestrator_analysis.md` for an illustrative analysis that
works through this ambiguity using the required
fact/inference/hypothesis/contradiction structure.

## Known data-quality caveats

- APAC application-log coverage for `checkout-api` is anomalously sparse
  during 13:00–14:00 UTC (`LOG-APP-010`) — a suspected log-pipeline
  sampling gap, not evidence of a quiet period.
- Customer feedback volume is similar across all three regions
  (13–14 reports each) despite substantially different technical failure
  signatures, so feedback volume alone is a poor proxy for technical
  severity in this dataset — see `dataset/customer_feedback.csv`.
- No order-value or revenue data is included in this dataset. Any revenue
  or financial-impact figure would have to come from a system outside this
  evidence set; it must not be inferred from authorization counts alone.
