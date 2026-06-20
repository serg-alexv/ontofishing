from pathlib import Path
import csv

from bounty_wizard.ontology import build_ontology_snapshot


def test_build_ontology_snapshot_scores_bridges_and_exports_files(tmp_path: Path):
    opportunities_csv = tmp_path / "opportunities.csv"
    opportunities_csv.write_text(
        "name,official_url,decision,deliverable\n"
        "Memory Prize,https://example.com/memory,execute_this_week,Reusable eval harness\n",
        encoding="utf-8",
    )
    concepts_csv = tmp_path / "concepts.csv"
    concepts_csv.write_text(
        "concept_id,label,category,artifact_reuse,description\n"
        "c-memory,Long-term memory,capability,direct,Agent memory systems\n"
        "c-evals,Evaluation harness,artifact,direct,Reusable benchmark harness\n"
        "c-privacy,Privacy review,risk,partial,Privacy threat modeling\n",
        encoding="utf-8",
    )
    edges_csv = tmp_path / "edges.csv"
    edges_csv.write_text(
        "source_type,source_id,target_type,target_id,edge_type,weight,evidence\n"
        "opportunity,Memory Prize,concept,c-memory,requires,0.9,Challenge asks for memory systems\n"
        "opportunity,Memory Prize,concept,c-evals,produces,0.8,Submission includes harness\n"
        "opportunity,Memory Prize,concept,c-privacy,mitigates,0.6,Privacy review improves safety\n"
        "concept,c-memory,concept,c-evals,enables,0.7,Memory systems need evaluation\n",
        encoding="utf-8",
    )

    result = build_ontology_snapshot(
        opportunities_csv=opportunities_csv,
        concepts_csv=concepts_csv,
        edges_csv=edges_csv,
        out_dir=tmp_path / "out",
    )

    assert result.opportunities[0].bridge_score == 84.7
    assert result.html_path.exists()
    assert result.edges_path.exists()

    exported_edges = list(csv.DictReader(result.edges_path.open(newline="", encoding="utf-8")))
    assert exported_edges[0]["edge_type"] == "requires"
    assert exported_edges[0]["weight"] == "0.9"

    html = result.html_path.read_text(encoding="utf-8")
    assert "Memory Prize" in html
    assert "bridge_score" in html
    assert "Long-term memory" in html
