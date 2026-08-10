# CAP-09 — Review, Quality Gates and Product Benchmarks

**Status:** CANDIDATE CAPABILITY SPEC  
**Architecture:** `ARCHITECTURE_CONTRACT_V0.2.md`  
**Scope:** structured validation → targeted editorial review → localized repair → measurable product quality

---

## 1. Purpose

Review exists to discover defects as cheaply and early as possible and route repair to the smallest authoritative owner.

It is not a single “AI gives video score” call.

---

## 2. Ownership

```text
Deterministic validators → ValidationResult
ReviewService            → ReviewReport
Technical QC tools       → measured findings
AI reviewers             → structured review proposals
Application              → repair routing/stale propagation
```

Review never writes EditPlan/ResolutionDecision/EDL directly.

---

## 3. Layered review model

Preferred stages:

```text
1. Plan Review
2. Resolution Review
3. Deterministic Timeline Validation
4. Proxy Editorial AV Review when needed
5. Final Technical / Delivery QC
```

Strong-model review is selective, not mandatory at every stage.

---

## 4. Plan Review

Inputs can be mostly structured/textual:

- Brief;
- protected facts;
- ScriptPlan;
- Shooting/Coverage summary;
- EditPlan;
- CommercialSkill;
- BeatMap/music summary.

Checks:

- story/Brief coverage;
- missing/changed facts;
- weak Hook/value/proof/CTA intent;
- implausible duration;
- repetitive framing plan;
- missing coverage;
- style/pacing inconsistency.

No full render required.

---

## 5. Resolution Review

Inspect specific selection decisions before rendering.

Review evidence may include:

```text
Slot
selected Shot(s)/CandidateWindow(s)
score components
confidence
alternatives
TemporalAnchors
continuity context
rights/locks
```

A reviewer can reject only one Slot/selection.

---

## 6. Deterministic Timeline Validation

Before render verify:

- source ranges;
- timeline ranges;
- media availability;
- rational time mapping;
- locks;
- overlap/transition feasibility;
- rights/source policy;
- spatial transform bounds;
- audio automation ranges;
- subtitle/overlay timing;
- output duration.

These are not VLM tasks.

---

## 7. Proxy Editorial AV Review

Use when dynamic audiovisual judgment is needed.

Prefer:

- low-resolution proxy render;
- only affected region;
- high-value Hook/proof/CTA/emotional region;
- contact sheet + short video when sufficient.

Possible judgments:

- pacing/naturalness;
- source-window awkwardness;
- action/music feel;
- reframe naturalness;
- subtitle rhythm/readability;
- music mood;
- continuity/watchability.

Do not send the full original source library just to review the final 30-second edit.

---

## 8. Final Technical QC

Local checks include:

- decode success;
- output duration/resolution/fps;
- required audio tracks;
- black/freeze/silence anomalies;
- loudness/peak;
- PTS/sync issues;
- subtitle/overlay clipping where measurable;
- codec/container profile;
- missing license/attribution output obligations.

VMAF/reference metrics apply to render fidelity, not storytelling quality.

---

## 9. ReviewFinding

Conceptual machine-actionable structure:

```yaml
severity: major
target_ref: ...
affected_owner: ShotResolver
affected_slot: Slot_03
affected_source_range: optional
affected_timeline_range: optional
problem: proof shot begins before meaningful action
evidence_refs: [...]
recommended_action: rerun_source_window_resolution
requires_new_analysis: false
affected_downstream:
  - ResolutionDecision
  - EDL range
  - PreviewChunk range
```

Exact schema can evolve, but repair routing is mandatory.

---

## 10. Repair routing

Examples:

### Bad source window

```text
Review
→ ShotResolver only
→ affected EDL range
→ affected preview range
```

### Weak EditSlot strategy

```text
Review
→ Director affected section/slots
→ Resolver affected slots
→ EDL affected ranges
```

### Bad reframe

```text
Review
→ SpatialComposer range
→ EDL spatial automation
```

### BGM too loud

```text
Review
→ AudioEditorialService
→ EDL audio automation
```

### Black frame caused by backend

