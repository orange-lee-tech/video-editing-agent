# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-25
current_phase: R0.12
phase_state: STAGE_A_WINDOWS_RUNTIME_PAYLOAD_CLOSURE_ACTIVE
active_work_order: R0.12-STAGE-A-FINAL-CLOSURE-002
active_construction_branch: work/r012-runtime-payload-closure
accepted_code_baseline: cb63713c0daa02b396fd4f5268d280af831d5f70
main_preparation_baseline: cb63713c0daa02b396fd4f5268d280af831d5f70
control_plane_baseline: e758c3dfb2cab08b901001c5c59379583d249a06
structural_progress_percent: 95
stage_a_completion_gate: OPEN
core_1_planning_product_gate: PASS
core_2_editing_product_gate: PARTIAL_HUMAN_PASS_RUNTIME_PAYLOAD_AND_SPEECH_EVIDENCE_OPEN
codex_release: OPEN_WINDOWS_RUNTIME_PAYLOAD_CLOSURE
previous_work_order: R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001
previous_work_order_result: EDITING_AUDIO_SUBTITLE_WAVE_ACCEPTED
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Routing truth

Accepted Workspace/UX baseline:

`4b2b4ed5f6e2347ae3b29381f39e79ad6930e393` (PR #17).

Accepted Windows Packaging foundation baseline:

`cb63713c0daa02b396fd4f5268d280af831d5f70` (PR #19).

PR #19 foundation head `cf3e4ff7f2a05b88dabef33867ef813f67956cfb` passed the Windows Packaging Candidate workflow and PR CI. The workflow uploaded the SHA-addressed artifact `VideoEditingAgent-windows-x64-cf3e4ff7f2a05b88dabef33867ef813f67956cfb` with GitHub artifact digest `sha256:1a3637a7e0725ae68e0854fc2dc2c0e7e581e406a4ca02db0b3645258bd9e46c`.

The squash-merged main head `cb63713c0daa02b396fd4f5268d280af831d5f70` passed main CI and document-registry.

## Current truth

- Planning Product/Human Gate remains PASS for the supported 1.0 surface.
- Remote reference URL remains deferred to 2.0; local reference video remains supported.
- Ordinary no-speech Editing Human evidence remains PASS.
- Project Workspace + UX consolidation is ACCEPTED / MERGED.
- Windows x64 onedir **foundation** is ACCEPTED / MERGED: manifest/schema, frozen/development locator, Doctor integration, PyInstaller build, static package inspection, packaged launcher/Doctor/external-Workspace smoke and SHA-addressed artifact evidence are real.
- The foundation artifact is not the final product artifact because FFmpeg/ffprobe, TransNet and speech runtime/model payloads are not yet closed as reproducible release payloads.
- Basic original speech + trusted subtitles remains a retained 1.0 Human Gate.
- The remaining Workspace ordinary-user Human check stays consolidated into the final packaged-artifact Human Gate; it is not waived.
- Stage-A completion remains OPEN and structural progress remains 95%.

## Active execution boundary

`R0.12-STAGE-A-FINAL-CLOSURE-002`

Active construction branch:

`work/r012-runtime-payload-closure`

Active task:

**Runtime Payload Closure** — convert the accepted packaging foundation's managed/external placeholders into exact Windows runtime payloads with provenance, hashes, notices, Doctor readiness and real load/execute evidence.

Required payload families:

1. FFmpeg/ffprobe — exact Windows x64 LGPL payload only; no GPL/nonfree developer `full_build` copying.
2. TransNetV2 — `transnetv2-pytorch==1.0.5`, package-owned weights, exact package identity plus CPU PyTorch/native dependency closure.
3. Speech — `faster-whisper==1.2.1`, pinned `Systran/faster-whisper-base@ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`, CPU/int8, local-files-only, exact native dependency/model identity.

Remote provider code may remain bundled; API secrets never bundle.

Codex may perform bounded Windows/native/build self-repair inside this released task. It must not expand into installer/onefile/updater/signing, Remote Reference 2.0, TTS, advanced separation/effects, or Domain/EDL authority changes.

Do not report Stage-A 100% until `docs/roadmap/STAGE_A_COMPLETION_GATE.md` and the final machine/Human gates genuinely pass.
