# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.11 — Spatial Composition / Auto Reframe  
**Engineering state:** WAITING_HUMAN — real Product Probe blocked by 9:16 source geometry; non-9:16 footage required  
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

The accepted motion-stability implementation remains green:

- canonical source-time ranges are half-open;
- grounded R0.8 seeded-tracking evidence is reused;
- `SpatialComposer` owns executable spatial decisions;
- `SpatialPathPolicy(version=r0.11-stability-candidate-v1)` is explicit and versioned;
- candidate defaults remain 12 px dead zone, 800 px/s per-axis center velocity limit, 1 s maximum lost hold and redundant-keyframe suppression;
- lost observations do not fabricate geometry;
- mandatory-focus containment outranks velocity limiting;
- path state is Shot-local;
- `SpatialPathQc` is inspectable;
- `SpatialTransformPlan` remains execution truth;
- Engineering Probe reported `26/26 PASS`;
- full pytest reported `475 passed`; Ruff, mypy, import contracts, build and diff checks were green;
- remote CI is green;
- no detector/model/provider dependency was introduced.

## Real Product Probe attempt result

Two user-rights-attested clips were inspected:

- `moving_occlusion1.mp4` — 720×1280, approximately 4.46 s, contains visible occlusion;
- `moving_occlusion2.mp4` — 720×1280, approximately 2.73 s, no intended occlusion.

Both are already exactly 9:16.

For the current 9:16 target and maximum legal-crop semantics, the only legal maximum crop is the whole 720×1280 frame. CENTER, RAW and STABILIZED would therefore be spatially identical and cannot provide valid Product Probe evidence.

Classification:

`EXECUTION_BLOCKED — TARGET_ASPECT_NO_CROP_LATITUDE`

This does **not** downgrade the accepted engineering baseline and does **not** establish a tracker defect. The geometry gate occurs before a meaningful tracking/stabilization comparison.

## Current gate

R0.11 now waits for rights-attested source footage with actual crop latitude relative to a 9:16 output.

Preferred evidence:

- landscape 16:9 source, ideally 1920×1080 or 1280×720;
- one moving-subject clip with a brief real occlusion/recovery;
- one moving-subject clip without occlusion;
- preferably 6–20 seconds each;
- preserve original source framing; do not pre-convert to 9:16.

Then execute:

```text
same non-9:16 source / same exact range / same 9:16 target
→ center/static
vs
raw/simple grounded tracking
vs
stabilized SpatialComposer
→ canonical plan previews + Spatial QC
→ Human Gate
```

Do not retune the accepted policy or add zoom/tracker/provider authority while waiting merely to make the current vertical footage usable.

## Future audio-provider backlog

Automatic rights-aware music discovery/acquisition remains recorded separately in:

`docs/research/AUDIO_PROVIDER_CANDIDATES_2026-08-14.md`

It does not reopen R0.10 and is not part of the R0.11 Product Probe.

No R0.12 implementation has begun.
