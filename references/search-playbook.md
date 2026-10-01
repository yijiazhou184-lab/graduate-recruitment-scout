# Search Playbook

Read this reference for a new scan, a watchlist refresh, or source expansion.

## Build query groups from the profile

Create queries from combinations of:

- graduation year or terms such as `graduate`, `new grad`, `campus`, `early careers`, and local equivalents;
- primary and secondary role names plus common synonyms;
- preferred locations and their common language variants;
- business priorities;
- employer watchlist names, aliases, and business lines;
- season or batch terms used in the target region;
- official career or ATS domain filters where known.

Search in each configured language. Vary the intent instead of repeating near-identical wording.

## Multi-round coverage

1. Start broadly with graduation eligibility, role family, and location.
2. Search each watchlist employer and relevant business line against official career pages.
3. Expand with synonyms learned from verified descriptions and official site taxonomy.
4. Check configured employer segments and underrepresented recommendation groups.
5. Stop after `consecutive_empty_rounds_before_stop` rounds produce no new eligible records.

Do not stop merely because one employer segment already supplies enough recommendations. Recommendation quotas control display, not collection.

## Regional and role ambiguity

- Translate location and graduate-program terms when the target market uses multiple languages.
- Verify the actual office location rather than relying on a regional landing page.
- Distinguish full-time graduate programs from summer, off-cycle, placement, and conversion internships.
- For titles such as `Analyst`, `Associate`, `Engineer`, or `Product`, classify from responsibilities and organizational context, not the title alone.
- For technology roles at financial institutions, verify that responsibilities concern technology, digital delivery, engineering enablement, systems analysis, technology operations, or technology change—not front-office finance.

## Reporting coverage

Record query groups, regions, employer segments, sources checked, verification date, and material access failures. Say “no new eligible roles found in the checked scope,” not “no jobs exist.”
