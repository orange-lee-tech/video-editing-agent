# Auto Reframe / Aspect-Ratio Composition — Survey V2 Closure Draft

**Status:** FOCUSED SURVEY PASS  
**Snapshot date:** 2026-08-11  
**Scope:** Resolved Visual Segment → Spatial Evidence → Reframe Intent → Smooth Crop/Scale Path → EDL Spatial Transform  
**Authority:** Informative research only; not an Architecture Contract.

---

## 1. Closure question

How should the product turn user-supplied footage into a different output aspect ratio such as 16:9 → 9:16 while preserving the important person/product/action, respecting text/safe zones, avoiding jitter and subject-switching, supporting ordinary CPU hardware, and never using generative outpainting as an ordinary fallback?

Current conclusion:

> **Treat Auto Reframe as a spatial editorial-resolution problem driven by tracked evidence and solved by a deterministic smooth camera/crop-path optimizer.**

Semantic/local perception tells the system what is important. A spatial composer turns that evidence into a bounded crop/scale trajectory. EDLBuilder commits the exact transform instructions. Renderer merely executes them.

This focused Survey Gate is sufficiently complete for Architecture Contract v0.2 and capability-spec design. Exact detector/tracker provider, path solver, crop penalties and thresholds remain benchmark decisions.

---

## 2. Auto Reframe is not “center crop” and not a Renderer feature

Naive behavior:

```text
output aspect ratio = 9:16
→ crop center of every source frame
```

fails whenever the important subject moves away from image center or several important elements occupy different parts of the source frame.

Auto Reframe requires editorial intent:

- which subject/product matters;
- whether one or several subjects must stay visible;
- desired headroom / look room / product visibility;
- whether motion should be followed or deliberately held;
- where subtitles / CTA / logos will occupy the output canvas;
- how much pan/zoom motion is stylistically acceptable.

Therefore the Renderer cannot own these decisions.

---

## 3. Constitution boundary: crop existing pixels only

Ordinary Auto Reframe may use deterministic operations such as:

- crop;
- scale;
- position;
- pan/zoom trajectory;
- deterministic padding / matte / blurred-background layout when explicitly allowed by style;
- static or deterministic graphic background/layout.

It must not silently use:

- generative outpainting;
- generative uncrop;
- synthesized background fill;
- object removal followed by generated pixels.

Historical AutoFlip discussions and other reframing systems may mention inpainting/deep uncrop. Those ideas are **neutralized** for this product’s normal path: the crop optimizer may borrow their problem formulation, but generative pixel completion is constitutionally unavailable unless a future explicit constitutional optional feature authorizes it.

---

## 4. Reframe inside visual continuity boundaries

Do not smooth a crop path across a hard Shot cut.

Preferred unit:

```text
Resolved visual selection
    ↓
committed Shot/source window
    ↓
spatial evidence within that continuous source range
    ↓
ReframeDecision
```

A hard edit cut is allowed to reset framing immediately because the source image itself changes.

Within one continuous visual segment, unnecessary crop jumps are penalized.

---

## 5. Reuse the TemporalEvidence system instead of creating a second perception stack

Auto Reframe should consume existing analysis where possible:

- Shot boundaries;
- tracked person/product ROI;
- face/pose/hand geometry;
- camera motion evidence;
- residual local motion;
- salient regions;
- product reveal / subject enter/exit anchors;
- VLM-labeled important subject when local evidence is ambiguous.

This avoids paying twice to understand the same footage.

Conceptually:

```text
TemporalEvidence / ShotAnalysis
        ↓
SpatialEvidenceView
        ↓
SpatialComposer
```

The reframer should not become a new global visual-understanding owner.

---

## 6. ReframeIntent should be structured

A future spatial intent may include:

```yaml
target_canvas: 1080x1920
required_subjects: [product]
preferred_subjects: [speaker]
framing: product_first
headroom_policy: natural
look_room_policy: preserve_when_possible
min_subject_visibility: ...
max_zoom: ...
max_pan_speed: ...
max_zoom_speed: ...
reserved_regions:
  - subtitle_safe_zone
  - cta_region
style_motion: restrained
manual_locks: [...]
```

