# AI Editing Core Mechanism — Research Draft

**Status:** ACTIVE RESEARCH DRAFT  
**Purpose:** Preserve the current best explanation of how Script + visual evidence + music evidence should
become a precise EDL without allowing an LLM to invent timestamps.

This document is intentionally more detailed than an ADR. It records a mechanism under investigation.
Only later evidence and Architecture Contract revisions may freeze it.

---

## 1. Core thesis

A high-quality AI editor should be:

- **coarse-to-fine** — progressively narrow the search space;
- **evidence-grounded** — decisions must reference real persisted evidence;
- **confidence-gated** — expensive models are escalation paths, not default fuel;
- **locally measurable** — timestamps, motion, speech and beat facts come from tools where practical;
- **incrementally revisable** — a failed slot should be repairable without rerunning the whole project.

The preferred rule is:

> **LLMs may select and explain cut decisions; by default they do not create exact cut timestamps.**

---

## 2. Authority chain

```text
Brief / ScriptPlan / ShootingPlan
              │
              ▼
          Director
              │
          EditSlots
              │
              ▼
Candidate Retrieval / Eligibility
              │
            Top-K
              │
              ▼
Evidence Escalation (only if needed)
              │
              ▼
Candidate Anchor Generation
              │
              ▼
          ShotResolver
              │
      ResolutionDecision
              │
              ▼
          EDLBuilder
              │
             EDL
              │
              ▼
      local render / review
```

The Director owns editorial intent, not source-file timestamps.

The Resolver owns concrete source selection and source-window resolution.

The EDLBuilder remains the final exact timeline authority producer.

---

## 3. What the Director should express

Example EditSlot intent:

```yaml
narrative_role: proof
purpose: demonstrate that the product starts quickly
visual_intent:
  subject: product
  action: user operates the product and a visible state changes
preferred_duration_seconds: [1.2, 1.8]
pacing: energetic
music_alignment: prefer_accent
continuity:
  previous: product exterior close-up
  avoid: abrupt jump to distant framing
importance: high
```

It should not contain an invented statement such as:

```yaml
source_file: IMG_4831.MOV
source_start: 17.382
source_end: 18.916
```

Exact source coordinates require evidence and belong downstream.

---

## 4. Candidate Retrieval

The Resolver should not ask an expensive multimodal model to inspect all assets for every slot.

Candidate generation should progress from cheap/high-recall to expensive/high-precision.

Conceptual sequence:

```text
all Shots
   ↓ hard eligibility filters
eligible Shots
   ↓ local lexical / metadata / cached-analysis retrieval
broad candidates
   ↓ semantic ranking / embedding where useful
Top-K
   ↓ targeted VLM observation only for ambiguous/high-value candidates
final evidence set
```

Hard eligibility examples:

- locked or forbidden source;
- insufficient duration;
- unusable technical quality;
- wrong media type;
- mandatory subject/action definitely absent;
- duplicate/reuse policy violated;
- source interval outside valid Shot boundaries.

Hard failures should not consume model tokens.

---

## 5. Multi-evidence candidate ranking

A single embedding similarity score is not enough.

A candidate may be conceptually modeled as:

```text
CandidateScore =
  semantic_fit
+ narrative_fit
+ action_fit
+ technical_quality
+ duration_fit
+ continuity_fit
+ music_fit
+ novelty
+ user_preference
-
  reuse_penalty
- technical_penalty
- unsafe_trim_penalty
- continuity_break_penalty
```

The exact formula is not frozen.

Weights should be supplied by the current editing skill / style / slot role.

Example:

- ad hook: high visual-energy, subject clarity, action and beat-alignment weights;
- Vlog reflection: higher emotional continuity and natural-duration weights, lower beat pressure.

---

## 6. Discrete Candidate Anchors instead of free-form milliseconds

For a Shot spanning `07.00 → 14.00`, do not ask an LLM to choose any arbitrary millisecond.

