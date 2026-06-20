# Grok Build as a bounded heavy worker

## Verdict
Yes: after Codex stabilizes tests and schema, the obvious next extension is a Grok Build worker in the same repo.

But do not make Grok the repo owner. Make it a bounded discovery unit:

- Grok discovers and collects evidence.
- Codex maintains code, tests, parsing, reports, and deterministic scoring.
- ChatGPT/human performs final strategic audit.

## Why this division works

Grok Build supports interactive and headless use from a project directory, and headless mode can emit JSON. That makes it suitable as a scripted research worker.

Codex reads project `AGENTS.md` files and is better used as the repository maintainer/test runner.

## Local commands

Install Grok Build:

```bash
curl -fsSL https://x.ai/cli/install.sh | bash
```

Run discovery:

```bash
./scripts/grok_discovery.sh
```

Import accepted candidates into the raw CSV:

```bash
python scripts/grok_import_candidates.py data/grok_runs/<run>.json --out data/opportunities_raw.csv
```

Score:

```bash
bounty-wizard score data/opportunities_raw.csv --out data/ranked_opportunities.csv
bounty-wizard advise data/ranked_opportunities.csv
```

## Guardrails

- Store Grok output under `data/grok_runs/` first.
- Never let raw Grok findings overwrite ranked/scored outputs.
- Import only accepted candidates with official URLs.
- Keep rejected findings for audit.
- Run tests after parser/scoring changes.
