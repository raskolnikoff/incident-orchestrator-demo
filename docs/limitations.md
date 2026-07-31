# Limitations

This is a reference implementation and design experiment, not a
production system. Being explicit about what it doesn't do is part of
the same discipline it asks of its own output.

## Scope limitations

- **Not deployed.** No claim is made or implied that this framework has
  run against a real incident, a real production system, or real data.
  It has been exercised conceptually against the synthetic dataset in
  this repository; the example outputs in `examples/` are illustrative,
  not logs of an actual model run.
- **Not an autonomous system.** There is no code in this repository that
  calls an LLM API, executes a production action, or sends a
  communication. The prompts are designed to be run manually (or wired
  into your own tooling) against your own model access.
- **One incident scenario.** The dataset models a single fictional
  incident type (checkout authorization degradation) at a single
  fictional company. The prompts are written to generalize, but they
  have not been tested against other incident shapes (e.g. a security
  incident, a data-quality incident, a multi-day slow-burn degradation).

## Dataset limitations

These are intentional, not oversights — see
`dataset/evidence_manifest.yaml`'s `known_limitations` field per entry —
but are worth stating plainly:

- The dataset is small by production standards (hundreds, not millions,
  of records) so it fits comfortably in an LLM context window.
- Evidence buckets are curated slices (e.g. `PAY-METRIC-001` covers a
  specific region/provider/time combination), not a fully queryable raw
  data warehouse. A production system would need real query
  infrastructure behind the evidence-ID abstraction.
- Some evidence is deliberately incomplete (sampling gaps, partial edge
  coverage, vague vendor language) to exercise the "missing evidence" and
  "data-quality limitations" output categories — real incidents will have
  their own, different gaps that this dataset doesn't anticipate.
- No order-value, revenue, customer-satisfaction, or support
  resolution-time data is included, which is why
  `examples/orchestrator_analysis.md` explicitly states what business-
  and customer-impact claims cannot be made from this evidence set.

## Prompt limitations

- **Context-window pressure.** The full dataset can exceed comfortable
  context budgets for some models; see
  `prompts/prompt_design_notes.md`, "Context-window management," for
  mitigations (pre-aggregation via
  `scripts/generate_dataset_summary.py`, hypothesis-based chunking).
- **Model-dependent quality.** The prompts are model-agnostic by design,
  but the quality of fact/inference separation, the rigor of the
  independent challenge, and the plausibility of drafted communications
  will vary by model capability. No specific model's output quality is
  claimed or guaranteed.
- **Evidence-ID citation is necessary but not sufficient.** A model can
  cite a real evidence ID next to an overstated claim
  (`scripts/validate_examples.py` checks that citations resolve, not
  that the claim they support is actually justified by that evidence).
  Human review remains necessary for that judgment.
- **The independent challenge can still miss things.** Running Prompt 02
  in a fresh context reduces self-rationalization but does not
  guarantee a correct or complete critique — it is a structural
  mitigation, not a proof of correctness.
- **Prompt-injection controls are not a sandbox.** The prompts explicitly
  treat all evidence as untrusted data and require an input-integrity
  review, but instruction text alone cannot guarantee isolation. A real
  deployment needs least-privilege tools, authenticated approval, content
  handling, and adversarial tests outside the model.

## Validation limitations

- `scripts/validate_dataset.py` and `scripts/validate_examples.py` are
  intentionally built on the Python standard library only (no PyYAML, no
  `jsonschema` package), which keeps the repository dependency-free but
  means the YAML parser (`scripts/_manifest.py`) and JSON Schema
  validator (`scripts/_schema_lite.py`) support only the restricted
  subset this repository actually uses — they are not general-purpose
  tools.
- Citation tooling proves identifier resolution, manifest coverage, and
  source-file snapshot integrity. It does not prove that a cited source
  semantically supports the adjacent natural-language claim; the
  human-reviewed traceability matrix and challenge pass cover that gap.
- The secret-scanning check in `scripts/validate_dataset.py` is a
  conservative pattern match, not a comprehensive secret-detection tool.
  It catches obvious cases; it is not a substitute for a dedicated
  secret-scanning product in a real codebase.
- The prohibited-name denylist is small and specific to this project's
  confidentiality constraints. It is not a general PII or
  confidentiality scanner.

## What would need to change for real-world use

See `docs/architecture.md`'s automation boundary table for the
LLM-supported / deterministic-system / human-approval-required split,
and the README's "Extension ideas" for concrete next steps (real evidence
connectors, an approval UI, automated timeout escalation, and so on) —
none of which are implemented here, by design, since this repository's
purpose is to demonstrate the pattern, not ship the product.
