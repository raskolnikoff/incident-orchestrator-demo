# Illustrative Orchestrator Analysis — INC-2026-0730-CHECKOUT

> **Illustrative example generated for this synthetic scenario.** This
> document shows the kind of output `prompts/01_incident_orchestrator.md`
> is designed to produce when run against `dataset/`. It was authored to
> demonstrate the framework's required structure and evidence-citation
> discipline against this repository's fictional dataset. It is not a
> claim that any particular model run produced this exact text. All
> figures below were computed directly from the files in `dataset/` and
> can be reproduced with `python3 scripts/generate_dataset_summary.py`.

---

## 1. Executive incident summary

On 2026-07-30, Northstar Commerce's checkout authorization success rate
declined in all three regions relative to the prior-day baseline, most
severely in Europe. Four independent changes or events were active in the
same window: a checkout-api release, a CDN cache-policy change, an EU
fraud-rule update, and a marketing campaign traffic increase, plus a
third-party payment provider's own vague acknowledgment of "elevated
processing times." No single one of these fully explains the observed
pattern across all three regions; more than one is likely contributing at
once, and the evidence available does not yet support ranking them with
high confidence. This document lays out what is confirmed, what is
inferred, what remains contested, and what decisions are pending human
approval.

## 2. Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 2026-07-29, all day | Baseline operating day, ~97.1% authorization success rate in every region | `KPI-HOURLY-001` |
| 07:15 | CDN cache TTL change applied to `/api/checkout/config`, staged edge-by-edge | `CDN-001` |
| 08:00 | checkout-api 3.12.0 canary begins in NA | `REL-001` |
| 09:00 | checkout-api 3.12.0 rolled out fleet-wide (NA + EU + APAC) | `REL-001` |
| 09:30 | Fraud rule set FR-2026-118 deployed to EU only | `FRAUD-001` |
| 10:00 | "Summer Flash Sale" campaign begins sending in NA and EU | `CAMPAIGN-001` |
| ~10:00–16:00 | Session volume up ~35–65% in NA/EU versus same hours on the baseline day | `KPI-HOURLY-006` |
| 11:05–14:43 | Elevated TIMEOUT/NETWORK_ERROR entries for ProviderAlpha-routed payment-orchestration requests, NA and EU | `LOG-APP-002` |
| 11:40 | Incident detected via automated authorization-rate alert | `dataset/incident_brief.md` |
| from 07:15 onward | CONFIG_MISMATCH errors and STALE cache responses observed, concentrated in APAC, smaller subset in NA | `GW-API-002`, `GW-API-003`, `LOG-APP-006` |
| from 09:30 onward | Elevated DECLINE_FRAUD entries, EU only | `LOG-APP-004` |
| ~mid-morning | ProviderAlpha status desk acknowledges "elevated processing times for a subset of transactions," scope unconfirmed | `VENDOR-001` |
| throughout the day | 40 customer reports filed across all three regions with varying symptom categories | `CS-FEEDBACK-001` … `CS-FEEDBACK-006` |
| ~15:00 onward | Provider-timeout rate recedes toward baseline (see `PAY-METRIC-003` vs `PAY-METRIC-001`) | `PAY-METRIC-001`, `PAY-METRIC-003` |

## 3. Evidence inventory

| Source type | Files | Evidence IDs |
|---|---|---|
| Application logs | `application_logs.jsonl` | `LOG-APP-001`…`LOG-APP-010` |
| Gateway / CDN logs | `api_gateway_logs.csv` | `GW-API-001`…`GW-API-006` |
| Regional KPIs | `hourly_kpis.csv` | `KPI-HOURLY-001`…`KPI-HOURLY-006` |
| Payment metrics | `payment_metrics.csv` | `PAY-METRIC-001`…`PAY-METRIC-006`, `PAY-METRIC-008` |
| Customer feedback | `customer_feedback.csv` | `CS-FEEDBACK-001`…`CS-FEEDBACK-006` |
| Change records | `release_notes.md`, `fraud_rule_change.md` | `REL-001`, `CDN-001`, `FRAUD-001` |
| Vendor communication | `vendor_email.md` | `VENDOR-001` |
| Internal chat | `internal_chat.md` | `CHAT-001`, `CHAT-002`, `CHAT-003` |
| Marketing schedule | `campaign_schedule.csv` | `CAMPAIGN-001` |
| Historical context | `incident_history.md` | `HIST-001` |
| Procedure | `operating_procedure.md` | `PROC-001` |

