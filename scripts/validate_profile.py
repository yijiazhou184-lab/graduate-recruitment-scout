#!/usr/bin/env python3
"""Validate a Graduate Recruitment Scout profile."""

from __future__ import annotations

import argparse
from pathlib import Path

from scout_common import load_json, validate_profile_data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    args = parser.parse_args()
    try:
        errors = validate_profile_data(load_json(args.profile))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Valid profile: {args.profile.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
