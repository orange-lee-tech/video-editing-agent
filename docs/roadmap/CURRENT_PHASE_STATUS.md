# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** PREVIEW BACKEND BENCHMARK ACTIVE — production Preview implementation not yet authorized  
**Updated:** 2026-08-16

## Progress meaning

The structural percentage measures real end-to-end product construction, not file count or backend module completion. Stage-A 100% still requires both product cores to work through an ordinary Windows user-facing path.

## Accepted R0.12 structural baselines

- `ff343833deb9296c1df0b6fc944735388d5c8296` — typed EDL tracks and deterministic validation.
- `4b2522ae1a6838517baf4c5bcf36d30026f86912` — exact rational spatial/audio automation.
- `b6c5684a9b07d79f20a10d28886cd087eaeecf10` — grounded decision-to-EDL assembly.
- `83fc2999297023f828fa77719cd357fe82eab5de` — deterministic EDL-driven FFmpeg Renderer.
- `9f06386f9f311fe241f250f4679fa6b2042699b0` — living Resolver → EDLBuilder → Renderer smoke.
- `827b84941e1726bab374f2ffea9a746f49f6e570` — structured subtitle execution.
- `1abc185a793d6a73ea55824bd2a036a1a134151a` — EditPlan parallel-entry compatibility.
- `500c8563e3686a5aaef055ffb5301553aa999fd9` — real Editing Director/Application entry with SQLite v6 EditPlan persistence and generated EditPlan → existing Retrieval/CandidateWindow/Resolver integration.

## Parallel workflow architecture

Planning-only, Editing-only and Combined remain parallel legitimate product meanings. Brief is the shared intent root; Planning artifacts enrich Editing only when present.

## Active R0.12 Work Order

`R0.12-PREVIEW-BACKEND-BENCHMARK-001` is ACTIVE.

This Work Order is intentionally evidence-first and code-light.

Roadmap V2 requires Preview selection from real Windows evidence among:

- GStreamer D3D11;
- approved LGPL-configured libmpv;
- libVLC.

CAP-08 defines PreviewBackend as interactive playback only. It has no EDL/timeline authority, does not repair EDL and does not define final render quality.

### Current sequence

1. user Windows environment inventory;
2. current official source/license/runtime verification;
3. controlled candidate installation where needed;
4. deterministic fixture + representative real-footage benchmark;
5. compare startup/seek/scrub/resource/stability/integration/distribution evidence;
6. record Preview ADR;
7. only then authorize a production Preview integration Work Order.

### Codex

NOT RELEASED for this benchmark. Preserve remaining quota for later integration work where it provides real execution leverage.

## Remaining R0.12 terrain

After the Preview decision, re-evaluate the most efficient order among:

1. bounded Stage-A Graphics + minimal transitions;
2. production Preview integration;
3. edit-friendly derivative media / Proxy + range-aware cache;
4. Renderer operational controls: progress/cancellation/diagnostics and controlled CPU/hardware routing.

These remain bounded tasks, not one giant final refactor.

## Stage-A 100% product-operability gate

Before structural construction reaches 100%:

- Planning core must run real reference/commercial intent to persisted inspectable ScriptPlan + executable ShootingPlan;
- Editing core must run user-selected local footage through real understanding/evidence, Director/Resolver, music, spatial/audio, subtitle/graphics/minimal transitions, canonical EDL, Renderer and Review/repair to a final MP4;
- Planning-only, Editing-only and Combined must all remain valid;
- the final Product Probe must not hand-author EditPlan/ResolutionDecision/EDL;
- an ordinary Windows user must be able to create/open a project, select footage and output location, provide intent, start, observe progress/failure and locate outputs without editing repository files.

Desktop/frontend technology remains intentionally undecided until the Preview backend and later Windows packaging evidence justify a commitment.