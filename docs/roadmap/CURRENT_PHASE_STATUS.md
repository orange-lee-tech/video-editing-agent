# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** STAGE-A PRODUCT I/O CONTRACT ACTIVE — Preview backend benchmark closed  
**Updated:** 2026-08-16

## Progress meaning

The structural percentage measures real end-to-end product construction, not file count, backend count or benchmark completion.

The hard 100% contract is `STAGE_A_COMPLETION_GATE.md`.

Current Product Gate state remains:

- Planning foundation accepted; ordinary-user Planning product flow still open.
- Editing foundation accepted; ordinary-user automatic final-MP4 product flow still open.

Stage-A 100% remains forbidden until both core Product Gates are PASS.

## Accepted R0.12 structural baselines

- `ff343833deb9296c1df0b6fc944735388d5c8296` — typed EDL tracks and deterministic validation.
- `4b2522ae1a6838517baf4c5bcf36d30026f86912` — exact rational spatial/audio automation.
- `b6c5684a9b07d79f20a10d28886cd087eaeecf10` — grounded decision-to-EDL assembly.
- `83fc2999297023f828fa77719cd357fe82eab5de` — deterministic EDL-driven FFmpeg Renderer.
- `9f06386f9f311fe241f250f4679fa6b2042699b0` — living Resolver → EDLBuilder → Renderer smoke.
- `827b84941e1726bab374f2ffea9a746f49f6e570` — structured subtitle execution.
- `1abc185a793d6a73ea55824bd2a036a1a134151a` — EditPlan parallel-entry compatibility.
- `500c8563e3686a5aaef055ffb5301553aa999fd9` — real Editing Director/Application entry with SQLite v6 EditPlan persistence and generated EditPlan → existing Retrieval/CandidateWindow/Resolver integration.

Accepted production-code baseline remains `500c8563e3686a5aaef055ffb5301553aa999fd9`.

## Parallel workflow architecture

Planning-only, Editing-only and Combined remain parallel legitimate product meanings. Brief is the shared intent root; Planning artifacts enrich Editing only when present.

## Preview backend benchmark — CLOSED

`R0.12-PREVIEW-BACKEND-BENCHMARK-001` is PASS/CLOSED.

Accepted decision:

`docs/adr/ADR-010_GSTREAMER_PRIMARY_PREVIEW_BACKEND.md`

- GStreamer is the primary Stage-A Preview backend family;
- libVLC remains a validated replaceable alternative, not default dual-bundled fallback;
- libmpv is hard-gate excluded for Stage A because an auditable LGPL Windows D3D11 distribution path would require disproportionate custom build/dependency/license maintenance;
- PreviewBackend remains playback-only;
- EDL remains sole exact timeline authority.

Durable libmpv gate record:

`docs/validation/R0.12_PREVIEW_LIBMPV_LGPL_HARD_GATE_EXCLUSION.md`

### Preview STOP rule

Do not reopen player benchmarking merely to collect more codecs/machines/metrics. A new backend-family investigation requires a concrete Product Probe failure or a new hard product requirement.

Known Preview evidence gaps — real VFR, Class-B/Class-C hosts and total no-GPU presentation — remain ordinary integration/Product-Probe risks rather than reasons to keep the family-selection benchmark active.

## Active Work Order

`R0.12-STAGE-A-PRODUCT-IO-CONTRACT-001` is ACTIVE.

The project now returns to the real Stage-A product boundary:

`ordinary-user inputs`
`→ owned application/domain chain`
`→ understandable progress/failure`
`→ persisted plans and/or final MP4`

The contract must freeze the product-facing input/output semantics for Planning-only, Editing-only and Combined without choosing a desktop/frontend framework.

### Immediate corridor

1. Stage-A Product I/O Contract;
2. mixed source-audio semantics + speech protection + final audible-lane QC;
3. Reference URL acquisition;
4. rights-aware public music provider/acquisition;
5. remaining bounded R0.12 productization, including production GStreamer Preview integration where justified;
6. minimum Review/repair loop;
7. ordinary-user Windows runtime / Environment Doctor;
8. practical product-facing integration for both real cores;
9. real Planning/Editing Product Probes + Human Gate.

This is the preferred final-10-percent route. Do not divert back into optional backend research without a dependency from this corridor.

### Codex

NOT RELEASED for the Product I/O contract itself.

The first expected post-contract Codex-worthy batch is mixed source-audio + speech protection + audible QC.

## Stage-A 100% product-operability gate

Before structural construction reaches 100%:

- Planning core must run real reference/high-performing/commercial intent to persisted inspectable ScriptPlan + executable ShootingPlan through an ordinary-user path;
- Editing core must run user-selected local footage through the real automatic pipeline to canonical EDL/Renderer/Review and a real final MP4;
- Planning-only, Editing-only and Combined must all remain valid;
- normal Product Probes must not hand-author EditPlan/ResolutionDecision/EDL;
- an ordinary Windows user must be able to create/open a project, select inputs/output, provide intent, start, observe progress/failure and locate outputs without repository-file editing.

Desktop/frontend technology remains intentionally undecided until the product I/O contract and later Windows packaging evidence justify a commitment.
