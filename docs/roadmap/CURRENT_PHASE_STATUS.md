# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.11 — Spatial Composition / Auto Reframe  
**Engineering state:** ACTIVE — interpolation/recovery implementation candidate green; final QC semantics repair required before Human Gate  
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
- `1be9a6121b53a46d1038b67737541b47ee97ec0a` — interpolation-aware spatial recovery candidate.

At `1be9a612`, remote `ci/quality-gate-diagnostic` is success.

## Current implementation state

The previous step-held preview defect has been structurally repaired:

- `SpatialTransformPlan` owns explicit `HOLD` / `LINEAR` interpolation;
- FFmpeg adapter v2 executes piecewise linear tracked paths deterministically;
- MediaPipe recovery remains provider-neutral and optional;
- exact external EfficientDet artifact hash is enforced while redistribution terms remain release-license pending;
- terminal short loss remains bounded to 1 s;
- recovered gaps are a separate bounded recovery bridge, currently candidate max 4 s;
- lost observations contain no geometry.

The real occlusion clip now recovers the intended subject after approximately 2.8667 s and produces a complete spatial Product Probe path.

## Final audit defect before Human Gate

`SpatialPathQc` containment is still evaluated using the latest prior keyframe crop rather than the canonical LINEAR interpolated crop at each available observation time.

This means current containment totals such as `96/96` are not yet authoritative evidence for LINEAR execution.

The defect is limited to QC/evidence semantics; no current evidence establishes a Renderer, recovery-provider or SpatialComposer path-generation failure.

## Active gate

Perform one bounded repair:

- unify canonical `HOLD` / `LINEAR` crop evaluation in a reusable upstream semantic;
- make both FFmpeg execution and SpatialComposer QC use that canonical semantic;
- add an interpolation-aware containment regression;
- rerun full Quality Gate and Product Probe QC/metadata;
- then stop for the user's Human Gate.

Do not retune spatial policy while this evidence defect is active.

## Licensing state

The Product Owner is willing to open-source the project, but the repository still has no selected root license. Do not automatically relicense or adopt AGPL merely because open-source intent exists.

The current MediaPipe detector model remains `RELEASE_LICENSE_PENDING` for redistribution. This does not block local Product Probe execution, but must be resolved before an applicable release/distribution path.

## R0.11 completion gate

R0.11 can close only after:

1. interpolation-aware QC is corrected and green;
2. movement A/B/C Human Gate is acceptable;
3. occlusion/recovery A/B/C Human Gate is acceptable;
4. model/dependency release status is recorded for the intended distribution path.

No R0.12 implementation has begun.
