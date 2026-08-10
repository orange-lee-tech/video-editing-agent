# CAP-04 — Retrieval, Director, Resolver and Sequence Optimizer

**Status:** CANDIDATE CAPABILITY SPEC  
**Architecture:** `ARCHITECTURE_CONTRACT_V0.2.md`  
**Scope:** EditSlot intent → high-recall Shot candidates → CandidateWindows → grounded sequence resolution

---

## 1. Purpose

This is the core automatic-editing capability.

It turns structured editorial intent plus persisted media/music evidence into concrete source selections without allowing a general LLM to invent IDs or timestamps.

---

## 2. Ownership

```text
Director         → EditPlan / EditSlot
ShotIndex        → retrieval candidates only
CandidateWindowGenerator → bounded legal source-window proposals
ShotResolver     → ResolutionDecision / ResolvedSelection
SequenceOptimizer→ deterministic strategy internal to Resolver
EDLBuilder       → final timeline coordinates, not Resolver
```

---

## 3. Director

Director reasons at story/edit-intent level.

It may decide:

- which Script sections survive;
- Slot count/order;
- narrative role;
- target duration;
- desired visual/action/subject;
- pacing;
- continuity intent;
- reuse policy;
- music alignment intent;
- spatial/reframe intent;
- Slot importance/intelligence budget.

It may not commit exact source timestamps.

---

## 4. EditSlot example

```yaml
narrative_role: proof
purpose: demonstrate fast product startup
desired_visual:
  subject: product
  action: user operates it and state visibly changes
target_duration: [1.2s, 1.8s]
pacing: energetic
music_alignment: prefer_accent
continuity:
  previous: product close-up
  avoid: abrupt distant framing
importance: high
```

No file path / source timestamp appears here.

---

## 5. Retrieval cascade

Preferred baseline:

```text
all current Shots
→ hard eligibility filter
→ lexical/metadata retrieval
+ dense semantic retrieval
→ rank fusion
→ broad Top-K
→ structured editorial rescoring
→ targeted observation/VLM only if evidence is insufficient
```

Retrieval optimizes recall. Resolver optimizes final precision/sequence quality.

---

## 6. Hard eligibility

Examples:

- wrong Asset usage role;
- rights/lock violation;
- mandatory subject definitely absent;
- media kind mismatch;
- source range invalid;
- insufficient duration under allowed trim rules;
- technical quality below hard floor;
- protected commercial fact conflict;
- prohibited source reuse.

Ineligible candidates do not receive a low score. They leave the search space.

---

## 7. Lexical retrieval

Especially useful for:

- brand/product names;
- exact spoken phrases;
- prices/model numbers;
- on-screen text;
- user labels;
- filenames;
- explicit action tags.

CJK search remains first-class.

---

## 8. Dense retrieval

First baseline embeds structured text derived from ShotAnalysis, not raw video by default.

Potential representations:

```text
visual_semantic_text
speech_text
user_semantic_text
```

A project-local exact vector scan is the preferred first scale baseline.

External vector DB/ANN is introduced only if real scale benchmarks justify it.

---

## 9. Rank fusion

Lexical and dense scores are not assumed numerically comparable.

Use rank fusion such as RRF-like baseline before calibrated raw score fusion.

After broad retrieval, Resolver computes normalized editorial features from authoritative evidence.

---

## 10. CandidateWindow generation

For each plausible Shot, build a bounded set of legal source windows from TemporalAnchors.

Inputs may include:

- Shot begin/end;
- speech phrase boundaries;
- VAD/silence;
- action onset/settle;
- subject reveal/center;
- motion peak;
- target Slot duration;
- user locks.

Output concept:

```text
CandidateWindow
├─ shot_ref
├─ source_range
├─ in_anchor_ref
├─ out_anchor_ref
├─ internal_event_refs
├─ duration
└─ confidence/evidence
```

Do not enumerate every millisecond pair.

---

## 11. Scoring hierarchy

### Hard constraints

Binary feasibility.

### Unary features

Candidate suitability for one Slot:

```text
semantic_fit
narrative_fit
subject_fit
action_fit
speech_fit
duration_fit
technical_quality
framing/composition
anchor_confidence
music opportunity
user preference
```

### Pairwise features

