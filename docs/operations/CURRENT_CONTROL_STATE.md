# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-17
current_phase: R0.12
phase_state: PUBLIC_MUSIC_ACQUISITION_GATE_ACTIVE
active_work_order: R0.12-PUBLIC-MUSIC-ACQUISITION-001
accepted_code_baseline: d15abf9258c0a080e37d666cd1112358723e823a
control_plane_baseline: e8df24910de5ce3c862fd800a15750b085ace41f
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
core_2_editing_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
previous_work_order: R0.12-REFERENCE-URL-ACQUISITION-001
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

`d15abf9258c0a080e37d666cd1112358723e823a`

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

GStreamer primary; Preview playback-only; EDL authority unchanged.

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

## Current active boundary — rights-aware public music acquisition

`R0.12-PUBLIC-MUSIC-ACQUISITION-001` is ACTIVE.

The accepted CAP-06/ADR-006 route is:

```text
provider-neutral MusicDiscoveryQuery
→ AudioMaterialCandidate metadata
→ rights/license eligibility gate
→ approved single-item acquisition
→ project-controlled local audio file
→ AssetIngestService
→ authoritative local audio Asset
→ existing BeatMap / MusicSelection / AudioEditorial
→ canonical EDL / Renderer
```

### Existing downstream owners are already valid

Do not redesign R0.10 music selection/audio editorial.

Existing reusable primitives include:

- `AudioMaterialProvider`;
- `MusicDiscoveryQuery`;
- `AudioMaterialCandidate`;
- `RightsEligibility`;
- `LicenseSnapshot`;
- local Asset ingest/provenance;
- BeatMap / MusicSelection / AudioEditorial;
- canonical EDL audio execution.

The active gap is provider discovery/acquisition + durable rights evidence, not another music architecture.

### Rights/provider direction

- current official primary-source terms/API evidence is required before provider promotion;
- technical downloadability is not product authorization;
- `royalty-free` alone is not sufficient rights proof;
- `UNKNOWN` rights are not silently upgraded to `ELIGIBLE`;
- provider discovery/acquisition must be programmatically permitted, not HTML scraping by convenience;
- acquire only the specifically approved item, not bulk catalogs;
- preserve source page/provider/item/license snapshot/integrity/provenance;
- generated-audio status is used only when the provider actually supplies evidence;
- local user music remains the safe fallback if no automatic provider clears the hard gate.

Existing provider backlog:

`docs/research/AUDIO_PROVIDER_CANDIDATES_2026-08-14.md`

is informative only and must be revalidated before implementation.

## Codex quota constraint

The user reports approximately **9% Codex quota remaining**.

Treat this as a hard resource constraint.

### ChatGPT + GitHub

Primary for the active gate:

- existing audio/rights seam audit;
- current official provider/API/terms/license research;
- provider comparison;
- discovery/rights/acquisition/diagnostics contract reduction;
- control-plane/validation docs;
- small deterministic GitHub work.

### Codex

**NO ACTIVE RELEASE.**

Do not use Codex for provider browsing, docs, repository reading, speculative adapters, or API/terms research.

Release Codex only after one provider path and the exact bounded implementation are frozen and local multi-file edit/test/repair value justifies the remaining quota.

### User PowerShell

Use only when a real Windows/network/provider/API/audio boundary requires evidence after provider choice and contract are frozen.

## Immediate active investigation

1. audit `AudioMaterialProvider`, rights models, Asset ingest/provenance and R0.10 music seams;
2. revalidate Pixabay and other serious provider candidates using current official primary sources;
3. locate at least one provider with explicit programmatic music discovery **and** acquisition permission, or establish a hard-gate exclusion truthfully;
4. freeze provider-neutral rights snapshot/acquisition/diagnostic semantics;
5. determine minimal production changes;
6. release Codex only if that concrete edit genuinely requires local multi-file execution;
7. use one real provider/API Engineering Probe only where deterministic/local evidence cannot answer the external behavior question.

## Immediate corridor after active work

1. close rights-aware public music acquisition or record a truthful hard-gate exclusion with local-user fallback;
2. remaining bounded R0.12 productization including production GStreamer Preview integration where justified;
3. minimum Review/repair loop;
4. ordinary-user Windows runtime / Environment Doctor;
5. practical product-facing integration;
6. real Planning/Editing Product Probes + Human Gate.

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

Do not concurrently start GUI/frontend, SFX-provider expansion, generated-music integration, or further Preview benchmarking.

Do not implement HTML scraping merely because a provider web page can be downloaded manually.

Do not release Codex until the public-music provider and rights boundary is demonstrably small, precise and worth the remaining quota.
