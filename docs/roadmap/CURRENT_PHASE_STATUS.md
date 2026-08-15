# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** SUBTITLE CLOSED — next R0.12 batch not yet activated  
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
- `827b84941e1726bab374f2ffea9a746f49f6e570` — structured subtitle execution, including fail-closed backend timing/layer representability and actual punctuated ASS filter-path evidence.

## R0.12 Subtitle — CLOSED

The accepted subtitle boundary provides:

- approved `StructuredSubtitleCue` → canonical EDL subtitle payload without fake media Assets;
- exact rational canonical timing with deterministic EDL schema v3 and v2 backward reading;
- validation for identity/track/range/text/language/layout/emphasis/overlap defects;
- deterministic ASS/libass burn-in through the canonical EDL-driven Renderer;
- upper/lower safe-zone intent and bounded emphasis;
- explicit structured rejection when the ASS baseline cannot represent a non-centisecond boundary without retiming;
- explicit structured rejection of multiple SUBTITLE tracks or nonzero subtitle layers in the Stage-A baseline;
- live Windows/libass evidence using an ASS artifact path whose parent contains comma and apostrophe punctuation;
- living Resolver → Renderer smoke remaining green.

The multilingual probe remains Engineering Probe evidence only. It proves controlled render-region behavior, not semantic glyph correctness under every installed font environment.

## Remaining R0.12 structural terrain

No downstream work order is active yet. Before the next Codex call, ChatGPT should pre-process and bound the remaining surfaces:

1. bounded Stage-A Graphics + minimal transition vocabulary, without a monolithic Effects Engine;
2. Preview backend benchmark/ADR using real Windows evidence;
3. edit-friendly derivative media / Proxy + range-aware cache with exact source-time mapping and affected-only invalidation;
4. remaining Renderer operational needs such as progress/cancellation, diagnostics and controlled CPU/hardware routing where structurally required.

Use GitHub directly for deterministic governance/audit changes and User PowerShell for simple local commands. Reserve Codex for Windows/runtime benchmarking, complex multi-file production changes and iterative debugging.

## Stage-A 100% product-operability gate

Before structural construction can reach 100%:

- **Planning core:** real user high-performing/reference/commercial intent must run through the real planning pipeline to persisted, inspectable user-visible `ScriptPlan` + executable `ShootingPlan`.
- **Editing core:** user-selected local footage must run through actual VisualUnderstanding/evidence, music, Director/Resolver, spatial/audio, subtitle/graphics/minimal transitions, canonical EDL, Renderer and Review/repair to a real final MP4.
- Hand-authored coverage text, ResolutionDecision, EDL or engineering fixtures must not masquerade as automatic pipeline output in the Product Probe.
- An ordinary Windows user must be able to create/open a project, select footage files/folder, select or identify an output folder, provide required planning/editing input, start the workflow, observe meaningful progress/failure and locate the produced Script/ShootingPlan/final MP4 without editing repository files.
- The current Python CLI remains an engineering adapter; CLI-only does not satisfy Stage-A 100%.

Desktop/frontend technology remains intentionally undecided until Preview/backend and Windows-packaging evidence are strong enough to choose without fashion-driven lock-in.

## Downstream structural constraints

R0.16 one-click execution must use actual VisualUnderstanding-derived evidence in Retrieval/Resolver; visual-only automatic BGM requires at least one concrete rights-aware discovery/acquisition provider path; Stage A needs the bounded editing-expression floor; and the final Reference/B爆款 → Script Product Probe must feed downstream speech/temporal/music/subtitle/transition/execution evidence back into Script/ShootingPlan guidance.
