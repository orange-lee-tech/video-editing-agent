# Resolver Score Calibration and Commercial Skills — Survey V2 Research Draft

**Status:** ACTIVE RESEARCH DRAFT  
**Snapshot date:** 2026-08-11  
**Scope:** Resolver Features → Skill Priors → Human Preference Calibration → User Adaptation → Review Rubrics  
**Authority:** Informative research only; not an Architecture Contract.

---

## 1. Research question

How should the system decide that one candidate Shot / CandidateWindow / sequence is better than another for:

- an e-commerce / performance advertisement;
- a product promo;
- a Vlog;
- a user-specific editing style;

without accumulating an opaque pile of hard-coded weights and platform folklore?

Current conclusion:

> Treat Resolver scoring as a **versioned policy and preference-calibration problem**, not a fixed formula. Separate hard constraints from measurable features; initialize genre/platform priors from documented practice; calibrate those priors on real benchmark preferences; allow project/user overlays without silently mutating the global base skill.

A `CommercialSkill` should be a versioned editing prior and review rubric, not a magic prompt and not a claim to know a platform's hidden recommendation algorithm.

---

## 2. Preserve the scoring hierarchy

Resolver quality should remain decomposed into at least four levels.

### 2.1 Hard constraints

Binary eligibility. Examples:

- user locks / exclusions;
- mandatory provenance / rights condition;
- source-window validity;
- mandatory subject definitely absent;
- technical quality below a non-negotiable floor;
- prohibited duplicate/reuse condition;
- insufficient duration under all allowed trim rules;
- authoritative Brief fact would be contradicted.

Hard constraints are not weights. An ineligible candidate does not receive a low score; it leaves the search space.

### 2.2 Unary candidate features

How well does this candidate satisfy one EditSlot by itself?

Candidate feature families:

```text
semantic_fit
narrative_fit
subject_fit
action_fit
speech_fit
duration_fit
visual_quality
framing_fit
composition_fit
anchor_confidence
music_energy_fit
beat_event_opportunity
novelty_local
```

### 2.3 Pairwise / transition features

How well does candidate B follow candidate A?

Examples:

```text
framing_diversity
shot_size_transition
motion_continuity
motion_contrast
camera_direction_continuity
subject_continuity
audio_continuity
color / exposure discontinuity
visual_novelty
repetition_penalty
```

### 2.4 Global sequence features

Does the complete proposed sequence satisfy the creative strategy?

Examples:

```text
Brief / Script coverage
Hook strength
brand / product visibility timing
CTA coverage
proof coverage
energy curve
cut-density curve
shot-size diversity
repetition
music-section fit
mandatory locked decisions
commercial message completeness
```

A sequence of individually high-scoring Shots can still be a bad edit if its transitions and global structure are poor.

---

## 3. CommercialSkill should be structured policy, not prompt prose

A future skill should conceptually carry structured policy such as:

```text
CommercialSkill
├─ identity
│  ├─ skill_id
│  ├─ version
│  ├─ genre
│  ├─ platform_scope
│  ├─ marketing_objective
│  └─ evidence / source dates
│
├─ format_constraints
├─ creative_priors
├─ unary_feature_priors
├─ transition_priors
├─ sequence_targets
├─ music / beat policy
├─ subtitle / text policy
├─ review_rubric
├─ calibration_provenance
└─ compatibility / supersession metadata
```

Do not freeze this exact schema yet. The important part is that policy is inspectable, versioned and separable from model prompts.

---

## 4. Distinguish constraints, best-practice priors and style preferences

This distinction is essential.

### A. Format / delivery constraints

Examples:

- required aspect ratio for a selected output preset;
- safe-zone geometry;
- maximum platform file limits;
- user-declared target duration bounds.

These may be enforced deterministically where authoritative.

### B. Data-backed platform guidance

Examples from current official guidance include:

- TikTok recommends a hook / body / close structure, early value proposition, captions/text, sound, CTA, vertical creative and safe-zone awareness;
- Meta emphasizes native 9:16 Reels creative, audio and important messages inside the safe zone;
- Google Ads ABCD guidance emphasizes Attention, Branding, Connection and Direction, including getting to the point quickly, early brand/product presence, focused messaging and explicit CTA.

These should become **soft priors / review checks**, not universal hard constraints.

TikTok itself describes these as starting points and explicitly recommends continuous testing and learning. Therefore a rule such as "Hook must always be exactly 3.0 seconds" would misrepresent the source guidance.

