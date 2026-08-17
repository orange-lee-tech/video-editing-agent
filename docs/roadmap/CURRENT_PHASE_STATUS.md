# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** PRODUCTION_GSTREAMER_PREVIEW_INTEGRATION_ACTIVE  
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
- `72ec275c1e72e876c4bcf828a44e7852208bab29` — accepted rights-aware public-music discovery, current-source verification and bounded Wikimedia audio acquisition implementation.

**Current accepted production-code baseline:** `72ec275c1e72e876c4bcf828a44e7852208bab29`.

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

### Rights-aware public music acquisition — PASS/CLOSED

Work Order:

`R0.12-PUBLIC-MUSIC-ACQUISITION-001`

Closure evidence:

`docs/validation/R0.12_PUBLIC_MUSIC_ACQUISITION_EVIDENCE.md`

Accepted production baseline:

`72ec275c1e72e876c4bcf828a44e7852208bab29`

Deterministic quality-gate baseline:

`97c9ba838b169a99fb50deb0aa13029209592dff`

Real Windows provider run:

`32026331114` — PASS.

Accepted result:

- Openverse provides discovery-only `wikimedia_audio` candidates and does not become rights authority;
- current Wikimedia Commons metadata re-verifies each selected source before automatic acquisition;
- narrow Stage-A automatic rights policy accepts CC0 / accepted Public Domain / CC BY semantics and fails closed for NC / ND / BY-SA / NonFree / restricted / unknown cases;
- raw + normalized rights evidence is persisted through ArtifactStore;
- one approved `upload.wikimedia.org` item is acquired through a bounded provider-specific transport with identified bot UA and typed throttling evidence;
- source SHA-1 / size and local SHA-256 are checked;
- exact FLAC/Ogg MIME aliases are comparison-only and unrelated MIME changes remain fail closed;
- real FFprobe classified the acquired 83,141,176-byte FLAC as audio and normal Asset ingest produced `provider_acquired_audio + music`;
- no Codex release was used;
- local user music remains a valid fallback.

## Active Work Order

`R0.12-PRODUCTION-PREVIEW-INTEGRATION-001` is ACTIVE.

This is **production integration of the already-selected GStreamer Preview family**, not a reopened backend benchmark.

Accepted ADR:

`docs/adr/ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`

### Product route to close

Subject to the existing code seam discovered by audit:

```text
application Preview request
→ existing PreviewBackend boundary
→ production GStreamer adapter
→ selected private runtime
→ local media playback / absolute seek / state diagnostics
```

Preview remains playback-only. Canonical EDL and Renderer authority are unchanged.

### Immediate rules

- audit existing Preview/application/runtime seams before writing a new API;
- preserve GstPlay/playbin3 high-level integration direction;
- normal path may autoplug valid D3D11 acceleration;
- explicit software video-decode fallback remains a supported degraded route;
- do not silently dual-bundle/switch to libVLC;
- do not reopen libmpv Stage-A exclusion;
- do not run more backend-family benchmarks;
- private-runtime lookup/configuration may be integrated here, while full ordinary-user Environment Doctor remains later;
- deterministic tests first, then one bounded real Windows probe through the **production adapter**.

### Codex resource constraint

Approximately **9% Codex quota remains**.

**Codex: NOT RELEASED.**

ChatGPT + GitHub first own code audit and contract reduction. Codex is reserved only if the exact production adapter proves to require material local Windows/runtime multi-file iteration.

## Immediate corridor after active work

1. close production GStreamer Preview integration behind the existing PreviewBackend seam;
2. minimum Review/repair loop;
3. ordinary-user Windows runtime / Environment Doctor;
4. practical product-facing integration;
5. real Planning/Editing Product Probes + Human Gate.

Do not expand this Work Order into renewed player selection, SFX marketplaces, generated music or generic media downloading.

## Stage-A 100% product-operability gate

Before structural construction reaches 100%:

- Planning core must run real reference/high-performing/commercial intent to persisted inspectable ScriptPlan + executable ShootingPlan through an ordinary-user path;
- Editing core must run user-selected local footage through the real automatic pipeline to canonical EDL/Renderer/Review and a real final MP4;
- Planning-only, Editing-only and Combined must all remain valid;
- normal Product Probes must not hand-author EditPlan/ResolutionDecision/EDL;
- an ordinary Windows user must be able to create/open a project, select inputs/output, provide intent, start, observe progress/failure and locate outputs without repository-file editing.

Official structural progress remains **90%**.