This is not a frozen schema.

Intent comes from:

- output/platform profile;
- EditSlot / Director intent;
- CommercialSkill;
- overlay/subtitle layout;
- user/manual instructions.

---

## 7. Spatial evidence should be semantic but provider-neutral

Useful observation data per sampled/key time:

```text
entity_ref / track_ref
bbox / mask
confidence
semantic role
face / eyes / pose points
product importance
screen position
visible fraction
saliency support
camera motion
occlusion / track-loss risk
```

The SpatialComposer should not know whether a box came from:

- OpenCV tracking;
- MediaPipe;
- SAM2;
- a future permissively licensed detector;
- user keyframe;
- targeted cloud VLM localization.

This makes commercial-license problems replaceable rather than structural.

---

## 8. Google AutoFlip remains a foundational algorithm reference

AutoFlip’s architecture is highly aligned with the problem:

```text
shot analysis
→ salient-region detection / tracking
→ choose camera mode
→ optimize crop trajectory
→ output target aspect ratio
```

Useful ideas to absorb:

- reason per shot rather than over the whole movie indiscriminately;
- assign different importance to different detected entities;
- choose between stationary and moving virtual-camera behavior;
- smooth noisy detection boxes into a stable crop trajectory;
- if critical content cannot fit, use a non-generative layout fallback such as padding/letterbox instead of blindly cropping it away.

AutoFlip is primarily an **algorithm/architecture reference**, not a decision to revive its old MediaPipe pipeline as our production dependency.

---

## 9. Watch to Edit validates explicit crop-path optimization

The paper “Watch to Edit: Video Retargeting using Gaze” formulates retargeting as preserving salient content while optimizing a cropping-window path under cinematography constraints.

Its path uses smooth piecewise constant/linear/parabolic behavior and regularized optimization rather than independently centering every frame.

This supports a crucial project rule:

> **reframe quality is a temporal path problem, not a frame-by-frame detection problem.**

Even perfect subject boxes can produce terrible output if the viewport chases every detection fluctuation.

---

## 10. 2026 LIVE-YT VC work reinforces human-temporal smoothing

“Subjective Portrait Region Cropping in Landscape Videos with Temporal Annotation Smoothing” introduces a large portrait-crop preference dataset and explicitly post-processes human annotations to improve temporal smoothness.

Research lesson:

- benchmark against human-acceptable crop regions/paths, not only object recall;
- temporal stability is a first-class quality dimension;
- dataset availability does not imply commercial training approval — exact dataset/source licenses must be audited before reuse.

This paper is a benchmark/method reference, not a dependency decision.

---

## 11. `auto-vertical-reframe` is a useful modern implementation reference with a major license trap

`KazKozDev/auto-vertical-reframe` demonstrates a contemporary pipeline:

```text
scene detection
→ YOLO segmentation + ByteTrack
→ face/pose + saliency
→ subject ranking
→ CameraObservation / CameraState
→ smoothed pan/zoom
→ FFmpeg encode
```

Especially useful implementation ideas:

- explicit `CameraObservation` vs persistent `CameraState`;
- subject lock;
- tracked identity and missed-frame handling;
- zoom state and velocity;
- per-axis movement limits/damping;
- two-subject framing mode;
- handcrafted saliency fallback;
- debug preview and telemetry;
- preset-specific camera aggressiveness.

### 11.1 Direct-dependency problem

The project’s top-level repository says MIT, but its main runtime uses Ultralytics YOLO/weights.

Ultralytics currently states that proprietary/closed commercial use requires its Enterprise License unless the larger project complies with AGPL-3.0.

Therefore:

> **REFERENCE-STRONG / DIRECT USE BLOCKED unless an explicit compatible commercial Ultralytics license is obtained.**

Do not let a permissive top-level README hide a restrictive transitive runtime/model dependency.

The same rule applies to optional saliency/model components: source license and model/checkpoint license must be audited separately.

---

