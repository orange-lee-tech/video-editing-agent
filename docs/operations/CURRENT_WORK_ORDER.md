# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.11 — interpolation-correct spatial preview + tracker recovery integration candidate  
**Updated:** 2026-08-14

## Accepted engineering baselines

- `ad4f47e5f659e108d34593675bc08177a2c2aff4` — deterministic motion-stability baseline.
- `66fc889094dd46dd51d5ccf028869c37658f648b` — canonical `SpatialTransformPlan` → FFmpeg execution adapter foundation.

Core invariants remain:

- spatial evidence providers produce observations only;
- `SpatialComposer` owns executable spatial decisions;
- `SpatialTransformPlan` is execution truth;
- Renderer/FFmpeg executes canonical decisions and may not invent crop/tracking/smoothing policy;
- lost observations contain no fabricated geometry;
- manual locks outrank automatic solve;
- source time remains canonical half-open `[start, end)`.

## Human Gate result — movement preview is NOT valid acceptance evidence yet

The user watched the existing `moving_occlusion2_landscape` center/raw/stabilized previews and reported:

- CENTER behaves like ordinary static center crop and sometimes leaves the person outside frame;
- RAW visibly jumps;
- STABILIZED also visibly jumps, despite otherwise smooth video playback.

CENTER behavior is the intended static baseline and is not a defect by itself.

However the RAW/STABILIZED Human Gate is **invalidated by the current preview execution semantics**, because `src/video_editing_agent/render/spatial_plan_ffmpeg.py` compiles crop keyframes as step-held `if(gte(t,...))` jumps. The current adapter therefore injects discrete crop jumps at canonical keyframes.

Do not interpret the user's report as evidence that `SpatialComposer` smoothing constants are wrong until a canonical interpolation-aware preview is rendered.

Classification of the previous movement Human Gate:

`HUMAN_GATE_INVALID — STEP_HELD_PREVIEW_EXECUTION`

## Tracker recovery benchmark result

The provider benchmark completed with no tracked implementation changes.

### Baseline Sparse-LK

- seed `(0.76, 0.38, 0.13, 0.44)`;
- 29 available + 1 lost observation;
- first loss `29/30 s`;
- reason `insufficient_support`;
- no reacquisition.

### Candidate A — YOLOX-Nano + ByteTrack

- YOLOX revision `6ddff4824372906469a7fae2dc3206c7aa4bbaee`;
- ByteTrack revision `d1bf0191adff59bc8fcfeaa0b33d3d1642552a99`;
- `yolox_nano.onnx`, SHA-256 `C789161ED43C8269FCD4E67C67EEEB4E80C622DA2EB296A20BC6007BD18A0B7D`;
- ONNX Runtime 1.23.2 CPU;
- six deterministic runs across two association thresholds;
- 52 available / 136 lost;
- first loss 1.731 s;
- no reacquisition of original target ID; reappearing person became ID 2;
- approximately 17–21 FPS, peak RSS approximately 150 MB.

Result:

`TECHNICALLY_INSUFFICIENT — IDENTITY_CONTINUITY_FAILURE`

### Candidate B — MediaPipe Object Detector + deterministic Sparse-LK reseed

- MediaPipe 0.10.31;
- `efficientdet_lite0.tflite`, SHA-256 `0720BF247BD76E6594EA28FA9C6F7C5242BE774818997DBBEFFC4DA460C723BB`;
- three runs with identical observation signatures;
- 96 available / 92 explicitly lost observations;
- main real occlusion: loss 1.565 s, recovery 4.428 s, latency 2.863 s;
- additional short gaps recovered at 1.432 s and 5.793 s;
- local identity contact-sheet inspection confirmed recovery of the originally seeded person without switching;
- lost frames contain no geometry;
- approximately 6.25–9.18 FPS, peak RSS approximately 127 MB;
- isolated environment approximately 183 MB.

Result:

`RECOVERY_CANDIDATE_TECHNICALLY_READY_LICENSE_PENDING`

Candidate B is the current technical recovery candidate. Do not silently replace the provider until the integration and licensing gates below are satisfied.

## Important second blocker — long-loss semantics

The current `SpatialPathPolicy(version=r0.11-stability-candidate-v1)` has `max_lost_hold_gap = 1 s` and current `DeterministicSpatialComposer._track()` returns unresolved once an observed lost gap exceeds that value.

