# Grok worker conventions

Use Grok Build as a bounded heavy worker, not as the repository owner.

Recommended workflow:

1. Run Codex first to make tests pass and stabilize the schema.
2. Run `scripts/grok_discovery.sh` to collect candidates into `data/grok_runs/`.
3. Convert only validated rows into `data/opportunities_raw.csv`.
4. Run `bounty-wizard score ...`.
5. Ask ChatGPT or Codex to audit ranked results.

The worker must not submit applications, send emails, create bounty reports, or mutate core source code unless explicitly instructed.
