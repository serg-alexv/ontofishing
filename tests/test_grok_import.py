from pathlib import Path
import csv
import json

from scripts.grok_import_candidates import import_candidates


def test_import_candidates_adds_unique_urls(tmp_path: Path):
    payload = {
        "accepted": [
            {
                "name": "Example",
                "official_url": "https://example.com/challenge",
                "domain": "AI safety",
                "status": "open",
                "status_evidence": "Official page says open",
                "deadline": "2026-12-31",
                "payout_amount": "$1000",
                "payout_numeric_usd_estimate": 1000,
                "eligibility": "Independent researchers allowed",
                "deliverable": "Reproducible submission",
                "source_type": "official",
                "effort": "M",
            }
        ]
    }
    src = tmp_path / "grok.json"
    out = tmp_path / "opportunities.csv"
    src.write_text(json.dumps(payload), encoding="utf-8")

    import_candidates(src, out)
    import_candidates(src, out)

    rows = list(csv.DictReader(out.open(newline="", encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["name"] == "Example"
    assert rows[0]["official_url"] == "https://example.com/challenge"