The real MediaPipe recovery gap is 2.863 s, so merely integrating the recovery provider is insufficient: the current Composer would fail closed before recovery arrives.

Do **not** solve this by fabricating geometry or hiding lost observations.

The next implementation must make long-loss/reacquisition semantics explicit. Preferred minimal direction:

- retain the existing 1 s short-loss hold behavior;
- distinguish an extended `recovery_wait` / equivalent state from normal short hold;
- continue emitting only legal held/fallback crop decisions, never invented focus geometry;
- permit a bounded later reacquisition window derived from real Product Probe evidence;
- record extended-loss duration/recovery in `SpatialPathQc`;
- fail closed if the explicit recovery window is exceeded or reacquisition cannot safely resume;
- do not silently reinterpret `max_lost_hold_gap` as an unlimited hold.

The exact recovery-window candidate is engineering work and remains Product-Probe calibrated, not constitutional truth.

## Implementation objective A — canonical interpolation semantics

The current step-held preview adapter must be repaired before another Human Gate.

Important authority rule:

**Renderer may not invent interpolation.**

If the canonical plan does not currently carry enough interpolation semantics, extend the canonical Application artifact minimally so interpolation is explicit and owned upstream.

Expected direction:

- static/hold plans remain explicitly held/static;
- tracked crop paths carry an explicit deterministic interpolation mode;
- initial tracked candidate should use bounded piecewise linear interpolation unless existing contracts justify another deterministic mode;
- FFmpeg compiler consumes that mode exactly;
- no hidden easing/smoothing is invented by Renderer;
- same canonical path must reproduce deterministically;
- focused tests prove intermediate-time crop positions, exact keyframe positions, range boundaries and fail-closed unsupported modes.

After this repair, regenerate the movement clip center/raw/stabilized previews using the same source range and compare again. Do not retune 12 px / 800 px/s merely to compensate for the old step-held executor.

## Implementation objective B — recovery provider integration candidate

After or alongside interpolation repair, integrate the smallest provider-neutral path needed to reproduce Candidate B observations on the rights-attested occlusion clip.

Requirements:

- provider remains behind the existing tracking evidence port/boundary;
- detector output never becomes crop authority;
- deterministic reseed must preserve the original intended subject identity;
- lost frames remain `lost` with no geometry;
- exact provider/model/runtime versions and model SHA are recorded;
- model is not committed to Git history unless a separate release/model-distribution decision explicitly authorizes that;
- benchmark-only private artifacts remain under ignored locations.

Do not add YOLOX+ByteTrack as the default after its observed identity continuity failure.

## Licensing / open-source gate

The Product Owner explicitly stated willingness to open-source the project.

That changes the strategic constraint: an AGPL-compatible route may now be considered in future provider selection.

However, **do not change the repository license automatically**:

- current repository has no root `LICENSE` file;
- `pyproject.toml` currently declares no project license;
- public source visibility is not yet an explicit open-source license choice;
- adopting an AGPL dependency or relicensing the project is a separate Product Owner governance decision.

For the current MediaPipe candidate, exact model-artifact terms remain a release gate. Continue to distinguish runtime/source license from model artifact rights.

## Next Product Probe

Once objectives A and B plus explicit long-loss semantics are implemented and Quality Gate is green:

1. regenerate movement A/B/C on the exact existing movement source range;
2. generate occlusion A/B/C on the exact existing occlusion source range using the recovery-capable evidence path;
3. keep all variants fair: same source/range/canvas/frame-rate/audio treatment;
4. run technical QC;
5. stop for Human Gate.

Human Gate questions stay simple:

For movement:

- best overall: `center / raw / stabilized / tie`;
- stabilized feel: `natural / jittery / chasing / laggy`;
- obvious defect.

For occlusion:

- best overall;
- recovery: `acceptable / unacceptable`;
- obvious wrong-focus, jump, stale hold, excessive lag or clipping.

## Explicitly not allowed

- no R0.12 proxy/cache work;
- no audio-provider implementation;
- no generative outpainting/uncrop;
- no Renderer-owned interpolation/crop authority;
- no fabricated focus geometry during loss;
- no permanent model artifact commit before license/distribution approval;
- no R0.11 closure before corrected movement Human Gate and real occlusion/recovery Human Gate.
