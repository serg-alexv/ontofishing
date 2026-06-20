# Codex task queue

## Task 1 — make tests pass
Implement pytest coverage for:
- hard reject: closed status
- hard reject: student-only eligibility
- warning: missing status evidence
- score >=85 -> execute_this_week
- 70-84 -> prepare_application

## Task 2 — add URL validator
Create `src/bounty_wizard/validate_urls.py` that checks HTTP status for official URLs with polite timeout and no retries by default.

## Task 3 — add interactive wizard
Add `bounty-wizard new` that prompts for fields and appends a row to `data/opportunities_raw.csv`.

## Task 4 — add report generator
Add `bounty-wizard report data/ranked_opportunities.csv --out reports/latest.md`.

## Task 5 — optional ADK prototype, only after v1 works
Create an experimental branch `adk-prototype` that wraps scoring/report generation as an ADK tool. Do not move core logic into ADK.
