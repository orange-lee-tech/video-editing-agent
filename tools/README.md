# Developer Tools

`tools/` contains developer/evidence/maintenance tooling that supports construction but is not ordinary runtime Domain authority.

- `media_corpus_manifest.py` manages/checks local corpus metadata without committing private media.
- `probes/` contains reusable phase Engineering/Product Probe harnesses.
- `maintenance/` contains small repository-doctor/handoff helpers for repeated construction work.

A tool may inspect or execute canonical decisions, but must not invent a parallel hidden authority path simply to produce a passing preview.

Generated media/probe outputs and generated handoff snapshots remain local and gitignored under `example/`, `.private/` or another explicitly ignored workspace.

Micro-tools should stay deterministic, cheap and narrow. If a tool starts making product/editorial decisions, it belongs behind the real product ownership seams instead of `tools/`.
