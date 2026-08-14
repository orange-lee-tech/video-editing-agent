# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.11 — Spatial Composition / Auto Reframe  
**Engineering state:** ACTIVE — deterministic track path accepted; analyzed-range hardening + motion-stability baseline next  
**Updated:** 2026-08-14

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.
- R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.

## Accepted R0.11 baselines

`ef0baa455c27c0ccb42ae74c4d24ede76e543a74` — `feat: add deterministic spatial composition foundation`

`3ea89a51354fd3df62eed82e7959201969ec8b57` — `feat: add deterministic spatial track paths`

Verified evidence at `3ea89a5`:

- manual-lock timing uses the canonical half-open selection range `[start, end)`;
- non-empty protected regions fail closed rather than being silently ignored;
- unsupported framing styles fail closed; `hold` and `track` are explicit supported paths;
- existing R0.8 `SeededTrackingProposal` / `TrackingSample` are reused rather than replaced;
- `SpatialEvidenceTrack` / `SpatialFocusObservation` preserve selection, Shot, source geometry, provider revision and evidence provenance;
- relative tracking time maps to canonical source time as `analyzed_source_range.start + relative_time`;
- tracker observations remain evidence; executable crop coordinates are regenerated and validated by `SpatialComposer`;
- dynamic `track` mode produces multiple source-time crop keyframes inside one resolved Shot;
- lost/occluded observations carry no fabricated geometry and use explicit `hold-last-legal-crop-v1` mechanism behavior;
- manual locks override auto solve at the locked source time;
- hard Shot cuts reset path state;
- legacy `ReframeDecision.keyframes` are derived from the canonical `SpatialTransformPlan` and are validated against it;
- Engineering Probe reported `17/17 PASS`;
- focused tests reported `33 passed`;
- full pytest reported `471 passed`;
- remote `ci/quality-gate-diagnostic` is green;
- no new detector/model dependency was introduced.

## Bounded review finding

One half-open-range leak remains in the tracking-conversion boundary.

`MediaTimeRange` is explicitly `[start, end)`, but `tracking_proposal_to_spatial_track()` currently rejects an observation only when `source_time > analyzed_source_range.end`. An observation exactly at `analyzed_source_range.end` can therefore survive conversion. If the analyzed range is a strict subrange of the resolved selection, that endpoint can still enter the executable track path even though it lies outside the track's authoritative analyzed interval.

The next batch must:

- change analyzed-range observation legality to `[analyzed_start, analyzed_end)`;
- make `SpatialEvidenceTrack` validate its own observation times so direct construction cannot bypass the invariant;
- add exact-analyzed-end and direct-construction regressions.

This is a bounded R0.11 contract repair, not a new phase.

## Next R0.11 boundary

After that repair, add the first deterministic motion-stability policy needed before a real Auto Reframe Product Probe:

```text
grounded time-varying focus evidence
→ legal per-sample crops
→ explicit/versioned dead-zone / hysteresis / motion-limit / loss-gap policy
→ deterministic stabilized SpatialTransformPlan
→ spatial QC metrics
→ real Product Probe harness/readiness
```

Required invariants:

- canonical source time remains authoritative;
- no executable keyframe may equal or exceed its authoritative half-open analyzed/selection end;
- provider/tracker rectangles never become executable crop coordinates directly;
- all crop/path state remains Shot-local;
- manual locks remain hard constraints;
- tracking loss never fabricates observations;
- stabilization parameters are explicit/versioned mechanism candidates, not claimed as product-calibrated truth before benchmark evidence;
- path QC must expose jitter/motion/coverage/fallback behavior rather than hiding it;
- no generative outpainting/uncrop;
- no R0.12 proxy/cache implementation.

R0.11 Product Probe is not yet accepted. A real moving/occlusion corpus and human comparison against center crop/simple tracking remain required.

## Future audio-provider backlog

The user's future requirement for automatic rights-aware music discovery/acquisition is preserved separately in:

`docs/research/AUDIO_PROVIDER_CANDIDATES_2026-08-14.md`

It does not reopen R0.10 and is not R0.11 implementation scope.

No R0.12 implementation has begun.