First generate meaningful anchor candidates from real observations:

```text
07.00 shot begin
07.18 speech begin
07.42 action begins
08.06 subject reaches center
08.74 motion peak
09.10 phrase boundary
09.42 action completes
10.03 gaze event
10.81 sentence end
12.72 next action begins
13.81 silence begins
14.00 shot end
```

Resolver chooses IN/OUT from a small legal anchor set rather than an unconstrained continuous interval.

This improves:

- determinism;
- validation;
- explainability;
- model stability;
- benchmarkability;
- cost.

---

## 7. Anchor sources

### 7.1 Speech anchors

Potential facts:

- word start/end;
- sentence/phrase start/end;
- VAD start/end;
- silence boundaries;
- speaker changes;
- filler-word spans;
- breath / pause cues where measurable.

For spoken-content editing, exact time should primarily derive from ASR/alignment timestamps.

The semantic model decides *what phrase to keep*; the timestamp engine resolves *where the phrase exists*.

### 7.2 Visual anchors

Potential facts:

- shot begin/end;
- action begin/end;
- object/contact events;
- subject enters/leaves;
- motion onset/peak/stop;
- camera-motion changes;
- quality transitions;
- gaze / gesture / product-state events;
- local temporal-model observations.

### 7.3 Music anchors

Potential facts:

- beat;
- downbeat;
- accent;
- phrase/section boundary;
- build-up/drop;
- energy transition.

BeatMap describes these music facts; it does not decide the cut.

### 7.4 Structural anchors

Potential facts:

- target slot duration;
- adjacent timeline boundaries;
- locked timeline points;
- mandatory coverage constraints;
- previous/next continuity conditions.

---

## 8. VLM as judge, not clock

A costly visual model should preferably choose among grounded candidate options instead of inventing a
floating-point time.

Poor default prompt pattern:

> "Find the exact timestamp where the action starts."

Preferred pattern:

```text
Local evidence found three legal IN candidates:
A — 1.21s: hand starts moving
B — 1.46s: product enters the main focal area
C — 1.71s: action becomes visually stable

For a 1.4-second proof shot, choose A/B/C or return uncertain.
```

Benefits:

- source validity is guaranteed;
- the model performs editorial judgment rather than timestamp arithmetic;
- output is easy to validate;
- disagreements can be benchmarked against human selections.

---

## 9. Confidence-gated escalation

Most trims should not require a VLM.

Conceptual policy:

```text
local evidence
   ↓
high confidence
   → commit candidate decision

medium confidence
   → cheap/local secondary check

low confidence + low importance
   → conservative fallback / user-visible uncertainty

low confidence + high importance
   → targeted VLM / stronger-model review
```

Hook, CTA and core product-proof slots may receive a larger intelligence budget than low-impact transitions.

---

## 10. Timing as constrained optimization

Once candidate Shots and candidate anchors exist, exact EDL construction can be treated as a small
optimization/constraint problem instead of LLM arithmetic.

Conceptual objective:

```text
minimize
  narrative_timing_error
+ beat_alignment_error
+ trim_awkwardness
+ continuity_penalty
+ reuse_penalty
+ quality_penalty
```

subject to constraints such as:

```text
source_start < source_end
source window within valid Shot
slot duration within allowed range
mandatory coverage satisfied
locks respected
no illegal timeline overlap
duplicate/reuse rules respected
```

Candidate algorithms to benchmark later:

- dynamic programming;
- beam search;
- constraint solver;
- weighted interval / sequence optimization;
- bounded combinatorial search over a small anchor set.

No algorithm is frozen yet.

---

## 11. Action-to-music alignment

Advanced beat sync should align meaningful visual events, not merely cuts.

Examples:

```text
product lands on table   ↔ accent
package opens            ↔ drop
turn completes           ↔ downbeat
camera push reaches item ↔ phrase entrance
keyword title appears    ↔ musical accent
```

Director decides which semantic events deserve synchronization.

