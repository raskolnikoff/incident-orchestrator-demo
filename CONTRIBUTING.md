# Contributing

Thanks for your interest in this project. It's a portfolio / reference
repository — a demonstration of a design pattern (human-governed LLM
incident orchestration) rather than a production tool with a roadmap —
but improvements, corrections, and adaptations are welcome.

## Ways to contribute

- **Report an issue** with the prompts, dataset, diagrams, or docs
  (inconsistencies, broken evidence citations, unclear wording, rendering
  problems).
- **Propose an extension** — see `docs/limitations.md` for ideas the
  current scope deliberately leaves out.
- **Adapt this framework** for your own scenario and, if you're willing,
  share what worked or didn't as an issue or discussion.

## Ground rules for any pull request

1. **Keep the dataset synthetic.** Do not introduce real company names,
   real incidents, real people, real credentials, or any content that
   could be mistaken for genuine internal data. `scripts/validate_dataset.py`
   checks for a small denylist and obvious secret patterns, but that is a
   safety net, not a substitute for judgment.
2. **Keep evidence traceable.** If you add or change a claim in
   `examples/`, add or update the corresponding entry in
   `dataset/evidence_manifest.yaml` and make sure the evidence ID is
   actually cited. `scripts/validate_examples.py` enforces this.
3. **Keep the human-in-the-loop boundary intact.** Don't add example
   content, prompts, or workflow steps where an LLM is modeled as the
   decision owner, or where a production/customer/vendor action happens
   without a named human approval gate. `schemas/decision_matrix.schema.json`
   and `schemas/automation_blueprint.schema.json` encode this as a
   machine-checkable constraint (see the `not` clauses on
   `decision_owner` / `owner_role` / `approver_role`).
4. **Preserve ambiguity where it's intentional.** The synthetic incident
   is deliberately multi-causal (see `dataset/incident_brief.md`, "Why
   this is not a single-cause incident"). Please don't "fix" the dataset
   or examples by collapsing it to a single clean root cause — that
   would undermine the thing this repository exists to demonstrate.
5. **Regenerate deterministically.** If you change
   `scripts/generate_dataset.py`, re-run it and check whether
   `dataset/evidence_manifest.yaml` needs updating to match new record
   counts or time ranges (`make validate` will catch drift).

## Before opening a PR

```bash
make validate   # dataset + evidence-traceability checks
make test        # unit + integration test suite
make diagrams     # re-render PlantUML sources (requires a local PlantUML install)
```

All three should pass cleanly. If `make diagrams` isn't runnable in your
environment (no local PlantUML/Java), that's fine — the `.puml` source
files are the source of truth and are reviewed as text; rendering is
handled by CI (`.github/workflows/render-diagrams.yml`).

## Style

- Calm, specific, evidence-grounded prose. Avoid hype language and
  unverifiable claims (see `docs/methodology.md` for the tone this
  repository aims for).
- Markdown tables over prose where a table is genuinely clearer.
- No emojis in repository content unless a maintainer specifically asks
  for them in a given file.