Full catalog with descriptions, reliability ratings, and known
limitations: `dataset/evidence_manifest.yaml`.

## 4. Fact / inference / assumption table

| # | Statement | Type | Evidence |
|---|---|---|---|
| 1 | Baseline (2026-07-29) authorization success rate was ~97.1% in NA, EU, and APAC alike | Fact | `KPI-HOURLY-001` |
| 2 | Incident-day authorization success rate fell to a low of ~87.9% in NA, ~85.4% in EU, ~94.3% in APAC (all during 11:00–16:00 UTC) | Fact | `KPI-HOURLY-002`, `KPI-HOURLY-003`, `KPI-HOURLY-004` |
| 3 | Requests routed to ProviderAlpha in NA/EU during 10:00–16:00 UTC show a 17.1% timeout rate (316/1,853), versus a 0% timeout rate for ProviderBeta-routed requests in the same period | Fact | `PAY-METRIC-001`, `PAY-METRIC-002` (corroborated at the application-log level by `LOG-APP-003`) |
| 4 | EU fraud-decline rate in the post-16:00 tail (after provider timeouts recede to 1.5%) is 13.3% (109/822), well above the 2–5% baseline range seen elsewhere | Fact | `PAY-METRIC-003` |
| 5 | checkout-api 3.12.0 shows a higher rate of `CHECKOUT_RETRY_EXCEEDED` entries than 3.11.4 in the same window | Fact | `LOG-APP-007`, `LOG-APP-008` |
| 6 | A subset of APAC (3 edge nodes) and NA (1 edge node) CDN edges served `cache_status=STALE` responses for `/api/checkout/config` after 07:15 UTC; no EU edges in the sample did | Fact | `GW-API-002`, `GW-API-003`, `GW-API-004` |
| 7 | All four of the release, CDN change, fraud-rule change, and campaign start were active within roughly the same two-hour window on the incident day | Fact | `REL-001`, `CDN-001`, `FRAUD-001`, `CAMPAIGN-001` |
| 8 | The new release's more aggressive retry policy may be amplifying load on an already-degraded ProviderAlpha, worsening the apparent timeout rate | Evidence-supported inference | `LOG-APP-007` (retry elevation) combined with `LOG-APP-002` (timeout timing). The two logs are not request-level joined in this dataset, so this is a plausible mechanism, not a confirmed link |
| 9 | The EU decline that persists past 16:00 UTC (when provider timeouts have receded) is attributable at least in part to the fraud-rule change rather than to the payment provider | Evidence-supported inference | `PAY-METRIC-003` shows timeouts near baseline (1.5%) while fraud declines remain elevated (13.3%) in the same window |
| 10 | "The checkout-api release is obviously the cause" | Internal assumption (not verified) | `CHAT-001`, stated before comparing against the fraud-rule and CDN signals; contradicted in part by finding #9 |
| 11 | "The fraud rule can't be moving the regional numbers that much" | Internal assumption (not verified) | `CHAT-002`, contradicted by finding #4 |
| 12 | ProviderAlpha's elevated processing times are the sole cause of the regional decline | Not supported | `VENDOR-001` does not confirm scope, timing, or exclusivity of cause; treating it as sole-cause confirmation would overstate what the vendor said |

## 5. Contradiction register

| # | Contradiction | Evidence in tension | Resolution status |
|---|---|---|---|
| 1 | `CHAT-001` asserts the release is "obviously" the sole cause and that "we didn't change anything else that matters," but three other changes were active in the same window | `CHAT-001` vs. `CDN-001`, `FRAUD-001`, `CAMPAIGN-001` | Unresolved. Flagged as overconfident, not adopted as fact |
| 2 | `CHAT-002` asserts the EU fraud-rule change "can't be moving the regional numbers that much," but the isolated post-16:00 fraud-decline rate (13.3%) is well above baseline | `CHAT-002` vs. `PAY-METRIC-003` | Unresolved. Flagged as unverified before the isolating analysis was available |
| 3 | Customer feedback volume is nearly identical across regions (NA 13, EU 13, APAC 14 across all symptom categories) despite EU showing the largest technical decline and APAC the smallest | `CS-FEEDBACK-*` totals vs. `KPI-HOURLY-002/003/004` | Unresolved. Feedback volume should not be used as a stand-in for technical severity in this dataset |
| 4 | Absence of application-log errors for APAC checkout-api during 13:00–14:00 UTC could be misread as a quiet, healthy hour, but the same window has anomalously sparse and explicitly sampled log coverage | `LOG-APP-010` | Resolved by treating the window as data-quality-limited, not as evidence of health |
| 5 | A single global authorization-rate figure (`KPI-HOURLY-005`) would understate the EU-specific severity, since APAC's smaller decline pulls the blended number toward NA's less-severe figure | `KPI-HOURLY-005` (derived) vs. `KPI-HOURLY-003` | Resolved by reporting per-region figures rather than the global blend as the primary metric |

