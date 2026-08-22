# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-22
current_phase: R0.12
phase_state: STAGE_A_WORKSPACE_UX_CONSOLIDATION_ACTIVE
active_work_order: R0.12-STAGE-A-FINAL-CLOSURE-002
active_construction_branch: work/r012-workspace-ux-consolidation
accepted_code_baseline: 756a30562dd512fba9868eeee43cf6422f60f642
main_preparation_baseline: d26249f71d895efff54c1d7167f4b6bc457b98f1
control_plane_baseline: e758c3dfb2cab08b901001c5c59379583d249a06
structural_progress_percent: 95
stage_a_completion_gate: OPEN
core_1_planning_product_gate: PASS
core_2_editing_product_gate: PARTIAL_HUMAN_PASS_PACKAGING_AND_SPEECH_EVIDENCE_OPEN
codex_release: OPEN_WORKSPACE_UX_ONLY
previous_work_order: R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001
previous_work_order_result: EDITING_AUDIO_SUBTITLE_WAVE_ACCEPTED
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Routing truth

Accepted production-code baseline is `756a30562dd512fba9868eeee43cf6422f60f642` (PR #13).

Accepted repository-attention/document-governance baseline is `e758c3dfb2cab08b901001c5c59379583d249a06` (PR #12).

Current documentation/packaging-preparation main baseline is `d26249f71d895efff54c1d7167f4b6bc457b98f1` after PRs #14/#15.

Durable evidence:

- `docs/validation/R0.12_EDITING_AUDIO_SUBTITLE_CLOSURE_2026-08-21.md`
- `docs/validation/R0.12_REFERENCE_COMPATIBILITY_CLOSURE_2026-08-22.md`

## Current truth

- Planning Product/Human Gate remains PASS for the supported 1.0 surface.
- Remote reference URL is **not** an ordinary 1.0 feature. The Tkinter URL field is hidden; local reference video remains supported.
- Bounded Bilibili acquisition remains an engineering fallback seam only. Provider-neutral remote/video-native `ReferenceObservation` is deferred to 2.0.
- Ordinary no-speech Editing Human evidence is PASS: real user footage reached final MP4 with source audio and natural rights-safe BGM; captions were correctly not fabricated.
- Basic speech-bearing original voice + trusted subtitle execution remains a retained 1.0 gate and still needs approved/pinned speech runtime/model plus real Human evidence.
- Production synthetic voice/TTS, advanced speech/ambience separation, rich subtitle/effects systems, remote-video observation and feature-rich NLE behavior are deferred beyond 1.0.
- Project Workspace + UX consolidation is now the active released construction wave and must complete before Packaging begins.
- A real Windows distributable proof remains required before structural 100%: ordinary target environment must not require Python, uv or repository execution.
- Packaging/bootstrap/resource location must remain replaceable and outside Domain authority.

## Active execution boundary

`R0.12-STAGE-A-FINAL-CLOSURE-002`

Active construction branch:

`work/r012-workspace-ux-consolidation`

Active specification:

`docs/operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`

Execution order:

1. repository attention/document governance — ACCEPTED;
2. bounded reference compatibility decision — ACCEPTED, remote URL deferred to 2.0 and hidden in 1.0;
3. Project Workspace + UX consolidation — ACTIVE / RELEASED;
4. compatible Windows packaging foundation and clean-machine-ish proof — PREPARED / NOT RELEASED;
5. final retained 1.0 Product/Human evidence and closure synchronization.

Do not report Stage-A 100% until `docs/roadmap/STAGE_A_COMPLETION_GATE.md` and the machine/human gates are genuinely satisfied.
