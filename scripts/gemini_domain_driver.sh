#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT_CSV="${1:-$PROJECT_ROOT/data/ranked_opportunities.csv}"
PROMPT_FILE="$PROJECT_ROOT/prompts/gemini_domain_driver.md"
RUN_DIR="$PROJECT_ROOT/data/semantic_runs"
STAMP="$(date +"%Y%m%d_%H%M%S")"
OUT_FILE="$RUN_DIR/gemini_semantic_${STAMP}.json"

mkdir -p "$RUN_DIR"

if ! command -v gemini >/dev/null 2>&1; then
  echo "ERROR: 'gemini' CLI command not found. Install/configure official Gemini CLI first." >&2
  exit 1
fi

if [[ ! -f "$INPUT_CSV" ]]; then
  echo "ERROR: input CSV not found: $INPUT_CSV" >&2
  exit 1
fi

if [[ -n "${GEMINI_API_KEY:-}" || -n "${GOOGLE_API_KEY:-}" ]]; then
  echo "NOTICE: Gemini API key env var is set. This may use API billing depending on your CLI configuration." >&2
fi

{
  cat "$PROMPT_FILE"
  printf '\n\nCSV INPUT:\n'
  cat "$INPUT_CSV"
} | gemini > "$OUT_FILE"

echo "Wrote semantic annotations: $OUT_FILE"
