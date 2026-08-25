# Current Work Order

**ID:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** HUMAN GATE REPAIR + WINDOWS RELEASE DELIVERY  
**Accepted engineering foundation:** `c2c959239cf8842388ac661777c19f20f64a6a90`  
**Current main / latest Human Gate candidate:** `1015096fc4c5b2b9138e98cbe713fc4cc1770c07`  
**Updated:** 2026-08-25  
**Codex release:** CLOSED pending focused local evidence

## Objective

Reach truthful Stage-A / 1.0 closure by repairing the defects demonstrated by the real Product/Human Gate, then deliver the stabilized Windows product through a guided `Setup.exe` installation path rather than a raw large ZIP.

The current task is not another broad architecture wave. Repair only the demonstrated Planning and Editing defects, improve the release-maintenance boundary, and preserve all accepted authority/safety invariants.

## Current Human Gate defects

### A. Planning factual-grounding defect — OPEN

Latest real failure:

- the Script reviewer correctly rejected a proposal that implied the bottle fits in a bag and can be held in one hand;
- the only cited authoritative fact was 350 ml capacity, which does not prove those fit/operability claims;
- the previous prompt-only bounded repair therefore remains insufficient.

Required repair direction:

- do not weaken the semantic reviewer;
- do not add open-ended model retry loops;
- introduce a bounded conservative recovery for `unsupported_claim` that removes claim-bearing implications and preserves only authoritative facts / neutral observable framing;
- re-review the recovered proposal before owner commit;
- prohibited content, brand constraints, locked authority and other hard violations remain fail-closed.

### B. Editing Director/Resolver grounding defect — OPEN

Latest real failure:

- ingest, public-music fallback, rights gate, acquisition and BeatMap succeeded;
- first Resolver pass reported unresolved coverage;
- the new bounded Resolver -> Director recovery executed;
- the revised EditPlan still requested multiple beats unsupported by the real local footage, so the flow correctly failed before EDL/render.

Required next action is **evidence inspection before modification**. Inspect the actual persisted local Workspace evidence, especially:

- Brief payload;
- latest shot analyses;
- both EditPlan revisions;
- resolver reasons / relevant temporal evidence if needed.

Do not guess at a new Director prompt or Resolver threshold before this evidence is observed.

## Repair-loop protocol — mandatory

During this active Human Gate repair boundary:

1. **No full Windows package per small repair.** The ~769 MB compressed / ~1.88 GB extracted onedir candidate is not an iteration transport.
2. Use focused local diagnostics from the external Workspace. Prefer `project.sqlite3` + `logs/`; request `history/` or `drafts/` only if necessary. Never request private source media unless the Human Gate itself requires visual judgment.
3. Use patch-first development: focused diff/patch, targeted tests, then full repository quality gate when appropriate.
4. Local developer runs may use PowerShell/CLI because this is an engineering feedback loop. Ordinary-user product behavior must still require no terminal knowledge.
5. GitHub CI validates source changes, but the full Windows Packaging Candidate workflow is run only at an explicit release-candidate checkpoint.
6. Only after Planning + Editing repair is stable should a new full Windows release artifact be built.
7. Final Human Gate must use the installer-produced ordinary product, not an ad-hoc repository/uv launch.

## Windows delivery / installer boundary — NOW IN SCOPE

The Product Owner has explicitly rejected raw ZIP extraction as the normal release experience and requires a guided `Setup.exe` flow.

The release solution must provide:

- install, upgrade/repair and uninstall;
- license/agreement page where applicable;
- installation path guidance;
- selectable desktop shortcut;
- finish-page launch option;
- clear detection/explanation of existing application-owned component conflicts;
- explicit consent before destructive replacement/reconfiguration;
- no arbitrary system Python/FFmpeg/PATH mutation by default;
- Workspace/projects/original media outside the install tree and preserved across app uninstall/update;
- practical componentization so heavy Editing/speech runtimes are not an indivisible payload for Planning-only users.

Preferred implementation study order:

1. **Inno Setup 7.1** as the primary guided `Setup.exe` candidate;
2. **NSIS Modern UI 2** as the permissive/custom-script alternative;
3. **Velopack** as a competing whole install/update stack, especially for delta/self-update needs;
4. WiX/Burn only if prerequisite chaining requirements justify its additional complexity.

Do not combine installer stacks merely because they exist. Choose the smallest established solution that satisfies the product contract and licensing constraints.

## Runtime decomposition target

The current large onedir should be treated as engineering staging, not a single indivisible release payload. Evaluate at least these logical ownership packs:

- **Core App:** GUI, application code, minimum private CPython/Tcl/Tk, profiles/Workspace/Planning cloud adapters;
- **Media Runtime:** FFmpeg/ffprobe;
- **Scene Detection Runtime:** TransNet + CPU Torch + reviewed weights;
- **Speech Runtime:** faster-whisper + CTranslate2/PyAV + pinned model.

Capability-oriented installation should preserve flexible production-line semantics: Planning-only can remain light; Editing adds media/scene components; trusted speech subtitles add speech components.

## Permanent invariants

- preserve replaceable adapters and canonical Domain/EDL/Renderer authority;
- no public/web/generated visual fallback for missing user footage;
- no plaintext provider secrets in install/project/log artifacts;
- keep source media immutable;
- keep user Projects/Profiles/outputs outside application installation ownership;
- retain CPU-capable ordinary baseline;
- destructive environment actions require explicit user consent;
- Remote Reference URL remains deferred to 2.0.

## Exit gates

This work order closes only when:

1. Planning-only real Human Gate passes the unsupported-claim scenario safely;
2. Editing-only real Human Gate reaches grounded final output for an appropriately satisfiable local-footage case, including clear speech/original voice/trusted subtitles, while honestly handling truly missing coverage;
3. Combined remains independently usable;
4. final Windows ordinary delivery is a tested `Setup.exe` flow with install/update-or-repair/uninstall and Workspace preservation;
5. exact final candidate identity and durable Human evidence are recorded.

Structural progress remains **95%** until those gates pass.
