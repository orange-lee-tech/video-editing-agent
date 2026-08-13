# Scripts

This directory contains repository/developer helper scripts and older standalone probe entry points.

## Policy

- `verify.ps1` and similar helpers support local repository verification.
- `probe_*.py` files from earlier phases are retained where they preserve reproducible engineering evidence.
- New phase evidence harnesses should normally live under `tools/probes/` unless a script is specifically a general repository/CI helper.

Scripts are not Domain authority and must not become a second implementation of product decisions. If a probe duplicates expected answers instead of executing canonical services/decisions, the probe is invalid even if it renders a plausible artifact.

Do not place secrets, private media or machine-specific absolute paths in committed scripts.