### C. Style preferences

Examples:

- natural Vlog breathing room;
- aggressive performance-ad cut density;
- understated transitions;
- strong beat-action synchronization;
- relaxed montage;
- user preference for longer reaction holds.

These are inherently preference-like and should remain overrideable and learnable.

---

## 5. Version official platform priors

Platform advice changes.

Therefore prefer:

```text
TikTokPerformanceAdSkill@2026.08
MetaReelsAdSkill@2026.08
YouTubeVideoAdSkill@2026.08
```

rather than eternal constants such as:

```text
PRODUCT_MUST_APPEAR_BY_SECOND_2 = True
```

A skill version should record:

- source organization;
- source document;
- source update date when known;
- what was interpreted as a hard output constraint vs a soft creative prior;
- our own benchmark calibration date.

When platform guidance changes, create a new skill version rather than silently changing historical project behavior.

---

## 6. Separate platform from genre

A commercial-ad style and a Vlog style are not simply two platform presets.

The same TikTok/Reels/Shorts output format can carry very different creative intent.

Recommended decomposition:

```text
Base Editing Policy
        +
Platform Profile
        +
Genre / CommercialSkill
        +
Project Brief Overlay
        +
User Style Overlay
```

Example:

```text
PlatformProfile: TikTok vertical/safe-zone/sound/caption priors
GenreSkill: Performance Product Ad
Project: 28-second thermos campaign, emphasize 12-hour insulation
UserStyle: prefers natural voice and few transitions
```

This avoids creating a giant `TikTokStyle` that mixes technical format, ad strategy and personal taste.

---

## 7. Advertising skill priors supported by current platform guidance

A first commercial-ad skill may reasonably start with priors such as:

```text
attention early
value proposition early
product / brand visibility early enough to support the message
clear USP / proof coverage
explicit CTA
vertical-native framing for vertical presets
safe-zone-aware text
caption / overlay support
sound-aware edit
focused messaging
```

But the magnitude of each Resolver weight must still be calibrated on real benchmark edits.

The platform sources support the **direction** of these priors, not a universal numeric weight.

Google's current ABCD framework also varies recommendations by objective (awareness, consideration, action, full funnel), which strongly supports making `marketing_objective` part of the skill context rather than using one global advertisement formula.

---

## 8. Vlog skill should protect naturalness, not imitate ad density

Vlog should not inherit performance-ad weights and merely turn them down.

A Vlog skill likely needs qualitatively different priors:

```text
speech completeness ↑
emotional continuity ↑
natural reaction hold ↑
chronological / situational coherence ↑
continuity ↑
forced beat-cut density ↓
aggressive CTA requirements absent
product-first requirement absent unless Brief requires it
```

X-Cut is useful as an architectural reference because it treats `vlog-natural` and `marketing-conversion` as distinct shareable editing styles and describes a style as preserving structure, pacing, music style, dubbing preferences and other editing recipes.

Its AGPL license and generative-media paths prevent treating it as our direct product backbone, but the idea of portable, inspectable style recipes is highly relevant.

---

## 9. Avoid fixed global weights before data exists

Do not begin by permanently defining:

```text
semantic = 0.31
action = 0.19
quality = 0.18
continuity = 0.12
...
```

Such values would have no empirical basis and would be difficult to debug later.

Instead:

1. define the feature set and observable meanings;
2. establish reasonable qualitative priors;
3. create benchmark comparisons;
4. fit / tune weights against human preference;
5. preserve every calibrated version.

The first implementation may still need provisional numeric values, but those values must be labeled **baseline calibration**, not domain truth.

---

## 10. Pairwise human preference is the preferred calibration signal

Absolute questions such as:

> Rate this Shot from 0 to 100.

are often noisy and hard to calibrate between people.

For Resolver decisions, a more actionable annotation is:

```text
For EditSlot 04, which is better?
A / B / tie / neither
```

For sequence calibration:

```text
Which edit is better for the same Brief?
Version A / Version B / tie
```

This produces pairwise preference data directly aligned with Resolver ranking.

A simple first learning approach can fit an interpretable preference model from **feature differences** between preferred and rejected candidates, with regularization to avoid unstable weights.

No heavy ML training stack is required for the first calibration system. The primary objective is interpretability and benchmarkability.

---

## 11. Feature normalization must be explicit

Resolver features come from different scales:

```text
semantic cosine similarity
visual-quality score
seconds of duration error
motion magnitude
beat offset milliseconds
reuse count
```

