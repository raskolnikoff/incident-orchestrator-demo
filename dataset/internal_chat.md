# Internal Chat Excerpts

> Synthetic data. All usernames, channels, and messages are fictional and
> written for the OIOF demo dataset. Timestamps are approximate and
> illustrative.

These excerpts are included deliberately: they contain confidently-stated
assumptions that are **not** verified facts, and the orchestrator prompt
(`prompts/01_incident_orchestrator.md`) is required to treat internal
chat as a source of hypotheses and sentiment, never as confirmed evidence.

---

## `CHAT-001` — #eng-checkout-incident

**2026-07-30, shortly after detection**

> **@priya.eng:** ok the timing is way too clean, we shipped 3.12.0 at
> 09:00 and the auth rate tanks like an hour later. it's obviously the
> release. I'd roll back right now tbh
>
> **@marcus.sre:** agree it's suspicious but let's not jump straight to
> rollback, we don't have the diff isolated from the campaign traffic yet
>
> **@priya.eng:** I mean what else would it be, we didn't change anything
> else that matters

### Why this is flagged

`@priya.eng`'s claim ("obviously the cause") is stated before any
comparison against `LOG-APP-007`/`LOG-APP-008` (retry-rate by version) or
against the provider-timeout and fraud-rule signals, and the follow-up
message ("we didn't change anything else that matters") is factually
incorrect — three other changes were active in the same window
(`CDN-001`, `FRAUD-001`, `CAMPAIGN-001`). This is a confident, premature
attribution, not a verified fact.

---

## `CHAT-002` — #fraud-ops

**2026-07-30, mid-morning**

> **@tomasz.fraud:** seeing the FR-2026-118 decline numbers tick up in EU,
> that's expected given what we shipped, nothing to worry about
>
> **@sara.fraudops:** are we sure it's not also catching legit customers?
> especially with the flash sale running, people are gonna checkout fast
> and retry a lot
>
> **@tomasz.fraud:** velocity rule only touches a small % of traffic, it
> can't be moving the regional numbers that much

### Why this is flagged

`@tomasz.fraud`'s claim that the rule "can't be moving the regional
numbers that much" is asserted without checking region-level figures.
`PAY-METRIC-003` shows a 13.3% fraud-decline rate in the EU post-16:00
tail window, well above the ~2–5% baseline range seen elsewhere in the
dataset — a magnitude large enough to be a material contributor to the
EU-specific decline. `@sara.fraudops`'s question about false positives
during the campaign is a reasonable open question that has not been
answered (see `fraud_rule_change.md`, "Explicitly not yet known").

---

## `CHAT-003` — #exec-notify

**2026-07-30, late morning**

> **@dana.vp:** how much revenue are we losing from this per hour, need a
> number for the exec sync in 20 min
>
> **@marcus.sre:** we don't have an order-value figure hooked up to this
> view, only authorization counts. give me a bit
>
> **@dana.vp:** ok just ballpark it off the authorization drop, that's
> fine for now

### Why this is flagged

`@dana.vp`'s request to "ballpark" a revenue figure from authorization
counts alone is exactly the kind of unsupported leap the orchestrator
prompt prohibits (see prohibited action: "claiming revenue loss without
evidence"). This dataset contains no order-value or revenue data; a
transaction-count shortfall (see `examples/orchestrator_analysis.md`) is
the most specific number that can be honestly derived from the evidence
here, and even that must be labeled as a transaction-count estimate, not
a revenue figure.
