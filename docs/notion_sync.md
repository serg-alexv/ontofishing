# Optional Notion Sync

This repository keeps CSV files as the source of truth. Notion sync is an optional output step for review, not a required part of scoring or ontology generation.

## Inputs

The sync script reads a ranked or annotated opportunities CSV and sends one summarized child page per row.

Recommended input:

```bash
data/ranked_opportunities.csv
```

It only sends a small allowlist of fields:

- `name`
- `official_url`
- `domain`
- `decision`
- `fit_score`
- `bridge_score`
- `payout_amount`
- `deadline`
- `deliverable`

It intentionally does not send raw status evidence, notes, rejection evidence, or full source dumps.

## Environment

The script uses Notion only when both variables are present:

```bash
export NOTION_TOKEN="secret_..."
export NOTION_PARENT_PAGE_ID="..."
```

If either variable is missing, the sync is skipped with a message and exits normally. This keeps the core CSV pipeline usable without Notion credentials.

## Dry Run

Preview the summarized rows without calling Notion:

```bash
python scripts/notion_sync.py data/ranked_opportunities.csv --dry-run
```

Dry run does not require `NOTION_TOKEN` or `NOTION_PARENT_PAGE_ID`.

## Live Sync

After setting both environment variables:

```bash
python scripts/notion_sync.py data/ranked_opportunities.csv
```

The script creates child pages under `NOTION_PARENT_PAGE_ID`. It uses a fixed delay of 0.4 seconds between page creation calls, keeping requests below Notion's documented average API rate limit of three requests per second.

## Boundary

This is one-way output:

- CSV remains canonical.
- Notion edits are not imported back into scoring inputs.
- Missing Notion configuration does not fail the core pipeline.
- No external services are called during tests.
