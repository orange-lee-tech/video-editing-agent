# Codex Execution Entry

Purpose: enter the active construction state with the minimum safe model-visible context.

## Active release

**Work Order:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Release:** ACTIVE — SINGLE COMPLEX BATCH  
**Writer:** Codex until commit/push/STOP

The ordinary-user surface audit is complete:

`docs/validation/R0.12_STAGE_A_PRODUCT_SURFACE_AUDIT.md`

Do not re-design the project from scratch. The implementation boundary is already frozen in:

`docs/operations/CURRENT_WORK_ORDER.md`

## Startup

```text
git status
git fetch
git switch main
git pull --ff-only
confirm clean working tree
```

If the working tree is not clean, STOP before pulling/resetting and determine whether the files are existing user/agent work. Never discard unknown local changes.

Then run foreman. On this Windows host, use process-local bypass if required:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 foreman
```

Read `.private/codex_brief.md` and act on L0. For this active release, also read:

- `docs/operations/CURRENT_WORK_ORDER.md`;
- `docs/validation/R0.12_STAGE_A_PRODUCT_SURFACE_AUDIT.md`.

Open secondary source/architecture files only when a concrete implementation trigger requires them.

## First local preflight for this batch

Before changing the desktop layer, verify the actual target Windows development environment:

```powershell
uv run python -c "import tkinter as tk; root=tk.Tk(); root.withdraw(); root.update_idletasks(); root.destroy(); print('TK_OK')"
ffmpeg -version
ffprobe -version
```

If Tkinter import/root creation fails on the actual Windows target, STOP and report that exact blocker before adding a GUI dependency.

Do not spend provider API calls merely to test widgets.

## Frozen implementation goal

Complete one thin Stage-A product layer over the accepted owner chains:

1. user-level Planning reference/fact inputs;
2. accepted reference-only acquisition/analysis → `ReferenceStyleGuidance` plumbing into both Script and Shooting workflows;
3. optional live observation of existing `ProductFlowEvent` progress;
4. ordinary runtime defaults / TransNet auto-resolution and understandable mandatory-capability diagnostics;
5. a minimal Windows launcher, preferably stdlib Tkinter if preflight passes;
6. readable exact ScriptPlan/ShootingPlan presentation;
7. file/folder selection and final MP4 discovery for Editing.

The UI is an adapter only. Keep request construction, folder expansion, runtime resolution, reference preparation and result presentation testable below widget code.

## Hard boundaries

Do not:

- build a timeline/NLE editor;
- make Planning mandatory for Editing;
- let reference-only media become Resolver/final-output footage;
- add stock/generated fallback visuals;
- add universal/authenticated/social downloaders;
- loosen semantic/commercial Review;
- redesign Resolver, EDL or Renderer without concrete evidence;
- expose AssetRef/ShotRef/CandidateWindow/ResolutionDecision/source timestamps/EDL as ordinary-user inputs;
- silently switch providers after a provider failure;
- add a heavy GUI framework unless Tkinter is proven unavailable on the target;
- claim Product Gate/Human Gate PASS;
- bump structural progress above 90%.

## Verification

Run focused tests while iterating, then the full repository Quality Gate.

Required coverage is listed in `CURRENT_WORK_ORDER.md`; do not substitute GUI screenshots for the deterministic application/controller tests.

Perform a bounded local Windows launcher smoke after tests. It may use mocked/injected operations for UI plumbing; final real Product Probe is owned by ChatGPT/user after merge.

## Completion / STOP gate

When the bounded implementation is complete:

1. run the normal repository Quality Gate as far as the local environment allows;
2. inspect final `git diff` / `git status`;
3. create **one coherent implementation commit**;
4. push to `main`;
5. STOP and report:
   - commit SHA;
   - files changed;
   - architecture/authority notes;
   - focused tests;
   - full gate results;
   - Tkinter/Windows smoke result;
   - known limitations;
   - final `git status`.

Do not self-authorize the real Product Probes, Human Gates, Work Order closure or next Roadmap stage.

## Interruption recovery

After a disconnect, inspect `git status` and `git diff`; resume unfinished work rather than replaying the original prompt.

Do not discard completed local edits or restart the whole batch because of a transport interruption.
