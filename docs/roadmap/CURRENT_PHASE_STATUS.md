# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.11 — Spatial Composition / Auto Reframe  
**Engineering state:** ACTIVE — replacement Product Probe media supplied; geometry inspection and real A/B/C preview generation next  
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

The accepted engineering foundation remains green: canonical half-open source time, R0.8 grounded tracking evidence, `SpatialComposer` crop authority, explicit `SpatialPathPolicy(version=r0.11-stability-candidate-v1)`, inspectable `SpatialPathQc`, canonical `SpatialTransformPlan`, Engineering Probe `26/26 PASS`, full pytest `475 passed` and remaining Quality Gate checks green.

## Previous Product Probe attempt

The prior two clips were both 720×1280 (9:16). With a 9:16 target and the current maximum legal-crop semantics, the only legal maximum crop was the full frame, so center/raw/stabilized would have been identical.

Classification was correctly recorded as:

`EXECUTION_BLOCKED — TARGET_ASPECT_NO_CROP_LATITUDE`

This was a media-geometry blocker, not a tracker or R0.11 implementation failure.

## Current gate reopened

The user now reports replacement material has been placed under:

`example/r0_11_product_probe/input/`

The next execution must discover the actual files and inspect display geometry rather than trusting names. Only non-9:16 media with meaningful crop latitude may proceed to the real Product Probe.

For two usable clips, execute:

```text
same source / same exact range / same 9:16 target
→ center/static
vs
raw/simple grounded tracking
vs
stabilized SpatialComposer
→ canonical SpatialTransformPlan previews + Spatial QC
→ Human Gate
```

Do not retune the accepted stabilization policy before Human Gate. Do not add zoom authority, a new detector/tracker/provider, Renderer-owned crop decisions, R0.12 proxy/cache work or audio-provider integration.

R0.11 remains open until the real previews are technically valid and the user completes the Human Gate.

## Future audio-provider backlog

Automatic rights-aware music discovery/acquisition remains recorded separately in:

`docs/research/AUDIO_PROVIDER_CANDIDATES_2026-08-14.md`

It does not reopen R0.10 and is not part of the R0.11 Product Probe.