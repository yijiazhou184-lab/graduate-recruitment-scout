#!/usr/bin/env python3
"""Normalize and deduplicate a Graduate Recruitment Scout CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

from scout_common import (
    composite_key,
    merge_records,
    normalize_record,
    read_csv,
    validate_rows,
    write_csv_atomic,
)


def normalize_and_merge(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: list[dict[str, str]] = []
    by_id: dict[str, int] = {}
    by_composite: dict[tuple[str, str, str, str], int] = {}
    for raw in rows:
        record = normalize_record(raw)
        key = composite_key(record)
        index = by_id.get(record["record_id"])
        if index is None and all(key):
            index = by_composite.get(key)
        if index is None:
            index = len(merged)
            merged.append(record)
        else:
            merged[index] = merge_records(merged[index], record)
        current = merged[index]
        by_id[current["record_id"]] = index
        current_key = composite_key(current)
        if all(current_key):
            by_composite[current_key] = index
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    destination = parser.add_mutually_exclusive_group()
    destination.add_argument("--output", type=Path)
    destination.add_argument("--in-place", action="store_true")
    args = parser.parse_args()
    output = args.input if args.in_place else args.output or args.input.with_name(f"{args.input.stem}.normalized.csv")
    try:
        original = read_csv(args.input)
        merged = normalize_and_merge(original)
        errors = validate_rows(merged)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        write_csv_atomic(output, merged)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Normalized {len(original)} rows into {len(merged)} rows: {output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
