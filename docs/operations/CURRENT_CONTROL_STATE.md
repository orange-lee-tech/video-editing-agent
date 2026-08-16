# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-16
current_phase: R0.12
phase_state: STAGE_A_PRODUCT_IO_CONTRACT_ACTIVE
active_work_order: R0.12-STAGE-A-PRODUCT-IO-CONTRACT-001
accepted_code_baseline: 500c8563e3686a5aaef055ffb5301553aa999fd9
control_plane_baseline: 0229f102a4016d942e6ea9f05d7b43d5191e2215
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
core_2_editing_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
previous_work_order: R0.12-PREVIEW-BACKEND-BENCHMARK-001
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

Accepted production-code baseline remains `500c8563e3686a5aaef055ffb5301553aa999fd9`.

## Stage-A completion truth

Structural progress remains **90%**.

Canonical hard gate:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Live state:

- `stage_a_completion_gate: OPEN`;
- Core 1 Planning: foundation accepted, ordinary-user product flow still open;
- Core 2 Editing: foundation accepted, ordinary-user automatic final-MP4 flow still open.

100% remains forbidden until both core Product Gates and the overall Stage-A gate are `PASS`.

## Preview decision — CLOSED

`R0.12-PREVIEW-BACKEND-BENCHMARK-001` is PASS/CLOSED.

Accepted ADR:

`docs/adr/ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`

Decision:

- primary Stage-A Preview backend family: **GStreamer**;
- initial accepted evidence baseline: GStreamer `1.28.6` Windows x86_64 MSVC private runtime;
- normal path: high-level GstPlay/playbin3 with D3D11 acceleration when available;
- degraded path: explicit software video decode with observable diagnostics;
- libVLC `3.0.23`: validated alternative adapter family, not default dual-bundled fallback;
- libmpv: hard-gate excluded for Stage A because the required auditable LGPL Windows D3D11 distribution path would make the project own a disproportionate custom build/transitive-license maintenance surface.

Durable libmpv gate record:

`docs/validation/R0.12_PREVIEW_LIBMPV_LGPL_HARD_GATE_EXCLUSION.md`

PreviewBackend remains playback-only. EDL remains sole exact timeline authority.

### Preview evidence retained

Accepted evidence includes:

- Class-A Windows environment/device capability;
- GStreamer/VLC official/private runtime provenance;
- actual deterministic windowed playback for both families;
- VLC D3D11VA hardware decode proof;
- GStreamer actual `playbin3 → decodebin3 → d3d11h264dec → D3D11Memory/NV12 → d3d11videosink` path;
- GstPlay/libVLC start-pause-eight-seek-resume-release control PASS;
- three real phone HEVC files: GStreamer normal 3/3 PASS, libVLC normal 3/3 PASS;
- GStreamer explicit software decode 3/3 PASS;
- libVLC explicit software decode PASS using per-media `:avcodec-hw=none`.

Retained gaps:

- no actual VFR file in the real-phone corpus;
- no Class-B/Class-C host evidence;
- no total no-GPU/no-presentation-device simulation.

These are integration/Product-Probe risks, not reasons to reopen backend-family selection.

## Current active boundary — Stage-A Product I/O Contract

`R0.12-STAGE-A-PRODUCT-IO-CONTRACT-001` is ACTIVE.

The project now focuses on the actual ordinary-user path:

`user-visible inputs`
`→ owned application/domain transformations`
`→ persisted/inspectable outputs`
`→ understandable progress/failure/retry`

The contract must cover Planning-only, Editing-only and Combined while preserving Brief as the shared root and Planning artifacts as optional Editing enrichment.

### Product I/O gap corridor

The immediate sequence is:

1. freeze Stage-A Product I/O Contract;
2. implement mixed source-audio semantics + speech protection + audible-lane QC;
3. implement Reference URL acquisition into controlled local reference media;
4. implement rights-aware public music discovery/acquisition into controlled local governed Assets;
5. finish remaining bounded R0.12 productization and production GStreamer Preview integration where justified;
6. minimum Review/repair loop;
7. ordinary-user Windows runtime / Environment Doctor;
8. practical product-facing integration;
9. real Product Probes / Human Gate.

## Known Product I/O risks carried into the active Work Order

### Mixed source audio — P0

A whole-EditPlan `MUTE/PRESERVE/DUCK` meaning is insufficient for a folder containing speech clips, environment clips and clips whose source audio should not be used. Ownership must move to source-selection/source-range semantics without giving Renderer editorial authority.

### VoiceTreatment — P1

The product must distinguish preserve / clean / allow-revoice / do-not-use-original. Poor source quality alone must not authorize replacement or deletion of user speech.

### Reference URL acquisition — P1

Target semantic route:

`supported URL → acquisition adapter → controlled local file → REFERENCE_ANALYSIS_ONLY → existing analysis/planning`

Login/DRM/unsupported/auth-required inputs fail closed.

### Public music provider — P0

Search is not sufficient. Product semantics require rights-aware selection + acquisition + controlled local governed Asset before the existing Music/BeatMap/audio chain can consume the result.

### Non-silent audible-lane QC

Final technical QC must reject an unintentionally silent result when the intent requires audible content. Renderer must not invent audio to repair this condition.

## Tool routing

### ChatGPT + GitHub

Primary for the active Product I/O contract and governance synchronization.

### User PowerShell

Use only when a genuine Windows/private-media/runtime boundary appears. No local benchmark is required merely to write the Product I/O contract.

### Codex

**NO ACTIVE RELEASE** for the contract.

The first expected next release is the bounded mixed source-audio + speech protection + audible-QC implementation batch after the contract freezes exact ownership and tests.

## Constitutional constraints

- EDL remains sole exact timeline authority.
- Renderer executes canonical EDL and does not make editorial decisions.
- PreviewBackend is playback-only.
- original user media is never overwritten.
- commercial output visual material remains user-supplied local media.
- reference media defaults to analysis-only.
- remote/public visual replacement footage is not silently acquired.
- CPU/software degraded strategies remain part of supported product direction.
- no temporary shortcut may fabricate Planning artifacts, source timestamps, Domain decisions or a Product Gate PASS.

## Documentation synchronization rule

Dynamic state is canonical only in:

- `docs/operations/CURRENT_CONTROL_STATE.md`;
- `docs/operations/CURRENT_WORK_ORDER.md`;
- `docs/roadmap/CURRENT_PHASE_STATUS.md`.

`tools/maintenance/repo_doctor.py` + `repository-governance` check machine-detectable consistency.

## STOP boundary

Do not reopen Preview family benchmarking after ADR-010 without a concrete Product Probe failure or new hard requirement.

Do not concurrently implement GUI/frontend, Reference URL, music acquisition or mixed-audio code until the active Product I/O contract locates their ownership boundaries precisely enough to issue bounded implementation work.
