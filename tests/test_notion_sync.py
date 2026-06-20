from pathlib import Path
import csv

from bounty_wizard.notion_sync import sync_csv_to_notion


def write_ranked_csv(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "name",
                "official_url",
                "domain",
                "decision",
                "fit_score",
                "bridge_score",
                "payout_amount",
                "deadline",
                "deliverable",
                "status_evidence",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "name": "Memory Prize",
                "official_url": "https://example.com/memory",
                "domain": "AI safety",
                "decision": "execute_this_week",
                "fit_score": "91.5",
                "bridge_score": "84.7",
                "payout_amount": "$10,000",
                "deadline": "2026-12-31",
                "deliverable": "Reusable benchmark harness",
                "status_evidence": "Long raw evidence that should not be sent to Notion",
                "notes": "Private scratch notes that should not be sent to Notion",
            }
        )


def test_sync_skips_when_notion_env_is_missing(tmp_path: Path):
    ranked_csv = tmp_path / "ranked.csv"
    write_ranked_csv(ranked_csv)

    result = sync_csv_to_notion(ranked_csv, env={}, dry_run=False)

    assert result.status == "skipped"
    assert result.created == 0
    assert "NOTION_TOKEN" in result.message


def test_dry_run_summarizes_rows_without_api_calls_or_env(tmp_path: Path):
    ranked_csv = tmp_path / "ranked.csv"
    write_ranked_csv(ranked_csv)
    calls = []

    result = sync_csv_to_notion(
        ranked_csv,
        env={},
        dry_run=True,
        post_json=lambda payload, token: calls.append((payload, token)),
    )

    assert result.status == "dry_run"
    assert result.created == 0
    assert result.planned == 1
    assert calls == []


def test_live_sync_posts_summarized_pages_and_throttles(tmp_path: Path):
    ranked_csv = tmp_path / "ranked.csv"
    write_ranked_csv(ranked_csv)
    calls = []
    sleeps = []

    result = sync_csv_to_notion(
        ranked_csv,
        env={"NOTION_TOKEN": "test-token", "NOTION_PARENT_PAGE_ID": "parent-page-id"},
        dry_run=False,
        post_json=lambda payload, token: calls.append((payload, token)),
        sleep=lambda seconds: sleeps.append(seconds),
    )

    assert result.status == "synced"
    assert result.created == 1
    assert sleeps == [0.4]

    payload, token = calls[0]
    assert token == "test-token"
    assert payload["parent"] == {"page_id": "parent-page-id"}
    assert payload["properties"]["title"]["title"][0]["text"]["content"] == "Memory Prize"

    payload_text = str(payload)
    assert "Reusable benchmark harness" in payload_text
    assert "Long raw evidence" not in payload_text
    assert "Private scratch notes" not in payload_text
