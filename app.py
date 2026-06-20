from __future__ import annotations

from pathlib import Path
import sys

import gradio as gr

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from bounty_wizard.cockpit import (
    build_demo_ontology,
    build_notion_dry_run,
    build_project_update,
    ensure_demo_ranked_csv,
    load_opportunity_rows,
    score_csv_for_cockpit,
)


WORK_DIR = Path("reports/cockpit")

CSS = """
:root {
  --otf-ink: #172026;
  --otf-muted: #5d6b70;
  --otf-line: #ccd8d5;
  --otf-teal: #0f8a7a;
  --otf-amber: #b26a00;
}
.gradio-container {
  max-width: 1220px !important;
  margin: 0 auto !important;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}
.otf-title h1 {
  color: var(--otf-ink);
  letter-spacing: 0;
  margin-bottom: 0.25rem;
}
.otf-title p, .otf-note {
  color: var(--otf-muted);
}
.otf-status {
  border: 1px solid var(--otf-line);
  padding: 12px;
  background: #f7fbfa;
}
button.primary {
  background: var(--otf-teal) !important;
  border-color: var(--otf-teal) !important;
}
"""


def _uploaded_path(uploaded_file: object | None) -> Path | None:
    if uploaded_file is None:
        return None
    name = getattr(uploaded_file, "name", None)
    return Path(name) if name else None


def load_demo_table() -> tuple[list[dict[str, str]], str]:
    result = ensure_demo_ranked_csv(WORK_DIR)
    return load_opportunity_rows(result.output_csv), result.summary


def score_upload(uploaded_file: object | None) -> tuple[list[dict[str, str]], str, str]:
    source = _uploaded_path(uploaded_file)
    if source is None:
        rows, summary = load_demo_table()
        return rows, f"{summary}\nNo upload supplied; loaded bundled example data.", ""
    result = score_csv_for_cockpit(source, WORK_DIR)
    return load_opportunity_rows(result.output_csv), result.summary, str(result.output_csv)


def export_ontology(uploaded_file: object | None) -> tuple[str, str, str]:
    source = _uploaded_path(uploaded_file)
    if source is None:
        ranked = ensure_demo_ranked_csv(WORK_DIR).output_csv
        message, html_path, edges_path = build_demo_ontology(WORK_DIR / "ontology", ranked)
    else:
        message, html_path, edges_path = build_demo_ontology(WORK_DIR / "ontology", source)
    return message, html_path.read_text(encoding="utf-8"), str(edges_path)


def notion_dry_run(uploaded_file: object | None) -> str:
    source = _uploaded_path(uploaded_file)
    if source is None:
        source = ensure_demo_ranked_csv(WORK_DIR).output_csv
    return build_notion_dry_run(source)


def compile_update(transcript_text: str) -> str:
    return build_project_update(transcript_text)


def create_app() -> gr.Blocks:
    with gr.Blocks(
        title="Ontofishing Cockpit",
        css=CSS,
        theme=gr.themes.Soft(primary_hue="teal", neutral_hue="slate"),
    ) as demo:
        gr.Markdown(
            """
# Ontofishing Cockpit
Local-first advisory cockpit for verifiable bounty, prize, challenge, and grant opportunities.
""",
            elem_classes=["otf-title"],
        )
        gr.Markdown(
            "CSV remains source-of-truth. External workers and Notion are optional outputs, not core dependencies.",
            elem_classes=["otf-status"],
        )

        upload = gr.File(label="Opportunity CSV", file_types=[".csv"])
        with gr.Tabs():
            with gr.Tab("Opportunities"):
                score_button = gr.Button("Score CSV", variant="primary")
                opportunity_table = gr.Dataframe(
                    headers=["name", "decision", "fit_score", "bridge_score", "official_url"],
                    label="Ranked opportunities",
                    wrap=True,
                    interactive=False,
                )
                score_status = gr.Textbox(label="Scoring status", lines=3)
                ranked_path = gr.Textbox(label="Ranked CSV path", interactive=False)
                score_button.click(score_upload, inputs=upload, outputs=[opportunity_table, score_status, ranked_path])
                demo.load(load_demo_table, outputs=[opportunity_table, score_status])

            with gr.Tab("Ontology"):
                ontology_button = gr.Button("Build ontology snapshot", variant="primary")
                ontology_status = gr.Textbox(label="Ontology export status")
                ontology_html = gr.HTML(label="ontology_snapshot.html")
                ontology_edges = gr.Textbox(label="ontology_edges.csv", interactive=False)
                ontology_button.click(export_ontology, inputs=upload, outputs=[ontology_status, ontology_html, ontology_edges])

            with gr.Tab("Notion Dry Run"):
                notion_button = gr.Button("Preview Notion output", variant="primary")
                notion_preview = gr.Textbox(label="Summarized rows only", lines=10)
                notion_button.click(notion_dry_run, inputs=upload, outputs=notion_preview)

            with gr.Tab("Project Update"):
                transcript = gr.Textbox(
                    label="Paste ChatGPT transcript exports here",
                    lines=10,
                    placeholder="Paste exported chat text when private ChatGPT links are not accessible to the runtime.",
                )
                update_button = gr.Button("Compile Ontofishing update", variant="primary")
                update_markdown = gr.Markdown(build_project_update())
                update_button.click(compile_update, inputs=transcript, outputs=update_markdown)

    return demo


app = create_app()


if __name__ == "__main__":
    app.launch()
