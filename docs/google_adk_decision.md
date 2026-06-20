# Google ADK / Agent Platform decision

## Verdict
Do not use Google ADK or Gemini Enterprise Agent Platform in v1.

## Why not v1
The current product is a local verification and ranking pipeline. It needs:
- deterministic scoring
- evidence fields
- small CSV/YAML files
- human review
- Codex-assisted implementation

It does not yet need:
- managed agent runtime
- enterprise governance
- vector search infrastructure
- long-running cloud agents
- multicloud deployment

## When to add ADK
Add Google ADK only when at least one is true:
- multiple specialized agents need deterministic graph orchestration
- sources and evidence exceed local-file management
- you need an always-on deployed service
- multiple users need access control and audit logs
- RAG over a growing private corpus is needed

## Safe extension pattern
Keep core scoring as pure Python. Add ADK as a thin orchestration layer:

Grok/ChatGPT discovery -> CSV -> Python scorer -> report
Optional ADK wrapper -> calls scorer/report tools

Never make ADK the source of truth.
