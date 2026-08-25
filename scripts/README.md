# Scripts

This directory contains repository/developer helper scripts and older standalone probe entry points.

## Current helpers

- `verify.ps1` — canonical local full Quality Gate wrapper. It runs repository doctor, Ruff
  format/check, mypy, pytest, import-linter, build, `git diff --check` and launcher smoke. A dirty
  tree is allowed during normal pre-commit verification; use `-RequireClean` only when cleanliness
  is itself part of the gate. `-SkipLauncherSmoke` is diagnostic/headless only.
- `maintain.ps1` — maintenance dispatcher. `preflight` runs repository doctor + Foreman and writes
  the compact `.private/codex_brief.md`; other tasks expose doctor, foreman, handoff and full verify.
- `probe_*.py` files from earlier phases are retained where they preserve reproducible engineering evidence.

New phase evidence harnesses should normally live under `tools/probes/` unless a script is specifically a general repository/CI helper.

Scripts are not Domain authority and must not become a second implementation of product decisions. If a probe duplicates expected answers instead of executing canonical services/decisions, the probe is invalid even if it renders a plausible artifact.

Do not place secrets, private media or machine-specific absolute paths in committed scripts.
