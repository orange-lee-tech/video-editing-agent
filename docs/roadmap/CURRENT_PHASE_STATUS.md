# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** MINIMUM_REVIEW_REPAIR_LOOP_ACTIVE  
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
- `ffb5dbd7d3fc4e995f89a7a231910fa0295fcbba` — ordinary non-required-speech MUTE acceptance repair while preserving required-speech fail-closed semantics.
- `d15abf9258c0a080e37d666cd1112358723e823a` — accepted direct-HTTPS Reference URL acquisition implementation.
- `72ec275c1e72e876c4bcf828a44e7852208bab29` — accepted rights-aware public-music discovery, current-source verification and bounded Wikimedia audio acquisition.
- `4ca3b83bfac50923bdcf15f1ad08d90b397daa23` — production playback-only GStreamer Preview seam, private-runtime adapter, exact seek and corrected hardware-video-decoder fallback filtering.

**Current accepted production-code baseline:** `4ca3b83bfac50923bdcf15f1ad08d90b397daa23`.

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

Accepted result includes grounded per-selection PRESERVE/DUCK/MUTE, typed VoiceTreatment/speech protection and fail-closed non-silent audible-lane QC.

### Reference URL acquisition — PASS/CLOSED

Work Order:

`R0.12-REFERENCE-URL-ACQUISITION-001`

Closure evidence:

`docs/validation/R0.12_REFERENCE_URL_ACQUISITION_CLOSURE.md`

Accepted production baseline:

`d15abf9258c0a080e37d666cd1112358723e823a`

Supported direct unauthenticated HTTPS references enter project-controlled storage as `reference_acquired + reference_analysis_only`; authenticated/social/DRM/bulk/live/universal downloader behavior remains outside Stage A.

### Rights-aware public music acquisition — PASS/CLOSED

Work Order:

`R0.12-PUBLIC-MUSIC-ACQUISITION-001`

Closure evidence:

`docs/validation/R0.12_PUBLIC_MUSIC_ACQUISITION_EVIDENCE.md`

Accepted production baseline:

`72ec275c1e72e876c4bcf828a44e7852208bab29`

Real Windows provider run:

`32026331114` — PASS.

Openverse remains discovery-only; current Wikimedia Commons metadata is the bounded rights authority; approved public audio crosses real acquisition, FFprobe and normal `provider_acquired_audio + music` Asset ingest.

### Production GStreamer Preview integration — PASS/CLOSED

Work Order:

`R0.12-PRODUCTION-PREVIEW-INTEGRATION-001`

Closure evidence:

`docs/validation/R0.12_PRODUCTION_GSTREAMER_PREVIEW_INTEGRATION_EVIDENCE.md`

Accepted production baseline:

`4ca3b83bfac50923bdcf15f1ad08d90b397daa23`

Final Windows production-adapter run:

`32030024748` — PASS.

Accepted result:

- a real playback-only Preview application port now exists;
- GStreamer/GstPlay runs behind that port with a deliberate 1.28.x private-runtime contract;
- local-media load, play/pause, exact absolute seek, status, stop and release are typed;
- Preview does not gain canonical EDL/editorial/render authority;
- explicit software-video mode demotes only factories separately classified as Decoder + Hardware + Video and restores ranks on release;
- the first superficially green real probe was rejected when diagnostics showed over-broad factory filtering, then repaired and re-probed;
- final hosted Windows AUTO/SOFTWARE_VIDEO paths passed through the production adapter;
- no further backend-family benchmark is authorized absent a new hard product trigger.

## Active Work Order

`R0.12-MINIMUM-REVIEW-REPAIR-LOOP-001` is ACTIVE.

This boundary closes the missing application-owned post-render Review verdict/correction route. It does **not** create a subjective AI critic or a second editorial authority.

### Audit-grounded starting point

Current repository already has:

- pre-render canonical EDL audible-lane QC;
- Renderer-owned technical output verification for resolution, frame rate, required audio-track presence and duration;
- deterministic PCM clipping/mostly-silent diagnostics;
- successful `RenderArtifact` carrying exact EDL id/revision and output metadata.

Current repository does **not** yet expose one production Review owner that ties those delivered-output facts to a typed final verdict/correction route.

### Product route to close

```text
canonical EDL revision
+ successful RenderArtifact
+ audible/output intent
→ rendered-media QC port
→ deterministic post-render evidence
→ Review verdict
→ PASS | explicit correction route | BLOCKED
```

### Ownership rules

- Review never mutates canonical EDL/EditPlan/ResolutionDecision/AudioMixDecision.
- Renderer remains execution + technical-delivery-verification owner.
- pre-render audible-lane QC remains pre-render; do not duplicate it as post-render authority.
- post-render PCM evidence may identify clipping/unexpected silence, but Review routes the correction to the legitimate owner.
- same-EDL technical rerender is distinct from an editorial re-decision.
- repair attempts are bounded explicitly; no recursive autonomous repair loop.
- provenance mismatch or insufficient evidence fails closed.

### Required evidence direction

Deterministic tests first, followed by one bounded real-media Review probe proving clean PASS and one deterministic defective-audio non-PASS verdict through the **production Review path**.

No subjective visual score or fake visual-model evidence is required.

### Codex resource constraint

Approximately **9% Codex quota remains**.

**Codex: NOT RELEASED.**

ChatGPT + GitHub remain primary unless the real FFmpeg/PCM adapter boundary proves to require materially more efficient local runtime iteration.

## Immediate corridor after active work

1. close minimum post-render Review / bounded repair routing;
2. ordinary-user Windows runtime / Environment Doctor;
3. practical product-facing integration;
4. real Planning/Editing Product Probes + Human Gate.

Do not expand this Work Order into renewed player selection, subjective AI reviewing, SFX marketplaces, generated music or generic media downloading.

## Stage-A 100% product-operability gate

Before structural construction reaches 100%:

- Planning core must run real reference/high-performing/commercial intent to persisted inspectable ScriptPlan + executable ShootingPlan through an ordinary-user path;
- Editing core must run user-selected local footage through the real automatic pipeline to canonical EDL/Renderer/Review and a real final MP4;
- Planning-only, Editing-only and Combined must all remain valid;
- normal Product Probes must not hand-author EditPlan/ResolutionDecision/EDL;
- an ordinary Windows user must be able to create/open a project, select inputs/output, provide intent, start, observe progress/failure and locate outputs without repository-file editing.

Official structural progress remains **90%**.
