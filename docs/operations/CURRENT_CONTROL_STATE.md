# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-25
current_phase: R0.12
phase_state: STAGE_A_FINAL_PRODUCT_HUMAN_GATE_ACTIVE
active_work_order: R0.12-STAGE-A-FINAL-CLOSURE-002
active_construction_branch: NONE
accepted_code_baseline: c2c959239cf8842388ac661777c19f20f64a6a90
main_preparation_baseline: c2c959239cf8842388ac661777c19f20f64a6a90
control_plane_baseline: c2c959239cf8842388ac661777c19f20f64a6a90
structural_progress_percent: 95
stage_a_completion_gate: OPEN
core_1_planning_product_gate: PASS
core_2_editing_product_gate: PARTIAL_HUMAN_PASS_FINAL_PACKAGED_SPEECH_GATE_OPEN
codex_release: CLOSED_NO_ACTIVE_CODEX_RELEASE
previous_work_order: R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001
previous_work_order_result: EDITING_AUDIO_SUBTITLE_WAVE_ACCEPTED
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Accepted engineering baseline

Stage-A engineering construction is now closed at main code baseline:

`c2c959239cf8842388ac661777c19f20f64a6a90` (PR #20).

Accepted predecessor baselines:

- Workspace/UX: `4b2b4ed5f6e2347ae3b29381f39e79ad6930e393` (PR #17);
- Windows Packaging foundation: `cb63713c0daa02b396fd4f5268d280af831d5f70` (PR #19).

PR #20 closes the exact Windows runtime payloads without changing Domain/EDL/Renderer authority:

- BtbN FFmpeg/ffprobe 8.1 LGPL-only shared payload with exact archive identity and runtime configuration validation;
- `transnetv2-pytorch==1.0.5` + `torch==2.13.0+cpu`, package-owned weights and a real CPU prediction probe;
- `faster-whisper==1.2.1` + CTranslate2/PyAV + exact local `faster-whisper-base` revision, CPU/int8/local-files-only and a real offline ASR probe;
- PyAV wheel-provided broad/GPL codec DLLs excluded and its extensions proven against the approved LGPL FFmpeg DLL set;
- CPython packaging interpreter pinned and fail-closed at 3.12.13;
- manifest, notices, deterministic component tree hashes, static inspection, Doctor, runtime probe, GUI launcher and external Workspace evidence retained.

## Independent verification

ChatGPT did not accept the initial Codex report blindly.

The first clean GitHub build exposed a missing PyTorch CPU index in runtime staging; this was fixed. A second review found that clean CI selected CPython 3.12.10 while the manifest declared 3.12.13; the workflow and build script were then pinned/fail-closed to 3.12.13.

The final PR head `e22cb3cb96ba13414cff7d13deaa15a647bd8542` passed PR CI, document-registry and the complete Windows Packaging Candidate workflow.

Merged main `c2c959239cf8842388ac661777c19f20f64a6a90` passed main CI and document-registry and produced a clean Windows Packaging artifact after build/inspect/smoke. The SHA-addressed artifact is:

`VideoEditingAgent-windows-x64-c2c959239cf8842388ac661777c19f20f64a6a90`

GitHub artifact digest:

`sha256:a21a71211c0bee6848f93852d2f4cf6d27cd194b89f92a1fed6e4c24ccd57d5d`

Compressed artifact size: `768923438` bytes.

## Current truth

- Planning Product/Human Gate remains PASS on the supported 1.0 surface.
- Remote Reference URL remains deliberately deferred to 2.0; local reference video remains supported.
- Ordinary no-speech Editing Human evidence remains PASS.
- Workspace/UX engineering and Windows Packaging/runtime engineering are ACCEPTED.
- The packaged GUI has an ordinary-user API/Provider settings surface; users do not need PowerShell to inject keys. Optional saved API profiles use Windows DPAPI and plaintext secret fields are forbidden from profile files.
- No active Codex construction release exists. Re-open Codex only if the final Human Gate exposes a genuine implementation defect.
- The only current Stage-A blocker is final ordinary-user packaged Product/Human evidence, especially clear original speech + trusted subtitles and the consolidated packaged Workspace/UX check.
- Structural progress remains 95%. Stage-A 100% is forbidden until the final Human Gate passes.

## Final gate boundary

Use the exact accepted packaged product path, not a repository/uv/Python developer path.

The final Human Gate must establish:

1. ordinary double-click launcher works without repository/Python/uv/Git setup;
2. API/Provider configuration works through the GUI without exposing keys;
3. external Project Workspace and output behavior remain understandable and outside the install tree;
4. supported Planning-only path remains usable;
5. Editing-only with clear single-speaker original speech produces a real final MP4 with preserved source voice and grounded trusted subtitles;
6. Combined mode remains usable when valid Planning context exists and Planning remains enrichment rather than an activation license;
7. original media remains untouched and failures/progress are understandable;
8. exact artifact/main identity and observations are recorded.

Only after those checks pass may `core_2_editing_product_gate`, `stage_a_completion_gate` and structural progress move to PASS / 100.
