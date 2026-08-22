# Codex Execution Entry

**Last updated:** 2026-08-22  
**Purpose:** expose whether Codex currently has an authorized local construction release.

## Release state

**Work Order:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Release:** OPEN — PROJECT WORKSPACE + UX CONSOLIDATION ONLY  
**Construction branch:** `work/r012-workspace-ux-consolidation`  
**Starting main baseline:** `d26249f71d895efff54c1d7167f4b6bc457b98f1`  
**Foreman:** ChatGPT  
**Authority:** `docs/operations/CURRENT_WORK_ORDER.md`  
**Wave specification:** `docs/operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`

Codex must not infer authorization from old chat history, archived wave specifications, stale branches, or future Packaging documents.

## Mandatory attention order

1. root `AGENTS.md`;
2. `docs/DOCUMENT_REGISTRY.json`;
3. `docs/operations/CURRENT_CONTROL_STATE.md`;
4. `docs/roadmap/CURRENT_PHASE_STATUS.md`;
5. `docs/operations/CURRENT_WORK_ORDER.md`;
6. `docs/operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`;
7. only task-relevant source/tests;
8. Product/Architecture/CAP/ADR only when a concrete implementation question requires them.

`docs/archive/**`, `.private/**`, `.tools/**`, `.uv-cache*/**`, `.venv/**`, `build/**` and `dist/**` remain default-excluded from ordinary discovery.

## Accepted baseline before this release

The bounded reference-compatibility decision is accepted in main merge:

`756a30562dd512fba9868eeee43cf6422f60f642` (PR #13)

Current 1.0 reference boundary:

- ordinary remote reference URL stays hidden;
- local reference video remains supported;
- bounded Bilibili acquisition is retained only as an engineering fallback seam;
- provider-neutral `ReferenceObservation`, remote/video-native observation and provider upload-media observation are deferred to 2.0.

Packaging readiness documents were refreshed after that decision, but Packaging implementation is **not** part of this release.

## Authorized objective

Make the existing Stage-A desktop product behave like one coherent user application before Packaging freezes writable-data/resource behavior.

Required outcomes:

- one shared top-level `项目工作区 / Project Workspace` context for Planning and Editing;
- existing `ProjectWorkspace` persistence remains authoritative;
- project-specific cache/work/autosave/bounded undo-redo/log/default-output state belongs under the selected workspace when persisted;
- ordinary Editing derives a visible project-local default output while preserving explicit Save As and safe collision behavior;
- form/API configuration actions are consolidated on the main window with Import / Export / Save / Delete and independent form/API selection;
- plaintext API keys never enter exported profiles, project files, logs or visible-output exports;
- form-level Clear / Undo / Redo operates on coherent active-form state and is safely gated while a task runs;
- Content Goal / References & Filming / Edit Goal / Media & Output become vertical collapsible sections suitable for ordinary laptop windows;
- remote reference URL remains hidden;
- the temporary pixel-camera mark is not frozen as permanent identity; recover the real approved feather asset only if it can be found from repository/history, otherwise leave icon replacement for Human Gate rather than inventing a lookalike.

## Explicitly forbidden

Do not:

- reopen Bilibili/Douyin/Xiaohongshu remote-reference product work;
- implement `ReferenceObservationPort` or other 2.0 remote-video observation capability;
- start PyInstaller/onedir/installer/Packaging construction;
- redesign Planning/Editing Domain authority;
- alter Resolver/EDL/Renderer/Review ownership;
- start production TTS or advanced separation;
- create a generic state/history framework beyond the smallest bounded form-state owner needed here;
- copy canonical Domain state into ad-hoc JSON snapshots merely to make a directory layout look tidy;
- store project-specific writable state in the future install directory;
- store plaintext secrets;
- perform unrelated repository-wide cleanup;
- claim Stage-A 100%.

## Execution protocol

1. reobserve `origin/main`, the construction branch and local working tree before editing;
2. preserve unknown local changes; no blind reset/stash/checkout/clean;
3. implement one coherent bounded Workspace/UX wave;
4. during iteration run focused tests and bounded self-repair only for blockers inside this release;
5. run the full engineering gate before handoff:
   - Ruff format/check;
   - mypy `src`;
   - full pytest;
   - import-linter;
   - build;
   - repo doctor;
   - `git diff --check`;
   - launcher smoke;
6. perform Windows manual smoke for workspace selection/project switching, default output, configuration import/export choices, Clear/Undo/Redo, collapse/expand, language and ordinary laptop window behavior;
7. confirm no plaintext secret leakage;
8. report exact changed files, tests, manual-smoke findings, any intentionally deferred item and next Human Gate;
9. stop. Do not continue into Packaging without a new release.

## Acceptance rule

Codex PASS is evidence only. ChatGPT must reobserve GitHub/local evidence and the user performs the ordinary Human Gate before this wave is accepted.
