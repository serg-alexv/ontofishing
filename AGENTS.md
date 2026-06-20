# Repository agent contract

This repository is a verification-first bounty/advisory pipeline. Both Codex and Grok Build may read this file.

## Architecture
- Codex = local code maintainer
- Grok Build = manually triggered subscription-auth heavy worker
- ChatGPT = audit / strategy / execution planning
- Python = deterministic scoring
- Google Cloud / ADK = postponed
- XAI_API_KEY = forbidden

## Billing constraint
- Do not use XAI_API_KEY.
- Do not require xAI Console API credits.
- Grok Build must be used only through local browser/OAuth subscription authentication.
- If unattended cloud/headless execution requires an API key, do not implement it.
- Prefer manual local execution over extra billing surfaces.

## Source of truth
- Core logic lives in `src/bounty_wizard/`.
- Raw external findings go into `data/grok_runs/` or `data/opportunities_raw.csv`.
- Ranked decisions come only from deterministic Python scoring plus human/ChatGPT audit.

## Allowed agent roles
- Codex: repository maintainer, implementation, tests, refactors, report generation.
- Grok worker: high-recall discovery, source hunting, contradiction finding, output normalization drafts.
- Human/ChatGPT: final strategic decision and adversarial audit.

## Non-negotiables
- Do not auto-submit bounty reports, grant applications, or security reports.
- Do not store API keys, cookies, tokens, private credentials, or browser session dumps in the repository.
- Do not implement aggressive scraping or bypass robots.txt/rate limits.
- Do not let web-search outputs overwrite scored data directly.
- Preserve official URLs, evidence fields, rejection reasons, and timestamps.
- Prefer official sources over aggregators.
- New code must be covered by tests when it changes scoring, parsing, or rejection logic.

## Grok worker boundary
- Grok may produce candidate opportunities and rejected-item evidence.
- Grok should write only to `data/grok_runs/` unless explicitly asked by the human.
- Grok findings must be imported into `data/opportunities_raw.csv` only after validation.
- Grok should not modify Python source files unless the task is explicitly a code task.

## Done means
- `pytest` passes.
- Generated files are placed under `data/` or `reports/`.
- Any opportunity accepted into the CSV has official URL, open-status evidence, eligibility, deliverable, payout/funding field, and risk notes.