## 6. Competing hypotheses

### H1 — Payment-provider (ProviderAlpha) latency/timeout degradation

- **Supporting:** 17.1% timeout rate for ProviderAlpha-routed NA/EU
  traffic during 10:00–16:00 UTC versus 0% for ProviderBeta in the same
  window (`PAY-METRIC-001`, `PAY-METRIC-002`); concentrated `TIMEOUT`/
  `NETWORK_ERROR` entries in the same window (`LOG-APP-002`); vendor's own
  (vague) acknowledgment of elevated processing times (`VENDOR-001`);
  precedent: two of the last three related incidents were
  provider-side (`HIST-001`).
- **Opposing:** The timeout rate recedes toward baseline by ~15:00 UTC
  (`PAY-METRIC-003` shows 1.5% in the post-16:00 tail), but EU's
  authorization decline persists past that point. A pure provider
  explanation does not account for the EU tail. APAC, where
  ProviderBeta is dominant, shows the smallest decline of the three
  regions, which is directionally consistent with H1 but does not by
  itself rule out other contributing causes there.
- **Confidence: medium-high** for explaining the 10:00–16:00 window in
  NA/EU specifically; **low** for explaining the full incident,
  especially the EU post-16:00 tail and any part of the APAC pattern.

### H2 — Regression introduced by the checkout-api 3.12.0 release

