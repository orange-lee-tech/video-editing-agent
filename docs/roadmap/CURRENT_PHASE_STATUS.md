# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** MIXED SOURCE-AUDIO / VOICE / AUDIBLE-QC IMPLEMENTATION ACTIVE  
**Updated:** 2026-08-16

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
- `500c8563e3686a5aaef055ffb5301553aa999fd9` — real Editing Director/Application entry with SQLite v6 EditPlan persistence and generated EditPlan → existing Retrieval/CandidateWindow/Resolver integration.

Accepted production-code baseline entering the active implementation remains `500c8563e3686a5aaef055ffb5301553aa999fd9` until a new code commit is semantically accepted.

## Parallel workflow architecture

Planning-only, Editing-only and Combined remain parallel legitimate product meanings. Brief is the shared intent root; Planning artifacts enrich Editing only when present.

## Preview backend benchmark — CLOSED

`R0.12-PREVIEW-BACKEND-BENCHMARK-001` is PASS/CLOSED.

Accepted decision:

`docs/adr/ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`

- GStreamer is the primary Stage-A Preview backend family;
- libVLC remains a validated replaceable alternative, not default dual-bundled fallback;
- libmpv is hard-gate excluded for Stage A;
- PreviewBackend remains playback-only;
- EDL remains sole exact timeline authority.

Preview family benchmarking remains under STOP unless a concrete Product Probe failure/new hard requirement appears.

## Stage-A Product I/O Contract — CLOSED

`R0.12-STAGE-A-PRODUCT-IO-CONTRACT-001` is PASS/CLOSED.

Canonical contract:

`docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

Validation:

`docs/validation/R0.12_STAGE_A_PRODUCT_IO_CONTRACT_EVIDENCE.md`

Accepted product boundary:

- project create/open maps to existing `ProjectWorkspace` composition;
- local footage is ingested into immutable local Assets; original media is never overwritten;
- Planning-only persists ScriptPlan/ShootingPlan through existing owner workflows;
- Editing-only remains independently activatable from Brief + local footage;
- Combined enriches the same Editing Core;
- Reference URL must first become controlled local `REFERENCE_ANALYSIS_ONLY` media;
- public music discovery must proceed through rights-aware acquisition into a controlled local `MUSIC` Asset;
- final MP4 uses explicit local Renderer output path;
- frontend technology remains undecided.

## Active Work Order

`R0.12-MIXED-SOURCE-AUDIO-QC-001` is ACTIVE.

This is a bounded implementation batch covering one shared authority surface:

1. source-audio treatment at grounded selection/source-range granularity;
2. explicit VoiceTreatment semantics and speech protection;
3. deterministic EDL mapping for mixed PRESERVE / DUCK / MUTE source audio;
4. intent-aware non-silent audible-lane QC;
5. preservation of Renderer as execution-only.

### Why now

Current `AudioMixDecision` exposes only one whole-EditPlan `source_audio_policy`. Current `plan_basic_mix()` selects whole-plan PRESERVE or MUTE based on speech presence, and EDLBuilder clones all source audio for global PRESERVE while global DUCK is unsupported.

That is insufficient for ordinary mixed footage containing speech, environment sound and unwanted source audio.

### Codex

**AUTHORIZED — SINGLE COMPLEX BATCH.**

Codex is primary writer for the implementation surface until it stops/reports. ChatGPT remains control plane and will reobserve `main`, review the diff/CI and accept/reject the batch.

## Immediate corridor after the active batch

1. accept/repair mixed source-audio + VoiceTreatment + audible QC;
2. Reference URL acquisition;
3. rights-aware public music provider/acquisition;
4. remaining bounded R0.12 productization including production GStreamer Preview integration;
5. minimum Review/repair loop;
6. ordinary-user Windows runtime / Environment Doctor;
7. practical product-facing integration for both real cores;
8. real Planning/Editing Product Probes + Human Gate.

Do not expand the current batch into Reference URL, music-provider, GUI or Preview implementation.

## Stage-A 100% product-operability gate

Before structural construction reaches 100%:

- Planning core must run real reference/high-performing/commercial intent to persisted inspectable ScriptPlan + executable ShootingPlan through an ordinary-user path;
- Editing core must run user-selected local footage through the real automatic pipeline to canonical EDL/Renderer/Review and a real final MP4;
- Planning-only, Editing-only and Combined must all remain valid;
- normal Product Probes must not hand-author EditPlan/ResolutionDecision/EDL;
- an ordinary Windows user must be able to create/open a project, select inputs/output, provide intent, start, observe progress/failure and locate outputs without repository-file editing.

Official structural progress remains **90%**.
