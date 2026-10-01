#!/usr/bin/env python3
"""Initialize a Graduate Recruitment Scout workspace without overwriting data."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from scout_common import write_csv_atomic


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("job-search"), help="Workspace directory")
    parser.add_argument("--profile-template", type=Path, help="Optional profile or preset to copy")
    args = parser.parse_args()

    root = args.root.resolve()
    skill_root = Path(__file__).resolve().parents[1]
    template = (args.profile_template or skill_root / "assets" / "profile.example.json").resolve()
    if not template.is_file():
        parser.error(f"profile template does not exist: {template}")

    root.mkdir(parents=True, exist_ok=True)
    (root / "daily").mkdir(exist_ok=True)
    (root / "pending").mkdir(exist_ok=True)

    created: list[Path] = []
    skipped: list[Path] = []
    profile = root / "profile.json"
    database = root / "graduate-jobs.csv"
    if profile.exists():
        skipped.append(profile)
    else:
        shutil.copyfile(template, profile)
        created.append(profile)
    if database.exists():
        skipped.append(database)
    else:
        write_csv_atomic(database, [])
        created.append(database)

    print(f"Workspace: {root}")
    for path in created:
        print(f"created: {path}")
    for path in skipped:
        print(f"kept existing: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
