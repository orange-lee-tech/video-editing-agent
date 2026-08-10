# Visual Event Anchor Generation — Survey V2 Research Draft

**Status:** ACTIVE RESEARCH DRAFT  
**Snapshot date:** 2026-08-11  
**Scope:** Camera Motion Compensation → Local/Subject Motion → Semantic Tracking → Temporal Event Anchors  
**Authority:** Informative research only; not an Architecture Contract.

---

## 1. Research question

How should the editor generate precise, useful temporal anchors such as:

- speech begins / ends;
- hand begins moving / stops;
- product enters / leaves frame;
- product reaches a useful composition;
- action reaches a visual peak;
- object contact / release is likely;
- camera pan / zoom begins or settles;

without confusing camera shake with subject motion, without assuming a GPU, and without asking a VLM to invent timestamps from scratch?

Current conclusion:

> Use a **camera-compensated, coarse-to-fine local evidence pipeline**. Separate global camera motion from residual/local motion first; generate candidate anchors from measurable trajectories and signals; attach confidence and provenance; ask a VLM only to label or choose among ambiguous grounded candidates.

A temporal anchor is evidence, not an edit. The Resolver later decides whether an anchor is useful for a specific EditSlot.

---

## 2. Motion is not semantic action

This distinction must remain explicit:

```text
motion event
    !=
semantic action event
```

Examples:

- optical flow can prove that pixels moved;
- a tracker can prove that a product bounding box moved;
- hand landmarks can show a hand approaching the product;
- only higher-level semantic evidence may justify labels such as "picks up product" or "demonstrates feature".

Therefore the local pipeline should generate grounded evidence first:

```text
motion_onset @ 7.42s
product_centered @ 8.06s
hand_product_distance_minimum @ 8.31s
action_settle @ 9.42s
```

A semantic provider may later interpret these as:

> likely product pickup and presentation.

The semantic provider should not erase the underlying measured anchors.

---

## 3. Never analyze motion across a Shot boundary

Shot boundaries are hard temporal discontinuities for visual-motion reasoning.

Do not compute camera motion or local motion across a cut. Every event-analysis unit begins inside a committed `Shot` interval.

Conceptually:

```text
Asset
  ↓
Shot
  ↓
CameraMotionEvidence
LocalMotionEvidence
TrackedEntityEvidence
TemporalAnchor[*]
```

This avoids treating a cut itself as an enormous motion spike.

---

## 4. CPU-first baseline: global camera motion compensation

### 4.1 Why raw optical-flow magnitude is insufficient

For handheld footage, a phone pan, push, tilt, rotation or shake can make most pixels move even when the subject is stationary.

A raw rule such as:

```text
flow magnitude > threshold
→ action
```

will therefore generate many false action anchors.

### 4.2 Estimate global image motion first

OpenCV's video-stabilization stack already provides robust global motion estimation between 2D point clouds, including translation, similarity, affine and homography models, with RANSAC-based estimation.

Research baseline:

```text
Frame t
  ↓
detect / retain distributed feature points
  ↓
track points to Frame t+1
  ↓
robust global transform fit (RANSAC)
  ↓
GlobalCameraTransform[t]
```

Prefer the simplest model that explains the frame pair sufficiently well.

Candidate policy:

- translation / similarity for ordinary handheld pans, tilts, minor rotation and zoom;
- affine when shear / more complex image-plane motion is materially present;
- homography only when evidence supports it, because an overly flexible model can absorb real foreground motion.

Do not freeze these model-selection thresholds before benchmark work.

### 4.3 Global motion quality matters

Every estimated transform should carry evidence quality, for example:

```text
inlier_ratio
reprojection_rmse
feature_count
feature_spatial_coverage
model_type
```

If global motion estimation is poor, residual object-motion evidence must have lower confidence rather than pretending the camera model is correct.

### 4.4 Camera motion itself is useful evidence

Do not merely subtract camera motion and throw it away.

Derive camera-motion observations such as:

```text
pan_left / pan_right candidate
pan_speed
rotation candidate
zoom_in / zoom_out candidate
camera_motion_onset
camera_motion_peak
camera_motion_settle
```

These can later help the Director / Resolver reason about:

- matching movement across cuts;
- avoiding awkward cut points during rapid camera motion;
- using a push-in completion as a natural emphasis point;
- distinguishing intentionally dynamic footage from unstable footage.

---

## 5. Residual/local motion after camera compensation

Once a global transform is estimated, local motion should be measured relative to that transform.

Two equivalent implementation families are worth benchmarking:

1. warp one frame according to the estimated camera transform, then measure remaining motion;
2. predict each tracked point's global displacement from the transform and subtract it from measured point displacement.

Conceptually:

```text
measured_flow
-
expected_camera_flow
=
residual_local_flow
```

Useful local features include:

- robust residual magnitude;
- residual direction;
- spatial concentration;
- connected / clustered moving regions;
- temporal derivative / acceleration;
- foreground occupancy.

A key distinction:

```text
large motion distributed across most of frame
+ strong global-transform fit
→ probably camera motion

localized residual cluster after compensation
→ likely local subject/object motion
```

