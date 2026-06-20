from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .models import Opportunity
from .scoring import score_opportunity


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    floats = [
        "payout_numeric_usd_estimate",
        "domain_fit",
        "verification_strength",
        "payout_value",
        "probability_of_success",
        "portfolio_value",
        "deadline_accessibility",
        "low_admin_friction",
        "eligibility_risk",
        "payment_risk",
        "stale_status_risk",
        "competition_noise",
    ]
    for k in floats:
        if k in row and row[k] not in (None, ""):
            row[k] = float(row[k])
    return row


def score_csv(input_path: Path, output_path: Path) -> None:
    with input_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        try:
            opportunity = Opportunity.model_validate(_normalize_row(row))
            result = score_opportunity(opportunity)
            out = row | {
                "fit_score": result.score,
                "decision": result.decision,
                "hard_reject": result.hard_reject,
                "rejection_or_warning_reasons": " | ".join(result.reasons),
            }
        except ValidationError as e:
            out = row | {
                "fit_score": 0,
                "decision": "reject",
                "hard_reject": True,
                "rejection_or_warning_reasons": f"Row {idx} validation error: {e}",
            }
        out_rows.append(out)

    fieldnames = sorted({k for r in out_rows for k in r.keys()})
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted(out_rows, key=lambda r: float(r.get("fit_score") or 0), reverse=True))


def advise(input_path: Path) -> None:
    with input_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault(row.get("decision", "unknown"), []).append(row)
    print(json.dumps({k: [r.get("name", "") for r in v[:10]] for k, v in groups.items()}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="bounty-wizard")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_score = sub.add_parser("score")
    p_score.add_argument("input_csv", type=Path)
    p_score.add_argument("--out", type=Path, default=Path("data/ranked_opportunities.csv"))

    p_advise = sub.add_parser("advise")
    p_advise.add_argument("input_csv", type=Path)

    args = parser.parse_args()
    if args.cmd == "score":
        score_csv(args.input_csv, args.out)
    elif args.cmd == "advise":
        advise(args.input_csv)


if __name__ == "__main__":
    main()