Do not combine raw values directly.

Use two categories:

### Absolute quality / safety quantities

Used for hard thresholds or absolute penalties where meaningful, for example:

- source window outside Shot boundary;
- unacceptable technical defect;
- authoritative duration violation.

### Relative ranking quantities

Normalize within an EditSlot candidate set where appropriate, for example:

- semantic fit percentile;
- candidate visual quality relative to available alternatives;
- transition novelty relative to prior sequence.

Normalization strategy itself should be versioned with the scoring model.

---

## 12. Preserve feature contributions for explainability

Every `ResolutionDecision` should ultimately be able to answer:

> Why was this candidate chosen over the next alternative?

Conceptually record:

```text
Candidate A score = 0.84
  semantic_fit        +0.22
  action_fit          +0.19
  technical_quality   +0.13
  continuity          +0.11
  beat opportunity    +0.08
  reuse penalty       -0.03
  ...

Candidate B score = 0.79
  semantic_fit        +0.25
  action_fit          +0.10
  continuity          +0.06
  ...
```

The exact representation can change, but scoring must not become an opaque single float with no provenance.

Explainability is valuable for:

- debugging;
- benchmark failures;
- user-facing "why this clip" explanations;
- Reviewer feedback;
- calibration analysis.

---

## 13. Score uncertainty separately from score value

A high score does not necessarily mean high certainty.

Examples:

- Candidate A clearly beats all alternatives on strong local evidence → high confidence;
- Candidate A is slightly ahead because all candidates have weak visual semantics → low confidence.

Therefore preserve:

```text
score
+
confidence / uncertainty
```

Possible uncertainty indicators:

- margin between first and second candidate;
- missing feature evidence;
- low TemporalAnchor confidence;
- disagreement between lexical and dense retrieval;
- disagreement between local semantic evidence and VLM review;
- tracker / ASR / BeatMap quality.

Escalation policy:

```text
high score + high confidence
→ commit locally

small score margin + low confidence + important Slot
→ targeted strong-model review
```

This is more cost-efficient than always running an expensive critic.

---

## 14. User behavior can create a local personalization overlay

The editor will naturally receive preference evidence through revisions.

Potential local events:

```text
accepted first cut
replaced selected Shot
shortened source window
extended reaction
removed transition
reduced subtitle density
locked clip
undo AI change
preferred candidate B over A
```

These can become a local `UserStyleProfile` / project-style overlay.

Important safety rule:

> Do not silently rewrite the global CommercialSkill because one user changed three clips.

Prefer:

```text
Global skill version
        ↓
user-local preference evidence
        ↓
personalized overlay
```

Promotion of a recurring preference should require enough evidence and remain inspectable / resettable.

---

## 15. Reference videos can seed style features without becoming source footage

A user-supplied reference video may contribute style observations such as:

```text
shot-duration distribution
cut density over time
hook duration region
shot-size transition pattern
music / cut relationship
caption density
transition frequency
energy curve
```

These observations can bias a project-level style overlay.

They must not cause the reference video's protected expression or frames to become source material.

This keeps reference analysis consistent with the Product Constitution.

---

## 16. Real campaign performance is valuable but optional and separate

If the product later receives legitimate user-provided performance outcomes (retention curves, CTR, conversion metrics, etc.), these could become additional calibration evidence.

However:

- no current architecture should depend on access to advertising-account data;
- platform metrics are confounded by audience, targeting, offer, placement, budget and many other variables;
- raw campaign performance must not be treated as a clean label that one edit decision alone was correct.

Initial calibration should therefore prioritize controlled benchmark and pairwise human/editor preference data.

---

## 17. Reviewer rubric and Resolver weights are related but distinct

CommercialSkill should include a Review rubric, but Reviewer score should not simply duplicate Resolver's weighted sum.

Resolver asks:

> Which available candidate sequence should I choose before rendering?

Reviewer asks:

> Did the resulting edit actually satisfy the Brief and creative goals?

Review dimensions may include:

```text
Brief adherence
Hook effectiveness
message clarity
product / brand clarity
proof quality
CTA clarity
pacing / naturalness
continuity
music fit
watchability
technical quality (from local QC, not duplicated by VLM)
```

A Reviewer failure should identify the affected owner / slot so that only necessary decisions are recomputed.

---

## 18. Specialized editing evaluators are emerging, but generic VLM judging is not enough

