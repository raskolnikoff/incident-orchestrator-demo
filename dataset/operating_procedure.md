# Incident Management Operating Procedure (`PROC-001`)

> Synthetic data. This is a fictional operating procedure written for the
> Northstar Commerce OIOF demo scenario. It is illustrative, not a template
> endorsed for real production use without your own organization's review.

## 1. Severity definitions

| Severity | Definition | Example threshold used in this dataset |
|---|---|---|
| SEV-1 | Widespread customer-facing outage or safety/legal exposure | Global checkout unavailable, or any confirmed data exposure |
| SEV-2 | Significant, partial degradation affecting a meaningful share of customers or revenue-generating flows | Regional authorization-success-rate drop exceeding 5 percentage points sustained over 30+ minutes |
| SEV-3 | Limited or intermittent degradation with workarounds available | Isolated errors affecting a small customer segment |
| SEV-4 | Minor issue, no material customer impact | Cosmetic or internal-only issue |

This incident (`INC-2026-0730-CHECKOUT`) was provisionally declared SEV-2
based on the EU and NA authorization-rate drops recorded in
`KPI-HOURLY-002` / `KPI-HOURLY-003`.

## 2. Escalation thresholds

- Any SEV-1 or SEV-2 declaration triggers automatic notification to the
  Incident Commander on-call rotation and the Executive Sponsor.
- A decision with **customer risk = high** or **reversibility = low**
  (see `schemas/decision_matrix.schema.json`) requires Incident Commander
  and the relevant functional Accountable role's joint sign-off before
  execution, regardless of severity.
- If a decision's approval deadline passes without a decision, it
  automatically escalates one level up the relevant reporting line and is
  logged as a timeout exception (see `prompts/03_automation_blueprint.md`).

## 3. Standing change authority

- Fraud rule changes below a defined blast-radius threshold (percentage
  of traffic affected) may be approved by the Fraud Operations Lead alone.
  Changes above that threshold require Risk & Governance sign-off.
- Production rollbacks of application releases require Checkout
  Engineering Lead approval and SRE Lead concurrence.
- Payment-provider rerouting requires Payment Operations Lead approval and
  Incident Commander concurrence, because it changes financial routing and
  carries settlement and reconciliation implications.
- CDN configuration purges require SRE Lead approval; broad/global purges
  additionally require Incident Commander concurrence due to origin-load
  risk.
- Customer-facing communication requires Communications Lead approval and
  Product Owner concurrence; external vendor communication requires
  Vendor Manager involvement.

## 3a. Change-freeze policy around marketing campaigns

Non-emergency production changes (application releases, fraud-rule
updates, CDN/cache configuration changes) to checkout-critical systems
require sign-off from both the initiating team's lead and the SRE Lead
if they are scheduled within a **24-hour window** of a marketing
campaign with a planned traffic uplift above 25% (see
`dataset/campaign_schedule.csv`, `expected_traffic_uplift_pct`). The
intent is to avoid stacking independent sources of risk during a
high-traffic window, and to keep the number of concurrent variables
small enough that a resulting incident stays diagnosable.

This policy exists precisely because of incidents like
`INC-2026-0730-CHECKOUT`: the checkout-api release, the CDN cache
change, and the EU fraud-rule change were all scheduled for the same
morning as the "Summer Flash Sale" campaign (45% planned NA uplift,
`CAMPAIGN-001`), each apparently cleared by its own team without a
cross-team change-freeze review. Whether that coordination gap
happened is itself a legitimate post-incident-review question — see
`examples/orchestrator_analysis.md`, §11, "Process workstream."

## 4. Roles referenced throughout this repository

| Role | Primary responsibility in an incident |
|---|---|
| Incident Commander | Overall coordination, severity declaration, closure |
| SRE Lead | Infrastructure and platform diagnosis, rollback/purge execution |
| Checkout Engineering Lead | Checkout-api application diagnosis and release decisions |
| Payment Operations Lead | Payment provider relationship and routing decisions |
| Fraud Operations Lead | Fraud rule diagnosis and change decisions |
| Product Owner | Customer-impact prioritization, feature-level trade-offs |
| Customer Support Lead | Support-channel signal aggregation, customer-facing workaround guidance |
| Communications Lead | Drafts and approves external/customer communication |
| Risk and Governance | Reviews decisions with compliance, fraud-policy, or disclosure implications |
| Executive Sponsor | Business-level accountability, resourcing, executive reporting |
| Vendor Manager | Third-party payment provider communication and escalation |

## 5. Evidence retention

All evidence cited in an incident analysis (application logs, gateway
logs, KPI extracts, payment metrics, customer feedback samples, change
records, vendor communication, and internal chat excerpts used as
context) must be retained for no less than 180 days after incident
closure, tagged with the incident ID, for post-incident review and audit.

## 6. Closure criteria

An incident may be closed only when:

1. The authorization-success rate has returned to within 1 percentage
   point of the relevant regional baseline for at least 2 consecutive
   hours, **and**
2. Every open Decision Matrix entry is in a terminal status
   (`Approved & Executed`, `Rejected`, or `Superseded`), **and**
3. A post-incident review has been scheduled.

Closure is a human decision by the Incident Commander. It is never
performed automatically by any tool, workflow, or model output produced
under this framework.
