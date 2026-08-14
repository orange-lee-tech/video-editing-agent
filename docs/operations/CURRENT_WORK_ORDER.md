# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.11 — real Auto Reframe Product Probe  
**Updated:** 2026-08-14

## Accepted implementation baseline

`ad4f47e5f659e108d34593675bc08177a2c2aff4` — `feat: stabilize deterministic spatial track paths`

The engineering foundation is accepted for real-media evaluation.

Verified baseline:

- analyzed-source observation legality is half-open `[start, end)` in both converter and `SpatialEvidenceTrack`;
- `SpatialPathPolicy(version=r0.11-stability-candidate-v1)` owns deterministic dead-zone, velocity-limit, lost-hold and redundant-keyframe behavior inside `SpatialComposer`;
- current mechanism candidates are 12 px dead zone, 800 px/s per-axis center velocity, 1 s maximum lost hold and redundant-keyframe suppression;
- these values are not yet product-calibrated truth;
- manual locks are hard constraints;
- lost observations never fabricate focus geometry;
- mandatory focus containment outranks velocity limiting;
- path state is Shot-local;
- `SpatialTransformPlan` remains execution truth;
- `SpatialPathQc` provides inspectable mechanism metrics;
- Engineering Probe reported `26/26 PASS`;
- full pytest reported `475 passed`; Ruff, mypy, import contracts, build and diff checks were green;
- remote `ci/quality-gate-diagnostic` is green;
- no new detector/model/provider dependency was introduced.

## Human-supplied Product Probe media

The user has placed two local private clips under:

`example/r0_11_product_probe/input/`

Declared stems / roles:

- `moving_occlusion1` — contains real occlusion;
- `moving_occlusion2` — moving subject without occlusion.

The user explicitly attested on 2026-08-14 that they have the right to use both clips for this project test.

These files must remain local/private and untracked. Do not copy them into tracked fixtures, Git history or GitHub artifacts.

## Product Probe objective

Run one bounded real-media comparison for both clips:

```text
same source clip / same authoritative source range / same output canvas
→ A — center/static crop
→ B — raw/simple grounded tracking path
→ C — stabilized SpatialComposer path
→ rendered previews + comparison metadata + SpatialPathQc
→ Human Gate
```

This batch is evidence generation, not algorithm retuning.

## Required execution

1. Start from current `origin/main`; confirm clean worktree before changes.
2. Discover the exact filenames/extensions matching `moving_occlusion1*` and `moving_occlusion2*` in `example/r0_11_product_probe/input/` rather than assuming an extension.
3. Compute and record source SHA-256 and technical metadata. Do not mutate the source files.
4. Choose an exact authoritative source range per clip based on the actual usable continuous Shot. The three variants for a given clip must use exactly the same range.
5. Use the same output canvas/aspect ratio for all variants; default target is the existing R0.11 vertical 9:16 canvas unless the source makes that impossible, in which case report rather than silently changing the benchmark.
6. Reuse the existing R0.8 seeded-tracking path to obtain grounded observations. Do not add or switch tracker/provider in this batch.
7. If the existing tracker cannot materially track either clip, stop that clip honestly as `TRACKER_BLOCKED`; do not manufacture observations.
8. Build three canonical spatial plans per usable clip:
   - **A center:** deterministic static/center baseline;
   - **B raw:** grounded tracking with stabilization neutralized or otherwise represented as an explicit deterministic simple-tracking baseline;
   - **C stabilized:** current `SpatialPathPolicy(version=r0.11-stability-candidate-v1)` unchanged.
9. Tracker/provider rectangles remain observations. Variant B and C executable crop coordinates must still be owned/validated by the spatial decision layer; Renderer/FFmpeg may not inherit crop authority.
10. Render each preview by consuming canonical `SpatialTransformPlan`. The preview/executor may translate the plan into FFmpeg commands but may not recompute editorial crop choices.
11. Generate six previews if both clips are usable:

