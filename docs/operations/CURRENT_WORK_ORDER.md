# Current Work Order

**ID:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** FINAL PRODUCT/HUMAN GATE  
**Accepted production-code baseline:** `c2c959239cf8842388ac661777c19f20f64a6a90`  
**Updated:** 2026-08-25  
**Codex release:** CLOSED — no active construction branch

## Objective

Reach truthful Stage-A / 1.0 structural closure by validating the accepted packaged Windows product through one consolidated ordinary-user Human Gate.

Engineering construction for the retained Stage-A surface is accepted through PR #20. No new Codex batch is authorized by default. If Human evidence exposes a concrete implementation defect, ChatGPT may release only the narrow repair required by that defect.

## Permanent construction principles

1. preserve compatible development and replaceable adapters;
2. keep bootstrap/runtime location outside Domain/editorial authority;
3. keep user originals immutable and user/project writable state outside the install tree;
4. never bundle or log plaintext provider secrets;
5. retain CPU-capable baseline behavior;
6. use exact evidence rather than inferred PASS;
7. do not expand retained 1.0 scope merely because the engineering phase is nearly complete;
8. ChatGPT/Codex engineering remains serial; Codex is currently closed.

## Accepted waves

### Wave A — governance — ACCEPTED

### Wave B — Planning reference compatibility — ACCEPTED / remote support deferred to 2.0

Local reference video remains supported. Generic remote Reference URL remains a deliberate 2.0 deferral and is not a Stage-A blocker.

### Wave C — Project Workspace + UX — ACCEPTED / PR #17

Merge: `4b2b4ed5f6e2347ae3b29381f39e79ad6930e393`.

### Wave D1 — Windows Packaging foundation — ACCEPTED / PR #19

Merge: `cb63713c0daa02b396fd4f5268d280af831d5f70`.

### Wave D2 — Windows runtime payload closure — ACCEPTED / PR #20

Merge: `c2c959239cf8842388ac661777c19f20f64a6a90`.

Accepted runtime closure includes:

- exact BtbN Windows x64 LGPL-only FFmpeg/ffprobe 8.1 payload;
- `transnetv2-pytorch==1.0.5` + `torch==2.13.0+cpu` + package-owned weights;
- `faster-whisper==1.2.1`, `ctranslate2==4.8.1`, `av==18.1.0`, pinned `Systran/faster-whisper-base` revision, CPU/int8/local-files-only;
- PyAV extension compatibility against the approved LGPL FFmpeg DLL set while excluding the wheel's broad/GPL codec DLL payload;
- exact CPython 3.12.13 packaging interpreter;
- manifest/NOTICE/component hash evidence;
- clean Windows packaged Doctor, real TransNet prediction, real offline ASR, launcher and external Workspace smoke;
- main SHA-addressed artifact `VideoEditingAgent-windows-x64-c2c959239cf8842388ac661777c19f20f64a6a90` with GitHub digest `sha256:a21a71211c0bee6848f93852d2f4cf6d27cd194b89f92a1fed6e4c24ccd57d5d`.

## Wave E — final retained Product/Human Gate — ACTIVE

This is now the only Stage-A closure wave.

### Human Gate A — ordinary packaged shell

PASS if an ordinary Windows user can:

- extract/use the accepted onedir artifact;
- double-click the application without repository/Python/uv/Git setup;
- select/create an external Project Workspace;
- configure API providers through the GUI;
- understand basic progress/failure/output location behavior;
- keep writable project/profile/output state outside the install tree.

### Human Gate B — Planning-only

PASS if the product GUI can run the supported Planning path from normal user inputs to persisted/inspectable ScriptPlan + ShootingPlan without repository editing.

### Human Gate C — Editing-only with clear speech

Use a short real local video with clear single-speaker speech and Planning enrichment disabled.

PASS if:

- automatic Editing reaches a real final MP4;
- original/source voice is preserved and intelligible;
- trusted subtitles correspond to the actual speech with acceptable timing;
- BGM remains natural enough not to bury speech;
- user originals remain unchanged;
- failure/progress state is understandable;
- no transcript/subtitle content is fabricated.

The already-accepted no-speech Editing Human evidence need not be repeated unless the packaged run reveals a regression in that path.

### Human Gate D — Combined semantics

With a valid Planning result bound to the selected Project Workspace/session, enable Planning enrichment and run a short Combined edit. PASS if Combined works through the ordinary UI while Editing-only remains independently usable.

### Human Gate E — credential/profile protection

The GUI already supports session-local API settings and optional protected API profiles. If a profile is saved, verify it can be loaded through the GUI and no plaintext API key is present in the visible profile file. Windows DPAPI is the protected credential persistence mechanism.

## Evidence required to close this work order

Record:

- exact accepted artifact/main SHA and artifact digest;
- Windows machine/environment class;
- provider choices used for Planning/visual understanding;
- final MP4/output locations and concise Human observations;
- PASS/FAIL for ordinary shell, Planning-only, Editing-only speech, Combined semantics and credential/profile behavior;
- any genuine limitation discovered.

If all required Human checks pass, update durable validation evidence, set Core 2 and Stage-A completion gates to PASS, set structural progress to 100, and close this work order.

If a check fails, keep progress below 100 and release only the narrow defect repair demonstrated by the failure.

## Explicitly post-Stage-A / non-blocking

Do not delay Stage-A 100% for:

- shrinking the current large onedir footprint;
- installer / onefile packaging;
- code signing;
- auto-update;
- longer artifact retention/release-channel polish;
- advanced TTS/separation/effects/NLE features;
- Remote Reference URL 2.0;
- optional release-hardening that does not affect the accepted ordinary-user path.

## Current progress

**95%** — held only for final Product/Human evidence.
