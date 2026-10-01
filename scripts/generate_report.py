#!/usr/bin/env python3
"""Generate a concise Markdown report from a validated job database."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from scout_common import load_json, read_csv, validate_rows


def _score(record: dict[str, str]) -> int:
    try:
        return int(record.get("match_score", ""))
    except ValueError:
        return -1


def _deadline(record: dict[str, str]) -> date | None:
    value = record.get("deadline", "")
    if len(value) != 10:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _escape(value: str) -> str:
    return (value or "").replace("|", "\\|").replace("\n", " ").strip()


def _role_link(record: dict[str, str]) -> str:
    label = _escape(record.get("role_title", "Untitled role"))
    url = record.get("apply_url") or record.get("official_source_url") or record.get("source_url")
    return f"[{label}]({url})" if url else label


def _table(records: list[dict[str, str]]) -> list[str]:
    lines = ["| Company | Role | Location | Score | Deadline | Why |", "|---|---|---|---:|---|---|"]
    for record in records:
        location = ", ".join(value for value in (record.get("city", ""), record.get("country", "")) if value)
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape(record.get("company", "")),
                    _role_link(record),
                    _escape(location),
                    _escape(record.get("match_score", "")),
                    _escape(record.get("deadline", "")),
                    _escape(record.get("match_reason", "")),
                ]
            )
            + " |"
        )
    return lines


def build_report(rows: list[dict[str, str]], today: date, limit: int, warning_days: int) -> str:
    counts = Counter(row.get("change_type", "") for row in rows)
    eligible = [row for row in rows if row.get("application_status") == "eligible"]
    recommendations = [row for row in eligible if row.get("change_type") in {"new", "updated", "deadline_soon"}]
    recommendations.sort(key=lambda row: (_score(row), row.get("posted_date", "")), reverse=True)
    recommendations = recommendations[:limit]
    deadline_limit = today + timedelta(days=warning_days)
    urgent = [row for row in eligible if (deadline := _deadline(row)) and today <= deadline <= deadline_limit]
    urgent.sort(key=lambda row: _deadline(row) or date.max)
    pending = [row for row in rows if row.get("application_status") == "pending_verification"]
    blocked = [row for row in rows if row.get("verification_status") == "blocked"]

    lines = [
        f"# Graduate job update — {today.isoformat()}",
        "",
        "## Summary",
        "",
        f"- New: {counts['new']}",
        f"- Updated: {counts['updated']}",
        f"- Deadline soon: {counts['deadline_soon']}",
        f"- Closed: {counts['closed']}",
        f"- Offline: {counts['offline']}",
        f"- Total eligible in database: {len(eligible)}",
        "",
        "## Recommended actions",
        "",
    ]
    lines.extend(_table(recommendations) if recommendations else ["No new or materially changed eligible roles in this database snapshot."])
    lines.extend(["", f"## Deadlines within {warning_days} days", ""])
    lines.extend(_table(urgent) if urgent else ["No verified deadlines in the warning window."])
    lines.extend(["", "## Pending verification", ""])
    if pending:
        for row in pending:
            lines.append(f"- {_escape(row.get('company', ''))} — {_role_link(row)}: {_escape(row.get('verification_reason') or row.get('risk_flags'))}")
    else:
        lines.append("No pending records.")
    if blocked:
        lines.extend(["", "## Source limitations", ""])
        for row in blocked:
            lines.append(f"- {_escape(row.get('source_name') or row.get('company', ''))}: {_escape(row.get('verification_reason') or row.get('risk_flags'))}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date in YYYY-MM-DD")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        today = datetime.strptime(args.date, "%Y-%m-%d").date()
        rows = read_csv(args.csv_file)
        errors = validate_rows(rows)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        limit = 12
        warning_days = 7
        if args.profile:
            output_config = load_json(args.profile).get("output", {})
            limit = int(output_config.get("recommendation_count", limit))
            warning_days = int(output_config.get("deadline_warning_days", warning_days))
        report = build_report(rows, today, limit, warning_days)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding="utf-8")
            print(f"Wrote report: {args.output.resolve()}")
        else:
            print(report, end="")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
