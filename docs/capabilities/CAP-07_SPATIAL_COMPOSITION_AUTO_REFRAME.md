# CAP-07 — Spatial Composition / Auto Reframe

**Status:** CANDIDATE CAPABILITY SPEC  
**Architecture:** `ARCHITECTURE_CONTRACT_V0.2.md`  
**Research:** `AUTO_REFRAME_ASPECT_RATIO_COMPOSITION.md`

---

## 1. Purpose

Convert a resolved user-supplied visual source into a target canvas/aspect ratio while preserving important people/products/actions, maintaining temporal framing stability and avoiding generative pixel synthesis.

---

## 2. Ownership

```text
Director/EditSlot/CommercialSkill → spatial intent
Spatial evidence providers        → tracked/semantic observations
SpatialComposer                   → ReframeDecision / SpatialTransformPlan
EDLBuilder                        → exact transform automation on timeline
Renderer                          → execute crop/scale/position
```

Renderer is not a cinematographer.

---

## 3. Reframe unit

Work within one continuous resolved source segment.

Do not smooth crop/zoom trajectory across a hard source Shot cut.

Hard cut resets spatial state unless a higher-level edit transition explicitly defines something else.

---

## 4. ReframeIntent

Potential dimensions:

```text
target canvas/aspect ratio
mandatory focus entities
preferred focus entities
framing style
headroom/look-room policy
product visibility target
minimum visible fraction
max zoom
max pan/zoom speed
reserved overlay/safe zones
motion style
manual keyframes/locks
```

Intent is provider-neutral.

---

## 5. Spatial evidence

Reuse existing analysis where possible:

- subject/product track;
- face/pose/hand landmarks;
- object bounds/mask;
- semantic importance;
- saliency;
- camera motion;
- residual local motion;
- visible fraction;
- confidence/occlusion risk.

Do not create a second duplicate video-understanding stack solely for reframing.

---

## 6. Product-aware importance

Face detection is not universal framing authority.

Commercial Slot examples:

```text
Hook       → person/product depending intent
Proof      → product/action/display may dominate
CTA        → product + reserved text zone
Vlog       → active speaker/emotional face may dominate
```

Importance is derived from EditSlot/Skill, not hardcoded object class bias.

---

## 7. Candidate crop generation

Given target aspect ratio and evidence, generate legal candidates using:

- mandatory entity bounds;
- preferred entity bounds;
- source frame;
- safe zones;
- allowed zoom;
- composition priors;
- manual locks.

Candidates remain inside source geometry.

A model may propose focus targets, but all crop coordinates are validated deterministically.

---

## 8. Camera modes

Useful high-level modes:

```text
hold/static
track/pan
controlled zoom
multi-subject contain
non-generative layout fallback
unresolved
```

Mode selection can reduce unnecessary motion compared with chasing every detector update.

---

## 9. Smooth path optimization

Optimize a temporal crop/scale trajectory, not each frame independently.

Conceptual objective:

```text
maximize:
  mandatory subject coverage
  preferred subject coverage
  composition quality
  semantic focus
  safe-zone compatibility

minimize:
  position velocity/acceleration
  zoom velocity/acceleration
  jitter
  unnecessary movement
  subject switching
  source-edge pressure
```

subject to source bounds, zoom limits, locks and visibility constraints.

---

## 10. Temporal stability mechanisms

Candidate techniques:

- hysteresis;
- subject-lock hold period;
- track-loss timeout;
- dead zone around current target;
- max velocity/acceleration;
- sparse target keyframes + interpolation;
- scene-boundary reset;
- subject-switch penalty.

The exact solver/parameters are benchmark work.

---

## 11. Multi-subject policy

When mandatory subjects cannot fit simultaneously:

```text
widen/reduce zoom
→ prioritize only if policy marks one optional
→ allowed deterministic pad/layout fallback
→ manual priority/keyframes
→ Resolver alternate Shot
→ unresolved/reshoot guidance
```

Do not oscillate randomly between subjects.

---

## 12. Safe zones and overlays

SpatialComposer requires read-only knowledge of planned:

- subtitle region;
- CTA/price text region;
- logo/brand region;
- platform UI/safe-zone constraints.

Otherwise later text can cover the subject selected by Auto Reframe.

Platform safe zones are versioned PlatformProfile data.

---

## 13. Non-generative invariant

Allowed normal paths:

- crop;
- scale;
- reposition;
- deterministic pan/zoom;
- matte/letterbox;
- deterministic blurred-background/layout where policy allows.

Forbidden normal fallback:

- generative outpainting;
- generative uncrop;
- synthesized missing background.

If crop cannot satisfy constraints, report it.

---

## 14. Manual/user control

Support concepts such as:

- lock focus subject;
- add crop keyframe;
- lock crop range;
- preserve two people;
- show more environment;
- keep product centered;
- disable follow behavior.

Natural language compiles into structured constraints.

Manual locks outrank later automatic re-solve until explicitly removed.

---

## 15. ReframeDecision

Likely durable Application artifact:

```text
resolved_selection_ref
focus entity refs
mode
spatial transform keyframes/path
confidence
constraint satisfaction
fallback state
warnings
evidence refs
policy version
```

It does not own final timeline coordinates.

---

## 16. EDL handoff

EDLBuilder maps source-local transform path into exact timeline automation.

EDL must represent time-varying:

```text
crop center x/y
scale/zoom
position
optional rotation
interpolation
```

MediaTime mapping must remain valid when preview/proxy derivatives are used.

---

## 17. Provider tiers

### Tier 0 CPU

- existing TemporalEvidence;
- user/VLM seed when needed;
- OpenCV tracking;
- handcrafted saliency;
- deterministic optimizer.

### Tier 1 optional local

- approved face/pose/object task models.

### Tier 2 GPU

- stronger segmentation/tracking/grounding.

### Tier 3 cloud

- sparse semantic localization/adjudication/recovery.

No GPU is required for the existence of this capability.

---

## 18. Dependency/licensing rule

Top-level project license is insufficient evidence.

Example from Survey V2:

- a modern MIT auto-reframe project uses Ultralytics YOLO as core runtime;
- Ultralytics currently requires AGPL-compatible openness or an Enterprise license for proprietary commercial deployment.

Therefore detector/tracker implementation is behind a Port and release approval includes transitive code/model terms.

---

## 19. Local QC

Measure:

- mandatory-subject visible fraction;
- face/head truncation;
- product truncation;
- source-bound violations;
- pan/zoom velocity/acceleration;
- jitter;
- subject-switch frequency;
- safe-zone collisions;
- fallback-layout duration;
- low-confidence tracking spans.

Editorial review judges naturalness/emphasis only when needed.

---

## 20. Benchmarks

Include:

- single/two-person talking head;
- person+product;
- hands+small product;
- product-only demo;
- moving/handheld camera;
- subject crossing/occlusion;
- wide Vlog environment;
- fast movement;
- impossible-fit cases.

Compare against:

- center crop;
- simple face tracking;
- current algorithm candidate;
- human preferred paths.

Metrics include human preference, subject coverage, jitter, switch errors, override rate, runtime and VLM escalation cost.

---

## 21. Not frozen here

- detector/tracker provider;
- saliency model;
- MediaPipe/SAM2 adoption;
- crop solver family;
- numeric smoothness weights;
- motion/zoom limits;
- fallback visual styling;
- keyframe UI design.
