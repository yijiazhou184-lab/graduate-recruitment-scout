---
name: graduate-recruitment-scout
description: Discover, verify, deduplicate, rank, and track full-time graduate and new-grad jobs from public sources. Use for campus-recruitment scans, graduate-job watchlists, recurring job radars, and evidence-backed job databases; do not use for experienced-hire searches, internships unless explicitly enabled, or submitting applications.
metadata:
  short-description: Build a verified graduate-job radar
---

# Graduate Recruitment Scout

Turn public graduate-recruitment pages into a traceable, deduplicated job database and an action-focused update report.

## Start here

1. Resolve the active profile in this order: instructions in the current request, a user-supplied profile path, `<workspace>/profile.json`, then [the example profile](assets/profile.example.json). Never silently treat example values as user facts.
2. If the workspace is missing, run `python scripts/init_workspace.py --root <workspace>` and tell the user which template values still need customization.
3. Read only the references needed for the requested operation:
   - For profile fields or presets, read [configuration](references/configuration.md).
   - For web discovery and verification, read [source policy](references/source-policy.md) and [search playbook](references/search-playbook.md).
   - For scoring or recommendations, read [ranking policy](references/ranking-policy.md).
   - For database writes, validation, merging, or reports, read [output schema](references/output-schema.md).

## Required workflow

- Use current web search and open the actual job-detail page. Search snippets and community posts are leads, not final evidence.
- Apply hard eligibility filters before scoring. Missing graduation eligibility, employment type, location, or application state makes a role `pending_verification`, not eligible.
- Prefer official employer or official ATS pages. Keep discovery provenance, but replace the final source and application URL with the official page when found.
- Record only facts visible on an opened source. Leave missing fields empty and explain material uncertainty in `risk_flags`.
- Normalize and deduplicate records with `scripts/normalize_jobs.py`; do not rewrite stable `first_seen` values.
- Validate the complete CSV with `scripts/validate_output.py` before presenting counts or recommendations.
- Generate a deterministic Markdown summary with `scripts/generate_report.py` when a daily or incremental report is requested.
- Stop after the configured number of consecutive search rounds produces no new eligible records. Report blocked sources once instead of repeatedly retrying them.

## Safety and boundaries

- Do not log in, bypass access controls or CAPTCHAs, submit applications, or disclose personal profile data without explicit authorization.
- Respect site terms, robots restrictions, and reasonable request rates. If access is blocked, preserve the lead as unverified and name the limitation.
- Do not claim exhaustive coverage. State the sources, regions, query groups, and verification date actually covered.
- Keep notifications action-focused: new eligible roles, important changes, approaching deadlines, repeated collection failures, or a decision required from the user.

## Deterministic helpers

All bundled scripts use the Python standard library and support Windows, macOS, and Linux:

- `init_workspace.py`: create a safe workspace without overwriting existing files.
- `validate_profile.py`: validate configuration and ranking totals.
- `normalize_jobs.py`: canonicalize URLs and text, create stable IDs, and merge duplicates.
- `merge_pending.py`: merge deferred CSV snapshots while preserving historical invariants.
- `validate_output.py`: validate headers, enums, dates, URLs, scores, and evidence requirements.
- `generate_report.py`: produce a concise Markdown report from validated records.
