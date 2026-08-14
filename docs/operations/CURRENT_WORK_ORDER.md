# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.11 — tracker recovery provider benchmark + movement Human Gate  
**Updated:** 2026-08-14

## Accepted R0.11 implementation

Accepted spatial foundation:

- `ad4f47e5f659e108d34593675bc08177a2c2aff4` — deterministic motion-stability baseline;
- `66fc889094dd46dd51d5ccf028869c37658f648b` — canonical `SpatialTransformPlan` → deterministic FFmpeg execution adapter.

Current spatial invariants remain unchanged:

- canonical half-open source-time ranges;
- spatial evidence providers produce observations only;
- `SpatialComposer` owns executable crop/path decisions;
- `SpatialPathPolicy(version=r0.11-stability-candidate-v1)` remains 12 px dead zone, 800 px/s per-axis center velocity, 1 s maximum lost hold, redundant-keyframe suppression;
- lost observations do not fabricate geometry;
- mandatory-focus containment outranks motion limiting;
- `SpatialTransformPlan` remains execution truth;
- Renderer/FFmpeg executes canonical plans only.

Remote `ci/quality-gate-diagnostic` is green at `66fc889`.

## Real Product Probe result

Replacement landscape media passed the 9:16 crop-latitude gate.

### Movement-only clip — usable Product Probe evidence

`moving_occlusion2_landscape.mp4`

Authoritative range:

`[7/10, 13/5)`

Reported evidence:

- 41 tracking observations: 40 available + one `target_exit`;
- CENTER: 1 keyframe;
- RAW: 41 keyframes, containment 40/40, maximum velocity 240 px/s;
- STABILIZED: 14 keyframes, containment 40/40, maximum velocity 195 px/s, 27 redundant keyframes suppressed;
- RAW/STABILIZED each held the final loss for one frame (~0.0333 s);
- generated previews are 540×960, 30 FPS, 1.9 s, H.264/AAC;
- no source-bound/aspect violation and no detected black intervals.

This evidence is now ready for Human Gate. Do not discard or rerun it merely because the occlusion clip failed.

## Movement Human Gate

The user should compare the three local previews already generated for `moving_occlusion2_landscape`:

- center;
- raw;
- stabilized.

Ask only:

- best overall framing: `center / raw / stabilized / tie`;
- stabilized feel: `natural / jittery / chasing / laggy`;
- obvious defect: `none / clipped subject / abrupt jump / wrong focus / excessive chase / excessive lag / other`.

Human-visible judgment is product authority. QC metrics are supporting evidence.

## Occlusion clip — tracker capability blocker

`moving_occlusion1_landscape.mp4`

Authoritative range:

`[0, 563298/90000)`

Current Sparse-LK evidence path lost support at relative `29/30` s and did not reacquire. Therefore it could not reach/evaluate the later intended real occlusion/recovery event.

Classification:

`TRACKER_RECOVERY_BLOCKED`

This does not establish a `SpatialComposer` defect and does not authorize spatial-policy retuning.

## Current engineering objective

Run one bounded **tracker recovery provider benchmark** against the same rights-attested occlusion clip and exact source range.

Read:

- `docs/capabilities/CAP-07_SPATIAL_COMPOSITION_AUTO_REFRAME.md`;
- `docs/research/R0_11_TRACKER_RECOVERY_PROVIDER_BENCHMARK_2026-08-14.md`.

The benchmark is tracking-evidence work only. Do not render new A/B/C spatial previews until a recovery candidate has demonstrated materially better observations.

## Candidate order

### Candidate A — primary

`YOLOX-Nano detector + ByteTrack association`

Benchmark locally first.

Requirements:

- preserve provider neutrality behind the existing evidence boundary;
- detector/tracker boxes are observations only;
- prefer ONNX/CPU execution for this benchmark;
- record exact runtime packages/versions;
- record exact detector model/checkpoint/ONNX source and SHA-256;
- do not infer model artifact licensing solely from the code repository license;
- do not permanently add the provider/dependency/model to product defaults in this benchmark batch.

### Candidate B — secondary only if A is insufficient

`MediaPipe Object Detector + deterministic reseed of the existing local tracker`

Use only if Candidate A materially fails recovery, identity continuity, CPU/runtime or dependency criteria.

Runtime license alone is not model-artifact approval. Record the exact model artifact and applicable terms separately.

### Candidate C — deferred

SAM 2 remains a stronger/heavier GPU-tier option and is not part of the first recovery benchmark unless A/B are materially insufficient.

Ultralytics YOLO is excluded from the default candidate path unless the product's commercial/open-source licensing strategy explicitly changes.

## Recovery benchmark metrics

For the exact occlusion clip/range measure at minimum:

- first-loss time;
- whether reacquisition occurs after the visible occlusion;
- reacquisition latency;
- target identity continuity / obvious wrong-subject switch;
- available/lost observation count;
- recovered geometry quality;
- deterministic repeatability across repeated runs;
- CPU wall-clock runtime / effective processing rate;
- package/model footprint;
- code/runtime/model/transitive license record completeness.

The success criterion is not generic detector mAP. It is whether the intended focus subject can be recovered well enough for `SpatialComposer` to resume canonical spatial decisions without fabricated geometry or wrong-subject switching.

## Benchmark workflow

1. `git status → fetch → main → pull --ff-only → clean`.
2. Keep the private media under `example/` untracked.
3. Use local/private benchmark scripts/output where possible; do not pollute permanent product dependencies during comparison.
4. Benchmark Candidate A on the exact source range.
5. Repeat enough to confirm deterministic/operational behavior.
6. If A is materially insufficient, benchmark B under the same evidence contract.
7. Do not auto-integrate a winner. Stop and report evidence to ChatGPT for the release/provider decision.
8. Do not change `SpatialComposer`, `SpatialPathPolicy`, crop constants or FFmpeg spatial authority.

## Final benchmark classification

Use one:

- `RECOVERY_CANDIDATE_READY_FOR_INTEGRATION` — at least one candidate materially recovers the intended subject and has no unresolved release-blocking license/runtime contradiction;
- `RECOVERY_CANDIDATE_TECHNICALLY_READY_LICENSE_PENDING` — recovery succeeds but exact model/runtime terms are not yet sufficiently recorded for release approval;
- `RECOVERY_BENCHMARK_INCONCLUSIVE` — tested candidates do not reliably recover the intended subject;
- `RECOVERY_BENCHMARK_BLOCKED` — required local runtime/model acquisition or evidence mechanism is unavailable.

## Explicitly not allowed

- no dead-zone / velocity / loss-gap retuning;
- no change to canonical spatial authority;
- no manual crop-path rescue;
- no generative outpainting/uncrop;
- no R0.12 proxy/cache work;
- no audio-provider work;
- no permanent new provider adoption before benchmark review;
- no R0.11 closure before movement Human Gate plus successful occlusion/recovery Product Probe.