```text
Review/Technical QC
→ Renderer/backend repair
```

No unnecessary upstream recomputation.

---

## 11. Review rubric is skill-aware

Performance ad may emphasize:

- Hook;
- product/brand clarity;
- proof;
- CTA;
- pacing;
- music/action support;
- commercial-message clarity.

Vlog may emphasize:

- coherence;
- speech completeness;
- emotional continuity;
- naturalness;
- visual variety;
- music fit.

Technical QC remains objective/shared.

---

## 12. Benchmark corpus classes

### Public/redistributable

May enter repository/CI when license permits.

Use for:

- engineering fixtures;
- reproducible open benchmark subsets;
- codec/render regressions.

### Private real footage

Local only, never GitHub.

Use for:

- real commercial/Vlog quality;
- human preference;
- action/crop/retrieval realism;
- product probes.

The benchmark runner can store metadata/results without uploading private media.

---

## 13. Engineering Probe vs Product Probe

Engineering Probe:

> Does machinery/contracts/provider wiring work?

Product Probe:

> Is the result useful on real footage?

Synthetic FFmpeg patterns can prove API/codec/ownership paths, not real editing quality.

---

## 14. Retrieval benchmark

Labels:

```text
EditSlot query
→ relevant Shot set
```

Metrics:

- Recall@K;
- miss rate for mandatory proof;
- MRR/nDCG where useful;
- latency/RAM/model footprint.

High candidate recall is primary before final Resolver ranking.

---

## 15. TemporalAnchor benchmark

Human editors annotate:

- event/acceptable cut region;
- preferred point;
- semantic label where useful.

Metrics:

- anchor recall within tolerance;
- nearest-anchor error;
- false positives/minute;
- camera-motion false-positive rate;
- CPU time/decoded frames;
- VLM escalation rate/cost.

---

## 16. CandidateWindow benchmark

Evaluate:

- human acceptable-window coverage;
- speech/action completeness;
- dead setup/teardown;
- IN/OUT timing error;
- human top-window preference.

---

## 17. Resolver/sequence benchmark

Evaluate:

- pairwise candidate preference;
- full-sequence human preference;
- Script coverage;
- continuity;
- shot diversity;
- pacing;
- action/music sync;
- reuse behavior;
- user override rate;
- optimizer runtime;
- VLM/API cost.

---

## 18. Music/audio benchmark

Evaluate:

- rights-filter correctness;
- music Top-K preference;
- music-window preference;
- energy/narration fit;
- loop quality;
- speech intelligibility;
- duck/fade naturalness;
- loudness/peak.

---

## 19. Auto Reframe benchmark

Evaluate:

- mandatory-subject coverage;
- product/face truncation;
- jitter;
- pan/zoom smoothness;
- subject-switch errors;
- safe-zone collisions;
- manual override rate;
- human preference vs center crop/simple tracker.

Correct `unresolved/infeasible` may be a success for impossible crops.

---

## 20. End-to-end commercial/Vlog benchmark

Same Brief/source corpus, compare versions A/B.

Dimension ratings/reasons:

- Brief adherence;
- first seconds/Hook;
- message/product clarity;
- naturalness;
- coverage;
- pacing;
- continuity;
- music/audio;
- reframe/subtitles;
- watchability;
- final preference.

Measure cost/time alongside preference.

---

## 21. Cost telemetry

Per workflow/revision persist where available:

```text
local analysis wall time
embedding/retrieval time
optimizer time
VLM calls
frames/video seconds sent
text tokens/provider cost estimate
music/provider calls
render time
review calls
```

A claimed cost improvement must preserve the quality priority hierarchy.

---

## 22. Regression history

Benchmark results should be versioned against:

- code commit;
- capability/algorithm version;
- model/provider version;
- CommercialSkill version;
- runtime/hardware profile;
- dataset version.

This produces a long-term evidence trail of actual improvement rather than anecdotal demos.

---

## 23. Not frozen here

- exact human rating UI;
- pass thresholds;
- benchmark dataset size;
- VLM reviewer model;
- final rubric weights;
- acceptable cost target;
- automated release gating thresholds.
