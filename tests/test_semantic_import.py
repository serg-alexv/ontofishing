import csv
import json
from pathlib import Path

from scripts.import_semantic_annotations import merge


def test_merge_semantic_annotations_by_name_and_url(tmp_path: Path):
    input_csv = tmp_path / "ranked.csv"
    input_csv.write_text(
        "name,official_url,decision\n"
        "ARC Prize,https://arcprize.org,execute_this_week\n",
        encoding="utf-8",
    )
    annotations = tmp_path / "ann.json"
    annotations.write_text(
        json.dumps({
            "annotations": [{
                "name": "ARC Prize",
                "official_url": "https://arcprize.org",
                "domain_tags": ["AGI", "reasoning"],
                "semantic_summary": "Reasoning benchmark opportunity.",
                "independent_researcher_angle": "Build a reproducible solver repo.",
                "best_application_angle": "Memory-guided program synthesis.",
                "hidden_constraints": ["High competition"],
                "questions_to_verify": ["Paper track rules"],
                "suggested_action": "execute_this_week",
                "confidence": 0.9,
            }]
        }),
        encoding="utf-8",
    )
    out_csv = tmp_path / "semantic.csv"
    merge(input_csv, annotations, out_csv)

    rows = list(csv.DictReader(out_csv.open(encoding="utf-8")))
    assert rows[0]["semantic_domain_tags"] == "AGI; reasoning"
    assert rows[0]["semantic_summary"] == "Reasoning benchmark opportunity."
    assert rows[0]["semantic_suggested_action"] == "execute_this_week"
