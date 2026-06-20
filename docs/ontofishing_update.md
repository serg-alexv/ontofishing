# Ontofishing Update

## Demo Target

Ontofishing is now shaped as a Hugging Face Gradio cockpit over the local bounty advisory pipeline.

The demo entrypoint is `app.py`. It presents the project as an end-user surface while preserving the repository's original rule: CSV files remain the source of truth.

## Combined Chat Source Status

Provided ChatGPT source links:

- `https://chatgpt.com/c/6a36eac8-fa5c-83ed-9417-b1703f8ad269`
- `https://chatgpt.com/c/6a36aaa8-6458-83eb-88bc-1a0ff554a2c2?messageId=finalAgentTurnStart`
- `https://chatgpt.com/c/6a355f03-a474-83eb-bf05-a737766af852`

The runtime cannot read private ChatGPT conversation contents from those URLs. The cockpit therefore preserves the links as source references and includes a transcript import box for pasted exports. It does not fabricate hidden chat contents.

## Current Local Capabilities

- Deterministic scoring and hard-reject handling.
- Grok worker prompt/import path using local subscription-auth CLI conventions.
- Gemini and agy semantic driver prompts/scripts.
- Ontology map export with typed weighted edges and `bridge_score`.
- Optional Notion output with dry-run mode and summarized rows only.
- Gradio cockpit for scoring, ontology export, Notion preview, and project update compilation.

## Deployment Shape

Hugging Face Space:

- SDK: Gradio
- App file: `app.py`
- Dependencies: `requirements.txt`

GitHub target:

- `https://github.com/serg-alexv/ontofishing`
- Branch: `main`

No API keys or tokens are stored in the repository.