Resolver determines whether a legal source window can place the chosen visual anchor close enough to a
BeatMap anchor while preserving natural motion and narration.

---

## 12. Layered Review Loop

Do not default to:

```text
full render → expensive VLM → reject → rerun everything
```

Preferred review layers:

```text
1. Plan Review
2. Resolution Review
3. deterministic timeline / technical QC
4. proxy editorial AV review when needed
5. final technical QC
```

### Plan Review

Inputs may be text/structured only:

- Brief;
- ScriptPlan;
- CommercialSkill;
- EditPlan;
- BeatMap summary;
- coverage summary.

Possible issues:

- weak hook intent;
- product shown too late;
- missing CTA;
- core fact omitted;
- pacing density implausible;
- repeated framing pattern.

### Resolution Review

Inspect individual selection evidence before rendering the full video.

Example:

```yaml
slot: EditSlot_03
selected_shot: Shot_41
source_window: [17.20, 18.73]
score:
  semantic: 0.91
  quality: 0.84
  action: 0.94
  continuity: 0.72
alternatives:
  Shot_17: 0.81
  Shot_53: 0.77
```

A reviewer can reject only this resolution if necessary.

### Editorial AV Review

Use a low-cost proxy render or only affected/high-value regions when possible.

Full dynamic VLM review is best reserved for semantic/temporal issues that structured evidence cannot
settle cheaply.

---

## 13. ReviewReport should route repair work

A useful finding should be machine-actionable:

```yaml
severity: major
target: EditSlot_03
problem: proof shot begins before meaningful product action
evidence: first 0.31s is setup motion
recommended_action: rerun source-window resolution
affected_owner: ShotResolver
requires_new_visual_analysis: false
affected_downstream:
  - ResolutionDecision_03
  - EDL
  - affected preview chunk
```

The intended repair behavior is:

> rerun the smallest authoritative owner that can fix the problem, then propagate staleness only downstream.

This is expected to be a major quality/cost advantage of the revisioned architecture.

---

## 14. Commercial editing skills as versioned priors

Commercial short-video and Vlog editing should not share one hardcoded rubric.

A future versioned skill may define:

```yaml
hook_policy: ...
brand_visibility_policy: ...
product_visibility_policy: ...
cta_policy: ...
shot_duration_distribution: ...
cut_density_range: ...
visual_energy_curve: ...
framing_diversity: ...
speech_continuity_policy: ...
caption_policy: ...
safe_zone_profile: ...
music_energy_policy: ...
beat_sync_strength: ...
transition_density: ...
review_rubric: ...
```

These are editing priors and constraints, not a bag of prompt prose.

They should be versioned because platform guidance and learned product benchmarks can change.

---

## 15. Cost discipline

The current strongest cost principles are:

1. **Analyze once** — cache revision-bound ShotAnalysis/ASR/BeatMap/model observations.
2. **Retrieve before observe** — narrow Top-K locally before expensive visual inspection.
3. **Local before cloud** — measurement belongs to local tools when possible.
4. **Confidence gate** — expensive models only for uncertainty that matters.
5. **Importance budget** — Hook/CTA/core proof can consume more intelligence budget.
6. **Targeted review** — repair and re-review only affected regions/owners.
7. **Escalating model tier** — use strong/expensive models as escalation, not default fuel.

The largest cost win is expected to come from reducing irrelevant model work, not merely selecting a model
with a cheaper token price.

---

## 16. Current open research questions

Before implementation, still research:

- hybrid retrieval strategy (lexical + structured facts + embeddings);
- embedding model candidates and commercial/local deployment;
- how to normalize candidate scores across evidence sources;
- action-event detector candidates suitable for CPU/optional GPU/cloud tiers;
- anchor confidence representation;
- optimal Top-K sizes and escalation thresholds;
- deterministic optimizer choice;
- human-editor benchmark protocol for source-window and beat/action alignment;
- how editing skills alter score weights without turning Domain logic into prompt spaghetti.
