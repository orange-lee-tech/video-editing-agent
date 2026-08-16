# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-16
current_phase: R0.12
phase_state: PREVIEW_LIBMPV_LGPL_GATE_ACTIVE
active_work_order: R0.12-PREVIEW-BACKEND-BENCHMARK-001
accepted_code_baseline: 500c8563e3686a5aaef055ffb5301553aa999fd9
control_plane_baseline: ca271e41ffc6eb9e4258d14059297dc0fadf1ccb
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
core_2_editing_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
previous_work_order: R0.12-EDITING-DIRECTOR-ENTRY-001
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

Accepted production-code baseline remains `500c8563e3686a5aaef055ffb5301553aa999fd9`. The active Work Order remains evidence/ADR-only; no production Preview implementation is authorized yet.

## Stage-A completion truth

Structural progress remains **90%**.

Canonical hard gate:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Live state:

- `stage_a_completion_gate: OPEN`;
- Core 1 Planning: foundation accepted, ordinary-user product flow still open;
- Core 2 Editing: foundation accepted, ordinary-user automatic final-MP4 flow still open.

100% remains forbidden until both core Product Gates and the overall Stage-A gate are `PASS`.

## Current active boundary

`R0.12-PREVIEW-BACKEND-BENCHMARK-001` is ACTIVE.

Current state:

`private candidate runtimes + deterministic playback/control PASS`
`→ real phone HEVC + explicit software fallback ACCEPTED`
`→ auditable libmpv LGPL gate ACTIVE`
`→ final candidate comparison`
`→ Preview backend ADR`
`→ close benchmark`

PreviewBackend remains playback-only. EDL remains sole exact timeline authority.

## Current Preview evidence state

### Stage 0 — environment/device capability — PASS

Durable evidence:

`docs/validation/R0.12_PREVIEW_STAGE0_WINDOWS_ENVIRONMENT_EVIDENCE.md`

Accepted Class-A host evidence includes ThinkPad T470s / Intel HD Graphics 520, restored Lenovo OEM driver `27.20.100.8854`, Oray retained, FFmpeg software H.264 decode PASS and D3D11VA H.264 decode PASS.

### Stage 1 — GStreamer/VLC provenance/private runtime — PASS

Durable evidence:

`docs/validation/R0.12_PREVIEW_STAGE1_CANDIDATE_PREPARATION_EVIDENCE.md`

Accepted:

- GStreamer 1.28.6 official MSVC private runtime with D3D11 decoder/sink capability;
- VLC/libVLC 3.0.23 official static win64 private runtime;
- no global executable PATH dependency required by the benchmark.

### Stage 3 — GStreamer/VLC real playback/control/fallback — ACCEPTED FOR CURRENT CLASS-A SCOPE

Durable evidence:

- `docs/validation/R0.12_PREVIEW_REAL_PLAYBACK_BENCHMARK_EVIDENCE.md`
- `docs/validation/R0.12_PREVIEW_WAVE3_REAL_MEDIA_SOFTWARE_FALLBACK_EVIDENCE.md`

Accepted evidence:

- both GStreamer and VLC completed actual windowed playback on the deterministic fixture;
- VLC directly proved D3D11VA hardware decode on Intel HD Graphics 520;
- GStreamer directly proved the real high-level hardware path `playbin3 → decodebin3 → d3d11h264dec → D3D11Memory/NV12 → d3d11videosink`;
- GStreamer GstPlay and libVLC both passed pause, eight randomized absolute seeks, resume and clean release;
- three real phone HEVC files: GStreamer normal 3/3 PASS, libVLC normal 3/3 PASS;
- GStreamer explicit software decode fallback: 3/3 PASS with DOT evidence;
- libVLC explicit software decode fallback: PASS using per-media `:avcodec-hw=none`;
- libVLC instance/global `--avcodec-hw=none` alone is recorded as unreliable for this tested embedding path because it still selected D3D11VA;
- per-media and combined libVLC runs logged `matching "none"` and `no hw decoder modules matched` while control remained PASS.

Evidence gaps retained honestly:

- no actual VFR behavior was present in the accepted real-phone corpus;
- Class-B ordinary-current-Windows evidence is missing;
- Class-C newer-accelerated evidence is missing;
- total no-GPU/no-presentation-device behavior was not simulated.

These gaps do not reopen the accepted deterministic, real-HEVC or explicit software-decode evidence.

### Current action — libmpv LGPL provenance/build gate

The third candidate family is now the active boundary.

Required outcome is one of:

1. an auditable Windows libmpv candidate configured for the approved LGPL path, with dependency/subproject build/license review; or
2. a documented hard-gate exclusion if a reproducible acceptable Windows LGPL build/distribution path cannot be established without disproportionate product/license/deployment risk.

Hard rules:

- upstream/default GPL builds are not silently adopted;
- arbitrary common third-party Windows binaries are not accepted as product evidence;
- build flags alone are insufficient without dependency/subproject review;
- Codex remains unreleased for provenance/build research.

### After libmpv

`GStreamer / libVLC / libmpv final comparison → Preview ADR → close benchmark`

Do not continue open-ended player benchmarking after the ADR.

## Tool routing

### ChatGPT + GitHub

- current-state/CI observation;
- official dependency/license/runtime verification;
- benchmark/ADR reasoning;
- small deterministic governance/validation writes;
- Preview Work Order closure.

### User PowerShell

- private runtime execution where a local Windows build/probe is actually required;
- private media and hardware/runtime evidence.

### Codex

**NO ACTIVE RELEASE.** Preserve quota for bounded production integration or difficult multi-file runtime debugging after the backend decision.

## Final-10-percent execution corridor

After Preview closure, return immediately to the product I/O/productization corridor rather than expanding player research:

1. Stage-A Product I/O Contract;
2. mixed source-audio semantics + speech protection + audible QC;
3. Reference URL acquisition;
4. rights-aware public music provider/acquisition;
5. remaining bounded R0.12 productization and production Preview integration;
6. minimum Review/repair loop;
7. ordinary-user Windows runtime / Environment Doctor;
8. practical product-facing integration for both cores;
9. real Product Probes / Human Gate, then and only then structural 100%.

## Constitutional constraints

- EDL remains sole exact timeline authority.
- PreviewBackend is playback-only.
- final rendering remains canonical EDL → Renderer.
- original user media is never overwritten.
- CPU/software fallback remains supported; GPU is optional routing.
- no unreviewed third-party binary becomes a product distribution dependency.
- GUI/desktop framework remains undecided during this benchmark.
- no temporary shortcut may fabricate Planning artifacts, source timestamps, Domain decisions or a Product Gate PASS.

## Documentation synchronization rule

Dynamic state is canonical only in:

- `docs/operations/CURRENT_CONTROL_STATE.md`;
- `docs/operations/CURRENT_WORK_ORDER.md`;
- `docs/roadmap/CURRENT_PHASE_STATUS.md`.

`tools/maintenance/repo_doctor.py` + `repository-governance` check machine-detectable consistency.

## STOP boundary

Do not concurrently implement Graphics/transitions, Proxy/cache, Renderer operational controls, GUI/desktop frontend, packaging or EDL redesign while the Preview benchmark remains active unless the Work Order is explicitly revised.
