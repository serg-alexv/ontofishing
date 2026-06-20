#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT_CSV="${1:-$PROJECT_ROOT/data/ranked_opportunities.csv}"
PROMPT_FILE="$PROJECT_ROOT/prompts/agy_domain_driver.md"
RUN_DIR="$PROJECT_ROOT/data/semantic_runs"
STAMP="$(date +"%Y%m%d_%H%M%S")"
OUT_FILE="$RUN_DIR/agy_semantic_${STAMP}.json"

mkdir -p "$RUN_DIR"

if ! command -v agy >/dev/null 2>&1; then
  echo "ERROR: 'agy' CLI command not found. Install/configure Antigravity CLI first." >&2
  exit 1
fi

if [[ ! -f "$INPUT_CSV" ]]; then
  echo "ERROR: input CSV not found: $INPUT_CSV" >&2
  exit 1
fi

{
  cat "$PROMPT_FILE"
  printf '\n\nCSV INPUT:\n'
  cat "$INPUT_CSV"
} | agy > "$OUT_FILE"

echo "Wrote semantic annotations: $OUT_FILE"
