# Codex Execution Entry

**Last updated:** 2026-08-21  
**Purpose:** expose whether Codex currently has an authorized local construction release.

## Release state

**Work Order:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Release:** CLOSED — no Codex construction is currently authorized  
**Foreman:** ChatGPT  
**Authority:** `docs/operations/CURRENT_WORK_ORDER.md`

Codex must not infer authorization from old chat history, archived wave specifications, or stale branch state.

## Mandatory attention order when released

1. root `AGENTS.md`;
2. `docs/DOCUMENT_REGISTRY.json`;
3. `docs/operations/CURRENT_CONTROL_STATE.md`;
4. `docs/roadmap/CURRENT_PHASE_STATUS.md`;
5. `docs/operations/CURRENT_WORK_ORDER.md`;
6. only task-relevant Product/Architecture/CAP/ADR material;
7. only then the bounded implementation/test surface.

`docs/archive/**` is `EXCLUDED_DEFAULT` and must not be opened unless the released task explicitly requires historical/provenance, backward-compatibility or legal evidence.

Local/runtime noise such as `.private/**`, `.tools/**`, `.uv-cache*/**`, `.venv/**`, `build/**` and `dist/**` is also excluded from ordinary discovery unless a concrete blocker requires it.

## Current closure terrain

The active Work Order preserves four bounded waves:

1. repository attention/document governance — ChatGPT/GitHub owned;
2. bounded Planning reference compatibility proof;
3. compatible Windows packaging foundation;
4. final retained Product/Human Gate and Stage-A closure.

A future Codex release should normally cover one coherent local wave, not all remaining terrain at once.

## Permanent execution rules

When explicitly released, Codex must:

- preserve the current working tree; no blind reset/stash/checkout/clean;
- observe before changing;
- use bounded self-repair for blockers inside the released scope;
- prefer compatible/additive change and stable ports/contracts;
- keep provider/model/runtime/renderer choices replaceable;
- keep packaging/bootstrap/resource location outside Domain authority;
- distinguish capability absence, approved degradation, skipped work and real failure;
- avoid speculative generic frameworks and unrelated repository-wide refactors;
- run focused checks during iteration and the required full gate before handoff;
- treat its own PASS report as evidence, not final acceptance;
- stop at the released boundary.

## Current status

No prompt should be sent to Codex until ChatGPT reobserves the accepted repository state and explicitly opens a bounded release under `R0.12-STAGE-A-FINAL-CLOSURE-002`.
