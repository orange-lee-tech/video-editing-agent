# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-17
current_phase: R0.12
phase_state: REFERENCE_URL_ACQUISITION_GATE_ACTIVE
active_work_order: R0.12-REFERENCE-URL-ACQUISITION-001
accepted_code_baseline: ffb5dbd7d3fc4e995f89a7a231910fa0295fcbba
control_plane_baseline: 87562a9824a9f9d29aa96a6563955467ba70068d
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
core_2_editing_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
previous_work_order: R0.12-MIXED-SOURCE-AUDIO-QC-001
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

`ffb5dbd7d3fc4e995f89a7a231910fa0295fcbba`

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

Accepted production baseline:

`ffb5dbd7d3fc4e995f89a7a231910fa0295fcbba`

Accepted semantics:

- per-grounded-selection source audio PRESERVE / DUCK / MUTE;
- VoiceTreatment with required-speech protection;
- ordinary non-speech MUTE remains valid;
- deterministic canonical EDL source-audio mapping;
- typed accidental-silence audible-lane QC;
- Resolver source authority and Renderer execution-only ownership preserved.

GitHub CI run #246 on the accepted repair HEAD completed successfully.

## Current active boundary — Reference URL acquisition

`R0.12-REFERENCE-URL-ACQUISITION-001` is ACTIVE.

The Stage-A Product I/O Contract already freezes the semantic route:

`supported URL`
`→ acquisition adapter`
`→ controlled project-local file`
`→ normal media ingest`
`→ REFERENCE_ANALYSIS_ONLY Asset`
`→ existing reference analysis/guidance`

### Existing downstream owner is already valid

`ReferenceStyleEvidenceService`:

- requires a video Asset;
- requires `AssetUsageRole.REFERENCE_ANALYSIS_ONLY`;
- asserts that the reference Asset is never visual-Resolver eligible;
- derives abstract technique evidence only;
- persists evidence through the content-addressed ArtifactStore;
- projects that evidence into provider-neutral Planning guidance.

Therefore the active gap is acquisition + controlled local media lifecycle, not another reference-analysis system.

### Current provider/security direction

- Stage A uses an explicit support policy/allowlist rather than promising arbitrary Internet URL support;
- direct unauthenticated HTTPS media is the lowest-risk baseline candidate;
- specifically audited provider/page adapters may be added only when technical, policy, license and deployment gates pass;
- login/account/session-required retrieval fails closed by default;
- browser-cookie extraction, credential scraping, CAPTCHA bypass and DRM/protected acquisition are outside the default Stage-A boundary;
- bulk playlist/channel/profile and live-stream acquisition are outside Stage A;
- unsupported/policy-disallowed URL input must produce understandable guidance to provide an allowed local reference file;
- reference acquisition can never grant editable visual/Resolver eligibility.

### yt-dlp gate

Technical breadth is not sufficient for automatic adoption.

Research entering this control state shows:

- extractor/site support changes as websites change;
- broad modern site coverage can add FFmpeg/JS/runtime and networking dependency surface;
- source licensing and bundled executable licensing differ;
- credential/cookie paths materially expand security risk;
- some major platforms' official developer policies prohibit downloading/caching audiovisual content without explicit approval.

Therefore a universal bundled yt-dlp/social-media downloader is not pre-approved for Stage A.

## Codex quota constraint

The user reports approximately **9% Codex quota remaining**.

Treat this as a hard resource constraint.

### ChatGPT + GitHub

Primary for the active gate:

- existing-code/reference-flow audit;
- provider/security/licensing research;
- contract and diagnostics design;
- control-plane/validation docs;
- small deterministic GitHub work.

### Codex

**NO ACTIVE RELEASE.**

Do not use Codex for research, docs, reading the repository, provider comparison, or speculative implementation.

Release Codex only if the final implementation has been reduced to a precise bounded multi-file edit/test/repair task and the expected Stage-A value justifies consuming the remaining quota.

### User PowerShell

Use only when a real Windows/network/runtime/private-media boundary needs evidence after the contract/provider choice is frozen.

## Immediate active investigation

1. inspect existing reference evidence/guidance tests;
2. inspect project-owned storage/lifecycle and Asset provenance vocabulary;
3. freeze provider-neutral acquisition request/result/diagnostics;
4. freeze SSRF/redirect/size/timeout/path/atomic-write security policy;
5. compare direct HTTPS acquisition against any justified provider adapter;
6. record provider/license/platform-policy evidence;
7. determine implementation size;
8. only then decide whether any Codex release is warranted.

## Immediate corridor after active work

1. close Reference URL acquisition;
2. rights-aware public music acquisition;
3. remaining bounded R0.12 productization including production GStreamer Preview integration;
4. minimum Review/repair loop;
5. ordinary-user Windows runtime / Environment Doctor;
6. practical product-facing integration;
7. real Product Probes / Human Gate.

## Constitutional constraints

- EDL remains sole exact timeline authority.
- Renderer executes canonical EDL and does not make editorial decisions.
- PreviewBackend is playback-only.
- original user media is never overwritten.
- commercial output visual material remains user-supplied local media.
- reference media defaults to analysis-only and remains Resolver-ineligible.
- Editing-only remains independent of fabricated Planning artifacts.
- remote acquisition cannot silently become output-eligible visual footage.
- no temporary shortcut may fabricate source timestamps, Domain decisions or a Product Gate PASS.

## Documentation synchronization rule

Dynamic state is canonical only in:

- `docs/operations/CURRENT_CONTROL_STATE.md`;
- `docs/operations/CURRENT_WORK_ORDER.md`;
- `docs/roadmap/CURRENT_PHASE_STATUS.md`.

`tools/maintenance/repo_doctor.py` + `repository-governance` check machine-detectable consistency.

## STOP boundary

Do not start public music acquisition, GUI/frontend, or further Preview work concurrently.

Do not promise social-platform download support solely because a third-party extractor works technically.

Do not release Codex until the Reference URL implementation boundary is demonstrably small, precise and worth the remaining quota.
