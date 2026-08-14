# R0.11 Tracker Recovery Provider Benchmark — 2026-08-14

## Context

The first valid non-9:16 Product Probe produced a partial result at:

`66fc889094dd46dd51d5ccf028869c37658f648b` — `feat: execute canonical spatial plans in ffmpeg`

Observed local Product Probe evidence reported by Codex:

- `moving_occlusion2_landscape.mp4` successfully produced comparable center/raw/stabilized 9:16 previews;
- raw tracking produced 41 keyframes while stabilized tracking produced 14 keyframes with 27 redundant keyframes suppressed;
- both raw and stabilized retained mandatory-focus containment for all 40 available observations;
- the canonical `SpatialTransformPlan` → FFmpeg executor produced valid 540×960 previews;
- `moving_occlusion1_landscape.mp4` failed before the intended occlusion/recovery event because the current Sparse-LK evidence path lost support at relative `29/30` s and did not reacquire;
- therefore the remaining blocker is tracker recovery/reacquisition capability, not `SpatialComposer` motion stability.

Do not retune R0.11 crop-path policy while solving this tracker problem.

## Architectural constraint

CAP-07 remains authoritative:

```text
Spatial evidence provider → tracked/semantic observations
SpatialComposer           → executable spatial decision
SpatialTransformPlan      → execution truth
Renderer/FFmpeg           → execute only
```

A replacement detector/tracker may improve observations and recovery, but it may not become crop authority.

## Candidate A — YOLOX-Nano + ByteTrack

Preferred first benchmark candidate.

Why:

- YOLOX official project license: Apache-2.0;
- ByteTrack official project license: MIT;
- ByteTrack is explicitly detector-driven and intended to associate detection boxes across video;
- both projects document ONNX / ONNX Runtime deployment paths;
- ONNX Runtime itself is MIT and supports a default CPU execution provider;
- detector-every-frame + association directly addresses the current Sparse-LK no-reacquisition failure mode;
- YOLOX-Nano is a plausible CPU/local Tier-1 candidate without adopting Ultralytics licensing.

Release gate:

- record the exact detector model/checkpoint/ONNX artifact source and SHA-256;
- do not infer model-weight terms only from the code repository license;
- record notices/transitive dependencies before release approval.

Status: `PRIMARY_BENCHMARK_CANDIDATE / NOT_YET_APPROVED_FOR_RELEASE`.

## Candidate B — MediaPipe Object Detector + deterministic Sparse-LK reseed

Secondary benchmark candidate.

Why:

- MediaPipe runtime/project license: Apache-2.0;
- official Google AI Edge documentation provides CPU-oriented Object Detector task support and EfficientDet-Lite / SSD MobileNet model families;
- a detector can be used only when the current local track is lost, then deterministically reseed the existing evidence path;
- this may preserve a lighter architecture than replacing the entire tracker.

Release gate:

- runtime license does not automatically prove the exact downloaded model bundle terms;
- record exact model artifact, source, hash and applicable terms before release approval;
- do not approve a model merely because MediaPipe code is Apache-2.0.

Status: `SECONDARY_BENCHMARK_CANDIDATE / MODEL_ARTIFACT_TERMS_REQUIRED`.

## Candidate C — SAM 2

Deferred Tier-2 candidate, not the first CPU benchmark.

- official SAM 2 code and model checkpoints are Apache-2.0;
- designed for image/video segmentation and can maintain prompted objects across video;
- default package stack is materially heavier and oriented toward PyTorch/CUDA-class execution;
- useful later for stronger segmentation/tracking/grounding, but unnecessary as the first recovery repair for the current product gate.

Status: `DEFERRED_GPU_TIER`.

## Explicit default exclusion — Ultralytics YOLO

Do not adopt Ultralytics YOLO into the default proprietary/commercial path without an explicit commercial-license decision.

Current Ultralytics licensing states that AGPL-3.0 is the open-source path and Enterprise licensing is required for proprietary/private commercial deployment without opening the larger project under AGPL-3.0.

Status: `EXCLUDED_FROM_DEFAULT_BENCHMARK_UNLESS_LICENSE_STRATEGY_CHANGES`.

## Benchmark scope

Use the already rights-attested local occlusion clip:

`example/r0_11_product_probe/input/moving_occlusion1_landscape.mp4`

Use the same authoritative source range previously selected:

`[0, 563298/90000)`

The benchmark is tracking-evidence only. Do not change spatial policy or rendering behavior.

Measure at minimum:

- first-loss time;
- whether reacquisition occurs after the visible occlusion;
- reacquisition latency;
- target identity continuity / obvious ID switch;
- available/lost observation count;
- recovered subject geometry quality;
- CPU runtime on the current machine;
- dependency/model footprint;
- deterministic repeatability;
- license/model-artifact completeness.

The primary success criterion is not generic detector mAP. It is whether the provider can recover the intended subject sufficiently well for `SpatialComposer` to resume its canonical path without fabricated geometry or wrong-subject switching.

## Execution order

1. Benchmark Candidate A locally first.
2. If Candidate A cannot recover the intended subject acceptably or has unacceptable CPU/runtime/dependency cost, benchmark Candidate B.
3. Do not benchmark Candidate C unless A/B are materially insufficient.
4. Do not permanently integrate a candidate merely because it runs.
5. Preserve provider neutrality behind the existing evidence boundary.
6. Final provider adoption requires benchmark evidence + transitive code/model/runtime license record.

## Product interaction

The successful movement-only Product Probe is independent evidence and should proceed to Human Gate now.

Tracker recovery work must not invalidate or delay the user's comparison of:

- center;
- raw;
- stabilized

for `moving_occlusion2_landscape.mp4`.
