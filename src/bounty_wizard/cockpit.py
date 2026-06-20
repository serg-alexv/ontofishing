from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .cli import score_csv
from .ontology import build_ontology_snapshot


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHAT_SOURCE_URLS = [
    "https://chatgpt.com/c/6a36eac8-fa5c-83ed-9417-b1703f8ad269",
    "https://chatgpt.com/c/6a36aaa8-6458-83eb-88bc-1a0ff554a2c2?messageId=finalAgentTurnStart",
    "https://chatgpt.com/c/6a355f03-a474-83eb-bf05-a737766af852",
]

DISPLAY_COLUMNS = ["name", "decision", "fit_score", "bridge_score", "official_url"]


@dataclass(frozen=True)
class CockpitScoreResult:
    output_csv: Path
    rows: list[dict[str, str]]
    summary: str


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_opportunity_rows(path: Path) -> list[dict[str, str]]:
    rows = read_csv_rows(path)
    return [{column: row.get(column, "") for column in DISPLAY_COLUMNS} for row in rows]


def score_csv_for_cockpit(input_csv: Path, out_dir: Path) -> CockpitScoreResult:
    out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = out_dir / "ranked_opportunities.csv"
    score_csv(input_csv, output_csv)
    rows = read_csv_rows(output_csv)
    noun = "opportunity" if len(rows) == 1 else "opportunities"
    return CockpitScoreResult(
        output_csv=output_csv,
        rows=rows,
        summary=f"Scored {len(rows)} {noun}. Output: {output_csv}",
    )


def ensure_demo_ranked_csv(out_dir: Path) -> CockpitScoreResult:
    return score_csv_for_cockpit(PROJECT_ROOT / "data" / "opportunities_raw.example.csv", out_dir)


def build_demo_ontology(out_dir: Path, opportunities_csv: Path | None = None) -> tuple[str, Path, Path]:
    source_csv = opportunities_csv or PROJECT_ROOT / "data" / "opportunities_raw.example.csv"
    result = build_ontology_snapshot(
        opportunities_csv=source_csv,
        concepts_csv=PROJECT_ROOT / "data" / "concepts.example.csv",
        edges_csv=PROJECT_ROOT / "data" / "ontology_edges.example.csv",
        out_dir=out_dir,
    )
    return (
        f"Built ontology snapshot with {len(result.opportunities)} opportunity bridge record(s).",
        result.html_path,
        result.edges_path,
    )


def build_notion_dry_run(input_csv: Path) -> str:
    from .notion_sync import sync_csv_to_notion

    result = sync_csv_to_notion(input_csv, dry_run=True)
    lines = [result.message]
    for row in result.rows[:10]:
        lines.append(f"- {row.get('name', 'Untitled')}: {row.get('decision', 'unknown')}")
    return "\n".join(lines)


def _transcript_extract(transcript_text: str) -> list[str]:
    lines = [line.strip() for line in transcript_text.splitlines() if line.strip()]
    interesting = [
        line
        for line in lines
        if any(marker in line.lower() for marker in ["task", "grok", "ontology", "notion", "gradio", "hugging"])
    ]
    return (interesting or lines)[:8]


def build_project_update(transcript_text: str = "") -> str:
    extracted = _transcript_extract(transcript_text)
    source_lines = "\n".join(f"- {url}" for url in CHAT_SOURCE_URLS)
    extracted_lines = "\n".join(f"- {line}" for line in extracted) if extracted else "- No pasted transcript text supplied."
    return f"""# Ontofishing project update

## Private ChatGPT source links
{source_lines}

These links are private from the runtime environment. The cockpit preserves them as source references and does not fabricate unavailable private transcript content.

## Local implementation state
- Task 1: deterministic scoring and hard-reject coverage.
- Task 2: Grok worker import path with subscription-auth CLI boundary.
- Task 3: semantic/domain driver imports for Gemini and agy.
- Task 4: local ontology map export with typed weighted edges and bridge scores.
- Task 5: optional summarized Notion output with dry-run mode.
- Demo: Gradio end-user cockpit over the local CSV pipeline.

## Transcript-derived notes
{extracted_lines}
"""


def cockpit_status() -> dict[str, Any]:
    return {
        "project": "Ontofishing",
        "source_of_truth": "CSV",
        "chat_sources": len(CHAT_SOURCE_URLS),
        "external_services_on_load": False,
        "notion_default": "dry-run",
    }
