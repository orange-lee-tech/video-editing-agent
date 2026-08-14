# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.11 — real Auto Reframe Product Probe with replacement non-9:16 media  
**Updated:** 2026-08-14

## Accepted implementation baseline

`ad4f47e5f659e108d34593675bc08177a2c2aff4` — `feat: stabilize deterministic spatial track paths`

The R0.11 engineering foundation remains accepted. The prior Product Probe was blocked only because both supplied clips were already exactly 9:16, leaving no crop latitude for a 9:16 target.

Accepted invariants remain:

- canonical half-open source-time ranges;
- R0.8 grounded seeded-tracking evidence;
- `SpatialComposer` owns executable crop/path decisions;
- `SpatialPathPolicy(version=r0.11-stability-candidate-v1)` remains unchanged;
- current uncalibrated candidates remain 12 px dead zone, 800 px/s per-axis center velocity limit, 1 s maximum lost hold and redundant-keyframe suppression;
- manual locks are hard constraints;
- lost observations do not fabricate geometry;
- mandatory-focus containment outranks velocity limiting;
- `SpatialTransformPlan` remains execution truth;
- Engineering Probe `26/26 PASS`;
- full pytest `475 passed` plus Ruff, mypy, import contracts, build and diff checks green.

## Replacement Product Probe media supplied

The user reports that replacement test material has now been placed under:

`example/r0_11_product_probe/input/`

Do not assume filenames or extensions. Discover the actual local files and inspect their geometry before proceeding.

The prior 9:16 clips may remain present and must not be mistaken for the replacement benchmark inputs.

## Geometry gate first

Before tracking or rendering:

1. enumerate candidate video files under `example/r0_11_product_probe/input/`;
2. inspect filename, SHA-256, codec, duration, resolution, display aspect and frame rate;
3. identify the two intended replacement moving-subject clips by actual local evidence;
4. require source geometry with real crop latitude relative to the 9:16 target;
5. prefer landscape 16:9; other non-9:16 sources are acceptable if they provide meaningful crop freedom;
6. if the replacement files are still effectively 9:16 after display-rotation/aspect handling, stop as `EXECUTION_BLOCKED — TARGET_ASPECT_NO_CROP_LATITUDE` rather than inventing zoom or crop authority.

## Product Probe execution

For each usable replacement clip:

```text
same source / same exact source range / same 9:16 target canvas
→ A — center/static crop
→ B — raw/simple grounded tracking path
→ C — stabilized SpatialComposer path
→ canonical SpatialTransformPlan execution
→ local previews + SpatialPathQc/comparison metadata
→ Human Gate
```

Requirements:

- choose one exact authoritative continuous source range per clip and use it unchanged for A/B/C;
- preserve the meaningful occlusion/recovery interval for the occlusion clip;
- reuse the current R0.8 seeded tracker; do not add/switch providers;
- tracker/provider rectangles remain observations only;
- A/B/C executable spatial decisions remain canonical `SpatialTransformPlan` decisions owned by the spatial layer;
- Renderer/FFmpeg may execute plans but may not recompute crop choices;
- use identical output canvas/resolution/frame-rate policy and identical audio treatment across A/B/C;
- no subtitles, graphics, music or presentation bias;
- keep `SpatialPathPolicy(version=r0.11-stability-candidate-v1)` unchanged before Human Gate;
- do not manually rescue a path or tune constants after preview inspection.

If two usable clips are found, generate six local/private previews under `example/r0_11_product_probe/output/`:

```text
<clip1>_center.mp4
<clip1>_raw.mp4
<clip1>_stabilized.mp4
<clip2>_center.mp4
<clip2>_raw.mp4
<clip2>_stabilized.mp4
```

Save local comparison metadata beside the previews including source hash/metadata/range, tracker identity, observation/loss information, plan IDs, policy IDs, keyframe counts, `SpatialPathQc`, render identity and output QC/hashes.

Human-visible occlusion is not automatically tracker loss. Record what the tracker actually reports; never manufacture a lost interval.

## Stop classifications

- `READY_FOR_HUMAN_GATE` — technically valid comparable A/B/C previews produced.
- `PARTIAL_PRODUCT_PROBE` — one clip succeeds and another has a concrete blocker.
- `TRACKER_BLOCKED` — current seeded tracker cannot materially follow the intended subject.
- `EXECUTION_BLOCKED — TARGET_ASPECT_NO_CROP_LATITUDE` — replacement geometry still has no meaningful crop freedom.
- `EXECUTION_BLOCKED` — canonical plans cannot be previewed without violating spatial authority and no bounded adapter can solve it cleanly.

## Explicitly not allowed

- no speculative policy retuning before Human Gate;
- no new detector/tracker/model/provider;
- no artificial zoom authority merely to force a benchmark;
- no synthetic Product Probe substitution;
- no Renderer-owned spatial decisions;
- no generative outpainting/uncrop;
- no R0.12 proxy/cache work;
- no audio-provider implementation;
- no R0.11 closure before Human Gate.

Keep all Product Probe media and outputs local/private/untracked.