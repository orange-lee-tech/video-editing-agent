# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE

**Current phase:** R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer

**Active boundary:** R0.9B — Canonical Edit Contracts → Resolver → Deterministic Optimizer

**Date:** 2026-08-13

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.

## R0.9A candidate

`ef6efa1f047201c96caeb2c56d7c895af00549a1` — `feat: add grounded hybrid candidate windows`

The R0.9A live probe passed and produced an inspectable real-media CandidateWindow preview. Post-review found three bounded contract issues that must be converged before Resolver work expands:

1. canonical `EditPlan` / `EditSlot` already exist in `domain/edit/model.py`; do not keep a competing Director definition;
2. canonical `CandidateWindow` already exists in `domain/edit/resolution.py`; do not keep a competing Director definition;
3. `MediaTimeRange` means an exact media interval and must not be reused as a min/max duration constraint.

These are structural hardening items, not a failed retrieval/window mechanism. R0.9B must fix them first and continue in the same batch into Resolver + deterministic sequence optimization.

## Active — R0.9B

Build the first deterministic grounded source-selection decision using the existing `ResolutionDecision` / `ResolvedSelection` contract. Preserve explainable feature contributions, score/confidence separation, alternatives, evidence provenance, hard-feasibility dominance and deterministic sequence optimization over bounded CandidateWindows.

The local probe should also export a non-authoritative resolved-sequence diagnostic preview for human inspection.

After R0.9B, run the real-footage R0.9 Product Probe / phase closure before entering R0.10.

## Operational control

Codex reads `CODEX_EXECUTION_ENTRY.md`, this file, then `CURRENT_WORK_ORDER.md`.
