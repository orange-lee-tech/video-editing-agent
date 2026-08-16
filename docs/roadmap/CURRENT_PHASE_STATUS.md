# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** EDITING DIRECTOR/APPLICATION ENTRY CLOSED — next R0.12 bounded work selection pending  
**Updated:** 2026-08-16

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
- `500c8563e3686a5aaef055ffb5301553aa999fd9` — real Editing Director/Application entry: provider-neutral Director proposal seam, independent Editing composition root, SQLite v6 EditPlan persistence, bounded DeepSeek adapter, fail-closed proposal validation and generated EditPlan → existing Retrieval/CandidateWindow/Resolver integration.

## Parallel workflow architecture — ACTIVE BASELINE

`ADR-009_TWO_CORE_WORKFLOWS_PARALLEL_ENTRY.md` establishes three legitimate meanings:

- **Planning Workflow:** `Brief → ScriptPlan → ShootingPlan` and may stop there;
- **Editing Workflow:** `Brief/editorial intent + user local footage → Editing Core → final output`, without fabricated Planning artifacts;
- **Combined Workflow:** Planning outputs enrich the same Editing Workflow as optional exact-revision context.

`Brief` is the common intent root. Planning may enrich Editing but is not its activation license.

Both the Domain compatibility correction and the upstream production Director/Application entry are now CLOSED.

## Closed R0.12 Editing Director/Application entry

`R0.12-EDITING-DIRECTOR-ENTRY-001` is `CLOSED — PASS` at accepted code baseline `500c8563e3686a5aaef055ffb5301553aa999fd9`.

Accepted path:

`exact persisted Brief`
`+ persisted Resolver-eligible local Shot/ShotAnalysis evidence`
`+ optional exact ScriptPlan/ShootingPlan context`
`→ provider-neutral Director proposal`
`→ production Director workflow`
`→ persisted revisioned EditPlan`
`→ existing Retrieval/CandidateWindow/Resolver kernel`

Key closure facts:

- Editing-only generation does not require or fabricate Planning artifacts;
- Combined mode preserves exact optional Planning lineage;
- `ProjectWorkspace.editing_runtime(...)` is independent from preproduction provider requirements;
- the Director provider does not receive or commit Shot IDs, Asset IDs, source timestamps, CandidateWindows, ResolutionDecisions or EDL coordinates;
- malformed provider scalar/time values and one-sided duration bounds fail closed;
- proposal slot identity is unique while existing Domain ordering semantics are preserved, including deterministic handling of equal `order` values;
- SQLite v5→v6 adds durable immutable EditPlan persistence without inventing legacy EditPlan rows;
- the generated EditPlan is proven to enter the existing Retrieval/CandidateWindow/Resolver kernel rather than a duplicate editing engine;
- downstream Resolver/EDLBuilder/Renderer authority was not materially redesigned.

Formal evidence: `docs/validation/R0.12_EDITING_DIRECTOR_ENTRY_CLOSURE.md`.

## Current active implementation work

NONE.

A new bounded Work Order must be activated before substantive production-code construction resumes.

## Remaining R0.12 structural terrain

1. bounded Stage-A Graphics + minimal transition vocabulary, without a monolithic Effects Engine;
2. Preview backend benchmark/ADR using real Windows evidence;
3. edit-friendly derivative media / Proxy + range-aware cache with exact source-time mapping and affected-only invalidation;
4. remaining Renderer operational needs such as progress/cancellation, diagnostics and controlled CPU/hardware routing where structurally required.

These are not automatically concurrent. The next task should be selected only after re-observing the roadmap and dependency order.

## Stage-A 100% product-operability gate

Before structural construction can reach 100%:

- **Planning core:** real user high-performing/reference/commercial intent must run through the real planning pipeline to persisted, inspectable user-visible `ScriptPlan` + executable `ShootingPlan`.
- **Editing core:** user-selected local footage must run through actual VisualUnderstanding/evidence, Director/Resolver, music, spatial/audio, subtitle/graphics/minimal transitions, canonical EDL, Renderer and Review/repair to a real final MP4.
- Planning-only, Editing-only and Combined must all remain legitimate product paths; Combined is composition, not the unique workflow.
- Hand-authored EditPlan/ResolutionDecision/EDL or engineering fixtures must not masquerade as automatic pipeline output in the final Product Probe.
- An ordinary Windows user must be able to create/open a project, select footage files/folder, select or identify an output folder, provide required planning/editing input, start the workflow, observe meaningful progress/failure and locate the produced Script/ShootingPlan/final MP4 without editing repository files.
- The current Python CLI remains an engineering adapter; CLI-only does not satisfy Stage-A 100%.

Desktop/frontend technology remains intentionally undecided until Preview/backend and Windows-packaging evidence are strong enough to choose without fashion-driven lock-in.
