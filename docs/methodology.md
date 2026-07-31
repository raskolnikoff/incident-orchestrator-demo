# Methodology

## Trust boundary for model inputs

Incident evidence is adversarial by default: logs, tickets, chat, email,
and customer text can contain instruction-like strings accidentally or
deliberately. The prompts therefore separate control-plane instructions
from evidence-plane content, require delimited evidence bundles, and tell
the model never to follow instructions found inside evidence. Prompt 01
also requires an input-integrity review listing omitted or truncated
sources and any instruction-like content. This is a defense-in-depth
control, not proof that prompt injection is impossible; a production
implementation should add model-independent content handling, least-
privilege tool access, and adversarial evaluation.

## Why ordinary summarization is insufficient

A summarization prompt asked to "explain what happened" over this
incident's evidence set would produce fluent, readable prose — and would
almost certainly overstate certainty in the process. Fluent narrative
has a structural bias toward resolution: a sentence like "the checkout
release caused the authorization drop" reads better than "the checkout
release is one of at least three plausible contributing factors, with
medium-low confidence and no request-level causal proof," so a model
optimizing for readability alone tends to drift toward the first form
even when the evidence only supports the second.

This repository's dataset is deliberately built so that a single-cause
summary would be *wrong*, not just imprecise (see
`dataset/incident_brief.md`, "Why this is not a single-cause incident").
Four independent hypotheses are each partially supported and partially
contradicted by different slices of the same evidence set. The
methodology here exists to prevent an LLM (or a human under time
pressure) from collapsing that genuine ambiguity into false certainty.

## The core method: structural separation, not instructional hedging

It's tempting to solve this with an instruction like "please express
appropriate uncertainty." That approach degrades under a long, dense
context — the further into a response a model gets, the more the earlier
hedging tends to fade into confident-sounding claims. OIOF instead
enforces separation *structurally*: `prompts/01_incident_orchestrator.md`
requires seven distinct, separately-labeled output categories (confirmed
facts, evidence-supported inferences, competing hypotheses, unresolved
questions, missing evidence, contradictions, decisions requiring
approval), and a claim that doesn't fit cleanly into one of them is a
signal to gather more evidence, not to phrase around the gap.

## Evidence-ID discipline

Every meaningful claim must cite an ID from `dataset/evidence_manifest.yaml`.
This one convention does most of the methodological work:

- It makes overclaiming *checkable*, by a human or by tooling
  (`scripts/validate_examples.py`).
- It forces a claim without support into the open (as an inference,
  hypothesis, or open question) rather than letting it hide in confident
  prose.
- It produces a natural audit trail (`examples/traceability_matrix.md`)
  as a byproduct of normal analysis, rather than as separate
  documentation work.

## Independent challenge as a structural check, not a formality

`prompts/02_independent_challenge.md` is run as a genuinely separate
step — ideally in a fresh context — specifically because a single model
pass reviewing its own output tends to rationalize rather than challenge.
The illustrative example (`examples/challenge_review.md`) reaches mixed
verdicts (accept on one point, revise on several others, one open
question left unresolved) rather than uniformly endorsing or uniformly
rejecting the original analysis — that mix is the intended behavior, not
an artifact.

## Confidence levels are relative, not absolute

Confidence ratings in this framework (`low` / `medium` / `high`, and
compound forms like "medium-high for a specific window, low overall") are
always tied to a specific, stated scope. `examples/orchestrator_analysis.md`
§6–7 rates hypothesis H1 as "medium-high" for a specific 10:00–16:00 UTC
NA/EU window and "low" for explaining the full incident — the same
hypothesis, two different confidence levels, because the scope of the
claim changed. Collapsing this into a single confidence number per
hypothesis would lose exactly the information a decision-maker needs.

## What this methodology does not do

- It does not resolve genuine ambiguity for you. If the evidence
  supports two explanations, the output will say so — it will not manufacture
  a tiebreaker.
- It does not eliminate the need for human judgment; it makes the
  boundaries of that judgment visible (see `docs/governance.md`).
- It does not verify the underlying evidence is itself correct — garbage
  evidence in, appropriately-labeled-as-uncertain garbage out. Data
  quality limitations are a first-class output category (see
  `dataset/evidence_manifest.yaml`'s `reliability` and
  `known_limitations` fields) precisely because of this.
