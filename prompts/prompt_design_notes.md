# Prompt Design Notes

This note explains the design decisions behind the four prompts in this
directory, so you can adapt them to your own incidents without breaking
the properties that make them useful.

## Why four separate prompts, not one mega-prompt

Each prompt has a distinct job and a distinct set of guardrails:

| Prompt | Job | Failure mode it exists to prevent |
|---|---|---|
| `01_incident_orchestrator.md` | Synthesize evidence into a structured analysis | A single fluent narrative that hides uncertainty behind confident prose |
| `02_independent_challenge.md` | Adversarially review the analysis | The analysis marking its own homework and rationalizing its first take |
| `03_automation_blueprint.md` | Turn an *approved* analysis into an operational workflow design | Jumping straight from "the model said X" to "a system now does X" with no human gate |
| `04_executive_brief.md` | Compress for a non-technical decision-maker | Losing the "what's still uncertain" signal on the way up the org chart |

Combining these into one prompt tends to produce a model that reviews its
own output in the same breath it generated it — which in practice means
weak self-review. Running Prompt 02 as a genuinely separate step (ideally
in a fresh context, per its own design note) is the single highest-value
structural decision in this framework.

## Why the fact/inference/hypothesis split is enforced structurally

It would be easy to just instruct a model to "be careful about
certainty." That instruction degrades quickly under a long, evidence-rich
context — models (and humans) drift toward confident narrative because
narrative reads better than hedged lists. Requiring specific,
separately-labeled output sections (fact table, contradiction register,
hypothesis list with supporting/opposing evidence) forces the structure
to survive even when the prose around it doesn't stay perfectly
disciplined. If a claim doesn't fit cleanly into section 4 or 6 of Prompt
01's output, that's a signal the claim needs more evidence, not more
confident phrasing.

## Why every claim must cite an evidence ID

Evidence-ID citation is the mechanism that makes the "self-review for
unsupported claims" step (section 17 of Prompt 01) actually checkable —
by a human, or by tooling. `scripts/validate_examples.py` in this
repository automates exactly this check: every evidence-ID-shaped token
in `examples/*.md` is looked up against `dataset/evidence_manifest.yaml`,
and any that don't resolve fail the build. That is only possible because
the prompt requires the citation discipline in the first place. If you
adapt these prompts for a real incident, keep the evidence-ID convention
even if your internal tooling doesn't validate it automatically yet — it
still forces a materially more checkable output.

## Why hypotheses are never resolved to a single winner inside the prompt

Prompt 01 explicitly prohibits collapsing competing hypotheses into one
"the root cause is X" statement, and Prompt 02 is partly designed to
catch it if that happens anyway. This is deliberate: root-causing a
multi-factor incident is a human judgment call that should happen after
reviewing the evidence, not something the model should pre-decide by
choosing which hypothesis to write about most confidently. In the
synthetic dataset here, more than one hypothesis is genuinely supported
by different slices of evidence at the same time (see
`dataset/incident_brief.md`, "Why this is not a single-cause incident") —
this is intentional, and a good orchestrator output should reflect that
irreducible ambiguity rather than paper over it.

## Context-window management

The full synthetic dataset (300 application log records, 180 gateway log
rows, 144 KPI rows, 216 payment-metric rows, 40 feedback records, plus
narrative files) is small by production standards but can still exceed
comfortable context budgets for some models when pasted in full. Two
practical approaches:

1. **Pre-aggregate.** Run `scripts/generate_dataset_summary.py` to get a
   compact statistical summary (counts, rates, and evidence-ID
   cross-references) and paste that alongside the narrative files
   instead of the raw structured files, reserving raw-file access for a
   specific follow-up question ("show me the raw ProviderAlpha timeout
   records") rather than every run.
2. **Chunk by hypothesis.** If your model's context is tight, run Prompt
   01 once per hypothesis's evidence subset (see the evidence manifest's
   `category` and `regions` fields to slice) and merge the fact tables
   and hypothesis sections manually before running Prompt 02.

Either way, always include `dataset/evidence_manifest.yaml` in full — it
is small, and it is the anchor that makes citation checking possible.

## Adapting these prompts to a real incident

- Replace the evidence-ID prefixes (`LOG-APP-`, `PAY-METRIC-`, etc.) with
  whatever your own systems naturally produce, but keep the *pattern* of
  a small number of stable, greppable prefixes.
- Keep the prohibited-actions list, and add your organization's own
  irreversible actions to it (e.g. "must not disable a security control,"
  "must not modify a customer's account balance").
- Keep Prompt 02 as a genuinely separate pass, ideally by a different
  reviewer (human or model) than whoever ran Prompt 01.
- Do not skip Prompt 04's "decision owner" field. If your organization
  doesn't yet have a clear owner for a given decision type, that gap is
  itself worth surfacing rather than defaulting to "whoever ran the
  prompt."
