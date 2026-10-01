from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from generate_report import build_report  # noqa: E402
from normalize_jobs import normalize_and_merge  # noqa: E402
from scout_common import (  # noqa: E402
    CSV_FIELDS,
    canonicalize_url,
    load_json,
    merge_records,
    normalize_record,
    stable_record_id,
    validate_profile_data,
    validate_rows,
)


def make_record(**overrides: str) -> dict[str, str]:
    record = {field: "" for field in CSV_FIELDS}
    record.update(
        {
            "company": "Example Systems",
            "role_title": "Graduate Product Analyst",
            "normalized_role_title": "Graduate Product Analyst",
            "city": "Shanghai",
            "country": "China",
            "employment_type": "full-time",
            "target_graduation": "2027",
            "application_status": "eligible",
            "verification_status": "verified",
            "page_status": "active",
            "source_type": "official_employer",
            "source_name": "Example Careers",
            "source_url": "https://careers.example.com/jobs/42",
            "official_source_url": "https://careers.example.com/jobs/42",
            "apply_url": "https://careers.example.com/jobs/42/apply",
            "first_seen": "2026-09-01",
            "last_verified": "2026-09-15",
            "source_checked_at": "2026-09-15T09:00:00+08:00",
            "change_type": "new",
            "match_score": "82",
            "match_reason": "Primary role and preferred location.",
            "eligibility_evidence": "Graduate intake accepts 2027 graduates.",
        }
    )
    record.update(overrides)
    record = normalize_record(record)
    if not overrides.get("record_id"):
        record["record_id"] = stable_record_id(record)
    return record


class UrlAndIdentityTests(unittest.TestCase):
    def test_canonical_url_removes_tracking_and_sorts_query(self) -> None:
        value = "HTTPS://Example.COM/jobs/42/?utm_source=newsletter&b=2&a=1#apply"
        self.assertEqual(canonicalize_url(value), "https://example.com/jobs/42?a=1&b=2")

    def test_tracking_parameters_do_not_change_record_id(self) -> None:
        first = make_record(apply_url="https://careers.example.com/apply?id=42&utm_source=a")
        second = make_record(apply_url="https://careers.example.com/apply?utm_medium=b&id=42")
        self.assertEqual(stable_record_id(first), stable_record_id(second))


class MergeTests(unittest.TestCase):
    def test_official_source_wins_and_history_is_preserved(self) -> None:
        board = make_record(
            record_id="job_1111111111111111",
            source_type="trusted_job_board",
            source_url="https://jobs.example.net/42",
            official_source_url="",
            apply_url="https://jobs.example.net/42/apply",
            first_seen="2026-08-20",
            last_verified="2026-09-10",
            deadline="2026-10-01",
        )
        official = make_record(
            record_id="job_2222222222222222",
            first_seen="2026-09-01",
            last_verified="2026-09-15",
            deadline="2026-10-03",
        )
        merged = merge_records(board, official)
        self.assertEqual(merged["record_id"], "job_1111111111111111")
        self.assertEqual(merged["source_type"], "official_employer")
        self.assertEqual(merged["first_seen"], "2026-08-20")
        self.assertEqual(merged["last_verified"], "2026-09-15")
        self.assertIn("CONFLICT_DEADLINE", merged["risk_flags"])

    def test_composite_duplicate_is_merged(self) -> None:
        first = make_record(
            record_id="job_1111111111111111",
            source_type="trusted_job_board",
            source_url="https://jobs.example.net/one",
            official_source_url="",
            apply_url="https://jobs.example.net/one/apply",
        )
        second = make_record(
            record_id="job_2222222222222222",
            source_url="https://careers.example.com/two",
            official_source_url="https://careers.example.com/two",
            apply_url="https://careers.example.com/two/apply",
        )
        merged = normalize_and_merge([first, second])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["source_type"], "official_employer")


class ValidationTests(unittest.TestCase):
    def test_example_and_preset_profiles_are_valid(self) -> None:
        for profile in (
            SKILL_ROOT / "assets" / "profile.example.json",
            SKILL_ROOT / "presets" / "china-2027-ai-product-hk-tech.json",
        ):
            with self.subTest(profile=profile.name):
                self.assertEqual(validate_profile_data(load_json(profile)), [])

    def test_invalid_weight_total_is_rejected(self) -> None:
        profile = load_json(SKILL_ROOT / "assets" / "profile.example.json")
        profile["ranking"]["weights"]["freshness"] = 6
        self.assertIn("ranking weights must sum to 100, got 101", validate_profile_data(profile))

    def test_invalid_group_quota_returns_an_error_instead_of_crashing(self) -> None:
        profile = load_json(SKILL_ROOT / "assets" / "profile.example.json")
        profile["output"]["recommendation_groups"] = [
            {"name": "Example", "quota": "four", "company_types": ["technology"]}
        ]
        errors = validate_profile_data(profile)
        self.assertTrue(any(".quota must be between 0 and 100" in error for error in errors))

    def test_unsupported_source_is_rejected(self) -> None:
        profile = load_json(SKILL_ROOT / "assets" / "profile.example.json")
        profile["sources"]["final_source_priority"] = ["unknown_source"]
        errors = validate_profile_data(profile)
        self.assertIn("sources.final_source_priority contains an unsupported source", errors)

    def test_valid_record_passes(self) -> None:
        self.assertEqual(validate_rows([make_record()]), [])

    def test_unverified_record_cannot_be_eligible(self) -> None:
        errors = validate_rows([make_record(verification_status="unverified")])
        self.assertTrue(any("eligible records" in error for error in errors))


class WorkspaceAndReportTests(unittest.TestCase):
    def test_initializer_does_not_overwrite_profile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "job-search"
            script = SCRIPTS / "init_workspace.py"
            first = subprocess.run(
                [sys.executable, str(script), "--root", str(root)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            profile = root / "profile.json"
            original = json.loads(profile.read_text(encoding="utf-8"))
            original["candidate"]["preferred_locations"] = ["Private Test Location"]
            profile.write_text(json.dumps(original), encoding="utf-8")
            second = subprocess.run(
                [sys.executable, str(script), "--root", str(root)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            kept = json.loads(profile.read_text(encoding="utf-8"))
            self.assertEqual(kept["candidate"]["preferred_locations"], ["Private Test Location"])

    def test_report_contains_actionable_sections(self) -> None:
        record = make_record(deadline="2026-09-20")
        report = build_report([record], date(2026, 9, 15), limit=12, warning_days=7)
        self.assertIn("Graduate job update — 2026-09-15", report)
        self.assertIn("Recommended actions", report)
        self.assertIn("Deadlines within 7 days", report)
        self.assertIn("Graduate Product Analyst", report)


if __name__ == "__main__":
    unittest.main()
