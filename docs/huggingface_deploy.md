# Hugging Face Space Deployment

The project deploys to `timelions/ontofishing` as a Gradio Space.

## Required Secret

Set a GitHub repository secret named `HF_TOKEN`.

The token must have permission to write to the Hugging Face Space. Do not commit the token to this repository.

## Automatic Deploy

The workflow `.github/workflows/deploy-huggingface.yml` runs on pushes to `main` and can also be triggered manually from GitHub Actions.

If `HF_TOKEN` is missing, the workflow emits a warning and skips deployment. The core GitHub pipeline remains usable.

## Manual Local Deploy

Use this only from a shell where `HF_TOKEN` is already set:

```bash
python -m pip install --upgrade "huggingface_hub>=0.35"
python - <<'PY'
import os
from huggingface_hub import HfApi

HfApi(token=os.environ["HF_TOKEN"]).upload_folder(
    folder_path=".",
    repo_id="timelions/ontofishing",
    repo_type="space",
    path_in_repo=".",
    commit_message="Deploy Ontofishing cockpit",
    delete_patterns=["*"],
    ignore_patterns=[
        ".git/*",
        ".github/*",
        ".codex/*",
        ".pytest_cache/*",
        ".venv/*",
        "__pycache__/*",
        "**/__pycache__/*",
        "*.pyc",
        "reports/*",
        "data/grok_runs/*",
        "data/semantic_runs/*",
        "data/ranked_opportunities.csv",
        "data/opportunities_raw.csv",
    ],
)
PY
```

## Verification

After deploy, verify:

```bash
curl -fsSL https://huggingface.co/spaces/timelions/ontofishing/raw/main/app.py | head
curl -fsSL https://timelions-ontofishing.hf.space/gradio_api/info
```

The first command should show the Gradio cockpit app, not `trackio.show()`.
