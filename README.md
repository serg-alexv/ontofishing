# Bounty Advisory Wizard + Codex Pipeline

A local-first pipeline for discovering, filtering, scoring, and executing bounty/prize/challenge/grant opportunities for an independent researcher/engineer.

## Purpose

This repository is intentionally **not** a crawler-first system. It is a verification-first advisory workflow:

1. Grok Heavy or a web-capable research agent discovers candidate opportunities.
2. The human or agent saves candidates to `data/opportunities_raw.csv`.
3. The wizard asks structured questions and applies hard rejection filters.
4. The scoring engine ranks opportunities by fit, verification strength, payout, effort, and risk.
5. Codex implements extensions, tests, integrations, and reports through controlled tasks.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp data/opportunities_raw.example.csv data/opportunities_raw.csv
bounty-wizard score data/opportunities_raw.csv --out data/ranked_opportunities.csv
bounty-wizard advise data/ranked_opportunities.csv
```

## Key files

- `src/bounty_wizard/scoring.py` — scoring and rejection logic.
- `src/bounty_wizard/cli.py` — CLI wizard.
- `data/schema.opportunity.json` — opportunity record schema.
- `data/sources.yaml` — source taxonomy and trust levels.
- `prompts/grok_heavy_discovery.md` — prompt for Grok Heavy discovery.
- `prompts/chatgpt_audit.md` — prompt for ChatGPT adversarial audit.
- `.codex/AGENTS.md` — repository operating rules for Codex.
- `.codex/tasks.md` — staged Codex task queue.
- `docs/google_adk_decision.md` — whether Google ADK/Agent Platform should be added.

## Design principle

Do not optimize for the largest number of listings. Optimize for the smallest number of **verifiable, executable, high-ROI opportunities**.
