# Current Work Order

**Status:** READY_FOR_HUMAN_GATE  
**Phase:** R0.11 — real Auto Reframe Product Probe Human Gate  
**Updated:** 2026-08-14

## Accepted implementation

`d06592560dbeb764666592effa00f7d5537715ef` — `fix: make spatial QC interpolation-aware`

Verified on GitHub:

- fast-forward implementation from `7aa09a7...`;
- remote `ci/quality-gate-diagnostic` is success;
- `SpatialTransformPlan.evaluate_crop()` is the canonical HOLD/LINEAR source-time evaluator;
- SpatialComposer QC and FFmpeg execution now share the same exact rational / round-half-up interpolation semantics;
- FFmpeg adapter remains `ffmpeg-spatial-transform-plan-v2`; preview execution semantics and preview bytes did not change in the final QC repair;
- MediaPipe recovery remains optional and provider-neutral;
- external EfficientDet model SHA is pinned and the model remains uncommitted;
- `SpatialPathPolicy(version=r0.11-stability-recovery-candidate-v2)` keeps terminal loss hold <=1 s and bounded reacquisition <=4 s;
- lost observations contain no geometry; recovery bridges grounded endpoints only;
- full reported Quality Gate is green with 487 tests.

## Authoritative Product Probe QC

Movement source:

`moving_occlusion2_landscape.mp4` — `[7/10, 13/5)`

- RAW: 40/40 interpolation-aware containment, 41 keyframes, max canonical velocity 240 px/s;
- STABILIZED: 40/40 containment, 14 keyframes, max canonical velocity 195 px/s.

Occlusion source:

`moving_occlusion1_landscape.mp4` — `[0, 563298/90000)`

- RAW: 96/96 interpolation-aware containment, 99 keyframes, max canonical velocity 600 px/s;
- STABILIZED: 96/96 containment, 14 keyframes, max canonical velocity 450 px/s;
- main loss `47/30` -> recovery `133/30`;
- recovery latency 2.8667 s;
- recovered identity is the intended seeded subject and is contained at recovery;
- no source/aspect violations, no unresolved plan, no fabricated lost geometry.

The six previously generated local/private previews remain technically valid and were reused byte-for-byte because the final repair changed QC semantics only.

## Human Gate — movement

Compare:

- `example/r0_11_product_probe/output/moving_occlusion2_landscape_center.mp4`
- `example/r0_11_product_probe/output/moving_occlusion2_landscape_raw.mp4`
- `example/r0_11_product_probe/output/moving_occlusion2_landscape_stabilized.mp4`

Report only:

- best overall: `center / raw / stabilized / tie`;
- stabilized feel: `natural / jittery / chasing / laggy`;
- obvious defect: `none / clipping / jump / wrong focus / excessive chase / excessive lag / other`.

## Human Gate — occlusion/recovery

Compare:

- `example/r0_11_product_probe/output/moving_occlusion1_landscape_center.mp4`
- `example/r0_11_product_probe/output/moving_occlusion1_landscape_raw.mp4`
- `example/r0_11_product_probe/output/moving_occlusion1_landscape_stabilized.mp4`

Report only:

- best overall: `center / raw / stabilized / tie`;
- recovery: `acceptable / unacceptable`;
- obvious defect: `none / wrong focus / abrupt jump / stale framing / excessive lag / clipping / other`.

Human-visible judgment is product authority. Do not tune again before the Product Owner reports this gate.

## Remaining release note

The exact EfficientDet model redistribution/commercial terms remain `RELEASE_LICENSE_PENDING`. This does not block this local Human Gate. The Product Owner is willing to open-source the project, but no root project license has yet been selected.

## Explicitly not allowed before Human Gate

- no SpatialPathPolicy tuning;
- no new tracker/provider/model;
- no rerender unless the user reports a concrete output defect requiring a bounded repair;
- no R0.12 implementation;
- no audio-provider work;
- no R0.11 closure before Human Gate.
