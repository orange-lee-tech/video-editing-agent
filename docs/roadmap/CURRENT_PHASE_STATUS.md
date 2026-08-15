# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** PARALLEL WORKFLOW SEMANTICS + EDITPLAN COMPATIBILITY CLOSED — next Application boundary not yet activated  
**Updated:** 2026-08-15

## Progress meaning

Canonical stage model: `docs/roadmap/DEVELOPMENT_STAGE_MODEL.md`.

The 0–100% project percentage measures structural construction: real end-to-end capability closure with correct authority, extensibility, deterministic execution, compatibility, observability, safe failure and genuine product operability.

Stage-A 100% requires both core product workflows to work through an ordinary Windows user-facing path. Backend module completion, synthetic smoke tests or hand-authored internal artifacts cannot substitute for that gate.

## Closed before R0.12

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Brief → ScriptPlan → ShootingPlan + commercial-authority baseline.
- R0.8 — Media Evidence Foundation.
- R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.
- R0.11 — Spatial Composition / Auto Reframe (`PASS_WITH_MINOR_DEFECT`).

## Accepted R0.12 structural baselines

- `ff343833deb9296c1df0b6fc944735388d5c8296` — typed EDL tracks, deterministic composition and structured validation.
- `4b2522ae1a6838517baf4c5bcf36d30026f86912` — exact rational spatial/audio automation and deterministic EDL serialization.
- `b6c5684a9b07d79f20a10d28886cd087eaeecf10` — grounded decision-to-EDL assembly.
- `83fc2999297023f828fa77719cd357fe82eab5de` — deterministic EDL-driven FFmpeg Renderer.
- `9f06386f9f311fe241f250f4679fa6b2042699b0` — living Resolver → EDLBuilder → Renderer integration smoke.
- `827b84941e1726bab374f2ffea9a746f49f6e570` — structured subtitle execution with fail-closed backend timing/layer representability.
- `1abc185a793d6a73ea55824bd2a036a1a134151a` — Brief-rooted EditPlan parallel-entry compatibility with preserved Combined provenance and downstream authority invariance.

## R0.12 Subtitle — CLOSED

The accepted subtitle boundary provides structured subtitle cues, exact rational canonical timing, deterministic ASS/libass burn-in, bounded emphasis/safe-zone intent, and fail-closed rejection where the Stage-A backend cannot represent timing/layer semantics. The living Resolver → Renderer smoke remains green.

The multilingual probe remains Engineering Probe evidence only. It proves controlled render-region behavior, not semantic glyph correctness under every installed font environment.

## Parallel workflow correction — CLOSED

`ADR-009_TWO_CORE_WORKFLOWS_PARALLEL_ENTRY.md` formally adopts the supervisory correction recorded in `docs/architecture/TWO_CORE_WORKFLOWS_PARALLELISM_AND_RISK_GOVERNANCE.md`.

Three legitimate workflow meanings are now explicit:

- **Planning Workflow:** `Brief → ScriptPlan → ShootingPlan` and may stop there;
- **Editing Workflow:** `Brief/editorial intent + user local footage → the existing Editing Core → final output`, without fabricated Planning artifacts;
- **Combined Workflow:** Planning outputs enrich the same Editing Workflow as optional exact-revision context.

The sequential chain in Architecture Contract v0.2 Section 1 remains valid as Combined Workflow, not as the unique product path. `Brief` is the common intent root.

`R0.12-EDITPLAN-COMPAT-001` is CLOSED at `1abc185a793d6a73ea55824bd2a036a1a134151a`. `EditPlan` now supports Brief-rooted Editing-only intent, exact Combined Planning context, legacy complete Planning provenance compatibility, and fail-closed broken provenance. Focused regression tests prove that Planning provenance does not alter Resolver or deterministic EDLBuilder authority when downstream inputs are otherwise identical.

No production redesign occurred in Resolver, CandidateWindow generation, Retrieval, EDLBuilder, Canonical EDL, Renderer, Media Understanding, subtitle, spatial, music or audio. No non-existent persistence migration was invented.

Durable evidence: `docs/validation/R0.12_EDITPLAN_PARALLEL_ENTRY_CLOSURE.md`.

## Next structural handoff

No downstream implementation Work Order is active yet.

Before resuming ordinary R0.12 productization batches, pre-process a bounded real Editing Application entry/orchestration boundary so the independent Editing workflow can actually enter the existing Editing Core from Brief/editorial intent + user footage, with optional Planning context. This must not be an empty wrapper, hand-authored EditPlan shortcut or second Editing Core.

This Application step is a structural integration foundation, not a claim that the full R0.16 one-click workflow is already finished.

## Remaining R0.12 structural terrain

After the bounded Editing-entry foundation, continue:

1. bounded Stage-A Graphics + minimal transition vocabulary, without a monolithic Effects Engine;
2. Preview backend benchmark/ADR using real Windows evidence;
3. edit-friendly derivative media / Proxy + range-aware cache with exact source-time mapping and affected-only invalidation;
4. remaining Renderer operational needs such as progress/cancellation, diagnostics and controlled CPU/hardware routing where structurally required.

Use GitHub directly for deterministic governance/audit changes and User PowerShell for simple local commands. Reserve Codex for Windows/runtime benchmarking, complex multi-file production changes and iterative debugging.

## Stage-A 100% product-operability gate

Before structural construction can reach 100%:

- **Planning core:** real user high-performing/reference/commercial intent must run through the real planning pipeline to persisted, inspectable user-visible `ScriptPlan` + executable `ShootingPlan`.
- **Editing core:** user-selected local footage must run through actual VisualUnderstanding/evidence, music, Director/Resolver, spatial/audio, subtitle/graphics/minimal transitions, canonical EDL, Renderer and Review/repair to a real final MP4.
- Planning-only, Editing-only and Combined must all remain legitimate product paths; Combined is composition, not the unique workflow.
- Hand-authored coverage text, EditPlan, ResolutionDecision or EDL must not masquerade as automatic pipeline output in the Product Probe.
- An ordinary Windows user must be able to create/open a project, select footage files/folder, select or identify an output folder, provide required planning/editing input, start the workflow, observe meaningful progress/failure and locate the produced Script/ShootingPlan/final MP4 without editing repository files.
- The current Python CLI remains an engineering adapter; CLI-only does not satisfy Stage-A 100%.

Desktop/frontend technology remains intentionally undecided until Preview/backend and Windows-packaging evidence are strong enough to choose without fashion-driven lock-in.

## Local quality-gate rule

Full local acceptance must mirror CI and include both formatting and linting:

```text
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
uv run lint-imports
uv build
git diff --check
```

Capability-specific probes remain additional gates where relevant.

## Downstream structural constraints

R0.16 one-click execution must use actual VisualUnderstanding-derived evidence in Retrieval/Resolver; visual-only automatic BGM requires at least one concrete rights-aware discovery/acquisition provider path; Stage A needs the bounded editing-expression floor; and the final Reference/爆款 → Script Product Probe must feed downstream speech/temporal/music/subtitle/transition/execution evidence back into Script/ShootingPlan guidance.
