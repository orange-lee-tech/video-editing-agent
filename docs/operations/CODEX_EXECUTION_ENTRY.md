# Codex Execution Entry

**Last updated:** 2026-08-25  
**Purpose:** expose whether Codex currently has an authorized local construction release.

## Release state

**Work Order:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Release:** OPEN — PROJECT WORKSPACE + UX CONSOLIDATION ONLY  
**Construction branch:** `work/r012-workspace-ux-consolidation`  
**Starting main baseline:** `d26249f71d895efff54c1d7167f4b6bc457b98f1`  
**Foreman:** ChatGPT  
**Authority:** `docs/operations/CURRENT_WORK_ORDER.md`  
**Wave specification:** `docs/operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`

Codex must not infer authorization from old chat history, archived wave specifications, stale branches, PR comments that conflict with the live control plane, or future Packaging documents.

## Mandatory attention order

1. root `AGENTS.md`;
2. `docs/DOCUMENT_REGISTRY.json`;
3. `docs/operations/CURRENT_CONTROL_STATE.md`;
4. `docs/roadmap/CURRENT_PHASE_STATUS.md`;
5. `docs/operations/CURRENT_WORK_ORDER.md`;
6. `docs/operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`;
7. this execution entry's **2026-08-25 closure repair** below;
8. only task-relevant source/tests;
9. Product/Architecture/CAP/ADR only when a concrete implementation question requires them.

`docs/archive/**`, `.private/**`, `.tools/**`, `.uv-cache*/**`, `.venv/**`, `build/**` and `dist/**` remain default-excluded from ordinary discovery.

## Accepted baseline before this release

The bounded reference-compatibility decision is accepted in main merge:

`756a30562dd512fba9868eeee43cf6422f60f642` (PR #13)

Current 1.0 reference boundary:

- ordinary remote reference URL stays hidden;
- local reference video remains supported;
- bounded Bilibili acquisition is retained only as an engineering fallback seam;
- provider-neutral `ReferenceObservation`, remote/video-native observation and provider upload-media observation are deferred to 2.0.

On 2026-08-25 the Product Owner explicitly confirmed that this 1.0 deferral was their intended product decision. `docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md` and the durable reference-compatibility closure were reconciled accordingly. This question is closed for Stage A and must not consume implementation time.

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

## 2026-08-25 closure repair — current bounded implementation task

The broad Workspace/UX implementation exists on PR #17, but review found three concrete boundary defects that must be repaired before Human Gate.

### 1. No selected Workspace must mean zero project mutation

Current `run_editing()` opens `ProjectWorkspace` before `EditingForm.to_request()` rejects an empty project path. Because `Path("")` resolves to `.`, an ordinary mis-click can create SQLite/provider/cache/work/log/draft/history/output state in the current working directory.

Required repair:

- validate that a Project Workspace was explicitly selected before any `ProjectWorkspace.open()` or other project-writable mutation;
- Planning and Editing must both fail cleanly before project creation when no Workspace is selected;
- do not move this rule into Domain; keep the repair at product/UI/application-composition boundary.

Regression evidence must prove that a no-Workspace Planning/Editing attempt creates no project files or project-owned directories.

### 2. Auto output default must rebase on Workspace switch

Current UI treats a non-empty output field as sufficient reason to keep it. That allows an auto-generated path under Workspace A to remain active after switching to Workspace B.

Required repair:

- explicitly distinguish `auto-generated workspace default` from `explicit user Save As override`;
- an auto default must follow the current Workspace when switching A → B → A;
- a genuine explicit Save As override must not be silently overwritten;
- collision-safe naming and explicit overwrite behavior remain intact;
- persisted/restored form state must not accidentally convert an old Workspace default into an explicit override.

Do not infer ownership from `field is non-empty` alone.

### 3. Planning session context must not cross project boundaries in the UI

The lower `EditingForm` project-match validation already fails closed and must remain unchanged.

Required repair:

- switching Workspace must clear or mark stale the previous `planning_context`;
- `use_planning` must be reset/disabled appropriately so A's exact Planning refs do not remain presented as usable inside B;
- switching back may only restore a context if it is genuinely valid for that Workspace/session state; do not fabricate or clone Planning refs.

### Focused verification additions

Add regression coverage for at least:

- no Workspace selected → no project mutation;
- A → B → A switch;
- drafts/history remain scoped to the correct Workspace;
- automatic default output rebases;
- explicit Save As survives correctly;
- old Planning context cannot leak across Workspace switch;
- Clear/Undo/Redo state remains coherent for file selections, checkbox state and planning-use state where applicable;
- mutation controls remain disabled while a task runs;
- form/API configuration import/export works separately and together;
- no plaintext secret leakage.

The launcher smoke remains a structural startup/composition smoke. If practical, extend automation to use a real temporary Workspace, but **do not** reinterpret launcher smoke as the Windows Human Gate.

## Explicitly forbidden

Do not:

- reopen Bilibili/Douyin/Xiaohongshu remote-reference product work;
- implement `ReferenceObservationPort` or other 2.0 remote-video observation capability;
- start Runtime Manifest, Resource Locator, Capability Doctor, PyInstaller, onedir, installer or other Packaging production construction;
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
3. inspect current branch diff/status first and continue from existing work rather than redoing completed Workspace implementation;
4. implement the three closure repairs above as one coherent bounded batch;
5. during iteration run focused tests and bounded self-repair only for blockers inside this release;
6. run the full engineering gate before handoff:
   - Ruff format/check;
   - mypy `src`;
   - full pytest;
   - import-linter;
   - build;
   - repo doctor;
   - `git diff --check`;
   - launcher smoke;
7. perform Windows manual smoke for no-Workspace behavior, workspace selection/project switching, draft/history isolation, default output vs explicit Save As, Planning-context switching, configuration import/export choices, Clear/Undo/Redo, collapse/expand, language and ordinary laptop window behavior;
8. run one real Planning smoke and one real Editing smoke on the target Windows development environment using ordinary product entry paths;
9. confirm no plaintext secret leakage;
10. report exact changed files, tests, manual-smoke findings, exact branch HEAD, any intentionally deferred item and next Human Gate;
11. stop. Do not continue into Packaging without a new release.

## Acceptance rule

Codex PASS is evidence only. ChatGPT must reobserve GitHub/local evidence and the user performs the ordinary Human Gate before this wave is accepted.
