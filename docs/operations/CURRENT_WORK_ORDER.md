# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.11 — interpolation-aware recovery Product Probe final QC repair  
**Updated:** 2026-08-14

## Accepted implementation candidate

`1be9a6121b53a46d1038b67737541b47ee97ec0a` — `feat: add interpolation-aware spatial recovery`

Verified on GitHub:

- single fast-forward implementation commit from `1a203e257...`;
- remote `ci/quality-gate-diagnostic` is green;
- canonical `SpatialTransformPlan` now explicitly owns `HOLD` / `LINEAR` interpolation;
- FFmpeg adapter `ffmpeg-spatial-transform-plan-v2` consumes canonical interpolation using exact rational time and deterministic round-half-up pixel evaluation;
- MediaPipe recovery is an optional provider behind the existing seeded-tracking evidence boundary;
- detector model remains external/uncommitted and SHA-256 pinned;
- `SpatialPathPolicy(version=r0.11-stability-recovery-candidate-v2)` separates terminal short hold (`<=1 s`) from bounded reacquisition (`<=4 s`);
- recovered lost runs bridge grounded before/after endpoints only; lost observations carry no geometry;
- full reported Quality Gate: 486 tests plus Ruff, mypy, import contracts, build and diff checks green.

## Real evidence now available

Integrated MediaPipe recovery on `moving_occlusion1_landscape.mp4` reproduced deterministically:

- 96 available / 92 lost;
- main loss `47/30`;
- recovery `133/30`;
- latency `2.8667 s`;
- same intended subject recovered;
- 96/96 reported grounded-observation containment;
- no fabricated lost geometry.

Six interpolation-aware local/private previews were generated for the existing movement and occlusion source ranges and passed technical decode/output checks.

## Audit finding before Human Gate

The previews are not rejected, but one QC calculation must be repaired before product acceptance evidence is trusted.

`DeterministicSpatialComposer._track_qc()` currently checks each available observation against the latest canonical keyframe at or before that observation time. That is correct for `HOLD`, but tracked plans now use `SpatialInterpolationMode.LINEAR`.

Therefore `contained_focus_count` is currently evaluated with stale HOLD semantics instead of the canonical interpolated crop actually executed at that source time.

The reported `96/96` containment is consequently not yet authoritative for LINEAR plans.

This is an **evidence/QC correctness defect**, not evidence that interpolation, recovery, or MediaPipe itself is wrong.

## Required bounded repair

1. Make canonical spatial-plan evaluation reusable outside Renderer.
2. There must be one deterministic evaluator for `HOLD` / `LINEAR` source-time crop semantics.
3. Prefer placing the pure evaluator with the canonical Application spatial artifact (for example a method/function owned alongside `SpatialTransformPlan`) so both SpatialComposer QC and Renderer consume the same semantics without an inward dependency on `render`.
4. Preserve exact rational time and deterministic round-half-up pixel behavior.
5. `SpatialComposer._track_qc()` must evaluate the actual canonical crop at every available observation time before checking containment.
6. Renderer must consume the same canonical evaluator/semantics and retain no independent interpolation policy.
7. Add focused regressions proving a LINEAR intermediate observation is checked against the interpolated crop rather than the prior keyframe crop.
8. Re-run the full Quality Gate.
9. Re-run Product Probe metadata/QC for both movement and occlusion trios. Re-render only if code/evidence comparison shows output bytes or execution semantics changed; otherwise preserve the already generated v2 previews and refresh metadata/QC honestly.
10. Stop for Human Gate only after interpolation-aware containment is authoritative.

## Do not change in this repair

- no SpatialPathPolicy retuning;
- no change to 12 px dead zone or 800 px/s velocity candidate;
- no change to 1 s terminal hold or 4 s reacquisition candidate;
- no new tracker/provider;
- no model bundling;
- no project-license change;
- no R0.12 work;
- no audio-provider work;
- no R0.11 closure.

## Human Gate after repair

Movement trio:

- best overall: `center / raw / stabilized / tie`;
- stabilized feel: `natural / jittery / chasing / laggy`;
- obvious defect: none / clipping / jump / wrong focus / excessive chase / excessive lag / other.

Occlusion trio:

- best overall: `center / raw / stabilized / tie`;
- recovery: `acceptable / unacceptable`;
- obvious defect: wrong focus / abrupt jump / stale framing / excessive lag / clipping / other.

Human judgment remains product authority; QC is supporting mechanism evidence only.
