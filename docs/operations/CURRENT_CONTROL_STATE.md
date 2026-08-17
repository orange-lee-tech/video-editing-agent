# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-17
current_phase: R0.12
phase_state: MINIMUM_REVIEW_REPAIR_LOOP_ACTIVE
active_work_order: R0.12-MINIMUM-REVIEW-REPAIR-LOOP-001
accepted_code_baseline: 4ca3b83bfac50923bdcf15f1ad08d90b397daa23
control_plane_baseline: bcb6e37e9ddc5a6fdc50687d4e680a59459c04c2
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
core_2_editing_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
previous_work_order: R0.12-PRODUCTION-PREVIEW-INTEGRATION-001
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

Current accepted production-code baseline is:

`4ca3b83bfac50923bdcf15f1ad08d90b397daa23`

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

`docs/adr/ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`

GStreamer primary; Preview playback-only; EDL authority unchanged. Backend-family selection remains closed.

### Stage-A Product I/O Contract — PASS/CLOSED

`docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

### Mixed source-audio / VoiceTreatment / audible QC — PASS/CLOSED

`R0.12-MIXED-SOURCE-AUDIO-QC-001`

Closure evidence:

`docs/validation/R0.12_MIXED_SOURCE_AUDIO_QC_CLOSURE.md`

### Reference URL acquisition — PASS/CLOSED

`R0.12-REFERENCE-URL-ACQUISITION-001`

Closure evidence:

`docs/validation/R0.12_REFERENCE_URL_ACQUISITION_CLOSURE.md`

Accepted production baseline:

`d15abf9258c0a080e37d666cd1112358723e823a`

### Rights-aware public music acquisition — PASS/CLOSED

`R0.12-PUBLIC-MUSIC-ACQUISITION-001`

Closure evidence:

`docs/validation/R0.12_PUBLIC_MUSIC_ACQUISITION_EVIDENCE.md`

Accepted production baseline:

`72ec275c1e72e876c4bcf828a44e7852208bab29`

Final bounded Windows provider run:

`32026331114` — PASS.

### Production GStreamer Preview integration — PASS/CLOSED

`R0.12-PRODUCTION-PREVIEW-INTEGRATION-001`

Closure evidence:

`docs/validation/R0.12_PRODUCTION_GSTREAMER_PREVIEW_INTEGRATION_EVIDENCE.md`

Accepted production baseline:

`4ca3b83bfac50923bdcf15f1ad08d90b397daa23`

Final bounded Windows production-adapter run:

`32030024748` — PASS.

Durable semantics:

- a real playback-only Preview application boundary now exists;
- GStreamer/GstPlay 1.28.x private-runtime integration executes local-media lifecycle and exact seek without stealing EDL authority;
- missing/runtime/plugin failures are typed;
- software-video mode demotes only factories separately classified as Decoder + Hardware + Video and restores ranks on release;
- the first superficially green real probe was rejected after diagnostics exposed over-broad factory filtering;
- corrected production code and final hosted Windows AUTO/SOFTWARE_VIDEO probe passed;
- prior T470s evidence remains the hardware-backed software-decode fallback evidence;
- no player/backend benchmark is reopened.

## Current active boundary — minimum Review / bounded repair routing

`R0.12-MINIMUM-REVIEW-REPAIR-LOOP-001` is ACTIVE.

This boundary fills the missing post-render application owner. It does not create a subjective AI critic or a second editing system.

### Audit truth

Current production already has three useful deterministic layers:

1. canonical EDL audible-lane QC before render;
2. Renderer-owned technical verification before a successful `RenderArtifact` is returned;
3. PCM clipping/mostly-silent inspection utility.

The living smoke currently stops before a final post-render Review verdict, and no production Review owner was discovered in the application tree.

### Frozen ownership

```text
canonical EDL        = sole exact executable timeline authority
Renderer             = execute EDL + technical delivery verification
Review               = classify deterministic delivered-output evidence
Editorial owners     = make semantic/content corrections when routed back
Renderer/Environment = same-EDL technical rerender owner when appropriate
```

Review cannot directly change EDL/EditPlan/ResolutionDecision/AudioMixDecision or fabricate a repaired artifact.

### Product route to close

```text
exact canonical EDL revision
+ successful RenderArtifact
+ audible/output intent
→ RenderedMediaQc port
→ deterministic post-render evidence
→ Review verdict
→ PASS | CORRECTION_REQUIRED | BLOCKED
```

### Correction semantics

- successful Renderer technical checks are trusted, not duplicated as a competing authority;
- pre-render audible-lane QC remains pre-render;
- unexpected clipping/mostly-silent rendered output becomes typed Review evidence;
- same-EDL technical rerender is a route, not a hidden Review execution action;
- editorial correction returns to the legitimate owner for a new decision/revision;
- artifact/EDL provenance mismatch or insufficient evidence fails closed;
- retry attempts are explicit and bounded; no recursive autonomous loop.

### Evidence gate

Require focused deterministic tests plus one bounded real-media production Review probe with:

- clean artifact → PASS;
- deterministic defective-audio artifact → typed non-PASS;
- no hidden EDL/editorial mutation.

## Codex quota constraint

Approximately **9% Codex quota remains**.

### ChatGPT + GitHub

Primary for:

- contract reduction;
- deterministic application/port implementation;
- focused tests;
- CI/probe review;
- governance/validation.

### Codex

**NO ACTIVE RELEASE.**

Release only if the bounded real FFmpeg/PCM Review adapter or integration becomes materially more efficient through local runtime multi-file iteration.

Do not spend Codex on docs, subjective Review heuristics or generic refactors.

### User PowerShell

Use only if GitHub-hosted real-media Review evidence is insufficient or a genuine Human Gate is required.

## Immediate corridor after active work

1. minimum post-render Review / bounded repair routing;
2. ordinary-user Windows runtime / Environment Doctor;
3. practical product-facing integration;
4. real Planning/Editing Product Probes + Human Gate.

## Constitutional constraints

- EDL remains sole exact timeline authority.
- Renderer executes canonical EDL and does not make editorial decisions.
- Review classifies evidence and routes correction; it does not edit.
- PreviewBackend remains playback-only.
- original user media is never overwritten.
- commercial output visual material remains user-supplied local media.
- public/remote audio remains rights-evidence-gated.
- reference media defaults to analysis-only and remains Resolver-ineligible.
- Editing-only remains independent of fabricated Planning artifacts.
- no temporary shortcut may fabricate source timestamps, rights evidence, Domain decisions, Review PASS or a Product Gate PASS.

## Documentation synchronization rule

Dynamic state is canonical only in:

- `docs/operations/CURRENT_CONTROL_STATE.md`;
- `docs/operations/CURRENT_WORK_ORDER.md`;
- `docs/roadmap/CURRENT_PHASE_STATUS.md`.

`tools/maintenance/repo_doctor.py` + `repository-governance` check machine-detectable consistency.

## STOP boundary

Do not reopen player benchmarks.

Do not build a subjective AI video critic.

Do not let Review mutate EDL or editorial decisions.

Do not expand this Work Order into Environment Doctor, full GUI/frontend, generated music, SFX-provider expansion or generic media downloading.
