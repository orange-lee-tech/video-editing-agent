# Codex Execution Entry

**Last updated:** 2026-08-25  
**Purpose:** expose the currently authorized local construction release.

## Release state

**Work Order:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Release:** CLOSED — FINAL PRODUCT/HUMAN GATE ACTIVE  
**Construction branch:** NONE  
**Accepted production-code baseline:** `c2c959239cf8842388ac661777c19f20f64a6a90`  
**Foreman:** ChatGPT  
**Authority:** `docs/operations/CURRENT_WORK_ORDER.md`

There is currently **no authorized Codex implementation batch**.

PR #20 accepted and merged the Windows runtime payload closure. The next required evidence is ordinary-user packaged Product/Human evidence, not another engineering wave.

## Accepted engineering result

The accepted baseline provides:

- exact Windows x64 LGPL-only FFmpeg/ffprobe payload;
- exact TransNetV2 + CPU Torch + package weights with a real packaged CPU prediction probe;
- exact faster-whisper/CTranslate2/PyAV + pinned local model with a real packaged offline ASR probe;
- PyAV compatibility against the approved LGPL FFmpeg DLLs while excluding its broad/GPL codec DLL payload;
- exact CPython 3.12.13 packaging baseline;
- manifest/NOTICE/component hashes and static package inspection;
- packaged Environment Doctor, GUI launcher and external Project Workspace smoke;
- SHA-addressed main artifact and evidence.

Accepted main artifact:

`VideoEditingAgent-windows-x64-c2c959239cf8842388ac661777c19f20f64a6a90`

GitHub artifact digest:

`sha256:a21a71211c0bee6848f93852d2f4cf6d27cd194b89f92a1fed6e4c24ccd57d5d`

## Current action

The Product Owner should run the final ordinary-user Human Gate described in `docs/operations/CURRENT_WORK_ORDER.md`.

Do not ask Codex to perform synthetic substitutes for this Human Gate.

## When Codex may be reopened

ChatGPT may create a new narrow execution release only if the Human Gate produces a reproducible implementation defect, for example:

- packaged launcher/runtime fails on the real supported Windows machine;
- FFmpeg/TransNet/speech Doctor state disagrees with actual runtime behavior;
- clear speech cannot reach the grounded subtitle path because of a packaging/runtime defect;
- Workspace/output ownership regresses in the packaged application;
- Planning-only / Editing-only / Combined ordinary product semantics regress.

A reopened Codex task must be bounded to the observed defect. It must not revive already accepted packaging work or expand into unrelated cleanup.

## Still out of scope

Without a new explicit release, do not start:

- installer / onefile / updater / signing;
- artifact-size optimization;
- Remote Reference URL 2.0;
- TTS or advanced separation/effects;
- Domain/EDL/Renderer authority changes;
- unrelated architecture cleanup.

## Final authority

Stage-A remains 95% until Human evidence closes the gate. ChatGPT/Product Owner retain final acceptance authority.
