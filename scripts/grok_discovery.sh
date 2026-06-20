#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT_FILE="${1:-$ROOT/prompts/grok_worker_discovery.md}"
OUT_DIR="$ROOT/data/grok_runs"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
OUT_FILE="$OUT_DIR/$STAMP.json"

mkdir -p "$OUT_DIR"

if ! command -v grok >/dev/null 2>&1; then
  echo "ERROR: official grok command not found. Install and authenticate it outside this script, then rerun." >&2
  exit 127
fi

if [[ -v XAI_API_KEY ]]; then
  echo "WARNING: API-key mode is not desired for this project; using the local grok login/OAuth session." >&2
fi

cd "$ROOT"

echo "Running Grok worker. Output: $OUT_FILE" >&2
# --no-auto-update avoids background update checks in scripted/headless runs.
# --output-format json requests a machine-readable final object from Grok.
grok --no-auto-update -p "$(cat "$PROMPT_FILE")" --output-format json > "$OUT_FILE"

echo "$OUT_FILE"