- **Supporting:** Elevated `CHECKOUT_RETRY_EXCEEDED` rate on 3.12.0
  versus 3.11.4 in the same window (`LOG-APP-007` vs. `LOG-APP-008`);
  release timing (09:00 UTC fleet-wide) precedes the observed decline
  onset; a more aggressive retry policy is a plausible amplifier of
  downstream provider load (see finding #8 above).
- **Opposing:** The retry-rate elevation is present across all three
  regions roughly equally, but the authorization-rate decline is not:
  APAC shows the smallest decline despite carrying the same release. If
  the release alone were the dominant cause, a more uniform regional
  effect would be expected. No request-level trace in this dataset
  directly links a specific retry-exceeded event to a specific
  provider timeout.
- **Confidence: low-medium**. Plausible contributing/amplifying factor,
  not established as a standalone cause of the regional pattern.

### H3 — Fraud-rule configuration causing false declines (EU)

- **Supporting:** EU-only fraud-decline rate of 13.3% in the isolated
  post-16:00 window, well above the 2–5% baseline range
  (`PAY-METRIC-003`); rule deployed at 09:30 UTC, shortly before the
  broader decline was detected (`FRAUD-001`); effect is EU-specific,
  matching the rule's EU-only scope, and explains why EU's decline is
  both the largest and the most persistent of the three regions.
- **Supporting (regional isolation):** The equivalent post-16:00
  ProviderAlpha tail in NA (`PAY-METRIC-004`) does not show a comparable
  fraud-decline elevation, which supports reading the EU effect as
  specific to the EU-only rule change rather than a provider-wide
  pattern that happens to overlap with EU.
- **Opposing:** Fraud Operations' working assessment is that the
  increase is largely intended card-testing suppression
  (`fraud_rule_change.md`), and no false-positive analysis has been
  performed to separate legitimate customers from suppressed fraud
  attempts: the 13.3% figure cannot currently be split into "correctly
  blocked" versus "false decline." The concurrent EU campaign
  (`CAMPAIGN-001`) independently increases rapid repeat-checkout
  behavior that the new velocity threshold is more likely to flag,
  which is a confound, not yet controlled for. Same-day pre-event
  buckets (`PAY-METRIC-005`, 00:00–08:00 UTC) show EU fraud-decline
  rates already within the normal baseline range before the rule
  change, which rules out a pre-existing EU-specific fraud pattern as
  an alternative explanation.
- **Confidence: medium** that the rule change is contributing materially
  to the EU decline; **low** on what fraction of that contribution is a
  false positive versus intended behavior.

### H4 — Stale or inconsistent configuration from CDN caching

- **Supporting:** `cache_status=STALE` responses observed on APAC (3
  edge nodes) and NA (1 edge node) after the 07:15 UTC change, absent
  in the EU sample (`GW-API-002`, `GW-API-003`, `GW-API-004`);
  `CONFIG_MISMATCH` errors concentrated in the same regions
  (`LOG-APP-006`); APAC customer reports concentrate on page/config
  errors rather than declined payments (`CS-FEEDBACK-003`), a
  symptom pattern more consistent with a config/rendering issue than a
  payment-authorization issue.
- **Opposing:** APAC shows the smallest authorization-rate decline of
  the three regions, suggesting this pattern is more closely tied to
  page/config errors and promo-display issues than to payment
  authorization specifically. The affected edge-node sample is small (3
  of an unknown total APAC edge count, 1 of an unknown total NA count):
  coverage of the full edge fleet is missing evidence.
- **Confidence: medium** that stale config is contributing to
  config/rendering errors in APAC and a smaller NA subset; **low** that
  it is a material driver of the authorization-rate decline specifically.

**No hypothesis is presented as conclusively proven, and more than one
almost certainly contributed simultaneously in different regions.**

## 7. Confidence levels with rationale

| Hypothesis | Confidence | Rationale |
|---|---|---|
| H1 (provider) | Medium-high for the 10:00–16:00 NA/EU window; low overall | Strong isolated-metric contrast (17.1% vs 0%), but doesn't explain the EU tail or APAC pattern alone |
| H2 (release regression) | Low-medium | Consistent retry-rate elevation, but no request-level causal link and no regional pattern match |
| H3 (fraud rule) | Medium for EU contribution; low on false-positive fraction | Strong isolated EU-only signal, but not yet separated from intended card-testing suppression |
| H4 (CDN staleness) | Medium for config/rendering errors; low for authorization-rate impact | Strong cache-status contrast, but affected region (APAC) shows the mildest authorization decline |

## 8. Customer-impact assessment

Forty customer reports were filed across all three regions during the
incident day, spanning declined-payment symptoms (NA-heavy,
`CS-FEEDBACK-001`), fraud-like decline messaging (EU-heavy,
`CS-FEEDBACK-002`), config/page-error symptoms (APAC-heavy,
`CS-FEEDBACK-003`), slow-checkout/timeout symptoms (cross-region,
`CS-FEEDBACK-004`), five delayed reports filed 6–18 hours after the
event (`CS-FEEDBACK-005`), and four reports too ambiguous to categorize
(`CS-FEEDBACK-006`). Report volume is similar across regions (13–14
each) and should not be read as a severity ranking: it does not track
the technical KPI decline, which was largest in EU and smallest in
APAC (see Contradiction #3). No customer-satisfaction score or support
resolution-time data is present in this evidence set; both would be
needed for a fuller customer-impact picture.

## 9. Business-impact assessment

**What can be said:** comparing incident-day authorized-transaction
counts against what would be expected at the prior-day baseline
authorization rate yields an estimated shortfall of approximately 1,091
transactions in NA, 1,602 in EU, and 354 in APAC: roughly 3,046
transactions total, of which about 2,272 (75%) fall within the
11:00–16:00 UTC window where the provider-stress signal is strongest.
This is a **transaction-count estimate**, computed directly from
`KPI-HOURLY-001` through `KPI-HOURLY-004`. The traffic increase behind
part of this picture is independently corroborated at the raw-log level
by general storefront/mobile-app traffic (`LOG-APP-009`) and general
checkout-api gateway volume (`GW-API-005`) during the campaign window,
consistent with `KPI-HOURLY-006`.

**What cannot be said:** this dataset contains no order-value or revenue
data. Multiplying the transaction shortfall by any assumed average order
value would be an invented number, not a finding, and is explicitly out
of scope for this analysis. Any revenue-impact figure must come from
finance/analytics systems outside this evidence set (see `CHAT-003` for
an example of exactly this kind of premature request, and why it was not
answered with a fabricated figure).

## 10. Data-quality limitations

- APAC `checkout-api` log coverage for 13:00–14:00 UTC is sparse and
  explicitly sampled (`LOG-APP-010`): absence of errors there is
  inconclusive, not evidence of a healthy hour.
- CDN edge-node coverage in the gateway-log sample is partial: 3 of an
  unknown total APAC edges, 1 of an unknown total NA edges
  (`GW-API-002`, `GW-API-003`): the true blast radius of stale
  configuration is not established.
- The fraud-decision control group used to establish the ~2–5% baseline
  fraud-decline range (EU pre-09:30, plus NA and APAC across the full
  day) is `LOG-APP-005`; it is a moderate-sized sample and should be
  treated as indicative rather than exhaustive.
- Five customer reports were filed 6–18 hours after the estimated event
  (`CS-FEEDBACK-005`); timing and symptom detail in these should be
  treated as approximate.
- Region-level KPI aggregation (`KPI-HOURLY-*`) masks payment-method-
  and provider-level variation; the payment-method-level view
  (`PAY-METRIC-*`) is required to see the ProviderAlpha/ProviderBeta
  contrast at all.
- No order-value, revenue, or customer-support resolution-time data is
  present in this evidence set.
- `VENDOR-001` is deliberately non-specific about scope and timing and
  should not be over-read as corroboration of any particular hypothesis.

## 11. Investigation workstreams

| Workstream | Owner (per `PROC-001`) | Goal |
|---|---|---|
| Provider timeout root cause | Payment Operations Lead | Get ProviderAlpha to confirm affected window/region/method; request their internal incident ticket status |
| Release regression analysis | Checkout Engineering Lead | Request-level trace linking `CHECKOUT_RETRY_EXCEEDED` events to downstream provider calls, to test the H1/H2 interaction hypothesis |
| Fraud false-positive analysis | Fraud Operations Lead | Separate the 13.3% EU post-16:00 decline rate into card-testing-suppression vs. legitimate-customer false positives |
| CDN blast-radius mapping | SRE Lead | Determine full edge-node population affected by the CDN change, beyond the sampled subset in `GW-API-002`/`GW-API-003` |
| Customer-impact triangulation | Customer Support Lead | Cross-reference support-ticket resolution data (not in this evidence set) against `CS-FEEDBACK-*` symptom categories |
| **Process workstream** | Incident Commander | Determine why the checkout-api release (`REL-001`), the CDN cache change (`CDN-001`), and the EU fraud-rule change (`FRAUD-001`) were all scheduled inside the 24-hour change-freeze window ahead of the flash-sale campaign (`CAMPAIGN-001`, 45% planned NA uplift) defined in `PROC-001` §3a, apparently without a cross-team freeze review. This is independent of which hypothesis turns out to be the dominant technical cause; it is a coordination-process finding either way. |

## 12. Immediate containment options

These are options for human evaluation, not recommendations to act
unilaterally; see Section 13 and `examples/decision_matrix.md`.

- Reroute a portion of ProviderAlpha traffic to ProviderBeta in NA/EU as
  a load-shedding test (reversible; requires Payment Operations Lead
  approval + settlement/reconciliation review).
- Roll back checkout-api to 3.11.4 (reversible; requires Checkout
  Engineering Lead + SRE Lead approval).
- Temporarily relax or revert the EU fraud rule velocity threshold
  pending false-positive analysis (reversible; requires Fraud Operations
  Lead approval).
- Force-purge the affected CDN edge caches for `/api/checkout/config`
  (reversible; requires SRE Lead approval, broader purge requires
  Incident Commander concurrence per `PROC-001`).
- Continue monitoring without intervention while investigation
  continues (always a valid option, see Decision Matrix).

## 13. Decision Matrix

See `examples/decision_matrix.md` for the full matrix. Summary of open
decisions:

| Decision ID | Decision required | Recommended option | Owner |
|---|---|---|---|
| `DEC-001` | Roll back checkout-api 3.12.0? | Hold rollback pending request-level trace; re-evaluate in 2 hours | Checkout Engineering Lead |
| `DEC-002` | Disable/revert EU fraud rule FR-2026-118? | Run false-positive spot-check before deciding; do not revert blind | Fraud Operations Lead |
| `DEC-003` | Reroute/bypass ProviderAlpha in NA/EU? | Begin a limited (10%) reroute test to ProviderBeta while monitoring | Payment Operations Lead |
| `DEC-004` | Purge CDN cache for `/api/checkout/config`? | Purge the 4 identified stale edge nodes now (low risk, contained scope) | SRE Lead |
| `DEC-005` | Issue customer communication? | Prepare a general-status message; hold specific-cause language until H1/H3 confidence increases | Communications Lead |
| `DEC-006` | Confirm/maintain SEV-2 declaration? | Maintain SEV-2; re-evaluate at next checkpoint | Incident Commander |

## 14. Human approval gates

Per `PROC-001`: `DEC-001` requires Checkout Engineering Lead approval and
SRE Lead concurrence. `DEC-002` requires Fraud Operations Lead approval
(within blast-radius threshold; escalates to Risk & Governance if the
scope grows). `DEC-003` requires Payment Operations Lead approval and
Incident Commander concurrence. `DEC-004` requires SRE Lead approval
(escalates to Incident Commander concurrence if scope expands beyond the
4 identified nodes). `DEC-005` requires Communications Lead approval and
Product Owner concurrence. `DEC-006` is an Incident Commander decision.
No decision in this matrix may be executed on the basis of this document
alone.

## 15. Communication drafts

**Status: draft, pending Communications Lead and Product Owner
approval, not sent.**

> *Internal stakeholder update (draft):* "We're investigating a checkout
> authorization issue affecting a subset of customers since approximately
> 11:40 UTC, most noticeable in Europe and North America. Multiple
> contributing factors are under investigation, including a payment
> processing partner and a recent configuration change. No single root
> cause has been confirmed yet. We'll share an update within two hours or
> sooner if the picture changes."

> *Customer-facing status message (draft, if a public status page update
> is approved):* "Some customers may experience delays or errors
> completing checkout. Our team is actively investigating. We apologize
> for the inconvenience and will update this page as we learn more."

Neither draft asserts a root cause, a resolution time, or a revenue/
compensation commitment, consistent with the confidence levels in
Sections 6–7.

## 16. Audit and traceability table

| Section | Evidence IDs cited |
|---|---|
| 2. Timeline | `KPI-HOURLY-001`, `CDN-001`, `REL-001`, `FRAUD-001`, `CAMPAIGN-001`, `KPI-HOURLY-006`, `LOG-APP-002`, `GW-API-002`, `GW-API-003`, `LOG-APP-006`, `LOG-APP-004`, `VENDOR-001`, `PAY-METRIC-001`, `PAY-METRIC-003` |
| 4. Fact/inference/assumption table | `KPI-HOURLY-001`–`004`, `PAY-METRIC-001`–`003`, `LOG-APP-002`, `LOG-APP-007`, `LOG-APP-008`, `GW-API-002`–`004`, `REL-001`, `CDN-001`, `FRAUD-001`, `CAMPAIGN-001`, `CHAT-001`, `CHAT-002`, `VENDOR-001` |
| 5. Contradiction register | `CHAT-001`, `CHAT-002`, `CDN-001`, `FRAUD-001`, `CAMPAIGN-001`, `PAY-METRIC-003`, `CS-FEEDBACK-001`–`006`, `KPI-HOURLY-002`–`005`, `LOG-APP-010` |
| 6–7. Hypotheses & confidence | `PAY-METRIC-001`–`004`, `LOG-APP-002`, `LOG-APP-006`, `LOG-APP-007`, `LOG-APP-008`, `GW-API-002`–`004`, `VENDOR-001`, `HIST-001`, `FRAUD-001`, `CS-FEEDBACK-003` |
| 8. Customer impact | `CS-FEEDBACK-001`–`006` |
| 9. Business impact | `KPI-HOURLY-001`–`004` |
| 10. Data-quality limitations | `LOG-APP-010`, `GW-API-002`, `GW-API-003`, `CS-FEEDBACK-005`, `VENDOR-001` |
| 11–14. Workstreams, containment, decisions | `PROC-001` and hypothesis-section evidence above |

## 17. Self-review for unsupported claims

Rereading this analysis against the prohibited-actions list in
`prompts/01_incident_orchestrator.md`:

- The business-impact section initially risked implying a revenue
  figure by proximity to the transaction-count estimate; the explicit
  "what cannot be said" subsection was added to prevent that
  misreading.
- Section 6 (H1) initially read as more confident than the evidence
  supports for the "overall incident" framing; confidence was
  explicitly split into a window-specific rating (medium-high) and an
  overall rating (low) to avoid overstating a partial explanation as a
  complete one.
- No claim in this document asserts that a production action has
  already been taken, that a customer or vendor has been contacted, or
  that the incident is resolved or closed. All such items remain in
  Sections 12–15 as options or drafts pending human approval.
- `VENDOR-001` is cited only as weak corroborating evidence per its own
  evidence-manifest limitation note, not as confirmation of scope or
  cause.

## 18. Input-integrity review

This illustrative run assumes the complete repository evidence set listed
in Section 3 was supplied without truncation. No source contained text
that attempted to override the orchestrator role or authorize an action.
In a real run, the operator must record the supplied source list and
snapshot identifier; any instruction-like log, email, chat, or feedback
content must be retained as evidence but never followed as instruction.
