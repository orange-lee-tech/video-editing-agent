# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.11 — Spatial Composition / Auto Reframe  
**Engineering state:** READY_FOR_HUMAN_GATE — canonical interpolation, recovery tracking, interpolation-aware QC and six real Product Probe previews are technically green  
**Updated:** 2026-08-14

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.
- R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.

## Accepted R0.11 foundations

- `ef0baa455c27c0ccb42ae74c4d24ede76e543a74` — static spatial composition.
- `3ea89a51354fd3df62eed82e7959201969ec8b57` — source-time track paths.
- `ad4f47e5f659e108d34593675bc08177a2c2aff4` — deterministic motion stability.
- `66fc889094dd46dd51d5ccf028869c37658f648b` — initial canonical FFmpeg spatial execution.
- `1be9a6121b53a46d1038b67737541b47ee97ec0a` — interpolation-aware recovery candidate.
- `d06592560dbeb764666592effa00f7d5537715ef` — canonical interpolation-aware QC repair.

At `d065925`, remote `ci/quality-gate-diagnostic` is success.

## Current implementation state

- `SpatialTransformPlan` owns explicit HOLD / LINEAR interpolation and canonical `evaluate_crop()` semantics.
- SpatialComposer QC uses the actual canonical interpolated crop at every available observation time.
- FFmpeg adapter v2 consumes the same interpolation semantics; no Renderer-owned smoothing authority exists.
- MediaPipe Object Detector + deterministic Sparse-LK reseed is the current recovery-capable evidence provider candidate.
- external EfficientDet artifact hash is enforced; model remains external/uncommitted and redistribution license status remains pending.
- terminal unrecovered loss is bounded to 1 s.
- recovered loss runs use a separate candidate `max_reacquisition_gap = 4 s` contract.
- lost observations contain no geometry; recovery bridges only grounded endpoints.

## Real Product Probe evidence

Movement:

- RAW 40/40 containment, 41 keyframes, max velocity 240 px/s;
- STABILIZED 40/40 containment, 14 keyframes, max velocity 195 px/s.

Occlusion/recovery:

- RAW 96/96 containment, 99 keyframes, max velocity 600 px/s;
- STABILIZED 96/96 containment, 14 keyframes, max velocity 450 px/s;
- main recovery `47/30 -> 133/30`, latency 2.8667 s;
- intended seeded subject recovered and contained;
- no source/aspect violations or unresolved plans.

All six local/private 540x960 Product Probe previews are technically valid. The final QC repair did not change preview execution semantics, so existing preview bytes were reused.

## Active gate

The Product Owner must now perform the Human Gate on both movement and occlusion trios.

Do not retune R0.11 policy or change providers before this judgment.

## Licensing state

The Product Owner is willing to open-source the project, but no root project license has yet been selected.

The current EfficientDet model remains `RELEASE_LICENSE_PENDING` for redistribution. This does not block the local Product Probe Human Gate; release/distribution policy must be resolved before an applicable packaged release.

## R0.11 completion gate

R0.11 can close after:

1. movement A/B/C Human Gate is acceptable;
2. occlusion/recovery A/B/C Human Gate is acceptable;
3. any concrete Human Gate defect is either accepted as a bounded candidate limitation or repaired and revalidated;
4. model/dependency release status remains explicitly recorded for the intended distribution path.

No R0.12 implementation has begun.
