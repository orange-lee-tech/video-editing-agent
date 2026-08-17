# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** RIGHTS-AWARE PUBLIC MUSIC ACQUISITION GATE ACTIVE  
**Updated:** 2026-08-17

## Progress meaning

The structural percentage measures real end-to-end product construction, not file count, backend count, benchmark completion or test count.

The hard 100% contract is `STAGE_A_COMPLETION_GATE.md`.

Current Product Gate state remains:

- Planning foundation accepted; ordinary-user Planning product flow still open.
- Editing foundation accepted; ordinary-user automatic final-MP4 product flow still open.

Stage-A 100% remains forbidden until both core Product Gates are PASS.

## Accepted R0.12 production-code baselines

- `ff343833deb9296c1df0b6fc944735388d5c8296` — typed EDL tracks and deterministic validation.
- `4b2522ae1a6838517baf4c5bcf36d30026f86912` — exact rational spatial/audio automation.
- `b6c5684a9b07d79f20a10d28886cd087eaeecf10` — grounded decision-to-EDL assembly.
- `83fc2999297023f828fa77719cd357fe82eab5de` — deterministic EDL-driven FFmpeg Renderer.
- `9f06386f9f311fe241f250f4679fa6b2042699b0` — living Resolver → EDLBuilder → Renderer smoke.
- `827b84941e1726bab374f2ffea9a746f49f6e570` — structured subtitle execution.
- `1abc185a793d6a73ea55824bd2a036a1a134151a` — EditPlan parallel-entry compatibility.
- `500c8563e3686a5aaef055ffb5301553aa999fd9` — real Editing Director/Application entry and persisted EditPlan integration.
- `ac5eb16fc8ecfb5ed29306826942765d264e0f3d` — per-selection mixed source-audio treatment, VoiceTreatment, deterministic source DUCK and audible-lane QC foundation.
- `ffb5dbd7d3fc4e995f89a7a231910fa0295fcbba` — acceptance repair allowing ordinary non-required-speech MUTE while preserving required-speech fail-closed semantics.
- `d15abf9258c0a080e37d666cd1112358723e823a` — accepted direct-HTTPS Reference URL acquisition implementation after quality-gate repair and real owner-seam validation.

**Current accepted production-code baseline:** `d15abf9258c0a080e37d666cd1112358723e823a`.

## Parallel workflow architecture

Planning-only, Editing-only and Combined remain parallel legitimate product meanings. Brief is the shared intent root; Planning artifacts enrich Editing only when present.

## Closed R0.12 control boundaries

### Preview backend benchmark — PASS/CLOSED

Accepted ADR:

`docs/adr/ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`

GStreamer is the primary Stage-A Preview backend family. Preview remains playback-only; EDL remains exact timeline authority.

### Stage-A Product I/O Contract — PASS/CLOSED

Canonical contract:

`docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

### Mixed source-audio / VoiceTreatment / audible QC — PASS/CLOSED

Work Order:

`R0.12-MIXED-SOURCE-AUDIO-QC-001`

Closure evidence:

`docs/validation/R0.12_MIXED_SOURCE_AUDIO_QC_CLOSURE.md`

Accepted result:

- mixed grounded selections can independently PRESERVE / DUCK / MUTE source audio;
- VoiceTreatment and speech-protection rules are typed and fail closed;
- ordinary non-speech source audio can be muted without fake voice declarations;
- EDLBuilder owns deterministic mapping only;
- Renderer remains execution-only;
- non-silent intent fails structural audible-lane QC when no approved audible segment exists;
- GitHub CI on accepted repair baseline passed.

### Reference URL acquisition — PASS/CLOSED

Work Order:

`R0.12-REFERENCE-URL-ACQUISITION-001`

Closure evidence:

`docs/validation/R0.12_REFERENCE_URL_ACQUISITION_CLOSURE.md`

Accepted baseline:

`d15abf9258c0a080e37d666cd1112358723e823a`

Accepted result:

- direct unauthenticated HTTPS reference media has a bounded Stage-A acquisition path;
- remote bytes land in project-controlled storage and cross normal ffprobe/AssetIngest/persistence;
- acquired references use `reference_acquired + reference_analysis_only`;
- remote reference media cannot become visual Resolver candidates;
- real network/media/Asset evidence and a focused owner-seam probe reached existing `ReferenceStyleEvidenceService`;
- the owner-seam probe explicitly disclosed synthetic Shot/VisualSemantics and did not claim real visual-AI execution;
- authenticated/social/DRM/bulk/live/universal downloader behavior remains outside the accepted boundary.

## Active Work Order

`R0.12-PUBLIC-MUSIC-ACQUISITION-001` is ACTIVE.

This begins as a **Product + Rights + Provider Gate / Code-Light First** boundary.

### Product route to close

```text
MusicIntent / provider-neutral query
→ public music discovery
→ rights/license eligibility gate
→ approved single-item acquisition
→ project-controlled local audio
→ AssetIngest
→ authoritative audio Asset
→ existing BeatMap / MusicSelection / AudioEditorial
→ canonical EDL / Renderer
```

The existing R0.10 music-selection/audio-editorial architecture remains authoritative and must not be redesigned.

### Current policy direction

- rights/programmatic-access clarity before catalog breadth;
- current official provider/API/terms evidence required before implementation;
- `royalty-free` or browser-downloadable is not automatic product authorization;
- reuse existing `AudioMaterialProvider`, `RightsEligibility` and `LicenseSnapshot` primitives where sufficient;
- no HTML scraping merely to manufacture an automatic provider;
- no hidden browser-cookie/credential acquisition;
- unknown rights do not silently become eligible;
- acquire only the specifically approved candidate rather than mirroring provider libraries;
- local user music remains the safe Stage-A fallback if no provider clears the hard gate.

### Existing provider backlog

`docs/research/AUDIO_PROVIDER_CANDIDATES_2026-08-14.md` remains informative only and must be revalidated from current primary sources.

Pixabay Music remains a candidate, not an approved automatic integration solely from existing research. SoundEffects+ remains outside the automatic music-provider baseline unless official restrictions materially change.

### Codex resource constraint

Approximately **9% Codex quota remains**.

**Codex: NOT RELEASED.**

ChatGPT + GitHub first own provider research, official API/terms/license verification, existing-code audit, contract reduction and governance. Codex is reserved only for a later precise bounded multi-file implementation/test/repair loop if genuinely necessary.

## Immediate corridor after active work

1. close rights-aware public music provider/acquisition or record a truthful hard-gate exclusion with local-user fallback;
2. remaining bounded R0.12 productization including production GStreamer Preview integration where justified;
3. minimum Review/repair loop;
4. ordinary-user Windows runtime / Environment Doctor;
5. practical product-facing integration;
6. real Planning/Editing Product Probes + Human Gate.

Do not expand this Work Order into SFX marketplaces, generated-music platforms or a generic media-downloader layer.

## Stage-A 100% product-operability gate

Before structural construction reaches 100%:

- Planning core must run real reference/high-performing/commercial intent to persisted inspectable ScriptPlan + executable ShootingPlan through an ordinary-user path;
- Editing core must run user-selected local footage through the real automatic pipeline to canonical EDL/Renderer/Review and a real final MP4;
- Planning-only, Editing-only and Combined must all remain valid;
- normal Product Probes must not hand-author EditPlan/ResolutionDecision/EDL;
- an ordinary Windows user must be able to create/open a project, select inputs/output, provide intent, start, observe progress/failure and locate outputs without repository-file editing.

Official structural progress remains **90%**.
