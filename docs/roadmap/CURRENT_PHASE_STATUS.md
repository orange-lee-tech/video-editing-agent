# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** EDITPLAN COMPAT CLOSED — real Editing Director/Application entry active  
**Updated:** 2026-08-15

## Progress meaning

Canonical stage model: `docs/roadmap/DEVELOPMENT_STAGE_MODEL.md`.

The 0–100% project percentage measures structural construction: real end-to-end capability closure with correct authority, extensibility, deterministic execution, compatibility, observability, safe failure and genuine product operability.

Stage-A 100% requires both core product workflows to work through an ordinary Windows user-facing path. Backend module completion, synthetic smoke tests or hand-authored internal artifacts cannot substitute for that gate.

## Closed before R0.12

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Brief → ScriptPlan → ShootingPlan + commercial-authority baseline.
- R0.8 — Media Evidence Foundation.
- R0.9 — grounded Director-intent downstream kernel: Retrieval → CandidateWindow → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.
- R0.11 — Spatial Composition / Auto Reframe (`PASS_WITH_MINOR_DEFECT`).

## Accepted R0.12 structural baselines

- `ff343833deb9296c1df0b6fc944735388d5c8296` — typed EDL tracks, deterministic composition and structured validation.
- `4b2522ae1a6838517baf4c5bcf36d30026f86912` — exact rational spatial/audio automation and deterministic EDL serialization.
- `b6c5684a9b07d79f20a10d28886cd087eaeecf10` — grounded decision-to-EDL assembly.
- `83fc2999297023f828fa77719cd357fe82eab5de` — deterministic EDL-driven FFmpeg Renderer.
- `9f06386f9f311fe241f250f4679fa6b2042699b0` — living Resolver → EDLBuilder → Renderer integration smoke.
- `827b84941e1726bab374f2ffea9a746f49f6e570` — structured subtitle execution with fail-closed backend representability.
- `1abc185a793d6a73ea55824bd2a036a1a134151a` — EditPlan parallel-entry compatibility: Editing-only Brief provenance without mandatory ScriptPlan/ShootingPlan, with downstream Resolver/EDL authority invariance.

## Parallel workflow architecture — ACTIVE BASELINE

`ADR-009_TWO_CORE_WORKFLOWS_PARALLEL_ENTRY.md` establishes three legitimate meanings:

- **Planning Workflow:** `Brief → ScriptPlan → ShootingPlan` and may stop there;
- **Editing Workflow:** `Brief/editorial intent + user local footage → Editing Core → final output`, without fabricated Planning artifacts;
- **Combined Workflow:** Planning outputs enrich the same Editing Workflow as optional exact-revision context.

`Brief` is the common intent root. Planning may enrich Editing but is not its activation license.

The Domain compatibility correction is CLOSED. The current gap is one layer higher: production Application/Director entry.

## Active R0.12 work order

`R0.12-EDITING-DIRECTOR-ENTRY-001` is ACTIVE.

Repository audit establishes:

- `ApplicationRuntime` currently exposes only preproduction/media operations;
- `ProjectWorkspace.runtime()` requires preproduction provider ports and cannot serve as an independent Editing-only composition root;
- `editing/director/` has CandidateWindow/retrieval helpers but no production Brief+media-evidence → EditPlan workflow;
- the R0.9 Product Probe manually authored EditSlots/EditPlan before correctly exercising the grounded retrieval/resolution kernel;
- SQLite schema v5 has no EditPlan repository/table.

The active work will add the smallest real upstream producer:

`exact persisted Brief`
`+ persisted Resolver-eligible local Shot/ShotAnalysis evidence`
`+ optional exact ScriptPlan/ShootingPlan context`
`→ provider-neutral Director proposal`
`→ production Director workflow`
`→ persisted revisioned EditPlan`
`→ existing Retrieval/CandidateWindow/Resolver kernel`

Because EditPlan is a top-level durable Domain Entity and a production producer will now exist, first official EditPlan persistence and a deterministic SQLite v5→v6 migration are part of this bounded structural step. There are no historical persisted EditPlan rows to fabricate or rewrite.

The concrete DeepSeek Director adapter remains replaceable behind a neutral port and may only return bounded editorial-intent proposal DTOs. It may not commit Shot IDs, source timestamps, CandidateWindows, ResolutionDecisions or EDL coordinates.

An independent Editing composition surface must not require dummy Planning providers. Existing planning/media behavior remains backward-compatible.

Codex is released for one bounded implementation/test session because this coherent change spans persistence, Application workflow, workspace/provider/CLI wiring and migration/integration tests. ChatGPT will independently review its resulting commit and CI before acceptance.

## Explicit boundary

This work does **not** reopen R0.9 and does not authorize redesign of Resolver/optimizer, CandidateWindow ownership, retrieval algorithms, EDLBuilder, Canonical EDL, Renderer, VisualUnderstanding, subtitle, spatial, music/audio, Preview, Proxy/cache, Graphics/transitions, Review, packaging or GUI.

The active Director work should use the currently implemented EditSlot fields. Full future CAP-04 intent vocabulary is not a reason to broaden this task.

## Remaining R0.12 structural terrain after this correction

1. bounded Stage-A Graphics + minimal transition vocabulary, without a monolithic Effects Engine;
2. Preview backend benchmark/ADR using real Windows evidence;
3. edit-friendly derivative media / Proxy + range-aware cache with exact source-time mapping and affected-only invalidation;
4. remaining Renderer operational needs such as progress/cancellation, diagnostics and controlled CPU/hardware routing where structurally required.

## Stage-A 100% product-operability gate

Before structural construction can reach 100%:

- **Planning core:** real user high-performing/reference/commercial intent must run through the real planning pipeline to persisted, inspectable user-visible `ScriptPlan` + executable `ShootingPlan`.
- **Editing core:** user-selected local footage must run through actual VisualUnderstanding/evidence, Director/Resolver, music, spatial/audio, subtitle/graphics/minimal transitions, canonical EDL, Renderer and Review/repair to a real final MP4.
- Planning-only, Editing-only and Combined must all remain legitimate product paths; Combined is composition, not the unique workflow.
- Hand-authored EditPlan/ResolutionDecision/EDL or engineering fixtures must not masquerade as automatic pipeline output in the final Product Probe.
- An ordinary Windows user must be able to create/open a project, select footage files/folder, select or identify an output folder, provide required planning/editing input, start the workflow, observe meaningful progress/failure and locate the produced Script/ShootingPlan/final MP4 without editing repository files.
- The current Python CLI remains an engineering adapter; CLI-only does not satisfy Stage-A 100%.

Desktop/frontend technology remains intentionally undecided until Preview/backend and Windows-packaging evidence are strong enough to choose without fashion-driven lock-in.
