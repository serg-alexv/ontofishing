# Codex operating rules for bounty-advisory-wizard

## Mission
Build a local-first advisory pipeline that ranks verifiable bounty/prize/challenge/grant opportunities for an independent researcher/engineer.

## Non-negotiables
- Do not implement aggressive scraping.
- Do not bypass robots.txt or rate limits.
- Do not auto-submit applications or security reports.
- Do not store API keys in the repo.
- Prefer official source URLs over aggregators.
- Every opportunity must preserve evidence fields and rejection reasons.
- Tests must cover scoring and hard-reject logic before expanding features.

## Architecture preference
- Keep v1 CLI-first and file-based: CSV/YAML/JSON.
- Add web UI only after the CLI flow is stable.
- Add cloud deployment only after repeated manual runs prove value.
- Google ADK/Agent Platform is optional v3 infrastructure, not v1 dependency.

## Commit style
Small commits with clear messages:
- feat: add source validator
- test: cover hard rejects
- docs: add Grok discovery prompt
- chore: update source taxonomy
