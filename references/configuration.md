# Configuration

Read this reference when creating, selecting, validating, or explaining a search profile.

## Resolution order

Use configuration in this order, with earlier items taking precedence:

1. Explicit instructions in the current user request.
2. An explicitly supplied profile path.
3. `<workspace>/profile.json`.
4. `assets/profile.example.json`, only as a structural example.

Do not infer that example or preset values describe the user. If a required preference is unavailable, use a broad search and label the affected ranking dimension as neutral.

## Profile sections

- `candidate`: graduation years, locations, languages, background signals, and optional work-authorization notes.
- `roles`: primary, secondary, and excluded role families or terms.
- `business_priorities`: industries, products, or business models that affect discovery and ranking.
- `companies`: an optional employer watchlist and broad employer segments. A watchlist is neither a whitelist nor automatic evidence of fit.
- `sources`: ordered final-evidence sources and discovery-only sources.
- `search`: query languages, stopping condition, internship inclusion, and full-time requirement.
- `ranking.weights`: six non-negative integer weights that must sum to 100.
- `output`: workspace path, recommendation limit, deadline-warning window, notification policy, and optional display groups.

The machine-readable contract is [profile.schema.json](profile.schema.json). Run:

```bash
python scripts/validate_profile.py path/to/profile.json
```

## Presets

Presets are named starting points for a region or job-search strategy. Copy a preset into the user's workspace before editing it. Never mutate the bundled preset during an ordinary search.

The bundled `china-2027-ai-product-hk-tech.json` captures the original project's focus on mainland China AI/product roles and Hong Kong technology analyst or technology project roles. Its graduation year and background signals are examples, not global defaults.

## Privacy

Store the minimum information required for discovery and ranking. Avoid names, phone numbers, personal email addresses, identification numbers, home addresses, credentials, application-account data, or free-form resume content. Keep real profiles and generated outputs outside the published Skill repository.
