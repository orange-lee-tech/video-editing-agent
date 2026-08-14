# Current Work Order

**Status:** WAITING_HUMAN  
**Phase:** R0.11 — real Auto Reframe Product Probe target-aspect media gate  
**Updated:** 2026-08-14

## Accepted implementation baseline

`ad4f47e5f659e108d34593675bc08177a2c2aff4` — `feat: stabilize deterministic spatial track paths`

The R0.11 engineering foundation remains accepted for real-media evaluation. No implementation defect was established by the latest Product Probe attempt.

Verified baseline remains:

- canonical half-open source-time legality;
- R0.8 grounded seeded-tracking evidence;
- `SpatialComposer` owns executable crop/path decisions;
- `SpatialPathPolicy(version=r0.11-stability-candidate-v1)` remains unchanged;
- current uncalibrated candidates remain 12 px dead zone, 800 px/s per-axis center velocity limit, 1 s maximum lost hold and redundant-keyframe suppression;
- manual locks are hard constraints;
- lost observations do not fabricate geometry;
- `SpatialTransformPlan` remains execution truth;
- Engineering Probe `26/26 PASS`;
- full pytest `475 passed` plus Ruff, mypy, import contracts, build and diff checks green;
- remote CI green.

## Product Probe attempt — blocked by source geometry

The user supplied and rights-attested two private clips under `example/r0_11_product_probe/input/`.

Observed local evidence reported by Codex:

### `moving_occlusion1.mp4`

- SHA-256 prefix: `A2DCDE8D67E2…`
- 927,933 bytes
- H.264/AAC
- 720×1280
- 134 frames
- approximately 30.06 FPS
- duration 4.457678 s
- candidate full range `[0/90000, 401191/90000)`

### `moving_occlusion2.mp4`

- SHA-256 prefix: `9977F2493A77…`
- 572,402 bytes
- H.264/AAC
- 720×1280
- 82 frames
- approximately 29.99 FPS
- duration 2.734356 s
- candidate full range `[0/90000, 246092/90000)`

Both sources are already exactly 9:16.

Under the current canonical maximum legal-crop semantics, a 720×1280 source targeting a 9:16 canvas has only one maximum legal crop:

`PixelCrop(left=0, top=0, width=720, height=1280)`

Therefore CENTER, RAW and STABILIZED would execute the same spatial plan. Such outputs cannot honestly evaluate tracking, occlusion recovery, chatter, chasing, dead-zone behavior or stabilization.

Final classification of this attempt:

`EXECUTION_BLOCKED — TARGET_ASPECT_NO_CROP_LATITUDE`

This is a Product Probe input-geometry blocker, not a tracker failure and not an R0.11 engineering failure.

## Why no implementation change is authorized

Do not force a benchmark by:

- silently changing the output aspect ratio;
- inventing zoom authority merely to create motion;
- adding arbitrary inset crop/scale behavior not owned by the current contract;
- adding a new tracker/model/provider;
- fabricating crop movement;
- generating identical A/B/C previews and presenting them as evidence.

The correct action is to supply source footage with real spatial latitude relative to the 9:16 target.

## Human input required

Provide replacement or additional rights-attested clips whose **source aspect ratio is not 9:16**, preferably ordinary landscape footage.

Recommended minimum Product Probe inputs:

1. `moving_occlusion1_landscape.*`
   - landscape 16:9 preferred (`1920×1080` or `1280×720` are ideal);
   - one clearly identifiable person/product moves horizontally or diagonally;
   - one real brief occlusion and recovery;
   - preferably 6–20 seconds continuous Shot;
   - some edge-of-frame movement is useful.

2. `moving_occlusion2_landscape.*`
   - same landscape preference;
   - clear subject movement without meaningful occlusion;
   - preferably 6–20 seconds;
   - enough horizontal displacement to distinguish center crop, raw chase and stabilized tracking.

Other non-9:16 sources such as 4:3 or square may be usable, but 16:9 landscape gives the clearest vertical Auto Reframe benchmark.

Do not pre-crop, pillarbox or letterbox the replacement footage into 9:16. Preserve the original camera frame.

Keep all Product Probe media local/private/untracked under:

`example/r0_11_product_probe/input/`

## Work to execute once suitable media exists

For each usable non-9:16 clip:

```text
same source / same exact source range / same 9:16 target canvas
→ A center/static baseline
→ B raw/simple grounded tracking
→ C stabilized SpatialComposer
→ canonical SpatialTransformPlan execution
→ local previews + SpatialPathQc/comparison metadata
→ Human Gate
```

The accepted stabilization policy must remain unchanged until the first real Human Gate.

## Explicitly not allowed while waiting

- no speculative policy retuning;
- no artificial zoom/crop authority added only to make current 9:16 samples useful;
- no new detector/tracker/model/provider;
- no synthetic Product Probe substitution;
- no Renderer-owned spatial decisions;
- no R0.12 proxy/cache work;
- no audio-provider implementation;
- no R0.11 closure.
