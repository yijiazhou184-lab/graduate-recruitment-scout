# Output Schema and State

Read this reference before creating, normalizing, merging, validating, or reporting the job database.

## Workspace

The default workspace is configured by `output.workspace_dir` and contains:

```text
job-search/
├── profile.json
├── graduate-jobs.csv
├── daily/
└── pending/
```

`scripts/init_workspace.py` creates this structure without overwriting existing files.

## CSV columns

`graduate-jobs.csv` uses the exact order defined by `CSV_FIELDS` in `scripts/scout_common.py`. Important groups are:

- Identity: `record_id`, employer, original and normalized role title, city, and country.
- Classification: role family and priority, employer type and scale, business focus, and location priority.
- Eligibility: employment type, graduation target, application and verification status, and evidence summaries.
- Source provenance: discovery source, final source type and name, opened URLs, page status, and verification timestamps.
- Change tracking: immutable `first_seen`, updated `last_verified`, and `change_type`.
- Recommendation: score, reason, reason codes, risks, and notes.

The field-level machine-readable contract is [job-record.schema.json](job-record.schema.json).

## Stable identity and deduplication

1. Canonicalize the best application URL by lowercasing the host, removing fragments, sorting query parameters, and dropping common tracking parameters.
2. When a canonical application or official URL exists, hash it for `record_id`.
3. Otherwise hash normalized employer, role title, city, and country.
4. Merge exact stable IDs first, then merge normalized employer + role + city + country keys.
5. Prefer the higher-priority source. Preserve the earliest `first_seen`, latest successful `last_verified`, and any material conflict notes.

Use `scripts/normalize_jobs.py` for this operation.

## States

- `application_status`: `eligible`, `pending_verification`, `ineligible`, `closed`, `offline`.
- `verification_status`: `verified`, `partially_verified`, `unverified`, `blocked`.
- `page_status`: `active`, `closed`, `removed`, `blocked`, `login_required`, `unknown`.
- `change_type`: `new`, `updated`, `deadline_soon`, `closed`, `offline`, `unchanged`.

Allowed transitions include new-to-unchanged, pending-to-eligible, eligible-to-closed, and active-to-offline. Never reset `first_seen` when a state changes.

## Dates and text

- Use ISO `YYYY-MM-DD`; use `YYYY-MM` only when the source gives no day.
- Store source-check timestamps as ISO 8601 with a timezone when time is available.
- Preserve factual meaning while collapsing whitespace.
- Leave unknown values empty. Do not use guessed dates or fabricated placeholder facts.
- Salary contains only values explicitly disclosed by the opened source.

## Safe writes

Validate a complete candidate CSV before replacing the main database. If the main file is locked or cannot be replaced, write the complete merged result to `pending/<timestamp>-graduate-jobs.csv`. Merge pending snapshots first on the next run with `scripts/merge_pending.py`.