This is much more reliable than a global optical-flow magnitude threshold.

---

## 6. Adaptive thresholds, not fixed pixel magic numbers

Motion thresholds should not be hard-coded in raw pixels because source resolution, crop, focal length and subject size vary greatly.

Prefer normalized signals such as:

- motion divided by frame diagonal;
- motion divided by tracked object diagonal;
- robust percentile relative to the current Shot's baseline;
- median / MAD-derived noise floor;
- hysteresis thresholds for onset and release.

Example conceptual detector:

```text
motion baseline
        ↓
robust noise estimate
        ↓
upper threshold → event begins
lower threshold → event ends after dwell
```

Hysteresis is valuable because a hand does not become "stopped" every time one frame dips below a threshold.

The exact parameters belong to benchmark calibration, not a permanent product constant.

---

## 7. Coarse-to-fine temporal analysis

Full native-FPS dense analysis of every frame is unnecessary for the first pass.

Recommended research strategy:

```text
Shot
 ↓
coarse temporal scan
 ↓
possible event region
 ↓
small temporal neighborhood
 ↓
native-FPS / finer analysis
 ↓
precise anchor
```

For example, a coarse scan may identify an onset neighborhood around `7.4s`; only a short neighborhood around it is then reprocessed at native FPS.

Benefits:

- lower CPU cost;
- fewer decoded frames;
- easier Windows CPU deployment;
- precise final anchors without running expensive analysis over the entire Shot.

The exact coarse sampling rate should be benchmarked by content class and Shot duration; it should not be frozen as one global FPS.

---

## 8. Event curve → anchor extraction

A useful local-motion pipeline should produce a temporal curve, not isolated frame flags.

Possible signals:

```text
residual_motion(t)
tracked_object_speed(t)
hand_speed(t)
hand_object_distance(t)
object_screen_position(t)
```

After light smoothing and robust change detection, derive anchors such as:

- `motion_onset`;
- `motion_peak`;
- `motion_offset`;
- `motion_direction_change`;
- `action_settle`;
- `camera_motion_onset`;
- `camera_motion_settle`.

An anchor should preserve:

```text
kind
source_time
confidence
evidence_refs
method
analysis_revision
```

The Resolver must be able to explain which measured evidence produced a candidate window.

---

## 9. Subject / product-specific tracking

Whole-frame residual motion is not enough for many commercial shots. We often need to know what **the product**, **the hand**, or another relevant subject did.

### 9.1 Seed semantics sparsely, track locally

A cost-efficient pattern is:

```text
user selection OR sparse VLM/object localization
        ↓
initial ROI / mask / box
        ↓
local tracker over the Shot
        ↓
trajectory evidence
```

The expensive semantic system identifies what to track once or at sparse recovery points; a local tracker propagates the target through neighboring frames.

### 9.2 CPU baseline trackers

OpenCV provides CPU trackers such as KCF and CSRT. These are suitable baseline candidates for short Shot-level object trajectories when an initial box is available.

Potential derived anchors:

- object enters frame;
- object exits frame;
- object reaches center / target composition region;
- object begins / stops moving;
- object changes direction;
- object size rapidly increases / decreases (approach / retreat candidate).

Tracker failure must be explicit; do not silently extrapolate through long occlusions.

### 9.3 Optional SAM 2 enhancement

SAM 2 supports promptable video segmentation/tracking and its code plus published checkpoints are Apache-2.0 according to the upstream project.

It is therefore a technically and licensing-wise interesting optional enhancement for machines that can support the model.

However:

- published speed figures are GPU-oriented;
- it must not become a required baseline;
- real Windows CPU/GPU deployment needs benchmarking;
- the Environment Doctor should expose whether the enhancement is actually available.

### 9.4 CoTracker is not a commercial dependency candidate

CoTracker is technically attractive for point tracking, but the majority of the current project is licensed CC-BY-NC. It should therefore be treated as research reference only for this commercial-oriented product unless upstream licensing materially changes.

---

## 10. Hand and hand-object events

Hand activity is especially important for product advertising:

- pointing;
- touching;
- picking up;
- placing;
- opening;
- pressing;
- presenting.

A practical architecture should separate geometry from semantic labeling.

Possible evidence chain:

```text
hand landmarks / hand box
+
product ROI
        ↓
relative trajectories
        ↓
hand speed
product speed
hand-product distance
box/mask overlap
        ↓
contact / pickup / release candidates
```

A semantic provider may then validate the meaning of a short ambiguous interval.

MediaPipe hand-landmark functionality remains an optional candidate for local hand geometry, but the exact distributed model files must pass the same model-license review as every other ML dependency.

---

## 11. Product enter / exit / reveal anchors

For advertising, screen-space composition itself is useful.

For a tracked target, derive normalized geometry:

```text
center_x / frame_width
center_y / frame_height
bbox_area / frame_area
visible_ratio
boundary_distance
```

Possible anchors:

- `subject_enter` — track first becomes reliably visible from frame boundary / occlusion;
- `subject_exit` — reliable disappearance toward a boundary or occlusion;
- `subject_centered` — subject enters a configured composition region;
- `subject_reveal` — visibility / area changes from low to stable high;
- `subject_closeup_peak` — relative screen occupancy reaches a useful local maximum.