## 12. ClipsAI provides a useful speaker-aware special case

`ClipsAI/clipsai` is MIT and targets podcasts/interviews/speeches.

Its reframing path combines:

- speaker segments;
- scene changes;
- sampled face detection;
- per-segment ROI calculation.

Useful lesson:

> temporal segmentation should reflect editorial semantics when available.

For a dialogue-heavy video, the active speaker is a strong reframe signal. For our product this becomes one signal among many rather than the universal assumption.

Direct reuse is not approved because its transitive WhisperX/Pyannote/FaceNet/MediaPipe model/runtime stack requires separate license/deployment review and its assumptions are narrower than our product.

---

## 13. Product ads require product-aware framing, not face-only framing

A commercial product video can contain:

- no person;
- person + product;
- hands + small product;
- two people + product;
- product text/display that must remain readable.

Therefore the ranking model cannot hardcode:

```text
face = most important thing
```

Importance comes from EditSlot/CommercialSkill:

```text
Hook: face may matter
Proof: product/control/display may matter more
CTA: product + text-safe layout may matter
Vlog: current speaker/emotional face may dominate
```

Subject ranking is an editorial policy input, not a universal CV truth.

---

## 14. Reframe modes

A useful solver may choose among a small set of camera behaviors per continuous segment:

### Static / hold

Use when important content remains safely inside one crop window.

### Track / pan

Follow meaningful subject motion while limiting speed and acceleration.

### Controlled zoom

Change crop scale when subject occupancy or deliberate emphasis requires it.

### Multi-subject contain

Widen to preserve multiple mandatory entities when possible.

### Non-generative fallback layout

If the requested aspect ratio cannot contain mandatory content without unacceptable cropping, allow an explicit style policy such as:

- scale-to-fit with bars/matte;
- deterministic blurred-background layout;
- alternative composition card/layout.

### Unresolved

If none are acceptable, return a structured failure so that:

- Resolver may choose a better source shot;
- user may add manual keyframes;
- user may accept a layout fallback;
- ShootingPlan/reshoot guidance can be surfaced where appropriate.

Do not manufacture missing pixels.

---

## 15. Candidate crop geometry

At a time/keyframe, the system can generate legal crop candidates from:

- required subject bounds;
- preferred subject bounds;
- target aspect ratio;
- source frame bounds;
- safe zones / overlay reservations;
- allowed zoom range;
- headroom/look-room priors;
- composition thirds / centering policies;
- manual locks.

This is analogous to CandidateWindow generation in temporal editing:

> **generate a bounded legal candidate set first, then optimize the sequence.**

Do not let a model output arbitrary unvalidated crop coordinates outside the source image.

---

## 16. Deterministic crop-path optimizer

Conceptual objective:

```text
maximize
  mandatory_subject_coverage
+ preferred_subject_coverage
+ composition_quality
+ semantic_focus
+ safe_zone_compatibility
+ original_camera_intent_compatibility

minimize
  crop_position_velocity
+ crop_position_acceleration
+ zoom_velocity
+ zoom_acceleration
+ detection_jitter
+ subject_switch_penalty
+ source_edge_pressure
+ unnecessary_camera_motion
```

subject to:

```text
crop remains inside source frame
output aspect ratio preserved
manual locks respected
mandatory subject visibility constraints respected where feasible
zoom bounds respected
movement limits respected
```

Candidate solver families:

- keyframe/path smoothing with regularization;
- dynamic programming / beam search over bounded crop candidates;
- convex/piecewise path optimization;
- hybrid mode selection + continuous smoother.

No solver or weights are frozen before benchmark evidence.

---

## 17. Avoid the “camera chases the detector” failure mode

Detection/tracking boxes are noisy and semantic importance does not change every frame.

Required mechanisms should include concepts such as:

- hysteresis;
- subject lock/minimum hold duration;
- confidence-aware track loss;
- dead zone around current crop target;
- velocity/acceleration limits;
- scene-boundary reset;
- sparse keyframe targets plus interpolation;
- deliberate subject-switch penalty.

