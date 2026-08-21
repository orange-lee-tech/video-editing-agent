# Codex Execution Entry

**Last updated:** 2026-08-22  
**Purpose:** expose whether Codex currently has an authorized local construction release.

## Release state

**Work Order:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Release:** CLOSED — previous reference-compatibility wave accepted; next local wave not yet released  
**Foreman:** ChatGPT  
**Authority:** `docs/operations/CURRENT_WORK_ORDER.md`

Codex must not infer authorization from old chat history, archived wave specifications, or stale branch state.

## Mandatory attention order when released

1. root `AGENTS.md`;
2. `docs/DOCUMENT_REGISTRY.json`;
3. `docs/operations/CURRENT_CONTROL_STATE.md`;
4. `docs/roadmap/CURRENT_PHASE_STATUS.md`;
5. `docs/operations/CURRENT_WORK_ORDER.md`;
6. the one explicitly released wave specification;
7. only task-relevant source/tests;
8. Product/Architecture/CAP/ADR only when a concrete implementation question requires them.

`docs/archive/**`, `.private/**`, `.tools/**`, `.uv-cache*/**`, `.venv/**`, `build/**` and `dist/**` remain default-excluded from ordinary discovery.

## Previous release result

The bounded Planning reference-compatibility wave is accepted in main merge:

`756a30562dd512fba9868eeee43cf6422f60f642` (PR #13)

Product decision after the engineering exploration:

- ordinary remote reference URL is hidden for Stage A / 1.0;
- local reference video remains supported;
- bounded Bilibili acquisition is retained only as a fallback engineering seam;
- provider-neutral `ReferenceObservation`, remote/video-native observation and provider upload-media observation are deferred to 2.0.

Durable evidence:

`docs/validation/R0.12_REFERENCE_COMPATIBILITY_CLOSURE_2026-08-22.md`

Do not resume Bilibili/Douyin/Xiaohongshu URL work without a new explicit product decision.

## Prepared next wave

The next intended bounded local wave is:

`docs/operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`

It consolidates:

- one shared Project Workspace context;
- project-local writable work/cache/autosave/undo-redo/log/output ownership;
- project-local default output destination;
- unified configuration actions on the main window;
- form-level Clear / Undo / Redo;
- vertical collapsible form sections;
- retirement of the temporary pixel-camera mark when the approved feather asset can be recovered;
- continued hiding of remote reference URL.

This wave is prepared but **not yet released**. ChatGPT/user must explicitly open it after reobserving the accepted repository/local state.

## Permanent execution rules

When explicitly released, Codex must:

- preserve the current working tree; no blind reset/stash/checkout/clean;
- observe before changing;
- use bounded self-repair for blockers inside the released scope;
- prefer compatible/additive change and stable ports/contracts;
- keep provider/model/runtime/renderer choices replaceable;
- keep packaging/bootstrap/resource location outside Domain authority;
- keep project-specific writable state outside the install directory;
- distinguish capability absence, approved degradation, skipped work and real failure;
- avoid speculative generic frameworks and unrelated repository-wide refactors;
- run focused checks during iteration and the required full gate before handoff;
- treat its own PASS report as evidence, not final acceptance;
- stop at the released boundary.

## Current status

No new local Codex construction should begin until the Project Workspace + UX wave is explicitly released from the latest accepted main baseline.
