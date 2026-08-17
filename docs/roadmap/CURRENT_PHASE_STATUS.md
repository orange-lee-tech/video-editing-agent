# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Review / runtime productization  
**Engineering state:** WINDOWS_ENVIRONMENT_DOCTOR_ACTIVE  
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
- `500c8563e3686a5aaef055ffb5301553aa999fd9` — Editing Director/Application entry and persisted EditPlan integration.
- `ac5eb16fc8ecfb5ed29306826942765d264e0f3d` — per-selection source-audio treatment, VoiceTreatment and audible-lane QC.
- `ffb5dbd7d3fc4e995f89a7a231910fa0295fcbba` — ordinary MUTE acceptance repair with required-speech fail-closed semantics.
- `d15abf9258c0a080e37d666cd1112358723e823a` — direct-HTTPS Reference URL acquisition.
- `72ec275c1e72e876c4bcf828a44e7852208bab29` — rights-aware public-music discovery/current-source verification/acquisition.
- `4ca3b83bfac50923bdcf15f1ad08d90b397daa23` — production playback-only GStreamer Preview seam and corrected software fallback.
- `2cfeb664552769ade09f58bc2905ab531733a66a` — minimum post-render Review, rendered-media QC and bounded correction routing.

**Current accepted production-code baseline:** `2cfeb664552769ade09f58bc2905ab531733a66a`.

## Parallel workflow architecture

Planning-only, Editing-only and Combined remain parallel legitimate product meanings. Brief is the shared intent root; Planning artifacts enrich Editing only when present.

## Closed R0.12 control boundaries

### Preview backend benchmark / production integration — PASS/CLOSED

- ADR: `docs/adr/ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`
- closure: `docs/validation/R0.12_PRODUCTION_GSTREAMER_PREVIEW_INTEGRATION_EVIDENCE.md`
- accepted production baseline: `4ca3b83bfac50923bdcf15f1ad08d90b397daa23`
- final bounded Windows production-adapter run: `32030024748` — PASS.

GStreamer remains the Stage-A primary Preview backend; Preview is playback-only and backend-family selection remains closed.

### Stage-A Product I/O Contract — PASS/CLOSED

`docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

### Mixed source-audio / VoiceTreatment / audible QC — PASS/CLOSED

- Work Order: `R0.12-MIXED-SOURCE-AUDIO-QC-001`
- closure: `docs/validation/R0.12_MIXED_SOURCE_AUDIO_QC_CLOSURE.md`

### Reference URL acquisition — PASS/CLOSED

- Work Order: `R0.12-REFERENCE-URL-ACQUISITION-001`
- closure: `docs/validation/R0.12_REFERENCE_URL_ACQUISITION_CLOSURE.md`
- accepted baseline: `d15abf9258c0a080e37d666cd1112358723e823a`

### Rights-aware public music acquisition — PASS/CLOSED

- Work Order: `R0.12-PUBLIC-MUSIC-ACQUISITION-001`
- closure: `docs/validation/R0.12_PUBLIC_MUSIC_ACQUISITION_EVIDENCE.md`
- accepted baseline: `72ec275c1e72e876c4bcf828a44e7852208bab29`
- bounded Windows provider run `32026331114` — PASS.

### Minimum post-render Review / bounded repair — PASS/CLOSED

- Work Order: `R0.12-MINIMUM-REVIEW-REPAIR-LOOP-001`
- closure: `docs/validation/R0.12_MINIMUM_REVIEW_REPAIR_CLOSURE.md`
- accepted production baseline: `2cfeb664552769ade09f58bc2905ab531733a66a`
- deterministic Quality Gate `32032812665` — PASS;
- harness Quality Gate `32033065948` — PASS;
- final Windows real-media Review run `32033179672` — PASS.

Accepted semantics:

- successful RenderArtifact remains tied to exact canonical EDL revision;
- post-render media facts cross a replaceable `RenderedMediaQc` seam;
- clean media reaches typed Review PASS;
- unexpected mostly-silent delivered audio routes to `AudioEditorialService` rather than being silently repaired;
- same-EDL technical retry is explicit and bounded;
- Review has no EDL/editorial/render mutation authority.

## Active Work Order

`R0.12-WINDOWS-ENVIRONMENT-DOCTOR-001` is ACTIVE.

This boundary addresses the Stage-A compatibility/deployment floor: an ordinary Windows product path must not assume a developer workstation or expose unexplained missing-runtime errors.

### Audit-grounded starting point

Current repository facts:

- project package requires Python 3.12+ and intentionally has no mandatory third-party runtime dependency list;
- FFmpeg/ffprobe are external executables relied on by ingest, frame extraction, render and post-render QC;
- GStreamer Preview uses a deliberate private-runtime contract;
- DeepSeek/Gemini/OpenAI provider configuration is currently environment-variable driven;
- optional local model/runtime components are not basic deterministic-core requirements;
- existing PowerShell install/probe scripts are developer-oriented evidence, not one product-owned capability report.

### Product route to close

```text
host/runtime/tool/provider/private-runtime facts
→ bounded actual capability probes
→ typed per-capability status + product impact
→ sanitized EnvironmentReport / repair guidance
→ rerun same probes after repair
```

### Ownership rules

- Environment Doctor belongs to Application/Infrastructure support and never mutates Domain creative state.
- executable/runtime presence alone is not READY where a tiny runtime probe is practical.
- GPU absence does not make the core product unavailable.
- provider-key presence may be reported, but secret values never leave configuration storage/environment.
- Preview does not silently switch backend families.
- installer technology remains unfrozen in this Work Order.

### Required evidence direction

Deterministic tests first, then one bounded Windows Environment Doctor Engineering Probe proving real host facts, actual FFmpeg/ffprobe readiness, a typed unavailable component, secret redaction and project-independent execution.

## Immediate corridor after active work

1. Windows Environment Doctor / ordinary-user runtime diagnostics;
2. practical product-facing orchestration/integration;
3. real Planning Product Probe + Human Gate;
4. real Editing automatic-final-MP4 Product Probe + Human Gate;
5. Stage-A 100% only if all hard gates genuinely pass.
