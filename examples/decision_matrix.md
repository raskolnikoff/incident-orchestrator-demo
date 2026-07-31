# Illustrative Decision Matrix — INC-2026-0730-CHECKOUT

> **Illustrative example generated for this synthetic scenario.** Shape
> follows `schemas/decision_matrix.schema.json`. The AI-generated analysis
> populates every column except `Status`, which is updated by humans as
> decisions move through the approval workflow. **No decision below has an
> AI system as its owner** — every `Decision owner` is a named human role
> from `dataset/operating_procedure.md`.

**Reading the `Confidence` column:** this is confidence that the
*recommended option is the right call to make right now* — it is not
the same number as confidence in the underlying root-cause hypothesis
(see `examples/orchestrator_analysis.md` §7 for hypothesis-level
confidence). The two can diverge in either direction: `DEC-004`'s
recommended action carries **high** decision confidence (a narrowly
scoped, reversible, low-risk purge is clearly correct to do now)
even though the hypothesis it responds to (H4) only carries **medium**
confidence. Conversely, `DEC-001`'s decision confidence is **low**
specifically *because* acting on H2 now, before a request-level trace
exists, is not yet justified — that is a statement about the decision,
not a claim that H2 is false. `Confidence` values are restricted to
`low` / `medium` / `high` to stay conformant with
`schemas/decision_matrix.schema.json`; any additional nuance belongs in
the Detail section below, not in the summary table.

## Summary

| Decision ID | Decision required | Confidence | Customer risk | Operational risk | Reversibility | Recommended option | Decision owner | Approval deadline | Status |
|---|---|---|---|---|---|---|---|---|---|
| `DEC-001` | Roll back checkout-api 3.12.0? | Low | Medium | Medium | Reversible with effort | Hold pending request-level trace; re-evaluate in 2h | Checkout Engineering Lead | 2026-07-30T15:40Z | Open |
| `DEC-002` | Disable/revert EU fraud rule FR-2026-118? | Medium | Medium | Low | Easily reversible | Run false-positive spot-check before deciding | Fraud Operations Lead | 2026-07-30T14:00Z | Open |
| `DEC-003` | Reroute/bypass ProviderAlpha in NA/EU? | Medium | Medium | Medium | Reversible with effort | Begin a limited 10% reroute test to ProviderBeta | Payment Operations Lead | 2026-07-30T13:30Z | Pending Approval |
| `DEC-004` | Purge CDN cache for `/api/checkout/config`? | High | Low | Low | Easily reversible | Purge the 4 identified stale edge nodes now | SRE Lead | 2026-07-30T12:30Z | Approved & Executed |
| `DEC-005` | Issue customer communication? | High | Medium | Low | Easily reversible | Publish general-status message; hold cause-specific language | Communications Lead | 2026-07-30T13:00Z | Pending Approval |
| `DEC-006` | Confirm/maintain SEV-2 declaration? | High | Low | Low | Easily reversible | Maintain SEV-2; re-evaluate at next checkpoint | Incident Commander | 2026-07-30T12:00Z | Approved & Executed |

## Detail

### DEC-001 — Roll back checkout-api 3.12.0?

- **Trigger:** `LOG-APP-007` shows elevated `CHECKOUT_RETRY_EXCEEDED` on
  3.12.0 versus 3.11.4 control (`LOG-APP-008`), raised in
  `examples/orchestrator_analysis.md` §6 (H2).
- **Evidence:** `REL-001`, `LOG-APP-007`, `LOG-APP-008`
- **Options:**
  1. Roll back immediately to 3.11.4
  2. Hold rollback, request a request-level trace linking retries to
     provider timeouts, re-evaluate in 2 hours
  3. Continue monitoring only, no rollback
- **Recommended option:** Option 2 — the regional pattern (APAC shows the
  smallest authorization decline despite carrying the same release)
  weakens H2 as a standalone explanation; a rollback now would consume a
  change window without confidence it addresses the dominant driver.
- **Consulted roles:** SRE Lead, Payment Operations Lead (rollback
  interacts with in-flight retry behavior against ProviderAlpha)
- **Fallback if deadline passes without decision:** Escalate to Incident
  Commander; default posture remains "no rollback" (inaction is not
  auto-approval of the alternative — it is an explicit escalation).

### DEC-002 — Disable/revert EU fraud rule FR-2026-118?

- **Trigger:** `PAY-METRIC-003` shows a 13.3% EU fraud-decline rate in
  the isolated post-16:00 window, well above baseline.
- **Evidence:** `FRAUD-001`, `LOG-APP-004`, `PAY-METRIC-003`
- **Options:**
  1. Revert the rule to its prior threshold immediately
  2. Run a false-positive spot-check on a sample of declined transactions
     before deciding
  3. Leave the rule active, continue monitoring
