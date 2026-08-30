# Current Work Order

**ID:** R0.12-STAGE-A-FINAL-CLOSURE-002  
**Status:** ACTIVE — FINAL HUMAN GATE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** FINAL ORDINARY-USER WINDOWS ACCEPTANCE  
**Accepted candidate:** 0.1.4 / 08667fc1e64003869a3176b6d953bedcd1e4d1b1  
**Updated:** 2026-08-30

## Objective

Run the final ordinary-user Human Gate on the exact 0.1.4 Windows RC.

## Release authority

- Version: **0.1.4**
- Source: `08667fc1e64003869a3176b6d953bedcd1e4d1b1`
- Windows RC run: `33312835714`
- Installer: `VideoEditingAgent-Setup-0.1.4.exe`
- SHA-256: `c3cdd132b7a6b4c836e921b9e6e451680f00c7ac8eb0cc05e4277a964f77e7e9`
- Release tag: `v0.1.4-rc-08667fc`
- Release asset ID: `536627232`
- Direct asset: `https://github.com/orange-lee-tech/video-editing-agent/releases/download/v0.1.4-rc-08667fc/VideoEditingAgent-Setup-0.1.4.exe`

## Human evidence from 0.1.3

The representative Editing run proved:

- input validation PASS;
- Gemini visual understanding PASS for all five observed calls;
- automatic public-music discovery returned 40 unique candidates;
- 26 failed current-source rights verification;
- 13 did not meet the attribution-free automatic rights gate;
- one rights-approved candidate failed acquisition;
- the task then failed at `music_preparation`.

This is a product-supply resilience failure, not a visual-understanding, media-ingest or Renderer failure.

## 0.1.4 repair

Automatic public-music rights policy remains unchanged and fail-closed.

When no automatic public BGM can be prepared:

1. emit a clear warning;
2. continue with no BGM;
3. preserve only grounded source-audio lanes already supported by the canonical EDL;
4. if at least one approved audible lane exists, continue to render/review;
5. if no approved audible lane exists, stop with an actionable instruction to select local music and attest rights.

Do not silently accept attribution-required, unknown, ineligible or otherwise non-automatic public music.

## Engineering verification

0.1.4 passed:

- repository Quality Gate;
- no-BGM-with-source-audio completion regression;
- no-audible-lane fail-closed regression;
- packaged windowed-GUI smoke;
- guided Setup.exe build;
- Planning-only install;
- Planning-only → Full upgrade;
- Full launcher;
- same-version repair;
- uninstall;
- external Workspace preservation;
- public GitHub Release publication.

## Product Owner action

Upgrade to the exact 0.1.4 installer and repeat the same real-footage Editing case.

Accept if:

- visual understanding completes with an available provider;
- automatic public music either succeeds or emits a warning and safely continues without BGM;
- no terminal windows flash;
- render/review reaches an approved final MP4;
- Workspace/original media remain safe.

If the footage has no usable source audio and public BGM is unavailable, selecting a local music file plus the existing rights-attestation checkbox is the intended fail-closed fallback.

Planning may be spot-checked once; do not repeat broad test permutations unless a material regression appears.

## Exit condition

If Planning remains acceptable and this 0.1.4 Editing run reaches an approved MP4 without a material blocker:

- record durable Human evidence;
- set Planning gate PASS;
- set Editing gate PASS;
- set Windows release delivery gate PASS;
- set Stage-A completion gate PASS;
- move structural progress **95% → 100%**;
- close R0.12.

After closure, open separate release-engineering work for component-level incremental updates and a curated/preverified automatic fallback music pool.
