# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.11 — contract hardening + time-varying track-path foundation  
**Updated:** 2026-08-14

## Accepted baseline

Current accepted R0.11 implementation baseline:

`ef0baa455c27c0ccb42ae74c4d24ede76e543a74` — `feat: add deterministic spatial composition foundation`

Remote review confirmed:

- SpatialComposer owns executable crop decisions;
- existing R0.8 spatial/tracking primitives and R0.9 ResolvedSelection/source time are reused;
- static/hold crop generation is deterministic and source-bound;
- exact target aspect ratio is preserved;
- mandatory impossible-fit returns non-generative unresolved;
- manual locks outrank automatic focus in the tested path;
- Engineering Probe `7/7 PASS`;
- focused tests reported `31 passed`;
- full pytest reported `466 passed`;
- remote `ci/quality-gate-diagnostic` is green;
- no detector/model dependency was added.

## Review defects to repair first

Before feature expansion, repair these bounded contract inconsistencies:

1. **Half-open source range:** `_manual()` currently accepts `source_time == selected_source_range.end`, but SpatialTransformPlan rejects it. Manual lock validation must use the same `[start, end)` contract and add an exact-end regression.
2. **Protected-region truth:** `SpatialCompositionRequest.protected_regions` must not be silently ignored. If deterministic safe-zone semantics are not implemented in this batch, non-empty protected regions must explicitly fail closed/unresolved rather than produce a normal plan.
3. **Framing-style truth:** arbitrary non-empty `framing_style` must not silently become `hold`. Make supported modes explicit. Unknown/unsupported modes fail closed or reject validation. `hold` remains supported; `track` may become supported only when the time-varying path below is actually implemented.

Do these repairs before adding dynamic behavior. Do not create a micro-phase for them.

## Coherent feature boundary after repairs

Reuse the existing R0.8 seeded tracking contract:

- `SeededTrackingProposal.analyzed_source_range`;
- `TrackingSample.relative_time`;
- sample status/reason/rectangle/support evidence.

Build the smallest provider-neutral, canonical time-varying spatial evidence seam and deterministic track path.

Required behavior:

1. Map tracking-relative sample time to canonical source time without creating a second timestamp authority.
2. Preserve Shot identity, selection identity, provider/provenance and source-range legality.
3. Represent time-varying focus observations separately from the existing static SpatialEvidenceView if overloading it would make semantics ambiguous.
4. Generate legal target-aspect crop candidates for valid samples; tracker rectangles remain observations only.
5. Add a supported `track` path that produces multiple source-time crop keyframes inside one resolved Shot.
6. Keep path state Shot-local. A hard Shot cut always resets path state.
7. Define tracking-loss/occlusion behavior explicitly. Missing/invalid tracker samples may not fabricate focus geometry. Use conservative fail-closed/hold behavior backed by explicit versioned policy; do not hide arbitrary thresholds as calibrated truth.
8. If smoothing/motion limiting is introduced, make parameters explicit/versioned and deterministic. Do not claim product-calibrated naturalness yet.
9. Manual locks are hard constraints. Dynamic auto solve must not alter a locked crop keyframe.
10. Protected regions must never be silently ignored. Implement deterministic semantics only if the existing CAP/ADR/contracts support them without inventing an arbitrary overlap threshold; otherwise return explicit unresolved/warning when requested.
11. Every executable keyframe must satisfy source bounds, target aspect ratio and `[source_start, source_end)` time legality.
12. Keep legacy ReframeDecision keyframes and SpatialTransformPlan consistent wherever both representations remain necessary; do not create two divergent execution truths.

## Engineering evidence required

Add focused regressions/probe coverage for at least:

- manual lock exactly at source end is rejected consistently;
- unsupported framing mode cannot silently return hold;
- non-empty protected regions cannot be silently ignored;
- relative tracking sample time maps to correct canonical source time;
- dynamic path is deterministic under equivalent input ordering;
- all dynamic crop keyframes remain legal;
- track path stays inside one Shot and resets on a different Shot;
- explicit tracking loss/occlusion behavior;
- manual locked keyframe remains unchanged by track solve;
- no generated/synthesized focus geometry is introduced.

Run the full repository Quality Gate.

## Explicitly not in this batch

- no YOLO/MediaPipe/SAM2/new detector dependency merely to improve appearance;
- no provider benchmark selection or license commitment yet;
- no claim that current smoothing constants are product-optimal;
- no R0.11 Product Probe claim from synthetic fixtures;
- no generative outpainting/uncrop;
- no Renderer-owned crop logic;
- no R0.12 preview/proxy/cache work.

## Stop conditions

Stop and report instead of inventing semantics if:

- existing SeededTrackingProposal cannot be mapped to canonical source time without changing time authority;
- supporting protected regions requires a new product-policy decision not present in CAP-07/ADR-007;
- dynamic path requires a new top-level Domain Entity or Architecture Contract change;
- a new dependency becomes necessary and its transitive code/model/runtime licensing is unresolved.

Otherwise complete the entire coherent boundary, commit/push one green batch, and report starting/ending HEAD, repaired contracts, new/reused types, dynamic path semantics, probe results, full Quality Gate, and remaining Product Probe/provider needs.

Do not close R0.11 and do not begin R0.12.
