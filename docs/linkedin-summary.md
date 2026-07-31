# LinkedIn Support Material

For sharing this repository publicly. All content below is generic to
the project — no real company, employer, or internal presentation is
referenced anywhere in this repository or in this material.

## A. LinkedIn post (~180–260 words)

> Large language models should not replace incident managers. They
> should help humans make better, more traceable decisions from
> incomplete information.
>
> I built a reference implementation exploring that idea: the
> Operational Incident Orchestration Framework (OIOF). It's a fully
> synthetic demo — a fictional e-commerce incident at a fictional
> company — designed to show a specific pattern rather than a product.
>
> The core problem with using an LLM for incident analysis isn't that it
> can't summarize logs. It's that fluent summaries quietly convert
> correlation into causation, flatten genuine uncertainty into false
> confidence, and can end up making decisions no one signed off on.
>
> This framework pushes back on that by structurally separating
> confirmed facts from inferences from competing hypotheses, requiring
> every claim to cite its evidence, running an independent "challenge"
> pass that isn't allowed to just agree with the first draft, and
> routing every consequential action through a named human owner — never
> the model.
>
> The repository includes: four model-agnostic prompts, a synthetic but
> analytically realistic dataset (deliberately multi-causal — no single
> clean root cause), PlantUML workflow and RACI diagrams, JSON Schemas
> that make "AI is never the decision owner" a testable constraint, and
> a full validation/test suite.
>
> Link in the first comment. Feedback welcome, especially from people
> who've lived through the "the model said X so we did X" failure mode.

## B. First comment (repository link)

> Repository: https://github.com/raskolnikoff/incident-orchestrator-demo
> — start with the README, then `docs/walkthrough.md` for a step-by-step
> tour, or `examples/` if you want to see the output shape first.

## C. Carousel option: three purpose-built slides

For a carousel-style post (rather than attaching a repository diagram
directly), use `assets/linkedin/rendered/*.svg`: three 16:9 slides
designed specifically for a five-second read, distinct from the
technical `diagrams/rendered/` set referenced in section D below.

1. `01_evidence-to-decision.svg` — fragmented evidence → classified
   facts/inferences/hypotheses → named human decision.
2. `02_human-in-the-loop-workflow.svg` — the six-step pipeline with the
   human approval gate visually emphasized and the escalation-on-timeout
   path shown.
3. `03_raci-accountability.svg` — the LLM drafts and recommends but is
   never Accountable; named human roles are.

Each slide carries its own `<title>` and `aria-label` (see
`assets/linkedin/README.md` for the full text), which double as
ready-to-paste alt text, so no separate alt-text list is needed for
these three. Editable sources live in `assets/linkedin/source/`; run
`make linkedin-assets` after editing one to keep `rendered/` in sync
(`make validate` checks this automatically).

## D. Suggested alt text for attached diagrams

- **`diagrams/rendered/framework_overview.svg`** — "Flow diagram showing
  seven pipeline stages: evidence sources, evidence normalization, LLM
  reasoning, independent challenge, human decision, controlled
  execution, and audit trail, with accountability owners labeled at each
  stage."
- **`diagrams/rendered/evidence_to_decision.svg`** — "Diagram showing raw
  evidence classified into confirmed facts, inferences, competing
  hypotheses, and contradictions, feeding into a human-approved decision
  matrix with three possible outcomes: approved, rejected, or
  deferred."
- **`diagrams/rendered/escalation_state_machine.svg`** — "State diagram
  showing an incident's lifecycle from Detected through Triaged,
  Investigating, Decision Pending, Contained, Monitoring, Resolved, and
  Review, with an Escalated state reachable from multiple points and
  exitable only by human action."
- **`diagrams/rendered/responsibility_model.svg`** — "RACI-style
  responsibility diagram grouping incident-management activities under
  the single human role accountable for each one, with dashed lines
  showing key consulted relationships."

## E. Hashtags

`#IncidentManagement` `#SRE` `#AIGovernance` `#HumanInTheLoop`
`#LLM` `#SiteReliability` `#ResponsibleAI`

## F. Why PlantUML and RACI matter to non-technical readers

A wall of prose describing "who does what" is hard to audit — it's easy
to state a responsibility once and forget to state its boundary. A RACI
table forces exactly one *accountable* owner per activity to be written
down explicitly, which makes gaps and overlaps visible at a glance
(`docs/governance.md`). A state diagram does the same for process: it
makes illegal or unconsidered transitions visually obvious (can an
incident go straight from "Detected" to "Resolved"? the diagram answers
that without anyone having to read a paragraph). Neither artifact
requires reading code — a Product leader, a compliance reviewer, or an
executive sponsor can look at
`diagrams/rendered/responsibility_model.svg` or
`diagrams/rendered/escalation_state_machine.svg` and immediately see
where their own approval sits in the process, which is exactly the
audience this framework is trying to keep in the loop.
