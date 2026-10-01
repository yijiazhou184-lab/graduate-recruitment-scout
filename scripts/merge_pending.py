#!/usr/bin/env python3
"""Merge pending snapshots into a Graduate Recruitment Scout database."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from normalize_jobs import normalize_and_merge
from scout_common import read_csv, validate_rows, write_csv_atomic


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", type=Path, default=Path("job-search/graduate-jobs.csv"))
    parser.add_argument("--pending-dir", type=Path, default=Path("job-search/pending"))
    parser.add_argument("--delete-merged", action="store_true", help="Delete snapshots only after a successful main write")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    snapshots = sorted(args.pending_dir.glob("*.csv")) if args.pending_dir.exists() else []
    try:
        rows = read_csv(args.main) if args.main.exists() else []
        original_count = len(rows)
        for snapshot in snapshots:
            rows.extend(read_csv(snapshot))
        merged = normalize_and_merge(rows)
        errors = validate_rows(merged)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        print(f"Main rows: {original_count}; snapshots: {len(snapshots)}; merged rows: {len(merged)}")
        if args.dry_run:
            return 0
        try:
            write_csv_atomic(args.main, merged)
        except PermissionError:
            args.pending_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            fallback = args.pending_dir / f"{stamp}-graduate-jobs.csv"
            write_csv_atomic(fallback, merged)
            print(f"Main database was locked; wrote complete snapshot: {fallback.resolve()}")
            return 2
        if args.delete_merged:
            for snapshot in snapshots:
                snapshot.unlink()
        print(f"Updated: {args.main.resolve()}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