Compatibility of B after A:

```text
framing variety
shot-size transition
motion continuity/contrast
camera direction
subject continuity
audio continuity
color/exposure discontinuity
novelty/repetition
```

### Global features

Whole-sequence properties:

```text
Brief/Script coverage
Hook/proof/CTA coverage
product/brand visibility timing
energy curve
cut density
shot diversity
reuse
music-section fit
locks
```

Exact features/weights are versioned strategy data, not Domain constants.

---

## 12. Score and uncertainty

Persist them separately.

```text
high score + high confidence
→ local commit candidate

small margin + missing evidence + important Slot
→ targeted strong-model adjudication
```

Uncertainty can consider:

- top-1/top-2 margin;
- missing evidence;
- retrieval disagreement;
- anchor confidence;
- ASR/tracker/VLM quality;
- contradictory constraints.

---

## 13. VLM escalation

Use strong visual intelligence for editorial ambiguity, e.g.:

> Which of A/B/C grounded actions best demonstrates the product benefit?

not:

> Search all videos and invent exact timestamps.

Importance budget:

- Hook / core proof / CTA: more intelligence allowed;
- low-impact transition: conservative local solution preferred.

---

## 14. ResolutionDecision

Must support one Slot → multiple selections.

Conceptual shape:

```text
ResolutionDecision
├─ slot ref(s)
├─ selections: ResolvedSelection[]
├─ score
├─ confidence
├─ reasons / feature contributions
├─ alternatives
├─ warnings
└─ evidence refs
```

Each `ResolvedSelection` includes:

```text
shot_ref
selected_source_range
selection role/order
anchor/evidence refs
```

Manual user choice is represented as an explicit manual override decision, not by corrupting EditPlan semantics.

---

## 15. Sequence optimizer

First strategy family:

```text
layered beam search / DAG-style dynamic programming
```

over a bounded candidate space.

Conceptual state may include:

```text
next slot
accumulated narrative duration
music/phrase state
last candidate
used Shot neighborhoods
coverage state
accumulated score
```

For each Slot:

```text
Top-K Shots
× CandidateWindows
→ expand legal states
→ unary + pairwise + global incremental score
→ prune
→ keep Top-W
```

The optimizer is deterministic once evidence/policy/version are fixed.

---

## 16. Elastic music alignment

Music alignment is an opportunity/constraint, not “cut every beat.”

Examples:

```text
product lands ↔ accent
package opens ↔ drop
turn completes ↔ downbeat
camera push settles ↔ phrase entrance
keyword title ↔ accent
```

One Shot may span multiple beats in low-energy/dialogue sections.

Resolver decides source feasibility; EDLBuilder decides exact timeline placement.

---

## 17. Localized re-resolution

Review finding should be able to target:

```text
Slot_03
→ rerun CandidateWindow/Resolver only
→ rebuild affected EDL range
→ invalidate affected preview chunks
```

Do not rerun Script/ShotAnalysis/other Slots without dependency reason.

---

## 18. Explainability

Store feature/evidence contributions sufficiently to answer:

> Why did candidate A beat candidate B?

This supports:

- debugging;
- human benchmark review;
- user-facing “why this clip?”;
- calibration;
- targeted Reviewer repair.

An opaque single `0.83` score is insufficient.

---

## 19. Benchmarks

### Retrieval

- Recall@K;
- mandatory-proof miss rate;
- lexical vs dense vs hybrid;
- CPU latency/RAM/model footprint.

### CandidateWindow

- human acceptable-window coverage;
- IN/OUT timing error;
- speech/action completeness;
- dead setup/teardown;
- top-window human preference.

### Resolver

- pairwise human preference agreement;
- candidate/transition correctness;
- unresolved rate;
- VLM escalation rate/cost.

### Sequence

- full-edit pairwise preference;
- Brief/Script coverage;
- continuity/pacing;
- action/music sync;
- user override rate;
- optimizer runtime.

---

## 20. Not frozen here

- embedding model;
- exact vector/index library;
- Top-K/RRF constants;
- feature normalization;
- score weights;
- confidence thresholds;
- VLM provider;
- CandidateWindow count;
- beam width/pruning;
- CP-SAT adoption.

Those require benchmark evidence and ADRs.
