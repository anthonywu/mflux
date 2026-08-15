---
name: mflux-dev-env
description: Set up and work in the mflux dev environment (arm64 expectation, uv, justfile recipes, lint/format/test).
---
# mflux dev environment

This repo expects macOS arm64 and prefers `uv` + justfile recipes.

## When to Use

- You’re setting up the repo locally or diagnosing environment/setup issues.
- You need the canonical way to run lint/format/check/build/test.

## Instructions

- Prereq: `just` ≥ 1.50 (`brew install just`). CI lints the justfile with `just --fmt --check`; run `just fmt-justfile` to auto-fix formatting.
- Prefer justfile recipes:
  - Install: `just install`
  - Lint: `just lint`
  - Format: `just format`
  - Pre-commit suite: `just check`
  - Build: `just build`
- Prefer `uv run ...` for running Python commands to ensure the correct environment.
- When running tests, keep `MFLUX_PRESERVE_TEST_OUTPUT=1` enabled (the justfile test recipes already do this).