Recent 2026 benchmarks reinforce the need to keep evaluation multidimensional:

- VEBench evaluates editing knowledge and operational reasoning, including selecting and temporally localizing clips from multiple candidates, and reports a substantial gap between current multimodal models and human editing cognition.
- VEFX-Bench separates instruction following, rendering quality and edit exclusivity; its authors report a specialized editing reward model aligning better with human judgment than generic VLM judges for its task domain.

These benchmarks do not exactly match our captured-footage / commercial-short-video constitution, so they should inform evaluation design rather than become a final product metric.

The key lesson is:

> Do not collapse editorial quality into one generic "AI thinks it looks good" score.

---

## 19. Calibration dataset hierarchy

Recommended long-term evidence hierarchy:

### Level 1 — deterministic engineering labels

- valid / invalid source window;
- speech clipped / not clipped;
- hard continuity violation;
- technical defect;
- lock violation.

### Level 2 — expert / user pairwise candidate preferences

- better Shot for same EditSlot;
- better IN/OUT CandidateWindow;
- better transition pair.

### Level 3 — sequence preference

- A/B whole-edit preference for same Brief;
- dimension-specific reason codes.

### Level 4 — longitudinal user preferences

- repeated revision behavior;
- accepted style decisions;
- explicit saved style.

### Level 5 — optional real-world performance evidence

Only when available and interpreted cautiously.

---

## 20. Benchmark metrics for Resolver calibration

Candidate-level metrics:

- Top-1 preference agreement;
- pairwise preference accuracy;
- NDCG / ranking consistency when ordered annotations exist;
- score margin on easy vs ambiguous examples;
- VLM escalation rate;
- average cost per Slot.

Sequence-level metrics:

- pairwise human preference win rate;
- Script / Brief coverage;
- Hook / CTA / proof rubric;
- continuity defects;
- pacing preference;
- beat/action synchronization preference;
- user override rate;
- API cost and wall time.

A lower API cost is only an improvement if editing quality is preserved.

---

## 21. CommercialSkill update process

Do not let a model silently self-modify production weights.

A new skill version should follow a deliberate path:

```text
new platform guidance / research / benchmark evidence
        ↓
proposed skill changes
        ↓
benchmark A/B
        ↓
human review
        ↓
versioned skill release
```

Old project revisions must remain reproducible against the skill version used at the time.

---

## 22. Current recommended control stack

```text
Base technical rules
        ↓
PlatformProfile
        ↓
Genre / CommercialSkill
        ↓
MarketingObjective
        ↓
Project Brief / reference-style overlay
        ↓
User preference overlay
        ↓
Resolver feature model
        ↓
sequence optimizer
```

This stack allows a user to request:

> natural Vlog for TikTok

without automatically receiving:

> performance-ad pacing merely because the platform is TikTok.

---

## 23. Current upstream/source notes

High-value sources reviewed in this phase:

- TikTok official Creative Best Practices / Creative Codes — Hook/body/close, early proposition, captions/text, sound, CTA, vertical/safe-zone guidance; TikTok explicitly frames best practices as starting points to test and learn.
- Meta for Business Reels Ads — 9:16 vertical creative, audio and key messages in the safe zone; A/B testing is part of the recommended workflow.
- Google Ads ABCDs — Attention, Branding, Connection, Direction and objective-specific variations; Google Creative Guidance automatically checks selected creative attributes such as early logo visibility, duration, voice-over and aspect ratios.
- X-Cut — AGPL research reference for portable style recipes, including separate `marketing-conversion` and `vlog-natural` concepts and preserving structure/pacing/music/dubbing preferences.
- VEBench (2026) — realistic editing operational-reasoning benchmark with clip selection and temporal localization tasks.
- VEFX-Bench / VEFX-Reward (2026) — multidimensional editing evaluation and specialized reward-model evidence.
- HIVE / DramaAD (2025) — decomposes automatic short-video editing into narrative-aware highlight/opening-ending/pruning subtasks and includes professionally edited advertisement clips in its benchmark.

No source here proves a universal numeric Resolver weight. Numeric calibration remains our benchmark responsibility.

---

## 24. Current conclusion

The Resolver should not become a bag of constants.

The strongest current direction is:

> **structured evidence features + versioned skill priors + pairwise human preference calibration + user-local overlays + explicit uncertainty + deterministic sequence optimization.**

CommercialSkill tells the system what editing qualities to prefer and how to review them; it does not directly own Shot identity, source timestamps, or the final EDL.
