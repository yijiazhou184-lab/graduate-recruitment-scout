"""Shared, dependency-free helpers for Graduate Recruitment Scout."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


CSV_FIELDS = [
    "record_id",
    "company",
    "watchlist_match",
    "role_title",
    "normalized_role_title",
    "role_family",
    "role_priority",
    "company_type",
    "company_scale_bucket",
    "business_focus",
    "background_fit",
    "location_priority",
    "department",
    "city",
    "country",
    "employment_type",
    "target_graduation",
    "responsibilities",
    "requirements",
    "keywords",
    "salary",
    "posted_date",
    "deadline",
    "application_status",
    "verification_status",
    "verification_reason",
    "page_status",
    "source_type",
    "source_name",
    "discovered_via",
    "source_url",
    "official_source_url",
    "apply_url",
    "first_seen",
    "last_verified",
    "source_checked_at",
    "change_type",
    "match_score",
    "match_reason",
    "eligibility_evidence",
    "location_evidence",
    "deadline_evidence",
    "classification_reason_codes",
    "risk_flags",
    "notes",
]

APPLICATION_STATUSES = {
    "eligible",
    "pending_verification",
    "ineligible",
    "closed",
    "offline",
}
VERIFICATION_STATUSES = {"verified", "partially_verified", "unverified", "blocked"}
PAGE_STATUSES = {"", "active", "closed", "removed", "blocked", "login_required", "unknown"}
SOURCE_TYPES = {
    "official_employer",
    "official_ats",
    "trusted_job_board",
    "community_lead",
    "search_engine",
}
CHANGE_TYPES = {"new", "updated", "deadline_soon", "closed", "offline", "unchanged"}
NOTIFICATION_POLICIES = {"action_only", "always", "never"}
WEIGHT_KEYS = {"role", "business", "employer", "candidate", "location", "freshness"}
SOURCE_PRIORITY = {
    "official_employer": 5,
    "official_ats": 4,
    "trusted_job_board": 3,
    "community_lead": 2,
    "search_engine": 1,
}

_TRACKING_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "referrer",
    "source",
    "trk",
    "trackingid",
}
_DATE_RE = re.compile(r"^\d{4}-\d{2}(?:-\d{2})?$")
_HTTP_RE = re.compile(r"^https?://", re.IGNORECASE)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def normalize_text(value: object) -> str:
    text = "" if value is None else str(value)
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def normalize_key(value: object) -> str:
    return re.sub(r"[\W_]+", "", normalize_text(value).casefold(), flags=re.UNICODE)


def canonicalize_url(value: object) -> str:
    raw = normalize_text(value)
    if not raw or not _HTTP_RE.match(raw):
        return raw
    try:
        parts = urlsplit(raw)
        host = (parts.hostname or "").lower()
        if not host:
            return raw
        port = parts.port
        if port and not ((parts.scheme.lower() == "http" and port == 80) or (parts.scheme.lower() == "https" and port == 443)):
            host = f"{host}:{port}"
        path = re.sub(r"/{2,}", "/", parts.path or "/")
        if path != "/":
            path = path.rstrip("/")
        query_items = []
        for key, item_value in parse_qsl(parts.query, keep_blank_values=False):
            lowered = key.casefold()
            if lowered.startswith("utm_") or lowered in _TRACKING_KEYS:
                continue
            query_items.append((key, item_value))
        query = urlencode(sorted(query_items), doseq=True)
        return urlunsplit((parts.scheme.lower(), host, path, query, ""))
    except ValueError:
        return raw


def stable_record_id(record: dict[str, str]) -> str:
    for field in ("apply_url", "official_source_url", "source_url"):
        candidate = canonicalize_url(record.get(field, ""))
        if _HTTP_RE.match(candidate):
            material = f"url:{candidate}"
            break
    else:
        material = "|".join(
            [
                "composite",
                normalize_key(record.get("company", "")),
                normalize_key(record.get("normalized_role_title") or record.get("role_title", "")),
                normalize_key(record.get("city", "")),
                normalize_key(record.get("country", "")),
            ]
        )
    return "job_" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def composite_key(record: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        normalize_key(record.get("company", "")),
        normalize_key(record.get("normalized_role_title") or record.get("role_title", "")),
        normalize_key(record.get("city", "")),
        normalize_key(record.get("country", "")),
    )


def normalize_record(raw: dict[str, object]) -> dict[str, str]:
    record = {field: normalize_text(raw.get(field, "")) for field in CSV_FIELDS}
    record["normalized_role_title"] = normalize_text(
        record["normalized_role_title"] or record["role_title"]
    )
    for field in ("source_url", "official_source_url", "apply_url"):
        record[field] = canonicalize_url(record[field])
    if record["source_type"] in {"official_employer", "official_ats"} and not record["official_source_url"]:
        record["official_source_url"] = record["source_url"]
    if not record["record_id"]:
        record["record_id"] = stable_record_id(record)
    return record


def _date_sort_key(value: str) -> tuple[int, int, int]:
    if not value:
        return (0, 0, 0)
    parts = value[:10].split("-")
    try:
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 else 0
        day = int(parts[2]) if len(parts) > 2 else 0
        return (year, month, day)
    except (ValueError, IndexError):
        return (0, 0, 0)


def _join_unique(*values: str) -> str:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        for part in re.split(r"\s*;\s*", value or ""):
            part = normalize_text(part)
            key = part.casefold()
            if part and key not in seen:
                seen.add(key)
                result.append(part)
    return "; ".join(result)


def merge_records(existing: dict[str, str], incoming: dict[str, str]) -> dict[str, str]:
    """Merge a duplicate into an existing record while preserving historical identity."""
    left = normalize_record(existing)
    right = normalize_record(incoming)
    preferred, fallback = (
        (right, left)
        if SOURCE_PRIORITY.get(right["source_type"], 0) > SOURCE_PRIORITY.get(left["source_type"], 0)
        else (left, right)
    )
    merged = {field: preferred.get(field, "") or fallback.get(field, "") for field in CSV_FIELDS}

    merged["record_id"] = left["record_id"] or right["record_id"] or stable_record_id(merged)
    first_values = [value for value in (left["first_seen"], right["first_seen"]) if value]
    last_values = [value for value in (left["last_verified"], right["last_verified"]) if value]
    if first_values:
        merged["first_seen"] = min(first_values, key=_date_sort_key)
    if last_values:
        merged["last_verified"] = max(last_values, key=_date_sort_key)

    conflict_fields = []
    for field in ("deadline", "target_graduation", "employment_type"):
        if left[field] and right[field] and normalize_key(left[field]) != normalize_key(right[field]):
            conflict_fields.append(f"CONFLICT_{field.upper()}")
    merged["risk_flags"] = _join_unique(left["risk_flags"], right["risk_flags"], *conflict_fields)
    merged["notes"] = _join_unique(left["notes"], right["notes"])
    merged["classification_reason_codes"] = _join_unique(
        left["classification_reason_codes"], right["classification_reason_codes"]
    )
    merged["discovered_via"] = _join_unique(left["discovered_via"], right["discovered_via"])
    return merged


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        actual = reader.fieldnames or []
        if actual != CSV_FIELDS:
            raise ValueError(
                f"{path}: CSV header mismatch. Expected {len(CSV_FIELDS)} fields in the documented order."
            )
        return [{field: row.get(field, "") or "" for field in CSV_FIELDS} for row in reader]


def write_csv_atomic(path: Path, rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def validate_profile_data(data: dict) -> list[str]:
    errors: list[str] = []

    def string_list(value: object, path: str, *, non_empty: bool = False) -> bool:
        valid = isinstance(value, list) and (not non_empty or bool(value))
        if valid:
            valid = all(isinstance(item, str) and bool(normalize_text(item)) for item in value)
        if not valid:
            qualifier = "non-empty " if non_empty else ""
            errors.append(f"{path} must be a {qualifier}list of non-empty strings")
        elif len({normalize_text(item).casefold() for item in value}) != len(value):
            errors.append(f"{path} must not contain duplicates")
            valid = False
        return valid

    required_sections = {
        "version",
        "candidate",
        "roles",
        "business_priorities",
        "companies",
        "sources",
        "search",
        "ranking",
        "output",
    }
    missing = sorted(required_sections - set(data))
    if missing:
        errors.append(f"missing top-level keys: {', '.join(missing)}")
    unexpected = sorted(set(data) - required_sections)
    if unexpected:
        errors.append(f"unexpected top-level keys: {', '.join(unexpected)}")
    if data.get("version") != 1:
        errors.append("version must be 1")

    candidate = data.get("candidate", {})
    if not isinstance(candidate, dict):
        errors.append("candidate must be an object")
    else:
        years = candidate.get("graduation_years")
        if not isinstance(years, list) or not years:
            errors.append("candidate.graduation_years must be a non-empty list")
        elif any(not isinstance(year, str) or not re.fullmatch(r"\d{4}", year) for year in years):
            errors.append("candidate.graduation_years must contain four-digit strings")
        for field in ("preferred_locations", "background_signals", "languages"):
            string_list(candidate.get(field), f"candidate.{field}")
        if not isinstance(candidate.get("work_authorization_notes"), str):
            errors.append("candidate.work_authorization_notes must be a string")

    roles = data.get("roles", {})
    if not isinstance(roles, dict):
        errors.append("roles must be an object")
    else:
        string_list(roles.get("primary"), "roles.primary", non_empty=True)
        string_list(roles.get("secondary"), "roles.secondary")
        string_list(roles.get("exclude"), "roles.exclude")

    string_list(data.get("business_priorities"), "business_priorities")

    companies = data.get("companies", {})
    if not isinstance(companies, dict) or not isinstance(companies.get("watchlist"), list):
        errors.append("companies.watchlist must be a list")
    else:
        string_list(companies.get("priority_segments"), "companies.priority_segments")
        for index, company in enumerate(companies["watchlist"]):
            if not isinstance(company, dict) or not normalize_text(company.get("name", "")):
                errors.append(f"companies.watchlist[{index}].name is required")
                continue
            string_list(company.get("aliases"), f"companies.watchlist[{index}].aliases")
            string_list(company.get("business_lines"), f"companies.watchlist[{index}].business_lines")

    sources = data.get("sources", {})
    if not isinstance(sources, dict):
        errors.append("sources must be an object")
    else:
        final_sources = sources.get("final_source_priority")
        discovery_sources = sources.get("discovery_sources")
        if string_list(final_sources, "sources.final_source_priority", non_empty=True):
            allowed = {"official_employer", "official_ats", "trusted_job_board"}
            if any(value not in allowed for value in final_sources):
                errors.append("sources.final_source_priority contains an unsupported source")
        if string_list(discovery_sources, "sources.discovery_sources", non_empty=True):
            allowed = {"search_engine", "trusted_job_board", "community_lead"}
            if any(value not in allowed for value in discovery_sources):
                errors.append("sources.discovery_sources contains an unsupported source")

    weights = data.get("ranking", {}).get("weights", {}) if isinstance(data.get("ranking"), dict) else {}
    if not isinstance(weights, dict) or set(weights) != WEIGHT_KEYS:
        errors.append("ranking.weights must contain exactly role, business, employer, candidate, location, freshness")
    elif any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in weights.values()):
        errors.append("ranking weights must be non-negative integers")
    elif sum(weights.values()) != 100:
        errors.append(f"ranking weights must sum to 100, got {sum(weights.values())}")

    search = data.get("search", {})
    if not isinstance(search, dict):
        errors.append("search must be an object")
    else:
        string_list(search.get("languages"), "search.languages", non_empty=True)
        stop_rounds = search.get("consecutive_empty_rounds_before_stop")
        if isinstance(stop_rounds, bool) or not isinstance(stop_rounds, int) or not 1 <= stop_rounds <= 10:
            errors.append("search.consecutive_empty_rounds_before_stop must be between 1 and 10")
        for field in ("include_internships", "require_full_time"):
            if not isinstance(search.get(field), bool):
                errors.append(f"search.{field} must be a boolean")

    output = data.get("output", {})
    if not isinstance(output, dict):
        errors.append("output must be an object")
    else:
        if not isinstance(output.get("workspace_dir"), str) or not normalize_text(output.get("workspace_dir")):
            errors.append("output.workspace_dir must be a non-empty string")
        if output.get("notification_policy") not in NOTIFICATION_POLICIES:
            errors.append("output.notification_policy must be action_only, always, or never")
        count = output.get("recommendation_count")
        if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 100:
            errors.append("output.recommendation_count must be between 1 and 100")
        warning_days = output.get("deadline_warning_days")
        if isinstance(warning_days, bool) or not isinstance(warning_days, int) or not 0 <= warning_days <= 90:
            errors.append("output.deadline_warning_days must be between 0 and 90")
        groups = output.get("recommendation_groups")
        if not isinstance(groups, list):
            errors.append("output.recommendation_groups must be a list")
        else:
            quota_total = 0
            for index, group in enumerate(groups):
                if not isinstance(group, dict):
                    errors.append(f"output.recommendation_groups[{index}] must be an object")
                    continue
                if not isinstance(group.get("name"), str) or not normalize_text(group.get("name")):
                    errors.append(f"output.recommendation_groups[{index}].name is required")
                quota = group.get("quota")
                if isinstance(quota, bool) or not isinstance(quota, int) or not 0 <= quota <= 100:
                    errors.append(f"output.recommendation_groups[{index}].quota must be between 0 and 100")
                else:
                    quota_total += quota
                string_list(
                    group.get("company_types"),
                    f"output.recommendation_groups[{index}].company_types",
                    non_empty=True,
                )
            if isinstance(count, int) and not isinstance(count, bool) and quota_total > count:
                errors.append("recommendation group quotas cannot exceed recommendation_count")
    return errors


def _valid_partial_date(value: str) -> bool:
    if not value:
        return True
    if not _DATE_RE.fullmatch(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d" if len(value) == 10 else "%Y-%m")
        return True
    except ValueError:
        return False


def validate_record(record: dict[str, str], row_number: int | None = None) -> list[str]:
    prefix = f"row {row_number}: " if row_number is not None else ""
    errors: list[str] = []
    for field in ("record_id", "company", "role_title", "application_status", "verification_status", "source_type", "source_url", "first_seen", "last_verified", "change_type"):
        if not normalize_text(record.get(field, "")):
            errors.append(f"{prefix}{field} is required")
    if record.get("record_id") and not re.fullmatch(r"job_[0-9a-f]{16}", record["record_id"]):
        errors.append(f"{prefix}record_id must match job_<16 lowercase hex characters>")
    for field, allowed in (
        ("application_status", APPLICATION_STATUSES),
        ("verification_status", VERIFICATION_STATUSES),
        ("page_status", PAGE_STATUSES),
        ("source_type", SOURCE_TYPES),
        ("change_type", CHANGE_TYPES),
    ):
        if record.get(field, "") not in allowed:
            errors.append(f"{prefix}{field} has an unsupported value: {record.get(field, '')!r}")
    for field in ("posted_date", "deadline", "first_seen", "last_verified"):
        if not _valid_partial_date(record.get(field, "")):
            errors.append(f"{prefix}{field} must be YYYY-MM-DD or YYYY-MM")
    for field in ("source_url", "official_source_url", "apply_url"):
        value = record.get(field, "")
        if value and not _HTTP_RE.match(value):
            errors.append(f"{prefix}{field} must use http or https")
    score = record.get("match_score", "")
    if score:
        try:
            numeric_score = int(score)
            if not 0 <= numeric_score <= 100:
                raise ValueError
        except ValueError:
            errors.append(f"{prefix}match_score must be an integer from 0 to 100")
    if record.get("application_status") == "eligible" and record.get("verification_status") not in {"verified", "partially_verified"}:
        errors.append(f"{prefix}eligible records must be verified or partially_verified")
    if record.get("source_type") in {"official_employer", "official_ats"} and not record.get("official_source_url"):
        errors.append(f"{prefix}official sources require official_source_url")
    return errors


def validate_rows(rows: Iterable[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_composites: set[tuple[str, str, str, str]] = set()
    for row_number, row in enumerate(rows, start=2):
        errors.extend(validate_record(row, row_number))
        record_id = row.get("record_id", "")
        if record_id in seen_ids:
            errors.append(f"row {row_number}: duplicate record_id {record_id}")
        seen_ids.add(record_id)
        key = composite_key(row)
        if all(key) and key in seen_composites:
            errors.append(f"row {row_number}: duplicate company + role + city + country")
        seen_composites.add(key)
    return errors