A small amount of controlled framing error is often preferable to continuous micro-panning.

---

## 18. Multi-subject and impossible-fit handling

If two mandatory subjects/products cannot fit the narrow crop simultaneously:

Preferred decision ladder:

1. reduce zoom / use maximum available source width while respecting target ratio;
2. optimize the crop for the current narrative priority if only one is strictly required;
3. use non-generative scale/pad layout if permitted;
4. request manual priority/keyframe when ambiguity matters;
5. return reframe infeasible so Resolver can try an alternate Shot;
6. surface missing-coverage/reshoot guidance when no source can satisfy the intent.

Do not randomly alternate between subjects or crop off a mandatory product to keep a face centered.

---

## 19. Overlay and safe zones must enter spatial composition before render

Subtitles, prices, CTA and logos consume screen space.

If the reframer chooses a perfect product position and the subtitle renderer later covers the product, the system has failed despite both components working independently.

Therefore a spatial composition context should support reserved regions such as:

```text
subtitle zone
CTA/button-like text zone
logo/brand zone
platform UI safe-zone constraints
```

The exact Overlay/Layout owner can be specified later, but the Reframe optimizer needs a read-only view of these constraints.

Platform safe-zone recommendations remain versioned PlatformProfile data, not universal constants.

---

## 20. Manual control and natural-language revision

Auto Reframe must remain user-controllable.

Useful controls:

- lock subject/product;
- add crop keyframe;
- lock crop for a range;
- choose two-person framing;
- “keep the product centered”;
- “do not crop the second person”;
- “show more environment”;
- “stop following my hand here.”

Natural-language instructions should compile into typed spatial constraints, not direct pixel mutation by an LLM.

Manual keyframes become high-priority constraints in the optimizer and survive later automatic recomputation unless unlocked.

---

## 21. Proposed ownership boundary

Research recommendation:

```text
Director / EditSlot / CommercialSkill
        ↓ ReframeIntent
SpatialEvidence providers
        ↓ observations
SpatialComposer
        ↓ ReframeDecision / SpatialTransformPlan
EDLBuilder
        ↓ exact executable crop/scale/position automation
Renderer
```

`SpatialComposer` owns the semantic/spatial resolution decision.

`EDLBuilder` owns the executable timeline representation.

`Renderer` owns neither.

This mirrors the temporal architecture:

```text
Director intent
→ Resolver concrete source decision
→ EDLBuilder exact timeline
```

without turning EDLBuilder into a hidden cinematographer.

---

## 22. EDL v0.2 implication: transforms must be time-varying

Historical EDLSegment fields such as one static `crop`, `scale` and `position` are insufficient.

Auto Reframe requires a deterministic transform curve / keyframe representation such as:

```text
SpatialTransformCurve
  crop-center x(t)
  crop-center y(t)
  scale/zoom(t)
  optional rotation(t)
  interpolation mode / segments
```

The exact schema belongs in the EDL/Spatial Composition capability specification.

The curve must map through canonical source time correctly even when edit-friendly/proxy artifacts were used for preview.

---

## 23. CPU / hardware tiers

### Tier 0 — CPU baseline

- existing Shot/TemporalEvidence;
- user/VLM-seeded ROI when necessary;
- OpenCV local tracker;
- simple face/region signals if cleanly available;
- handcrafted saliency;
- deterministic crop-path optimizer.

### Tier 1 — optional local semantic geometry

- approved MediaPipe task models;
- commercially clean detector/tracker model after audit.

MediaPipe source is Apache-2.0, but exact distributed task models must still be audited individually.

### Tier 2 — GPU enhancement

- SAM2 or another approved stronger segmentation/tracking provider;
- heavier grounding/localization models when useful.

### Tier 3 — cloud intelligence

- sparse high-value localization / semantic priority adjudication;
- recovery when local tracking fails;
- Reviewer inspection of ambiguous crop choices.

No GPU is required for the existence of Auto Reframe.

---

## 24. Review / QC for reframing

Deterministic metrics can include:

