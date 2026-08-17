# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** REFERENCE URL ACQUISITION CONTRACT / PROVIDER GATE ACTIVE  
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

**Current accepted production-code baseline:** `ffb5dbd7d3fc4e995f89a7a231910fa0295fcbba`.

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

## Active Work Order

`R0.12-REFERENCE-URL-ACQUISITION-001` is ACTIVE.

This is initially a **Product + Provider Acquisition Contract / Code-Light Gate**, not a Codex implementation release.

### Product route to close

`supported Reference URL`
`→ acquisition adapter`
`→ controlled project-local file`
`→ normal ingest`
`→ REFERENCE_ANALYSIS_ONLY Asset`
`→ existing Shot / ShotAnalysis / ReferenceStyleEvidence`
`→ Planning guidance`

The downstream reference-analysis chain already exists and remains unchanged.

### Current policy direction

- explicit supported URL classes/allowlist rather than universal downloader claims;
- direct public HTTPS media is the lowest-risk baseline candidate;
- login/cookie/credential/CAPTCHA/DRM paths fail closed by default;
- platform policy must be distinguished from technical extractor capability;
- unsupported remote references fall back to user-provided local reference media;
- no remote reference Asset may become Resolver eligible.

### Codex resource constraint

Approximately **9% Codex quota remains**.

**Codex: NOT RELEASED.**

ChatGPT + GitHub first own repository audit, provider research, contract, security boundary and implementation-size reduction. Codex is reserved only for a later bounded multi-file local edit/test/repair loop if genuinely necessary.

## Immediate corridor after active work

1. close Reference URL acquisition contract/provider gate and, if justified, its minimal implementation/probe;
2. rights-aware public music provider/acquisition;
3. remaining bounded R0.12 productization including production GStreamer Preview integration where justified;
4. minimum Review/repair loop;
5. ordinary-user Windows runtime / Environment Doctor;
6. practical product-facing integration;
7. real Planning/Editing Product Probes + Human Gate.

Do not expand Reference URL work into a universal social-media downloader.

## Stage-A 100% product-operability gate

Before structural construction reaches 100%:

- Planning core must run real reference/high-performing/commercial intent to persisted inspectable ScriptPlan + executable ShootingPlan through an ordinary-user path;
- Editing core must run user-selected local footage through the real automatic pipeline to canonical EDL/Renderer/Review and a real final MP4;
- Planning-only, Editing-only and Combined must all remain valid;
- normal Product Probes must not hand-author EditPlan/ResolutionDecision/EDL;
- an ordinary Windows user must be able to create/open a project, select inputs/output, provide intent, start, observe progress/failure and locate outputs without repository-file editing.

Official structural progress remains **90%**.
