# Source Policy

Read this reference whenever discovering or verifying jobs on the web.

## Source roles

1. `official_employer`: an employer-controlled career page. Preferred final evidence.
2. `official_ats`: the employer's identifiable page on an applicant-tracking system. Preferred final evidence.
3. `trusted_job_board`: a direct employer listing on a configured recruiting platform. Use as final evidence only when an official page cannot be found and the listing identifies the employer and application path.
4. `community_lead`: a forum, campus community, newsletter, or repost. Discovery only unless the user explicitly changes the policy.
5. `search_engine`: discovery only. A result snippet never establishes job facts.

When an official page is found, keep the original discovery provenance in `discovered_via`, but use the official page for `source_url`, `official_source_url`, and normally `apply_url`.

## Verification requirements

Open the detail page and check:

- employer and role title;
- whether the page is still accessible and accepting applications;
- graduate, campus, early-career, or target-year eligibility;
- full-time versus internship or temporary employment;
- location and remote or hybrid terms;
- responsibilities and hard requirements;
- application URL, posting date, and deadline when disclosed;
- whether the source represents the employer or merely republishes content.

Do not infer omitted dates, salary, visa support, degree requirements, or graduation eligibility. Use `pending_verification` when a missing field changes whether the user can apply.

## Access and responsible use

- Do not sign in, submit forms, circumvent CAPTCHAs, bypass robots or access controls, or scrape at abusive rates.
- Treat blocked, dynamic, removed, and login-only pages as specific source limitations.
- Do not repeatedly retry the same blocked source in one run.
- Follow source terms and the user's configured source allowlist.
- Store short evidence summaries, not full copyrighted job descriptions.

## Conflicts

Prefer the more authoritative and more recent opened source. Preserve the losing value or conflict description in `risk_flags`. Do not silently combine incompatible locations, graduation years, or deadlines.
