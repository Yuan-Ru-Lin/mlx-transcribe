# Lessons

## Bump the version before reinstalling the tool

uv caches built wheels by version. Running `uv tool install . --force` after
editing source but without bumping `version` in `pyproject.toml` reuses the
stale cached wheel, so the installed tool silently lacks the changes.

**Rule:** when reinstalling this package via `uv tool install . --force`,
bump the version in `pyproject.toml` first. Never work around it with
`uv cache clean` — the version bump is the correct fix and keeps the
installed tool traceable to the source it was built from.