```text
moving_occlusion1_center.mp4
moving_occlusion1_raw.mp4
moving_occlusion1_stabilized.mp4
moving_occlusion2_center.mp4
moving_occlusion2_raw.mp4
moving_occlusion2_stabilized.mp4
```

12. Save local comparison metadata beside the previews, including at least:
   - exact source filename, SHA-256 and source range;
   - output canvas;
   - tracker/provider identity + revision;
   - canonical plan identity;
   - path-policy identity for each variant;
   - `SpatialPathQc`;
   - tracking lost/occlusion observations;
   - render/QC result;
   - any unresolved/fallback reason.
13. Keep Product Probe output under `example/r0_11_product_probe/` and untracked/private.
14. Run focused R0.11 tests plus the full repository Quality Gate for any tracked harness/code changes.
15. Commit/push only reusable deterministic harness/test/code changes. Never commit source clips or rendered Product Probe media.

## Fairness requirements

- A/B/C for the same clip use the same decoded source and exact source range.
- Do not crop a harder/easier interval selectively between variants.
- Do not change stabilization parameters after seeing preview C in this batch.
- Do not manually rescue one variant with crop keyframes unless the same intervention is part of the explicit benchmark definition; normal benchmark should be fully automatic.
- Do not add subtitles/graphics/music or other presentation differences.
- Preserve source audio consistently or mute consistently across all three variants; audio must not bias the framing comparison.
- Do not label synthetic metrics or synthetic fixtures as Product Probe evidence.

## Clip-specific evidence expectations

### `moving_occlusion1`

Primary question: does the stabilized path behave acceptably through real occlusion/loss and recovery without abrupt jump, wrong focus, indefinite stale hold or fabricated tracking geometry?

Record the actual detected/tracked lost interval. Do not assume the human-visible occlusion necessarily produces tracker loss; if it does not, record that distinction.

### `moving_occlusion2`

Primary question: does stabilization reduce chasing/jitter while still following genuine subject movement without excessive lag or clipping?

This clip is particularly useful for comparing raw tracking against stabilized tracking without occlusion confounding the result.

## Product Probe completion state

After previews and metadata are produced, report:

- starting/ending HEAD;
- exact local source filenames discovered and SHA-256 prefixes;
- chosen source ranges;
- tracker/provider result for each clip;
- preview output paths;
- A/B/C plan and QC summary;
- render/QC status;
- focused/full Quality Gate status;
- any material blocker.

Then set classification to:

`READY_FOR_HUMAN_GATE`

only if the previews are genuinely comparable and technically valid.

Do not declare R0.11 PASS or close R0.11 before the user watches the previews.

## Human Gate

Ask only for simple judgments.

For each clip:

- best overall framing: `center / raw / stabilized / tie`;
- stabilized feel: `natural / jittery / chasing / laggy`;
- obvious defect: none, clipped subject, abrupt jump, wrong focus, excessive chase, excessive lag, other.

For `moving_occlusion1` additionally ask:

- occlusion/recovery: `acceptable / unacceptable`.

Human-visible preference is authoritative product evidence; mechanism metrics are supporting evidence only.

## If the Product Probe exposes a defect

Keep R0.11 open and make exactly one bounded repair based on the observed failure. Retune dead-zone / velocity / loss-gap only against the real before/after evidence.

If the seeded tracker itself is the material blocker, proceed to the already-planned provider benchmark/license gate instead of masking it inside `SpatialComposer`.

## Explicitly not allowed in this batch

- no speculative policy retuning before Human Gate;
- no new YOLO/MediaPipe/SAM2/detector/tracker;
- no external provider/license commitment;
- no synthetic Product Probe substitution;
- no generative outpainting/uncrop;
- no Renderer-owned crop authority;
- no R0.12 proxy/cache implementation;
- no audio-provider integration or scraping;
- no R0.11 closure before Human Gate.
