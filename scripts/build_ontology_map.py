#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from bounty_wizard.ontology import build_ontology_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local ontology snapshot from CSV files.")
    parser.add_argument(
        "--opportunities",
        type=Path,
        default=Path("data/ranked_opportunities.csv"),
        help="CSV source of truth for opportunities.",
    )
    parser.add_argument("--concepts", type=Path, default=Path("data/concepts.example.csv"))
    parser.add_argument("--edges", type=Path, default=Path("data/ontology_edges.example.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("reports/ontology"))
    args = parser.parse_args()

    result = build_ontology_snapshot(
        opportunities_csv=args.opportunities,
        concepts_csv=args.concepts,
        edges_csv=args.edges,
        out_dir=args.out_dir,
    )
    print(result.html_path)
    print(result.edges_path)


if __name__ == "__main__":
    main()
