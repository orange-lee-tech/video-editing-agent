# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-17
current_phase: R0.12
phase_state: WINDOWS_ENVIRONMENT_DOCTOR_ACTIVE
active_work_order: R0.12-WINDOWS-ENVIRONMENT-DOCTOR-001
accepted_code_baseline: 2cfeb664552769ade09f58bc2905ab531733a66a
control_plane_baseline: 7c91fc8c50d56931baa6032b377f60548ac6c80b
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
core_2_editing_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
previous_work_order: R0.12-MINIMUM-REVIEW-REPAIR-LOOP-001
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

Current accepted production-code baseline:

`2cfeb664552769ade09f58bc2905ab531733a66a`

## Stage-A completion truth

Structural progress remains **90%**.

Canonical hard gate:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Live state:

- `stage_a_completion_gate: OPEN`;
- Core 1 Planning: foundation accepted, ordinary-user product flow open;
- Core 2 Editing: foundation accepted, ordinary-user automatic final-MP4 flow open.

100% remains forbidden until both Product Gates and the overall Stage-A gate are PASS.

## Closed control boundaries

### Preview backend + production integration — PASS/CLOSED

- `docs/adr/ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`
- `docs/validation/R0.12_PRODUCTION_GSTREAMER_PREVIEW_INTEGRATION_EVIDENCE.md`
- accepted baseline `4ca3b83bfac50923bdcf15f1ad08d90b397daa23`
- Windows run `32030024748` — PASS.

GStreamer remains primary; Preview remains playback-only; player/backend benchmark remains closed.

### Stage-A Product I/O Contract — PASS/CLOSED

`docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

### Mixed source-audio / VoiceTreatment / audible QC — PASS/CLOSED

- `R0.12-MIXED-SOURCE-AUDIO-QC-001`
- `docs/validation/R0.12_MIXED_SOURCE_AUDIO_QC_CLOSURE.md`

### Reference URL acquisition — PASS/CLOSED

- `R0.12-REFERENCE-URL-ACQUISITION-001`
- `docs/validation/R0.12_REFERENCE_URL_ACQUISITION_CLOSURE.md`
- accepted baseline `d15abf9258c0a080e37d666cd1112358723e823a`

### Rights-aware public music acquisition — PASS/CLOSED

- `R0.12-PUBLIC-MUSIC-ACQUISITION-001`
- `docs/validation/R0.12_PUBLIC_MUSIC_ACQUISITION_EVIDENCE.md`
- accepted baseline `72ec275c1e72e876c4bcf828a44e7852208bab29`
- Windows provider run `32026331114` — PASS.

### Minimum post-render Review / bounded repair — PASS/CLOSED

- `R0.12-MINIMUM-REVIEW-REPAIR-LOOP-001`
- `docs/validation/R0.12_MINIMUM_REVIEW_REPAIR_CLOSURE.md`
- accepted production baseline `2cfeb664552769ade09f58bc2905ab531733a66a`
- deterministic Quality Gate `32032812665` — PASS;
- real-media Windows Review run `32033179672` — PASS.

Durable semantics:

- Review consumes exact RenderArtifact/EDL provenance and deterministic post-render evidence;
- clean delivered media can pass;
- unexpected mostly-silent audio with audible intent routes back to `AudioEditorialService`;
- same-EDL technical retry is explicit and bounded;
- Review cannot mutate EDL/editorial/render state.

## Current active boundary — Windows Environment Doctor

`R0.12-WINDOWS-ENVIRONMENT-DOCTOR-001` is ACTIVE.

### Audit truth

The Stage-A compatibility floor cannot assume a preconfigured developer workstation.

Current runtime facts are fragmented:

- Python 3.12+ is required;
- FFmpeg/ffprobe are external executables used across media ingest/render/Review;
- GStreamer Preview uses a private-runtime contract;
- cloud intelligence provider keys are configured through environment variables;
- optional local acceleration/model packages are not basic-core requirements;
- existing PowerShell installers and Probes are developer evidence rather than one product-owned capability report.

### Frozen ownership

```text
machine/runtime facts
→ EnvironmentDoctor application owner
→ replaceable capability probes
→ typed per-capability status/product impact
→ sanitized repair report
```

Environment Doctor may inspect and classify. It cannot mutate Domain/EDL/project creative state and cannot install arbitrary dependencies in this Work Order.

### Minimum capability truth to expose

- supported Windows / Python runtime;
- FFmpeg + ffprobe execution readiness;
- configured Preview private-runtime readiness/state;
- DeepSeek Planning/Director configuration presence;
- Gemini/OpenAI visual-provider alternative configuration presence;
- optional capability/degradation without making GPU mandatory;
- sanitized repair guidance and rerun instruction.

### Secret boundary

API key values, OAuth tokens, cookies and full environment dumps are forbidden from Doctor results and repair reports.

Provider key presence is configuration evidence only; it is not a live provider-connectivity PASS.

### Installer boundary

The Work Order does **not** freeze final installer technology, private Python packaging, admin/system-wide mutation, signed updates or CUDA/Torch model management.

### Real evidence gate

Require deterministic tests plus one bounded Windows production Environment Doctor Probe proving:

- actual host facts;
- real FFmpeg/ffprobe readiness;
- typed non-ready handling for one unavailable component;
- synthetic secret redaction;
- no project/Domain mutation;
- structured output suitable for later UI consumption.

## Codex quota constraint

Approximately **9% Codex quota remains**.

### ChatGPT + GitHub

Primary for contract reduction, deterministic implementation/tests, CI/Windows Engineering Probe and governance.

### Codex

**NO ACTIVE RELEASE.**

Release only for a genuine Windows-only multi-file runtime defect that connector-first + hosted Windows evidence cannot close efficiently.

### User PowerShell

Use only if hosted Windows evidence is insufficient or a real local-user/Human Gate is required.

## Immediate corridor after active work

1. Windows Environment Doctor / ordinary-user runtime diagnostics;
2. practical product-facing orchestration/integration;
3. real Planning Product Probe + Human Gate;
4. real Editing automatic-final-MP4 Product Probe + Human Gate;
5. Stage-A 100% only after all hard gates pass.

## Constitutional constraints

- canonical EDL remains the sole exact timeline authority;
- Preview remains playback-only;
- Renderer executes canonical EDL and does not make editorial decisions;
- Review classifies evidence and routes correction only;
- Planning-only / Editing-only / Combined remain legitimate parallel entries;
- originals remain protected from overwrite;
- untrusted media/provider text cannot become execution authority;
- structural progress remains 90% until ordinary-user product-gate structure genuinely changes.
