## What

<!-- One short paragraph: what changes and why. Link issues: Fixes #... -->

## Checklist (definition of done)

- [ ] Tests added/updated. Pure-unit tests run in CI by default; only mark `@pytest.mark.slow` / `high_memory_requirement` tests that download weights or generate images (CI runs everything else).
- [ ] `ruff check` and `ruff format` are clean (`uv run ruff` uses the version pinned in the dev dependencies of `pyproject.toml`, which is the single source of truth for pre-commit and CI; `pre-commit run -a` covers it locally).
- [ ] `CHANGELOG.md`: entry under `Unreleased` referencing this PR number.
- [ ] Docs updated where behavior changed — README examples/table rows are part of the API contract (see `.cursor/rules/RULE.md`).
- [ ] New model: shared config wiring (aliases, default steps, mflux-save dispatch, capabilities, completions), thin CLI entrypoint, and `src/mflux/models/<name>/README.md`.
- [ ] New/changed CLI: ignored/rejected options declared (`IGNORED_OPTIONS`/`REJECTED_OPTIONS`) and `warn_ignored_options` actually called in `main()` — `mflux-capabilities` must stay truthful.

## Verification

<!-- Commands you ran and what you observed. Include generated images/screenshots for model-affecting changes. -->
