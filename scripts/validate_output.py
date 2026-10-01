#!/usr/bin/env python3
"""Validate a Graduate Recruitment Scout CSV database."""

from __future__ import annotations

import argparse
from pathlib import Path

from scout_common import read_csv, validate_rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()
    try:
        rows = read_csv(args.csv_file)
        errors = validate_rows(rows)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Valid database: {args.csv_file.resolve()} ({len(rows)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
