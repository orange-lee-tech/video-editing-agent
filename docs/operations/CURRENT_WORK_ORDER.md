# Current Work Order

**Status:** WAITING_HUMAN  
**Phase:** R0.11 — real Auto Reframe Product Probe media gate  
**Updated:** 2026-08-14

## Accepted implementation baseline

`ad4f47e5f659e108d34593675bc08177a2c2aff4` — `feat: stabilize deterministic spatial track paths`

The current engineering foundation is accepted for real-media evaluation.

Verified baseline:

- analyzed-source observation legality is half-open `[start, end)` in both converter and `SpatialEvidenceTrack` value contract;
- explicit versioned `SpatialPathPolicy` owns dead-zone, velocity-limit, lost-hold and redundant-keyframe behavior inside `SpatialComposer`;
- current candidate values are 12 px dead zone, 800 px/s per-axis center velocity, 1 s maximum lost hold and redundant-keyframe suppression;
- these values are mechanism candidates, not product-calibrated truth;
- manual locks are hard constraints;
- lost observations never fabricate focus geometry;
- mandatory focus containment outranks velocity limiting; unsafe lag fails closed;
- path state is Shot-local;
- `SpatialTransformPlan` remains execution truth;
- `SpatialPathQc` provides inspectable mechanism metrics;
- Engineering Probe reported `26/26 PASS`;
- full pytest reported `475 passed` and the remaining Quality Gate checks were green;
- remote `ci/quality-gate-diagnostic` is green;
- no new detector/model/provider dependency was introduced.

## Why work is paused

The current private corpus does not contain a verified real case that simultaneously exercises meaningful subject movement and tracking occlusion. Camera motion and hand/object interaction alone are not sufficient Product Probe evidence.

Do not invent another synthetic Product Probe and do not continue tuning numeric policy constants without human-viewable real evidence.

## Human input required

Provide at least one rights-attested local video clip suitable for Auto Reframe evaluation.

A useful minimal clip is:

- one continuous Shot, preferably roughly 8–30 seconds;
- a clearly trackable person or product that genuinely moves across the frame;
- at least one brief real occlusion / temporary tracking loss, or a comparable moment where the subject disappears behind another object/person;
- ordinary handheld or fixed-camera footage is acceptable;
- edge-of-frame movement is useful but not mandatory;
- 1080p or higher is convenient but not a constitutional requirement.

Prefer footage owned by the user or otherwise clearly authorized for this private Product Probe.

Recommended local untracked location:

`example/r0_11_product_probe/input/`

The `example/` material must remain local/private and untracked.

## Work to execute once real media exists

Use the actual supplied media and complete one bounded R0.11 Product Probe.

1. Inspect source technical metadata and choose one exact authoritative source range; do not silently alter it between variants.
2. Reuse the existing R0.8 seeded tracking path to create grounded observations. If the existing tracker cannot materially track the supplied case, report that evidence honestly rather than silently switching providers.
3. Produce three comparable canonical spatial decisions/plans:

```text
A — center/static crop baseline
B — raw/simple grounded tracking path
C — stabilized SpatialComposer path
```

4. All variants must use the same source range, output canvas/aspect ratio and source footage.
5. Variant B may use an explicit neutralized/no-stabilization path policy or equivalent deterministic baseline, but tracker rectangles still may not become Renderer-owned crop authority.
6. Variant C must use the current explicit versioned stabilization policy.
7. Build/render previews by consuming canonical `SpatialTransformPlan`; FFmpeg/Renderer may not recompute editorial crop choices.
8. Save inspectable comparison metadata and `SpatialPathQc` beside the previews.
9. Preserve source hashes; no source mutation.
10. Do not claim Product Probe success before Human Gate review.

## Human Gate after previews

Ask only for simple product judgments, not an expert scoring worksheet.

At minimum:

- Which framing feels best overall: center / raw / stabilized / tie?
- Does stabilized framing feel natural or noticeably laggy/jittery?
- During the occlusion, is the hold/recovery acceptable?
- Any obvious defect: subject clipped, abrupt jump, wrong focus, excessive chasing, excessive lag, or other visible problem?

Human disagreement with a mechanism metric is valid product evidence and is not automatically an engineering failure.

## If the real probe exposes a defect

Keep R0.11 open and issue one bounded repair based on the observed failure. Tune dead-zone / velocity / loss-gap values only against real evidence and record the before/after comparison.

If the existing seeded tracker itself is the material blocker, move to the already-planned provider benchmark/license gate instead of hiding the weakness in `SpatialComposer`.

## Explicitly not allowed while waiting

- no speculative dead-zone / velocity / gap retuning;
- no YOLO/MediaPipe/SAM2/new detector merely to keep coding;
- no external provider/license commitment;
- no synthetic Product Probe acceptance;
- no generative outpainting/uncrop;
- no Renderer-owned crop authority;
- no R0.12 preview/proxy/cache implementation;
- no audio-provider integration or scraping.

Do not close R0.11 and do not begin R0.12 until the real Product Probe and Human Gate are complete.
