from __future__ import annotations

import csv
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping


NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2026-03-11"
THROTTLE_SECONDS = 0.4
SUMMARY_FIELDS = [
    "official_url",
    "domain",
    "decision",
    "fit_score",
    "bridge_score",
    "payout_amount",
    "deadline",
    "deliverable",
]


@dataclass(frozen=True)
class NotionSyncResult:
    status: str
    planned: int
    created: int
    message: str
    rows: list[dict[str, str]] = field(default_factory=list)


def _trim(value: str, limit: int = 400) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def read_summarized_rows(input_csv: Path) -> list[dict[str, str]]:
    with input_csv.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    summaries: list[dict[str, str]] = []
    for row in rows:
        summary = {"name": _trim(row.get("name", ""), 180)}
        for field_name in SUMMARY_FIELDS:
            value = _trim(row.get(field_name, ""))
            if value:
                summary[field_name] = value
        summaries.append(summary)
    return summaries


def _paragraph(text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def build_page_payload(parent_page_id: str, row: dict[str, str]) -> dict[str, Any]:
    title = row.get("name") or "Untitled opportunity"
    lines = [
        f"{label}: {row[field_name]}"
        for field_name, label in [
            ("decision", "Decision"),
            ("fit_score", "Fit score"),
            ("bridge_score", "Bridge score"),
            ("domain", "Domain"),
            ("payout_amount", "Payout"),
            ("deadline", "Deadline"),
            ("official_url", "Official URL"),
            ("deliverable", "Deliverable"),
        ]
        if row.get(field_name)
    ]
    return {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": _trim(title, 2000)}}]
            }
        },
        "children": [_paragraph(line) for line in lines],
    }


def post_notion_page(payload: dict[str, Any], token: str) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        NOTION_API_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Notion API request failed with HTTP {exc.code}: {detail}") from exc


def sync_csv_to_notion(
    input_csv: Path,
    *,
    env: Mapping[str, str] | None = None,
    dry_run: bool = False,
    post_json: Callable[[dict[str, Any], str], Any] = post_notion_page,
    sleep: Callable[[float], None] = time.sleep,
    throttle_seconds: float = THROTTLE_SECONDS,
) -> NotionSyncResult:
    env_values = os.environ if env is None else env
    rows = read_summarized_rows(input_csv)

    if dry_run:
        return NotionSyncResult(
            status="dry_run",
            planned=len(rows),
            created=0,
            message=f"Dry run: would create {len(rows)} Notion page(s).",
            rows=rows,
        )

    token = env_values.get("NOTION_TOKEN")
    parent_page_id = env_values.get("NOTION_PARENT_PAGE_ID")
    if not token or not parent_page_id:
        return NotionSyncResult(
            status="skipped",
            planned=len(rows),
            created=0,
            message="Skipped Notion sync: NOTION_TOKEN and NOTION_PARENT_PAGE_ID are required.",
            rows=rows,
        )

    created = 0
    for row in rows:
        post_json(build_page_payload(parent_page_id, row), token)
        created += 1
        sleep(throttle_seconds)

    return NotionSyncResult(
        status="synced",
        planned=len(rows),
        created=created,
        message=f"Created {created} summarized Notion page(s).",
        rows=rows,
    )
