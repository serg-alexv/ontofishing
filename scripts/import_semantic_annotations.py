#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

EXTRA_COLUMNS = [
    "semantic_domain_tags",
    "semantic_summary",
    "independent_researcher_angle",
    "best_application_angle",
    "hidden_constraints",
    "questions_to_verify",
    "semantic_suggested_action",
    "semantic_confidence",
]


def load_annotations(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw.get("annotations", raw if isinstance(raw, list) else [])
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        url = str(item.get("official_url", "")).strip()
        if not name and not url:
            continue
        out[(name.lower(), url.lower())] = item
    return out


def as_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    return str(value)


def merge(input_csv: Path, annotations_json: Path, out_csv: Path) -> None:
    annotations = load_annotations(annotations_json)
    with input_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        base_fields = list(reader.fieldnames or [])

    fieldnames = base_fields + [c for c in EXTRA_COLUMNS if c not in base_fields]

    for row in rows:
        key = (row.get("name", "").strip().lower(), row.get("official_url", "").strip().lower())
        ann = annotations.get(key)
        if not ann:
            # URL-only fallback for minor name drift.
            url = row.get("official_url", "").strip().lower()
            matches = [v for (n, u), v in annotations.items() if u and u == url]
            ann = matches[0] if matches else {}
        row["semantic_domain_tags"] = as_cell(ann.get("domain_tags"))
        row["semantic_summary"] = as_cell(ann.get("semantic_summary"))
        row["independent_researcher_angle"] = as_cell(ann.get("independent_researcher_angle"))
        row["best_application_angle"] = as_cell(ann.get("best_application_angle"))
        row["hidden_constraints"] = as_cell(ann.get("hidden_constraints"))
        row["questions_to_verify"] = as_cell(ann.get("questions_to_verify"))
        row["semantic_suggested_action"] = as_cell(ann.get("suggested_action"))
        row["semantic_confidence"] = as_cell(ann.get("confidence"))

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge semantic driver annotations into an opportunities CSV.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("annotations_json", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    merge(args.input_csv, args.annotations_json, args.out)


if __name__ == "__main__":
    main()
