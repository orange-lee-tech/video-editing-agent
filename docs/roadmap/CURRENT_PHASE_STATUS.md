# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.11 — Spatial Composition / Auto Reframe  
**Engineering state:** WAITING_HUMAN — deterministic motion-stability baseline accepted; real Product Probe media required  
**Updated:** 2026-08-14

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.
- R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.

## Accepted R0.11 baselines

- `ef0baa455c27c0ccb42ae74c4d24ede76e543a74` — deterministic static spatial composition foundation.
- `3ea89a51354fd3df62eed82e7959201969ec8b57` — deterministic source-time track paths.
- `ad4f47e5f659e108d34593675bc08177a2c2aff4` — deterministic motion-stability baseline.

## Verified evidence at `ad4f47e5`

Remote review confirms:

- `SpatialEvidenceTrack` now enforces its own half-open analyzed range `[start, end)`;
- `tracking_proposal_to_spatial_track()` rejects exact analyzed-end and before-start observations;
- canonical source time remains `analyzed_source_range.start + relative_time`;
- `SpatialPathPolicy(version=r0.11-stability-candidate-v1)` is explicit and participates in decision identity;
- current uncalibrated mechanism candidates are 12 px center dead zone, 800 px/s per-axis center velocity limit, 1 s maximum lost hold and redundant-keyframe suppression;
- velocity limiting fails closed rather than silently cropping out mandatory focus;
- over-limit tracking loss fails closed;
- manual locks remain exact hard constraints;
- stabilization stays Shot-local;
- `SpatialPathQc` exposes focus containment, geometry legality, movement/velocity, direction changes, held loss and keyframe suppression;
- `SpatialTransformPlan` remains execution truth and the legacy decision view derives from it;
- Engineering Probe reported `26/26 PASS`;
- focused/full validation reported `475` pytest tests plus Ruff, mypy, import contracts, build and diff checks green;
- remote `ci/quality-gate-diagnostic` is green;
- no detector/model/provider dependency was added.

The current numeric path-policy defaults remain mechanism candidates only. They are not yet product-calibrated natural-camera values.

## Real Product Probe gate

The existing private corpus was audited. It contains camera motion and hand/object interaction, but it does not provide verified coverage of a moving subject plus meaningful tracking occlusion. Synthetic fixtures are therefore not accepted as Product Probe evidence.

R0.11 now waits for rights-attested local footage suitable for a real comparison:

```text
same source range / same target canvas
→ center/static crop
vs
raw/simple tracking path
vs
stabilized SpatialComposer path
→ rendered previews + spatial QC
→ Human Gate
```

The Product Probe executor must consume canonical `SpatialTransformPlan` decisions. FFmpeg/Renderer may execute those plans but may not recreate crop authority.

No further speculative spatial algorithm work should begin while waiting for suitable media. The real-media probe harness should be completed against the actual supplied files, not against another synthetic placeholder corpus.

## Future audio-provider backlog

The future requirement for automatic rights-aware music discovery/acquisition remains recorded in:

`docs/research/AUDIO_PROVIDER_CANDIDATES_2026-08-14.md`

It does not reopen R0.10 and is not R0.11 implementation scope.

No R0.12 implementation has begun.
