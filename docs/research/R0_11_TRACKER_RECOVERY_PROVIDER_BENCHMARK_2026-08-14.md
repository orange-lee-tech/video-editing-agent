# R0.11 Tracker Recovery Provider Benchmark — 2026-08-14

## Context

The first valid non-9:16 Product Probe produced a partial result at:

`66fc889094dd46dd51d5ccf028869c37658f648b` — `feat: execute canonical spatial plans in ffmpeg`

Subsequent Human Gate and provider-benchmark evidence changed the active interpretation:

1. the movement previews are not valid SpatialComposer acceptance evidence yet because the current FFmpeg adapter is step-held and visibly jumps at crop keyframes;
2. the current Sparse-LK evidence path cannot reacquire after loss;
3. a MediaPipe detector + deterministic Sparse-LK reseed candidate does reacquire the originally seeded person deterministically;
4. the successful real reacquisition gap is 2.863 s, which exceeds the current 1 s lost-hold contract and exposes a separate long-loss/recovery semantic gap.

Do not conflate these layers.

## Architectural constraint

CAP-07 remains authoritative:

```text
Spatial evidence provider → tracked/semantic observations
SpatialComposer           → executable spatial decision
SpatialTransformPlan      → execution truth
Renderer/FFmpeg           → execute only
```

A detector/tracker may improve observations and recovery, but it may not become crop authority.

Renderer may not invent interpolation or smoothing not represented by the canonical spatial decision.

## Current Sparse-LK baseline

Rights-attested clip:

`example/r0_11_product_probe/input/moving_occlusion1_landscape.mp4`

Authoritative range:

`[0, 563298/90000)`

Observed baseline:

- seed `(0.76, 0.38, 0.13, 0.44)`;
- 29 available + 1 lost observation;
- first loss `29/30 s`;
- reason `insufficient_support`;
- no reacquisition.

Status:

`BASELINE_RECOVERY_FAILURE`

## Candidate A — YOLOX-Nano + ByteTrack

Benchmark evidence:

- YOLOX revision `6ddff4824372906469a7fae2dc3206c7aa4bbaee`;
- ByteTrack revision `d1bf0191adff59bc8fcfeaa0b33d3d1642552a99`;
- model `yolox_nano.onnx`;
- size 3,659,407 bytes;
- SHA-256 `C789161ED43C8269FCD4E67C67EEEB4E80C622DA2EB296A20BC6007BD18A0B7D`;
- ONNX Runtime 1.23.2 CPU;
- OpenCV 4.13.0;
- NumPy 2.3.5;
- six deterministic runs across two association thresholds;
- 52 available / 136 lost;
- first loss 1.731 s;
- no reacquisition of original target ID 1;
- reappearing intended person became ID 2;
- approximately 17–21 FPS;
- peak RSS approximately 150 MB.

Interpretation:

The detector/association path is operationally faster than Candidate B on this machine, but its current identity semantics fail the actual product requirement: the original intended focus subject must survive temporary loss/reappearance as the same grounded subject.

Status:

`TECHNICALLY_INSUFFICIENT — IDENTITY_CONTINUITY_FAILURE`

Do not integrate Candidate A as the default merely because it is faster.

## Candidate B — MediaPipe Object Detector + deterministic Sparse-LK reseed

Benchmark evidence:

- MediaPipe 0.10.31;
- OpenCV 4.13.0;
- NumPy 2.5.2;
- model `efficientdet_lite0.tflite`;
- size 4,602,795 bytes;
- SHA-256 `0720BF247BD76E6594EA28FA9C6F7C5242BE774818997DBBEFFC4DA460C723BB`;
- three independent runs produced identical observation signatures;
- 96 available / 92 explicitly lost observations;
- main real occlusion loss 1.565 s;
- recovery 4.428 s;
- latency 2.863 s;
- additional short gaps recovered at 1.432 s and 5.793 s;
- local identity contact-sheet inspection confirmed recovery of the originally seeded person without observed switching;
- lost frames contain no geometry;
- approximately 6.25–9.18 FPS;
- peak RSS approximately 127 MB;
- isolated environment approximately 183 MB.

Interpretation:

Candidate B demonstrates the missing functional mechanism: detector-assisted deterministic reacquisition/reseed can recover the same intended subject while preserving explicit lost observations.

Status:

`RECOVERY_CANDIDATE_TECHNICALLY_READY_LICENSE_PENDING`

## Model/runtime licensing state

Verified release facts remain deliberately separated:

- MediaPipe runtime/source project is Apache-2.0;
- the exact downloaded EfficientDet-Lite0 model artifact used in the benchmark is recorded by filename and SHA-256 above;
- exact redistribution/commercial terms for that exact downloaded artifact were not independently established during the benchmark;
- therefore no bundled-model release approval is claimed.

The Product Owner has stated willingness to open-source the project. This removes the former assumption that the product must remain proprietary, but it does not itself choose a software license.

Current repository state:

- no root `LICENSE` file;
- no project license declaration in `pyproject.toml`.

Therefore public visibility must not be treated as an already-selected open-source license.

Ultralytics/AGPL-family options may be reconsidered later only after an explicit repository-license strategy decision. They are not needed to complete the current Candidate-B integration review.

## Human Gate feedback on movement preview

The user reports:

- center crop behaves like ordinary static editing and loses the moving person for part of the clip;
- raw visibly jumps;
- stabilized visibly jumps as well, though playback itself is smooth.

The current FFmpeg adapter is `ffmpeg-spatial-transform-plan-step-v1`: it holds crop coordinates until the next keyframe and then changes them discretely.

Therefore this Human Gate is classified:

`HUMAN_GATE_INVALID — STEP_HELD_PREVIEW_EXECUTION`

This is not evidence to retune SpatialComposer dead-zone/velocity constants.

## Long-loss/reacquisition contract gap

Current path policy:

- short lost hold limit = 1 s;
- Composer returns unresolved once an observed loss exceeds that bound.

Candidate B's real reacquisition arrives after 2.863 s.

Therefore the next implementation must explicitly separate:

- short ordinary lost hold;
- bounded extended recovery wait/fallback;
- successful later reacquisition;
- terminal unresolved state.

No focus geometry may be invented during the lost interval.

A bounded recovery wait may keep a legal last/fallback crop, but that behavior must be explicit in the canonical decision/QC rather than a hidden extension of the existing 1 s rule.

## Next engineering order

1. Add explicit canonical interpolation semantics to the spatial plan/decision layer.
2. Make FFmpeg execute the canonical interpolation instead of step-held jumps for tracked paths.
3. Keep static/hold semantics explicit.
4. Integrate the smallest provider-neutral Candidate-B recovery path without making detector boxes crop authority.
5. Add explicit extended-loss/reacquisition state/QC based on real Product Probe evidence.
6. Rerun full Quality Gate.
7. Regenerate movement A/B/C on the same movement range.
8. Generate occlusion A/B/C on the same occlusion range.
9. Stop for Human Gate.

Do not tune motion constants merely to compensate for the prior step-held renderer.