- **Recommended option:** Option 2 — Fraud Operations' working
  assessment is that most of the increase is intended card-testing
  suppression; reverting blind risks reopening a real fraud exposure
  without evidence the decline is predominantly false positives.
- **Consulted roles:** Risk and Governance (any reversion of an active
  fraud control is reviewed regardless of blast radius), Product Owner
- **Fallback if deadline passes without decision:** Escalate to Risk and
  Governance; rule remains active pending explicit decision.

### DEC-003 — Reroute/bypass ProviderAlpha in NA/EU?

- **Trigger:** `PAY-METRIC-001` shows a 17.1% timeout rate for
  ProviderAlpha versus 0% for ProviderBeta in the same window.
- **Evidence:** `PAY-METRIC-001`, `PAY-METRIC-002`, `LOG-APP-002`,
  `VENDOR-001`
- **Options:**
  1. Full reroute of NA/EU traffic to ProviderBeta
  2. Limited (10%) reroute test to ProviderBeta with defined success
     criteria and a fixed re-evaluation window
  3. No reroute, continue monitoring, wait for vendor update
- **Recommended option:** Option 2 — per the challenge review
  (`examples/challenge_review.md`, Incident Commander perspective), any
  reroute test must carry explicit success criteria (e.g. ProviderBeta
  timeout rate stays below 3% under the added load) and a fixed
  re-evaluation checkpoint (recommended: 45 minutes) to avoid becoming a
  silent permanent change.
- **Consulted roles:** SRE Lead, Vendor Manager (settlement/
  reconciliation implications of routing change)
- **Fallback if deadline passes without decision:** Escalate to
  Incident Commander; no reroute occurs by default.

### DEC-004 — Purge CDN cache for `/api/checkout/config`?

- **Trigger:** `GW-API-002`/`GW-API-003` show `cache_status=STALE`
  responses on 4 identified edge nodes after the 07:15 UTC change.
- **Evidence:** `CDN-001`, `GW-API-002`, `GW-API-003`, `GW-API-004`,
  `LOG-APP-006`
- **Options:**
  1. Purge only the 4 identified stale edge nodes
  2. Purge the entire global edge cache for this endpoint
  3. No action, wait for staged propagation to complete naturally
- **Recommended option:** Option 1 — narrowly scoped, low operational
  risk, doesn't require resolving H1/H2/H3 first, and directly targets
  the confirmed staleness without the broader origin-load risk of a
  global purge.
- **Consulted roles:** none required beyond SRE Lead for this narrow
  scope per `PROC-001`; a global purge (option 2) would additionally
  require Incident Commander concurrence.
- **Fallback if deadline passes without decision:** Escalate to SRE
  on-call lead; staleness persists on the 4 known nodes until purged.

### DEC-005 — Issue customer communication?

- **Trigger:** 40 customer reports filed across all regions
  (`CS-FEEDBACK-001`–`006`); incident duration exceeds the internal
  communication-threshold in `PROC-001`.
- **Evidence:** `CS-FEEDBACK-001`–`006`
- **Options:**
  1. Publish a general-status message (no specific cause named)
  2. Publish a cause-specific message naming the payment provider
  3. Hold all external communication pending more confidence
- **Recommended option:** Option 1 — matches the confidence levels in
  `examples/orchestrator_analysis.md` §6–7; naming a specific cause
  (option 2) would overstate current confidence, and holding entirely
  (option 3) risks leaving customers without any acknowledgment for an
  incident that has already generated 40 reports.
- **Consulted roles:** Product Owner, Customer Support Lead
- **Fallback if deadline passes without decision:** Escalate to
  Communications Lead's manager; no external message is published by
  default.

### DEC-006 — Confirm/maintain SEV-2 declaration?

- **Trigger:** Regional authorization-rate declines exceed the SEV-2
  threshold (>5 percentage points sustained 30+ minutes) defined in
  `PROC-001`.
- **Evidence:** `KPI-HOURLY-002`, `KPI-HOURLY-003`, `PROC-001`
- **Options:**
  1. Maintain SEV-2
  2. Escalate to SEV-1 (would require evidence of widespread outage,
     which is not present — checkout remains partially functional in
     every region)
  3. Downgrade to SEV-3
- **Recommended option:** Option 1 — EU's peak decline (~12 points below
  baseline) exceeds the SEV-2 threshold; no region shows the widespread
  unavailability that would justify SEV-1.
- **Consulted roles:** Executive Sponsor (notified per `PROC-001`
  automatic-notification rule for SEV-2)
- **Fallback if deadline passes without decision:** Severity remains at
  its last-declared level (SEV-2) — silence never auto-escalates or
  auto-downgrades.
