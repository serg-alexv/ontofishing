#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from bounty_wizard.notion_sync import sync_csv_to_notion


def main() -> None:
    parser = argparse.ArgumentParser(description="Optionally push summarized opportunity rows to Notion.")
    parser.add_argument("input_csv", type=Path, help="Ranked or annotated opportunities CSV.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would sync without calling Notion.")
    args = parser.parse_args()

    result = sync_csv_to_notion(args.input_csv, dry_run=args.dry_run)
    print(result.message)
    if args.dry_run:
        for row in result.rows:
            print(f"- {row.get('name', 'Untitled opportunity')}: {row.get('decision', 'unknown')}")


if __name__ == "__main__":
    main()