- mandatory-subject visible fraction;
- face/head truncation;
- product truncation;
- crop window outside source bounds;
- crop position velocity/acceleration;
- zoom velocity/acceleration;
- abrupt subject switches;
- jitter;
- safe-zone/overlay collision;
- excessive edge pressure;
- time spent in fallback layout;
- low-confidence tracking spans.

Editorial proxy review is reserved for questions such as:

- does the framing feel natural?
- is the product emphasized at the right moment?
- does the crop follow the wrong person?
- would a wider non-generative layout be preferable?

A failed reframe should invalidate only the affected SpatialTransformPlan / EDL range / preview chunks where possible.

---

## 25. Benchmark design

The benchmark corpus should deliberately include:

- single talking head;
- two speakers;
- person + product;
- hands + small product;
- product-only demonstrations;
- horizontal pans;
- handheld camera motion;
- subject crossing frame;
- subject leaving/entering;
- temporary occlusion;
- multiple moving people;
- small important text/display on product;
- wide environmental Vlog;
- fast sports-like motion;
- already-vertical footage;
- cases genuinely impossible to crop safely to 9:16.

Metrics:

- human preferred crop-path win rate;
- mandatory-subject coverage;
- important-object truncation rate;
- jitter / path smoothness;
- subject-switch errors;
- safe-zone collisions;
- manual override rate;
- CPU/GPU time;
- VLM escalation rate;
- final user preference versus center crop and simple tracking baselines.

The system should be rewarded for correctly declaring “cannot safely crop” when appropriate.

---

## 26. Upstream posture after focused survey

| Upstream / source | Current posture | Why |
|---|---|---|
| Google AutoFlip | REFERENCE-STRONG | foundational shot/saliency/path framing; legacy implementation not adopted wholesale; generative fallback ideas neutralized |
| Watch to Edit | REFERENCE-STRONG | explicit smooth crop-path optimization / cinematography constraints |
| LIVE-YT VC / SmartVidCrop research | BENCHMARK/METHOD REFERENCE | human temporal crop preferences; dataset license must be audited |
| KazKozDev/auto-vertical-reframe | REFERENCE-STRONG, DIRECT-BLOCKED | excellent modern implementation patterns, but core Ultralytics dependency creates AGPL/Enterprise commercial issue |
| ClipsAI | REFERENCE-STRONG special case | speaker-aware segmentation/framing; transitive model/runtime audit required |
| MediaPipe | OPTIONAL DIRECT-CANDIDATE at framework level | Apache-2.0 source, on-device; individual task-model licenses still audited |
| SAM2 | OPTIONAL ENHANCEMENT CANDIDATE | strong tracking/segmentation; not default CPU baseline |
| Ultralytics YOLO default stack | BLOCKED unless commercial license strategy explicitly approves | proprietary closed-product use currently requires Enterprise under upstream terms |

No status here is final legal approval.

---

## 27. Focused Survey verdict

**PASS for architecture design.**

The remaining unknowns are benchmark/specification issues:

- default detector/tracker provider;
- model/checkpoint commercial approval;
- crop candidate generation policy;
- path solver family;
- smoothness/velocity/zoom thresholds;
- safe-zone/layout integration details;
- fallback visual style;
- UI for manual crop locks/keyframes.

These are not reasons to reopen broad ecosystem discovery.

Architecture Contract v0.2 should now introduce the spatial-composition ownership seam and time-varying EDL transforms without selecting a specific CV vendor.

---

## 28. Primary references retained for later audit

- Google AutoFlip open-source framework article / historical MediaPipe implementation
- `google-ai-edge/mediapipe`
- Watch to Edit — arXiv:1807.03125
- Subjective Portrait Region Cropping in Landscape Videos with Temporal Annotation Smoothing — arXiv:2604.24947
- `KazKozDev/auto-vertical-reframe`
- `ClipsAI/clipsai`
- Ultralytics current licensing documentation
- OpenCV / SAM2 / tracking references already recorded in `VISUAL_EVENT_ANCHOR_GENERATION.md`

Future dependency approval must re-check exact upstream revisions, model files and terms at adoption time.