These are facts / candidates. A CommercialSkill decides whether "centered product reveal" is desirable for a Hook or proof Slot.

---

## 12. Static-camera special case

When global camera motion is near zero for a stable period, classical foreground/background methods such as OpenCV MOG2 may provide an additional cheap moving-region signal.

Do not use background subtraction blindly on moving-camera footage.

A reasonable router is:

```text
camera_motion_confidence high and magnitude low
→ background-subtraction evidence allowed

meaningful camera motion
→ rely on camera-compensated residual motion instead
```

---

## 13. Confidence fusion

An anchor should not only have a timestamp; it should carry confidence based on independent evidence.

Possible confidence factors:

```text
camera_model_confidence
tracker_confidence
motion_signal_strength
temporal_persistence
semantic_corroboration
boundary_distance
occlusion_risk
```

Examples:

```text
ASR word end
+ VAD speech end
+ silence begins
→ very strong speech-completion anchor

motion onset
+ poor camera RANSAC fit
+ heavy blur
→ weak visual anchor
```

Confidence is later used by the evidence-escalation gate.

---

## 14. VLM escalation policy

A VLM should normally **choose or label grounded alternatives**, not create arbitrary floating-point timestamps.

Preferred request shape:

```text
Candidate A @ 7.42s — local motion begins
Candidate B @ 7.86s — product becomes fully visible
Candidate C @ 8.06s — product reaches stable center framing

For this EditSlot, which point is the most natural IN?
Return A / B / C / uncertain.
```

Escalate only when:

- local evidence is contradictory;
- semantics determine the choice;
- the Slot is important enough to justify API cost;
- the selected window has high editorial impact (Hook, proof, CTA, key emotional moment);
- Reviewer specifically requests re-observation.

Do not ask the VLM again when local evidence already has high confidence.

---

## 15. Failure modes that must be benchmarked

The first anchor benchmark corpus should deliberately include:

- handheld shake;
- intentional pan / tilt / push-in;
- zoom;
- rolling-shutter-like instability;
- motion blur;
- low light;
- reflective products;
- moving background / crowds;
- partial occlusion;
- small products;
- hand crossing product;
- camera and product moving simultaneously;
- fast whip motion;
- slow deliberate action;
- static product reveal;
- talking-head gesture;
- action that begins before speech;
- speech that continues after the visual action completes.

The system should measure not only event precision but false-anchor rate.

---

## 16. Anchor benchmark design

Human editors should annotate **acceptable temporal regions**, not always a single sacred frame.

For each target event, record where practical:

```text
acceptable_start_range
preferred_point
acceptable_end_range
event_type
semantic_label
```

Metrics should include:

- anchor recall within tolerance;
- absolute temporal error to preferred point;
- false positives per minute / Shot;
- coverage of human-acceptable anchor region;
- camera-motion false-positive rate;
- CPU processing time;
- decoded-frame count;
- VLM escalation rate;
- API cost per minute of source footage.

The product goal is not merely sub-frame precision; it is to ensure that good human edit points enter the candidate space reliably and cheaply.

---

## 17. Current candidate tiers

### Tier 0 — default CPU / deterministic

- committed Shot boundaries;
- ASR / word timestamps;
- VAD / silence;
- OpenCV sparse tracking / global motion estimation;
- camera-compensated residual motion;
- OpenCV KCF / CSRT when an ROI seed exists;
- screen-space geometry and trajectory logic.

### Tier 1 — optional local semantic geometry

- hand / pose landmark provider after model-license verification;
- stronger local object tracking / segmentation;
- lightweight temporal event models if benchmarks justify them.

### Tier 2 — GPU/local enhancement

- SAM 2 video tracking/segmentation or comparable future providers;
- heavier temporal localization models.

### Tier 3 — cloud intelligence

- targeted VLM semantic arbitration;
- sparse target localization / re-identification when local tracking loses the subject;
- high-value ambiguous action interpretation.

GPU availability improves the toolbox; it must not determine whether the editor can function.

---

## 18. Current architecture recommendation

Do not yet freeze a specific class schema, but preserve this capability boundary:

```text
TemporalEvidencePort
    ↓
TemporalEvidence / TemporalAnchor proposals
    ↓
validated persisted analysis revision
    ↓
CandidateWindow generation
    ↓
Resolver
```

Visual event analyzers must not directly commit `ResolutionDecision` or mutate EDL.

---

## 19. Upstream / source notes

High-value sources reviewed in this phase:

- OpenCV Global Motion Estimation / videostab documentation — robust global 2D motion estimation with RANSAC and multiple motion models.
- OpenCV Tracking API — KCF / CSRT CPU tracker candidates.
- OpenCV BackgroundSubtractorMOG2 — static-camera foreground evidence candidate.
- Meta SAM 2 — promptable video segmentation/tracking; code and published checkpoints described by upstream as Apache-2.0.
- Meta CoTracker — technically strong point tracking, but majority license is CC-BY-NC and therefore unsuitable as a normal commercial dependency.

No research status here constitutes final legal approval or dependency selection.
