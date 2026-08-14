# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.11 — Spatial Composition / Auto Reframe  
**Engineering state:** ACTIVE — real two-clip Product Probe authorized and ready to execute  
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

## Verified engineering state

At the accepted motion-stability baseline:

- analyzed/source time legality is canonical half-open `[start, end)`;
- R0.8 seeded-tracking evidence is reused;
- `SpatialComposer` owns executable crop/path decisions;
- `SpatialPathPolicy(version=r0.11-stability-candidate-v1)` is explicit and versioned;
- current uncalibrated candidate values are 12 px center dead zone, 800 px/s per-axis center velocity limit, 1 s maximum lost hold and redundant-keyframe suppression;
- manual locks remain hard constraints;
- lost observations do not fabricate focus geometry;
- mandatory-focus containment outranks velocity limiting;
- stabilization is Shot-local;
- `SpatialPathQc` exposes inspectable movement/loss/geometry metrics;
- `SpatialTransformPlan` remains execution truth;
- Engineering Probe reported `26/26 PASS`;
- full pytest reported `475 passed`; Ruff, mypy, import contracts, build and diff checks were green;
- remote `ci/quality-gate-diagnostic` is green;
- no detector/model/provider dependency was added.

The current policy values remain mechanism candidates only. They are not product-calibrated until real human-viewed evidence supports them.

## Real Product Probe media now supplied

On 2026-08-14 the user confirmed two local private clips under:

`example/r0_11_product_probe/input/`

Roles:

- `moving_occlusion1*` — moving subject with real occlusion;
- `moving_occlusion2*` — moving subject without occlusion.

The user explicitly attested that they have the right to use both clips for this project test.

The media remains local/private and must not be tracked or uploaded to GitHub.

## Active Product Probe boundary

Execute the real comparison against both clips:

```text
same source / same exact source range / same target canvas
→ center/static baseline
vs
raw/simple grounded tracking
vs
stabilized SpatialComposer
→ canonical SpatialTransformPlan execution
→ rendered local previews + SpatialPathQc/comparison metadata
→ Human Gate
```

No speculative algorithm or parameter tuning should occur before the first Human Gate.

The comparison must preserve decision truth: tracker/provider outputs remain observations; `SpatialComposer` owns executable decisions; FFmpeg/Renderer only executes canonical plans.

If the existing seeded tracker cannot materially track a supplied clip, record `TRACKER_BLOCKED` and treat provider capability as the next evidence gate rather than silently switching implementations.

## Human Gate required before R0.11 closure

The user will compare center/raw/stabilized previews for both clips.

Primary product questions:

- which framing feels best overall;
- whether stabilized motion feels natural versus jittery/chasing/laggy;
- whether any subject is clipped or focus becomes wrong;
- for `moving_occlusion1`, whether occlusion and recovery are acceptable.

Human preference is authoritative product evidence. Spatial QC is supporting evidence.

R0.11 remains open until this Human Gate is complete.

## Future audio-provider backlog

Automatic rights-aware music discovery/acquisition remains recorded separately in:

`docs/research/AUDIO_PROVIDER_CANDIDATES_2026-08-14.md`

It does not reopen R0.10 and is not part of this Product Probe.

No R0.12 implementation has begun.
