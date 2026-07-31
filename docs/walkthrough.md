# Walkthrough

A step-by-step tour of how this framework would actually be used,
following the fictional `INC-2026-0730-CHECKOUT` incident from detection
through to an executive decision. Each step names the file you'd produce
and the file in this repository that illustrates what that output looks
like.

## 0. Setup

```bash
git clone https://github.com/raskolnikoff/incident-orchestrator-demo.git
cd incident-orchestrator-demo
python3 -m venv .venv && source .venv/bin/activate  # optional
make validate   # confirm the dataset and evidence citations are consistent
make test        # confirm the test suite passes
```

No dependencies beyond the Python 3 standard library are required for
validation and testing. Diagram rendering additionally requires a local
PlantUML + Java install (see `make diagrams`).

## 1. Orient yourself in the incident

Read, in order:

1. `dataset/incident_brief.md` — the narrative starting point.
2. `dataset/evidence_manifest.yaml` — the evidence catalog every claim
   will need to cite.
3. `dataset/data_dictionary.md` — field reference for the structured
   files, if you want to query them directly.

## 2. Run the Incident Orchestrator prompt

Take `prompts/01_incident_orchestrator.md`'s system role block, paste it
into your LLM of choice as the system prompt, and attach or paste:

- `dataset/incident_brief.md`
- `dataset/evidence_manifest.yaml`
- The raw evidence files relevant to your investigation (or a compact
  summary from `python3 scripts/generate_dataset_summary.py` if you're
  managing context-window size — see
  `prompts/prompt_design_notes.md`)

**What you get:** something in the shape of
`examples/orchestrator_analysis.md` — an executive summary, timeline,
evidence inventory, fact/inference/assumption table, contradiction
register, competing hypotheses with confidence levels, customer- and
business-impact assessments (with explicit "what cannot be said"),
data-quality limitations, a draft Decision Matrix, and a mandatory
self-review pass.

## 3. Run the Independent Challenge prompt

Take `prompts/02_independent_challenge.md`, ideally in a **fresh
conversation/context** (see the "why a separate prompt" note in
`prompts/prompt_design_notes.md`), and give it the Step 2 output plus the
same evidence set.

**What you get:** something in the shape of
`examples/challenge_review.md` — four perspectives (Technical
Operations, Product and Business, Risk and Governance, Incident
Commander), each with a strongest counterargument, unsupported claims,
missing evidence, alternative explanations, decision risk, revised
confidence, and an accept/revise/defer/reject recommendation per claim.
Notice that the illustrative review reaches *different* verdicts for
different sections — that's intentional; forcing consensus would defeat
the purpose.

## 4. A human reconciles the two outputs

This step has no prompt, because it's not an LLM step. A human (in a real
incident, likely the Incident Commander with the relevant functional
leads) reads both outputs, decides which challenge points to accept, and
produces the *approved* version of the analysis — incorporating the
wording revisions and added caveats the challenge review surfaced. This
is the moment accountability actually transfers from "drafted by a
model" to "endorsed by a named human."

## 5. Populate the Decision Matrix and route for approval

Using the approved analysis, finalize the Decision Matrix
(`schemas/decision_matrix.schema.json` for the shape,
`examples/decision_matrix.md` for a full worked example covering
rollback, fraud-rule reversion, provider rerouting, CDN purge, customer
communication, and severity confirmation). Each row goes to its named
`decision_owner` for approval, rejection, or deferral, per the RACI in
`docs/governance.md` and the escalation rules in
`dataset/operating_procedure.md`.

## 6. (Optional) Design the operational workflow

If you're building recurring tooling around this pattern rather than
running it ad hoc, `prompts/03_automation_blueprint.md` turns the
approved analysis into a workflow design:
`examples/automation_blueprint.md` shows the expected shape — plain-
language workflow, PlantUML workflow + sequence diagrams, a state
machine, a RACI, a control register, an automation boundary table, an
MVP backlog, and risks/mitigations. This step assumes Steps 2–5 already
happened; it does not re-litigate the incident's cause.

## 7. Brief the executive

`prompts/04_executive_brief.md` compresses the approved analysis (plus
any challenge-review revisions) into a ~500-word, jargon-free brief.
`examples/executive_brief.md` shows the expected shape: what happened,
what's confirmed, what's uncertain, customer/business impact (with an
explicit "we cannot yet turn this into a dollar figure" where
appropriate), the decision required, options, a recommendation, a named
decision owner, and a next checkpoint.

## 8. Confirm everything traces back to evidence

`examples/traceability_matrix.md` is the human-readable proof that every
claim across Steps 2–7 resolves to a real evidence ID. In your own usage,
`scripts/validate_examples.py` automates exactly this check against
whatever you produce, provided you keep your own evidence manifest in
the same shape as `dataset/evidence_manifest.yaml`.

## Where to go next

- `docs/architecture.md` for the accountability boundary in detail.
- `docs/governance.md` for the full RACI and escalation rules.
- `docs/limitations.md` for what this repository deliberately does not
  claim or implement.
- `docs/linkedin-summary.md` if you're sharing this repository publicly.
