from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

FIELDS = [
    "name", "official_url", "domain", "status", "status_evidence", "deadline",
    "payout_amount", "payout_numeric_usd_estimate", "eligibility", "deliverable",
    "jurisdiction_or_payment_constraints", "source_type", "effort", "domain_fit",
    "verification_strength", "payout_value", "probability_of_success", "portfolio_value",
    "deadline_accessibility", "low_admin_friction", "eligibility_risk", "payment_risk",
    "stale_status_risk", "competition_noise", "notes",
]


def load_json(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    # Grok `--output-format json` should be one JSON object. Keep a strict parser so
    # failures are visible instead of silently importing malformed findings.
    return json.loads(text)


def normalize_row(item: dict[str, Any]) -> dict[str, str]:
    row: dict[str, str] = {}
    for field in FIELDS:
        value = item.get(field, "")
        if value is None:
            value = ""
        row[field] = str(value)
    return row


def import_candidates(input_json: Path, output_csv: Path) -> None:
    payload = load_json(input_json)
    accepted = payload.get("accepted", [])
    if not isinstance(accepted, list):
        raise ValueError("Expected top-level key 'accepted' to be a list")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, str]] = []
    if output_csv.exists():
        with output_csv.open(newline="", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))

    seen = {r.get("official_url", "") for r in existing if r.get("official_url")}
    rows = existing[:]
    for item in accepted:
        if not isinstance(item, dict):
            continue
        url = str(item.get("official_url", ""))
        if not url or url in seen:
            continue
        rows.append(normalize_row(item))
        seen.add(url)

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import accepted Grok candidates into opportunities CSV")
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--out", type=Path, default=Path("data/opportunities_raw.csv"))
    args = parser.parse_args()
    import_candidates(args.input_json, args.out)
