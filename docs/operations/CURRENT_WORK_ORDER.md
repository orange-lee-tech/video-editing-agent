# Current Work Order

**ID:** R0.12-STAGE-A-FINAL-CLOSURE-002  
**Status:** ACTIVE — FINAL HUMAN GATE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** FINAL ORDINARY-USER WINDOWS ACCEPTANCE  
**Accepted candidate:** 0.1.3 / 93d8483bb1d10e4bc5903c33f626fdd9f0d0e7ea  
**Updated:** 2026-08-30

## Objective

Run one final ordinary-user Human Gate on the exact 0.1.3 Windows RC. Do not broaden this gate into incremental-updater construction.

The repository is public. The 0.1.3 Release asset is therefore a valid public download target.

## Release authority

- Version: **0.1.3**
- Source: `93d8483bb1d10e4bc5903c33f626fdd9f0d0e7ea`
- Windows RC run: `33286816025`
- Installer: `VideoEditingAgent-Setup-0.1.3.exe`
- SHA-256: `0efa9bd847161b42fc9a2b000ebbc5e6dc18d8f8385fd2f489f96feff1cac9e8`
- Release tag: `v0.1.3-rc-93d8483`
- Release asset ID: `536028836`
- Direct asset: `https://github.com/orange-lee-tech/video-editing-agent/releases/download/v0.1.3-rc-93d8483/VideoEditingAgent-Setup-0.1.3.exe`

## What 0.1.3 closes

- Planning unsupported-claim repair/review conflict.
- One full-plan deterministic fact-only fallback after repeated claim veto.
- Gemini hard per-day quota classification and actionable recovery guidance.
- Disposable Human-Gate/test Workspace clean-before-run.
- All prior 0.1.1/0.1.2 Windows packaging/runtime fixes remain included.

## Engineering verification

The 0.1.3 RC passed:

1. repository Quality Gate;
2. packaged windowed-GUI smoke;
3. exact packaging environment;
4. Inno Setup verification;
5. guided Setup.exe build;
6. Planning-only install;
7. Planning-only → Full upgrade;
8. Full launcher;
9. same-version repair;
10. uninstall;
11. external Workspace preservation;
12. public GitHub Release publication.

## Product Owner action

Use this exact 0.1.3 installer and perform only two representative product tasks:

### Planning

Use the same or equivalent brief that previously triggered unsupported portability/commute claims.

Accept if:

- the product returns a usable ScriptPlan/ShootingPlan;
- unsupported claims are removed rather than merely reworded;
- no manual engineering intervention is required.

### Editing

Use a clean disposable Human-Gate project/workspace and representative real footage.

Use any configured visual provider with usable quota. If Gemini daily quota is exhausted, either wait for reset or switch Settings → Visual API Provider to OpenAI; provider quota exhaustion is not itself evidence that local editing is broken.

Accept if:

- visual understanding proceeds when the selected provider is available;
- no terminal windows flash;
- the run reaches an approved final MP4;
- Workspace/original media remain safe.

Also verify that an older installed version detects 0.1.3 and opens a working public download.

## Exit condition

If both Planning and Editing pass without a material product blocker:

- record durable Human evidence;
- set Planning gate PASS;
- set Editing gate PASS;
- set Windows release delivery gate PASS;
- set Stage-A completion gate PASS;
- move structural progress **95% → 100%**;
- close R0.12.

Immediately after Stage-A closure, open a separate release-engineering work order for component-level incremental updates.

Do not require full binary-delta/Web Setup machinery before closing the current core Human Gate.
