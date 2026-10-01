# Contributing

Contributions should improve observable behavior, portability, or maintained domain guidance without embedding a contributor's personal profile in the core Skill.

Before opening a change:

1. Keep `SKILL.md` concise and route conditional detail to the relevant reference.
2. Put personal, regional, employer, or seasonal preferences in a profile or preset.
3. Add or update tests for deterministic behavior.
4. Use synthetic fixtures only.
5. Run `python -m unittest discover -s tests -v` and the Skill validator.

Source-specific changes should explain why the source is reliable, whether it is a discovery or final-evidence source, and what access limitations apply. Do not add instructions for bypassing logins, CAPTCHAs, robots controls, or site terms.
