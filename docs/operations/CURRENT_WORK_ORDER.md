# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.11 — analyzed-range hardening + deterministic motion-stability baseline  
**Updated:** 2026-08-14

## Accepted baseline

Current accepted R0.11 implementation baseline:

`3ea89a51354fd3df62eed82e7959201969ec8b57` — `feat: add deterministic spatial track paths`

Remote review confirmed:

- the three prior contract repairs are present: selection-end manual locks reject, protected regions fail closed, unsupported framing styles fail closed;
- `SpatialEvidenceTrack` / `SpatialFocusObservation` reuse R0.8 tracking proposals and canonical source time;
- `track` mode produces source-time crop keyframes through `SpatialComposer` authority;
- lost observations contain no geometry and use explicit hold-last-legal-crop mechanism behavior;
- manual locks remain exact crop constraints;
- Shot cuts reset track state;
- `ReframeDecision` legacy keyframes are validated as a view derived from canonical `SpatialTransformPlan`;
- Engineering Probe `17/17 PASS`;
- focused tests reported `33 passed`;
- full pytest reported `471 passed`;
- remote `ci/quality-gate-diagnostic` is green;
- no new detector/model dependency was added.

## Repair first: analyzed-source-range half-open truth

`MediaTimeRange` is canonical half-open `[start, end)`.

Current converter behavior still permits an observation exactly at `SeededTrackingProposal.analyzed_source_range.end` because the guard uses `> end` instead of `>= end`.

This must be repaired before motion-policy expansion.

Requirements:

1. `tracking_proposal_to_spatial_track()` must reject any observation outside `[analyzed_start, analyzed_end)`, including exact end.
2. `SpatialEvidenceTrack.__post_init__` must independently validate every observation against its own `analyzed_source_range`; direct construction may not bypass the invariant.
3. Add regressions for exact analyzed end, before-start time and direct invalid `SpatialEvidenceTrack` construction.
4. Preserve the existing valid mapping `source_time = analyzed_start + relative_time`; do not create a second timestamp authority.

Do not create a micro-phase for this repair.

## Coherent feature boundary after repair

The current raw track path legally follows every available tracking observation. That proves mechanism, but it is intentionally not yet a natural camera policy.

Build the smallest deterministic, versioned motion-stability layer needed before Product Probe work.

### Policy ownership

Keep policy inside the `SpatialComposer` decision boundary. Tracker/provider outputs remain observations only.

Introduce a provider-neutral policy/config value contract if useful. Parameters must be inspectable and versioned.

Candidate mechanism dimensions include:

- center dead-zone / hysteresis so tiny detector noise does not move the crop;
- maximum crop-center velocity per source-time unit;
- optional acceleration/change-rate limiting if it remains simple and deterministic;
- explicit maximum tracking-loss hold gap before unresolved/fallback;
- sparse-keyframe suppression when two consecutive legal crops are materially identical;
- source-edge pressure / focus containment checks.

Numeric defaults, if required for a reference mechanism, must be labeled uncalibrated candidates. Do not describe them as product-optimal.

### Required semantics

1. Stabilization starts from canonical legal crop candidates; it cannot make an illegal crop legal by approximation.
2. Every output keyframe remains inside source bounds, preserves exact target aspect ratio and lies inside both the authoritative analyzed range and resolved selection range.
3. Manual crop locks are hard constraints and must survive stabilization bit-for-bit.
4. Stabilization is Shot-local. No state crosses a hard Shot cut.
5. A lost observation never invents focus geometry.
6. Holding the last legal crop is allowed only under an explicit versioned gap policy. Once the policy says the gap is too long, return unresolved/fallback/warning instead of pretending tracking is still valid.
7. If a focus moves faster than the motion limit, deterministic motion limiting may lag the focus only while mandatory focus containment remains valid; otherwise widen/fallback/unresolved according to current non-generative policy. Do not silently crop out a mandatory subject.
8. Keep `SpatialTransformPlan` as execution truth; any legacy view derives from it.

## Spatial QC / engineering evidence

Add inspectable mechanism metrics or helpers sufficient to measure at least:

- mandatory-focus containment/visible fraction where representable;
- source-bound violations;
- target-aspect violations;
- crop-center displacement / velocity;
- abrupt direction changes or a simple jitter metric;
- number/duration of held-lost spans;
- number of suppressed/redundant keyframes;
- unresolved/fallback reason.

Add deterministic regression/probe coverage for at least:

- exact analyzed-end observation rejected;
- direct out-of-range `SpatialEvidenceTrack` rejected;
- small observation jitter stays inside the dead zone and does not cause crop chatter;
- a real movement sequence still moves the crop rather than freezing it;
- velocity limiting is deterministic and does not violate mandatory focus containment;
- short lost span follows the explicit hold policy;
- over-limit lost span fails closed/unresolved;
- manual locked keyframe remains unchanged after stabilization;
- hard Shot cut resets stabilization state;
- equivalent input ordering produces the same plan;
- all resulting keyframes are legal and legacy/canonical views cannot diverge.

The bounded Engineering Probe may use deterministic fixtures. Synthetic fixtures are mechanism evidence only.

## Product Probe readiness

Do not claim a Product Probe from synthetic geometry.

After the stabilization mechanism is green, prepare the smallest real-media Product Probe path needed to compare:

```text
center crop
vs
simple raw tracker/chasing path
vs
current stabilized SpatialComposer path
```

Useful real cases include:

- single moving person/product;
- handheld camera motion;
- short occlusion/loss;
- subject near source edge;
- genuinely impossible 9:16 fit.

A Product Probe preview/executor must consume the canonical `SpatialTransformPlan`; it may not recompute editorial crop choices in FFmpeg/Renderer code.

If the current local private corpus does not contain a materially useful moving/occlusion case, report `NEEDS_REAL_PRODUCT_PROBE_MEDIA` rather than manufacturing synthetic Product Probe success.

## Explicitly not in this batch

- no YOLO/MediaPipe/SAM2/new detector dependency merely to improve appearance;
- no provider benchmark winner or license commitment yet;
- no claim that mechanism constants are product-calibrated;
- no synthetic Product Probe acceptance;
- no generative outpainting/uncrop;
- no Renderer-owned crop decisions;
- no R0.12 preview/proxy/cache implementation;
- no audio-provider implementation from the future backlog.

## Stop conditions

Stop and report instead of inventing semantics if:

- enforcing analyzed-range truth requires changing canonical MediaTime semantics;
- stabilization would require violating mandatory-focus constraints without an existing fallback policy;
- a Product Probe executor would need Renderer to recreate crop decisions rather than consume `SpatialTransformPlan`;
- a new top-level Domain Entity or Architecture Contract change becomes necessary;
- a new external dependency becomes necessary and its transitive code/model/runtime licensing is unresolved.

Otherwise complete one coherent green batch, commit/push, and report:

- starting/ending HEAD;
- analyzed-range repair and regressions;
- introduced/reused policy/QC types;
- exact dead-zone / velocity / loss-gap mechanism semantics and versioning;
- Engineering Probe results;
- full Quality Gate;
- Product Probe readiness classification (`READY_FOR_REAL_PRODUCT_PROBE` or `NEEDS_REAL_PRODUCT_PROBE_MEDIA`).

Do not close R0.11 and do not begin R0.12.
