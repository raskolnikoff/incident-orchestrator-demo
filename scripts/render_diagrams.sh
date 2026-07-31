#!/usr/bin/env bash
# render_diagrams.sh — Render diagrams/source/*.puml to SVG and PNG under
# diagrams/rendered/, using a local PlantUML installation.
#
# Usage:
#   scripts/render_diagrams.sh
#
# Requires: a `plantuml` executable on PATH (which itself requires a Java
# runtime). On macOS: `brew install plantuml`. On Debian/Ubuntu:
# `apt-get install plantuml`. If PlantUML is not available, this script
# exits with a clear message and a non-zero status rather than failing
# silently — the .puml source files remain valid and editable regardless,
# and diagrams/rendered/ (if already populated) is left untouched.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${REPO_ROOT}/diagrams/source"
OUTPUT_DIR="${REPO_ROOT}/diagrams/rendered"

if ! command -v plantuml >/dev/null 2>&1; then
  echo "plantuml not found on PATH." >&2
  echo "Install it (e.g. 'brew install plantuml' or 'apt-get install plantuml')" >&2
  echo "and re-run this script. diagrams/source/*.puml remain valid and" >&2
  echo "readable without rendering; only the SVG/PNG output is skipped." >&2
  exit 1
fi

mkdir -p "${OUTPUT_DIR}"

echo "Rendering SVG..."
plantuml -tsvg -o "${OUTPUT_DIR}" "${SOURCE_DIR}"/*.puml

echo "Rendering PNG..."
plantuml -tpng -o "${OUTPUT_DIR}" "${SOURCE_DIR}"/*.puml

echo "Done. Output in ${OUTPUT_DIR}"
ls -la "${OUTPUT_DIR}"
