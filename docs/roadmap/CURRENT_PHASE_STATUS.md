# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.11 — Spatial Composition / Auto Reframe  
**Engineering state:** ACTIVE — static spatial foundation accepted; contract hardening + time-varying track path next  
**Updated:** 2026-08-14

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.
- R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.

## Accepted R0.11 foundation baseline

`ef0baa455c27c0ccb42ae74c4d24ede76e543a74` — `feat: add deterministic spatial composition foundation`

Verified foundation evidence:

- Application-level SpatialComposer remains spatial decision authority;
- R0.8 NormalizedRectangle/tracking provenance and R0.9 ResolvedSelection/source ranges are reused;
- provider-neutral ReframeIntent, source/canvas geometry, PixelCrop, SpatialEvidenceView, manual crop locks and SpatialTransformPlan exist;
- static/hold composition is deterministic and caller-order independent;
- executable crops remain inside source bounds and preserve exact target aspect ratio;
- mandatory-focus impossible fit returns non-generative unresolved;
- each Shot is solved independently from its exact source start;
- focused tests and bounded Engineering Probe are green;
- full pytest reported 466 passed and remote ci/quality-gate-diagnostic is green;
- no new detector/model dependency was introduced.

## Review findings before the next feature step

The foundation is directionally accepted, but three contract issues must be hardened before broader dynamic behavior:

1. Manual lock time validation currently allows a keyframe exactly at `selected_source_range.end`, while SpatialTransformPlan correctly requires keyframes to satisfy the half-open interval `[start, end)`. This creates an internal contract contradiction.
2. `protected_regions` is present on SpatialCompositionRequest but the current composer does not consume it. Protected/safe-zone intent must never be silently ignored; until deterministic semantics are implemented, non-empty protected regions must fail closed or return explicit unresolved/warning behavior.
3. `ReframeIntent.framing_style` accepts arbitrary non-empty strings while the current composer always emits `hold`. Unsupported intent must not silently collapse to another mode. The next dynamic boundary should introduce explicit supported mode semantics.

These are bounded R0.11 contract issues, not architecture failures and not reasons to introduce a new vision stack.

## Next R0.11 boundary

After hardening those contracts, extend the accepted foundation into the first time-varying track path using existing R0.8 seeded-tracking evidence:

```text
SeededTrackingProposal / TrackingSample(relative_time)
→ canonical source-time spatial evidence track
→ legal per-sample crop candidates
→ deterministic track-path plan
→ explicit gap/occlusion behavior
→ spatial QC
```

Required invariants:

- canonical source time remains authoritative;
- provider/tracker observations never become executable crop coordinates directly;
- no crop/path state crosses a hard Shot cut;
- manual locks remain hard constraints;
- unknown/unsupported framing modes fail closed;
- protected regions are never silently ignored;
- tracking loss/occlusion never fabricates observations;
- numeric smoothing/gap policies remain explicit/versioned and are not presented as calibrated product truth before benchmark evidence;
- no generative outpainting/uncrop;
- no R0.12 proxy/cache implementation.

R0.11 Product Probe is not yet ready. No R0.12 implementation has begun.
