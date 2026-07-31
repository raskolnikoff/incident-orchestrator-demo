# Security Policy

## Scope

This repository is a **documentation and design-pattern portfolio**: a
set of prompts, a synthetic dataset, illustrative example outputs,
PlantUML diagrams, JSON Schemas, and Python standard-library validation
scripts/tests. It does not run a service, expose a network endpoint, or
process real user data. There is no production deployment of this
framework — see `docs/limitations.md`.

The main security-relevant properties this repository maintains are:

- **No real data.** Every dataset file, incident, communication, and
  identifier is synthetic (see the root `README.md` disclaimer). If you
  believe any content here resembles real data, a real person, or a real
  organization's internal information, please report it (see below) —
  that would be a bug in this repository, not intentional content.
- **No secrets.** `scripts/validate_dataset.py` scans the repository for
  common secret-shaped patterns (API keys, private key headers, etc.) as
  part of `make validate`, and this check runs in CI.
- **No executable automation.** The scripts in this repository validate
  and render static content; they do not call external services, accept
  network input, or execute model-generated code.

## Reporting a vulnerability or data-exposure concern

If you find:
- content that appears to be real (rather than synthetic) data or
  identifiable personal information,
- a credential or secret accidentally committed,
- a dependency or script behavior with a genuine security implication,

please open a private report via GitHub's "Report a vulnerability"
feature on this repository (Security tab), or open an issue marked
clearly as sensitive without including the sensitive detail in the issue
body, and a maintainer will follow up for details privately.

## Out of scope

Since this repository has no runtime service, categories like
authentication bypass, injection against a live endpoint, or denial of
service against a running instance are not applicable. Reports about the
*prompts'* content (e.g. "this prompt could be adapted to produce
harmful output") are welcome as regular issues/discussion rather than
security reports, since the prompts are advisory text for a human
operator, not executable code.
