# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-17
current_phase: R0.12
phase_state: PRODUCTION_GSTREAMER_PREVIEW_INTEGRATION_ACTIVE
active_work_order: R0.12-PRODUCTION-PREVIEW-INTEGRATION-001
accepted_code_baseline: 72ec275c1e72e876c4bcf828a44e7852208bab29
control_plane_baseline: 9c340e3770c312c8745699c12e442538b8b20963
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
core_2_editing_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
previous_work_order: R0.12-PUBLIC-MUSIC-ACQUISITION-001
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

`72ec275c1e72e876c4bcf828a44e7852208bab29`

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

GStreamer primary; Preview playback-only; EDL authority unchanged. Backend-family selection is closed and must not be reopened without a concrete Product Probe failure/new hard requirement.

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

Accepted durable semantics:

- supported direct unauthenticated HTTPS reference media can enter project-controlled storage;
- remote bytes cross normal ffprobe/AssetIngest/persistence;
- acquired reference media is `reference_acquired + reference_analysis_only`;
- remote reference media remains visual-Resolver ineligible;
- a real network/media/Asset probe plus focused existing-owner seam probe reached `ReferenceStyleEvidenceService`;
- synthetic Shot/VisualSemantics used only for the owner-seam mechanism were explicitly disclosed and are not a real visual-model claim;
- social/authenticated/cookie/CAPTCHA/DRM/bulk/live/universal downloader behavior remains outside the Stage-A boundary.

### Rights-aware public music acquisition — PASS/CLOSED

`R0.12-PUBLIC-MUSIC-ACQUISITION-001`

Closure evidence:

`docs/validation/R0.12_PUBLIC_MUSIC_ACQUISITION_EVIDENCE.md`

Accepted production baseline:

`72ec275c1e72e876c4bcf828a44e7852208bab29`

Deterministic quality-gate baseline:

`97c9ba838b169a99fb50deb0aa13029209592dff`

Final bounded Windows provider run:

`32026331114` — PASS.

Accepted durable semantics:

- Openverse is discovery-only and discovery results remain rights-unverified until current source verification;
- current Wikimedia Commons metadata is the rights-verification authority for this Stage-A provider adapter;
- accepted automatic pool is intentionally narrow: CC0 / accepted Public Domain / CC BY semantics; NC / ND / BY-SA / NonFree / restricted / unknown fail closed;
- raw and normalized rights evidence is content-addressed through ArtifactStore;
- `upload.wikimedia.org` acquisition is provider-specific, bounded and public-host constrained;
- identified bot User-Agent and typed HTTP 429 / `Retry-After` evidence are preserved without automatic hammering;
- source SHA-1 / byte size and local SHA-256 integrity are checked;
- only exact FLAC/Ogg MIME aliases are canonicalized for comparison, while actual HTTP MIME remains evidence;
- real FFprobe 8.1 classified the acquired 83,141,176-byte file as FLAC audio;
- normal Asset ingest produced `provider_acquired_audio + music` with content hash equal to acquisition SHA-256;
- no Codex release was used;
- local user music remains a valid Stage-A fallback.

## Current active boundary — production GStreamer Preview integration

`R0.12-PRODUCTION-PREVIEW-INTEGRATION-001` is ACTIVE.

This boundary integrates the already-selected GStreamer family behind the existing/accepted Preview seam. It does **not** reopen backend-family benchmarking.

Accepted decision:

`docs/adr/ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`

### Ownership remains frozen

```text
canonical EDL  = sole exact executable timeline authority
Renderer       = final render/execution authority
PreviewBackend = playback-only adapter
GStreamer      = Stage-A production implementation family behind PreviewBackend
```

Preview cannot repair, reinterpret, retime or silently replace EDL decisions.

### Immediate control action

ChatGPT + GitHub first audit:

- existing PreviewBackend / preview application ports;
- current preview adapters or benchmark-only code;
- time/seek and local-media request types;
- runtime/configuration composition seams;
- reusable GStreamer benchmark/probe mechanisms that do not leak benchmark authority into production;
- tests/import contracts around application ↔ provider/infrastructure ownership.

Only after this audit may the exact production edit be frozen.

### Accepted production direction

- GStreamer 1.28.6 Windows x86_64 MSVC private runtime is the initial accepted evidence baseline;
- high-level GstPlay/playbin3 control direction;
- normal path allows valid D3D11 acceleration;
- explicit software video-decode fallback remains supported and diagnosable;
- missing/broken runtime/plugin/device conditions need typed application diagnostics;
- private runtime is supplied deliberately rather than assuming arbitrary global PATH;
- no silent automatic libVLC cross-backend fallback;
- libmpv remains Stage-A hard-gate excluded;
- no new player benchmark without a concrete hard product trigger.

### Scope split

This Work Order may integrate the adapter's private-runtime lookup/configuration contract and enough capability reporting to prove the adapter can run.

The full ordinary-user Windows Environment Doctor / installer / repair UX remains a later dedicated productization boundary unless a minimal piece is unavoidable for production adapter proof.

## Codex quota constraint

Approximately **9% Codex quota remains**.

### ChatGPT + GitHub

Primary initially for:

- code/repository audit;
- exact port/adapter contract reduction;
- small deterministic implementation where connector-first work remains reliable;
- focused tests;
- CI/probe review;
- governance/validation.

### Codex

**NO ACTIVE RELEASE.**

Release only if the audit proves a bounded local Windows/runtime/multi-file implementation or repair materially benefits from Codex enough to justify the remaining quota.

Do not spend Codex on renewed GStreamer/libVLC/libmpv comparison, documentation, or benchmark archaeology.

### User PowerShell

Use only if GitHub-hosted Windows evidence cannot represent the real private-runtime production adapter boundary or a Human Gate is genuinely required.

## Immediate corridor after active work

1. production GStreamer Preview adapter integration behind the existing PreviewBackend seam;
2. minimum Review/repair loop;
3. ordinary-user Windows runtime / Environment Doctor;
4. practical product-facing integration;
5. real Planning/Editing Product Probes + Human Gate.

## Constitutional constraints

- EDL remains sole exact timeline authority.
- Renderer executes canonical EDL and does not make editorial decisions.
- PreviewBackend is playback-only.
- original user media is never overwritten.
- commercial output visual material remains user-supplied local media.
- public/remote audio is separate from forbidden remote visual sourcing and still requires rights evidence.
- provider candidates/URLs do not become timeline authority.
- reference media defaults to analysis-only and remains Resolver-ineligible.
- Editing-only remains independent of fabricated Planning artifacts.
- no temporary shortcut may fabricate source timestamps, rights evidence, Domain decisions or a Product Gate PASS.

## Documentation synchronization rule

Dynamic state is canonical only in:

- `docs/operations/CURRENT_CONTROL_STATE.md`;
- `docs/operations/CURRENT_WORK_ORDER.md`;
- `docs/roadmap/CURRENT_PHASE_STATUS.md`.

`tools/maintenance/repo_doctor.py` + `repository-governance` check machine-detectable consistency.

## STOP boundary

Do not reopen player benchmarks.

Do not silently bundle or switch to libVLC.

Do not reopen libmpv Stage-A exclusion without a new hard requirement.

Do not expand this Work Order into full GUI/frontend, SFX-provider expansion, generated music, Proxy redesign, or generic media downloading.

Do not let Preview become EDL/final-render authority.
