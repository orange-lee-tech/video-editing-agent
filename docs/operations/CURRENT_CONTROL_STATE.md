# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-16
current_phase: R0.12
phase_state: MIXED_SOURCE_AUDIO_QC_IMPLEMENTATION_ACTIVE
active_work_order: R0.12-MIXED-SOURCE-AUDIO-QC-001
accepted_code_baseline: 500c8563e3686a5aaef055ffb5301553aa999fd9
control_plane_baseline: cc5cd0206cfc26f5f6076014bdfe69e7463e63f5
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
core_2_editing_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
previous_work_order: R0.12-STAGE-A-PRODUCT-IO-CONTRACT-001
previous_work_order_result: PASS
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Routing truth

The accepted two-core architecture remains unchanged:

- Planning-only: `Brief → ScriptPlan → ShootingPlan`;
- Editing-only: `Brief/editorial intent + user local footage → Editing Core`;
- Combined: Planning artifacts optionally enrich the same Editing Core.

Accepted production-code baseline entering the active implementation remains `500c8563e3686a5aaef055ffb5301553aa999fd9`.

## Stage-A completion truth

Structural progress remains **90%**.

Canonical hard gate:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Live state:

- `stage_a_completion_gate: OPEN`;
- Core 1 Planning: foundation accepted, ordinary-user product flow still open;
- Core 2 Editing: foundation accepted, ordinary-user automatic final-MP4 flow still open.

100% remains forbidden until both core Product Gates and the overall Stage-A gate are `PASS`.

## Closed control boundaries

### Preview backend benchmark — PASS/CLOSED

Accepted ADR:

`docs/adr/ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`

- GStreamer primary Stage-A Preview family;
- libVLC validated alternative;
- libmpv Stage-A hard-gate exclusion;
- Preview playback-only; EDL authority unchanged.

Do not reopen backend-family benchmarking without a concrete Product Probe failure/new hard requirement.

### Stage-A Product I/O Contract — PASS/CLOSED

Canonical contract:

`docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

Validation:

`docs/validation/R0.12_STAGE_A_PRODUCT_IO_CONTRACT_EVIDENCE.md`

Accepted ordinary-user semantics now freeze:

- project create/open → existing `ProjectWorkspace`;
- selected local files/folders → per-file local Asset ingest;
- Planning-only → persisted ScriptPlan/ShootingPlan owner workflows;
- Editing-only → independent Brief + local footage path;
- Combined → same Editing Core enriched by exact Planning revisions;
- Reference URL → controlled local `REFERENCE_ANALYSIS_ONLY` file/Asset before planning analysis;
- public music → rights-aware acquisition → controlled local `MUSIC` Asset before Music/BeatMap/Audio;
- final MP4 → explicit Renderer output path;
- no frontend framework decision yet.

## Current active boundary — mixed source-audio / voice / audible QC

`R0.12-MIXED-SOURCE-AUDIO-QC-001` is ACTIVE.

The current implementation defect is concrete:

- `AudioMixDecision` has one whole-EditPlan `source_audio_policy`;
- `plan_basic_mix()` chooses whole-plan PRESERVE when speech exists and MUTE otherwise;
- `DeterministicEDLBuilder` clones every selected video segment onto SOURCE_AUDIO for global PRESERVE;
- whole-plan DUCK is unsupported;
- mixed selected source ranges therefore cannot independently preserve/duck/mute their original audio.

### Frozen implementation ownership

Resolver / `ResolvedSelection` retains authoritative selected Shot/source range.

Audio Editorial owns treatment intent at grounded selection/source-range granularity.

Required source treatment:

- PRESERVE
- DUCK
- MUTE

Required VoiceTreatment policy:

- PRESERVE
- CLEAN
- ALLOW_REVOICE
- DO_NOT_USE_ORIGINAL

EDLBuilder deterministically maps approved treatment to exact SOURCE_AUDIO selections/ranges.

Renderer executes validated EDL only and must not infer/rewrite treatment.

For non-silent intent, final technical QC must fail closed when no approved audible lane exists. Renderer must not invent audio to repair that condition.

### Codex

**ACTIVE RELEASE — SINGLE COMPLEX BATCH.**

Codex is primary writer for the implementation/test surface described by `CURRENT_WORK_ORDER.md` until it stops and reports.

ChatGPT must not concurrently edit those same source/test files during the batch.

After Codex report:

`reobserve origin/main → inspect commit/diff → inspect CI/governance → verify required audio/EDL/QC cases → accept/repair → sync control plane`

Codex does not self-authorize the next Work Order.

## Immediate corridor after the active batch

1. accept/repair mixed source-audio + VoiceTreatment + audible-lane QC;
2. Reference URL acquisition;
3. rights-aware public music acquisition;
4. remaining bounded R0.12 productization including production GStreamer Preview integration;
5. minimum Review/repair loop;
6. ordinary-user Windows runtime / Environment Doctor;
7. practical product-facing integration;
8. real Product Probes / Human Gate.

## Tool routing

### ChatGPT + GitHub

- current-state/CI observation;
- architecture/acceptance review;
- Work Order/control-plane synchronization;
- small independent governance writes.

### User PowerShell

Use only for genuine local/private-media/runtime boundaries. This implementation batch itself belongs to Codex's local repo edit/test loop.

### Codex

Primary writer for the active bounded implementation batch.

## Constitutional constraints

- EDL remains sole exact timeline authority.
- Renderer executes canonical EDL and does not make editorial decisions.
- PreviewBackend is playback-only.
- original user media is never overwritten.
- commercial output visual material remains user-supplied local media.
- reference media defaults to analysis-only.
- Editing-only remains independent of fabricated Planning artifacts.
- poor source speech quality does not authorize semantic deletion/replacement/revoice.
- no temporary shortcut may fabricate source timestamps, Domain decisions or a Product Gate PASS.

## Documentation synchronization rule

Dynamic state is canonical only in:

- `docs/operations/CURRENT_CONTROL_STATE.md`;
- `docs/operations/CURRENT_WORK_ORDER.md`;
- `docs/roadmap/CURRENT_PHASE_STATUS.md`.

`tools/maintenance/repo_doctor.py` + `repository-governance` check machine-detectable consistency.

## STOP boundary

Do not concurrently open Reference URL, music acquisition, GUI/frontend or production Preview implementation while Codex owns the current mixed-audio/QC batch.

Do not increase structural progress from 90% merely because this batch adds tests or typed decisions.
