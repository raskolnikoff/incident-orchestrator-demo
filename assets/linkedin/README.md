# LinkedIn Carousel Assets

Three 16:9 presentation-quality SVG slides distilling this repository's
governance pattern into a five-second-readable carousel. They are a
companion to `docs/linkedin-summary.md` (the post copy, hashtags, and
carousel pointer), not a replacement for the technical diagrams in
`diagrams/`.

## Why these exist as a separate asset set

`diagrams/source/*.puml` are technical artifacts: accurate, detailed,
and meant to be read alongside `docs/architecture.md` or
`docs/governance.md`. They are not built for a five-second scroll-past
glance on a social feed — several use small multi-line labels, tables,
or sequence lifelines that only resolve at diagram-viewer resolution.

These three assets exist to carry the same *claims* (never the same
literal diagram) at carousel resolution: minimal text, one visual idea
each, legible at thumbnail size. Where the two disagree on anything
factual, the PlantUML source in `diagrams/source/` is authoritative;
these are a distillation of it, not an independent description.

## The three slides

| # | File | Distills | Core claim |
|---|---|---|---|
| 1 | `01_evidence-to-decision.svg` | `framework_overview.puml`, `evidence_to_decision.puml` | Evidence is classified into facts / inferences / hypotheses; the LLM recommends, a named human decides. |
| 2 | `02_human-in-the-loop-workflow.svg` | `human_approval_sequence.puml`, `incident_workflow.puml`, `escalation_state_machine.puml` | Six-step pipeline; nothing reaches execution without a human approval gate; a missed deadline escalates to a human and never auto-approves. |
| 3 | `03_raci-accountability.svg` | `responsibility_model.puml`, `docs/governance.md` | The LLM is never the Accountable role; every activity has exactly one named human owner; some roles are Consulted only. |

## Design system

Shared across all three files (declared in each file's own header
comment, repeated here for convenience):

| Element | Value |
|---|---|
| Canvas | 1600×900 (16:9) |
| Titles | `#111827` |
| Body text | `#374151` |
| Captions / meta | `#6B7280` |
| Evidence / neutral-system fill | `#F3F4F6`, border `#D1D5DB` / `#9CA3AF` |
| LLM fill | `#EFF6FF`→`#BFDBFE` (darker = higher confidence), border `#3B82F6` |
| Human / accountability fill | `#FFFBEB`, border `#F59E0B` |
| "Never" / boundary accent | `#B91C1C` on `#FEF2F2` |
| Divider rules | `#E5E7EB` |
| Font stack | `-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif` (system fonts, so nothing needs embedding) |

Every mark is an authored vector primitive (`rect`, `circle`, `path`,
`line`) — no `<image>`, no `<foreignObject>`, no embedded raster or
photographic content, and no company logo or brand mark anywhere.
`scripts/validate_linkedin_assets.py` enforces the no-raster and
no-prohibited-name rules; `tests/test_linkedin_assets.py` additionally
asserts that each slide's required "never autonomous" phrase survives
future edits (see the table below).

| File | Required phrase(s) |
|---|---|
| `01_evidence-to-decision.svg` | "Recommends only", "Never decides" |
| `02_human-in-the-loop-workflow.svg` | "Nothing executes without it", "Never auto-approves" |
| `03_raci-accountability.svg` | "NEVER THE ACCOUNTABLE OWNER", "Never the model" |

## Source vs. rendered

- **`source/`** — the editable masters. Each file opens with a comment
  block explaining which `.puml` diagram(s) it distills and what
  technical claim it must not contradict. Edit these.
- **`rendered/`** — the same markup with that authoring comment
  stripped: the clean, ready-to-download file to actually attach to a
  post. Never edit these directly; they're generated.

To regenerate `rendered/` after editing anything in `source/`:

```bash
make linkedin-assets
# or directly:
python3 scripts/export_linkedin_assets.py
```

`make validate` (via `scripts/validate_linkedin_assets.py`) fails the
build if `rendered/` ever drifts out of sync with `source/`, if a
viewBox stops being 16:9, if raster/embedded imagery is introduced, or
if a required no-autonomy phrase is removed.

## Exporting to PNG/JPG for upload

LinkedIn accepts SVG poorly in some post types; if you need a raster
export:

```bash
rsvg-convert -w 1600 -h 900 assets/linkedin/rendered/01_evidence-to-decision.svg -o 01.png
```

(`rsvg-convert` is available via `brew install librsvg` on macOS or
`apt-get install librsvg2-bin` on Debian/Ubuntu; any SVG-to-PNG renderer
at 1600×900 or greater produces an equivalent result, since every
element is vector.)

## Synthetic-scenario note

These slides describe the *framework pattern*, not the specific
synthetic incident in `dataset/`. They deliberately don't mention
Northstar Commerce, ProviderAlpha, or any dataset-specific detail, so
they stay reusable as a general explanation of the governance pattern
independent of this repository's illustrative scenario.
