# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.11 — Spatial Composition / Auto Reframe  
**Engineering state:** ACTIVE — movement Product Probe ready for Human Gate; occlusion path blocked by tracker reacquisition and entering provider benchmark  
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
- `66fc889094dd46dd51d5ccf028869c37658f648b` — canonical `SpatialTransformPlan` → deterministic FFmpeg execution adapter.

At `66fc889`, remote `ci/quality-gate-diagnostic` is green. The implementation diff is bounded to the FFmpeg spatial-plan executor and two focused regressions; it does not change `SpatialComposer`, the seeded tracker or stabilization constants.

## Real Product Probe — partial success

The replacement 1280×720 landscape clips passed the 9:16 crop-latitude gate.

### Movement path

`moving_occlusion2_landscape.mp4` produced technically valid center/raw/stabilized previews.

Reported evidence:

- source range `[7/10, 13/5)`;
- 41 observations, 40 available and one terminal `target_exit`;
- CENTER 1 keyframe;
- RAW 41 keyframes, containment 40/40, max velocity 240 px/s;
- STABILIZED 14 keyframes, containment 40/40, max velocity 195 px/s, 27 keyframes suppressed;
- rendered previews 540×960 / 30 FPS / 1.9 s with no reported black intervals.

This branch of the Product Probe is ready for the user's Human Gate now.

### Occlusion/recovery path

`moving_occlusion1_landscape.mp4` exposed a provider capability failure before the intended later occlusion/recovery event:

- authoritative range `[0, 563298/90000)`;
- current Sparse-LK support was lost at relative `29/30` s;
- no reacquisition occurred;
- therefore the later real occlusion/recovery could not be evaluated.

This is a tracker-recovery blocker, not evidence against `SpatialComposer` motion stability.

## Active engineering gate

The next engineering work is a provider-neutral tracker recovery benchmark, documented in:

`docs/research/R0_11_TRACKER_RECOVERY_PROVIDER_BENCHMARK_2026-08-14.md`

Candidate order:

1. YOLOX-Nano + ByteTrack as the primary local/CPU benchmark candidate;
2. MediaPipe Object Detector + deterministic reseed only if the primary candidate is materially insufficient;
3. SAM 2 deferred to a heavier GPU tier.

Ultralytics YOLO remains excluded from the default proprietary/commercial path absent an explicit licensing strategy change.

No provider is approved merely because its code repository is permissively licensed. Exact model artifacts, runtimes and transitive dependencies require their own release record.

## R0.11 completion gate

R0.11 remains open until both are satisfied:

1. movement Human Gate establishes whether center/raw/stabilized behavior is product-acceptable;
2. a recovery-capable tracking evidence path enables a real occlusion/recovery A/B/C Product Probe and Human Gate.

Do not retune current spatial constants while the active failure is tracker reacquisition.

## Future audio-provider backlog

Automatic rights-aware music discovery/acquisition remains recorded separately in:

`docs/research/AUDIO_PROVIDER_CANDIDATES_2026-08-14.md`

It does not reopen R0.10 and is not part of R0.11.
