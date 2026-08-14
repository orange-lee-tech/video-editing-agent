# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.11 — Spatial Composition / Auto Reframe  
**Engineering state:** ACTIVE — spatial authority and deterministic geometry foundation  
**Updated:** 2026-08-14

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.
- R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.

## R0.10 closure evidence

R0.10 closed after engineering verification, a real-music Product Probe and explicit Human Gate acceptance.

Closing implementation baseline:

`4782889f3746cf1024abfa0c45f3402cfec834a3` — `fix: canonicalize music candidate ordering`

Human Gate result:

- music candidate: **Track B**;
- music moment: **selected**;
- mix: **structured**;
- obvious audible defect: **none**.

The low Track B BeatMap confidence `0.0633` remained visible and was not compensated by hidden score changes. Durable closure evidence is recorded in `docs/validation/R0.10_FINAL_CLOSURE.md`.

## Active R0.11 boundary

R0.11 now owns mixed-aspect spatial composition and Auto Reframe.

The first coherent implementation boundary is deliberately foundational:

```text
existing ResolvedSelection + existing tracking/TemporalEvidence
→ provider-neutral ReframeIntent / spatial evidence view
→ deterministic legal crop candidates
→ deterministic SpatialComposer decision/path
→ bounded validation/QC
```

This first boundary must establish ownership and geometry before adopting any new detector/tracker dependency.

Required invariants:

- `SpatialComposer`, not Renderer, owns crop/scale/reposition decisions;
- a model/provider may observe or propose focus targets but cannot write executable crop coordinates directly;
- crop candidates remain inside source geometry and preserve target aspect ratio;
- hard source Shot cuts reset spatial path state;
- manual locks/keyframes outrank automatic re-solve once represented;
- impossible-fit cases return fallback/unresolved rather than generative outpainting;
- reuse R0.8 tracking/TemporalEvidence where possible; do not create a duplicate video-understanding stack;
- do not add a tenth top-level Domain Entity merely for reframing; keep new application artifacts behind the accepted v0.2 ownership model;
- proxy/cache remains R0.12 productization scope.

## R0.11 first exit target

Before broad Product Probe work, the repository should have a deterministic CPU-capable spatial foundation that can:

- express a target aspect-ratio intent;
- consume grounded existing spatial evidence;
- generate/validate legal crop candidates;
- produce an inspectable `ReframeDecision`/spatial transform path;
- prove source-bound, Shot-boundary, deterministic-repeatability and impossible-fit behavior with focused engineering evidence.

No R0.12 implementation has begun.
