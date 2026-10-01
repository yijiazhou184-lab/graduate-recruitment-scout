# Ranking Policy

Read this reference when scoring, grouping, or recommending records.

## Hard filters first

Do not rank a record as eligible until the available evidence supports:

- the configured graduation year or a compatible graduate/new-grad population;
- the configured employment type;
- an acceptable location or remote arrangement;
- an open or plausibly open application state;
- all disclosed hard degree, discipline, language, and authorization requirements.

Use `pending_verification` when a material condition is unknown. Use `ineligible` when evidence shows a hard mismatch. Closed or removed listings use `closed` or `offline` rather than `ineligible`.

## Weighted score

Score each eligible record from 0 to 100 using the profile weights:

- `role`: primary versus secondary direction and responsibility-level fit.
- `business`: match to configured industry or business priorities.
- `employer`: watchlist business-line match or priority employer segment.
- `candidate`: evidence-backed match to configured skills, language, or background signals.
- `location`: preferred location or acceptable remote arrangement.
- `freshness`: recency, open status, and usable application path.

Award points only when the source or profile provides supporting evidence. Do not give full employer points for brand alone, or primary-role points because a title contains a fashionable keyword.

`match_reason` must identify the strongest evidence and material limitation. `classification_reason_codes` should contain stable semicolon-separated labels such as `PRIMARY_ROLE`, `WATCHLIST_BUSINESS_LINE`, `PREFERRED_LOCATION`, `GRAD_YEAR_CONFIRMED`, or `AUTHORIZATION_UNKNOWN`.

## Ordering and groups

Order records by:

1. eligible before pending or ineligible;
2. primary before secondary roles;
3. match score;
4. deadline urgency within a useful preparation window;
5. posting freshness;
6. diversity of employers and role families when scores are close.

Recommendation groups and quotas are presentation targets, not collection requirements. Never fill a quota with an ineligible, closed, low-quality, or unverified record. A record belongs to at most one display group.
