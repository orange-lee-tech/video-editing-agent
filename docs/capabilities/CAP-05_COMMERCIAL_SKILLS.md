# CAP-05 — Commercial Skills, Platform Profiles and Preference Calibration

**Status:** CANDIDATE CAPABILITY SPEC  
**Architecture:** `ARCHITECTURE_CONTRACT_V0.2.md`  
**Scope:** Editing priors / platform constraints / genre policy / user preference → Resolver and Review policy

---

## 1. Purpose

CommercialSkill turns editing craft into inspectable, versioned policy instead of a hidden prompt or a pile of magic constants.

It answers:

> What qualities should this kind of video prefer, and how should we evaluate them?

It does not own media identity, source timestamps or EDL.

---

## 2. Policy stack

Recommended composition:

```text
Base Editing Policy
+
PlatformProfile
+
Genre / CommercialSkill
+
MarketingObjective
+
Project Brief Overlay
+
Reference Style Overlay
+
UserStyle Overlay
```

This keeps technical format, platform guidance, genre craft and personal taste separate.

---

## 3. PlatformProfile

Represents versioned platform/output facts and guidance.

Potential content:

- aspect ratio/output presets;
- safe-zone information;
- caption/text layout considerations;
- sound-first/sound-supported guidance;
- current official creative best-practice evidence;
- evidence source/date;
- what is a hard technical constraint vs soft creative prior.

Do not encode platform folklore as eternal constants.

---

## 4. Genre Skill

Examples:

```text
PerformanceProductAd
ProductDemo
NaturalVlog
NarrativeVlog
```

Different genres may use the same TikTok/Reels/Shorts PlatformProfile but strongly different pacing/continuity/CTA policies.

---

## 5. MarketingObjective

Commercial ads may vary by:

- awareness;
- consideration;
- conversion/action;
- full-funnel/mixed objective.

Objective can alter priorities without inventing a new platform style.

---

## 6. Skill content

A versioned skill may contain:

```text
identity/version
platform/genre/objective compatibility
format constraints
creative priors
unary feature priors
transition priors
global sequence targets
music/beat policy
spatial/reframe policy
subtitle/text policy
review rubric
calibration provenance
supersession metadata
```

Exact schema is implementation work.

---

## 7. Performance-ad priors

Reasonable qualitative starting directions include:

- early attention/value;
- clear product/brand when relevant;
- proof/demonstration coverage;
- focused messaging;
- explicit CTA when Brief requires;
- stronger visual-energy/cut-density tolerance;
- useful action/music opportunities;
- safe-zone-aware text;
- narration intelligibility.

These are priors, not guaranteed platform-ranking rules.

---

## 8. Vlog priors

Natural Vlog should not be “ad weights × 0.5”.

Possible priorities:

- speech completeness;
- chronology/situational coherence;
- emotional continuity;
- natural reaction holds;
- source-audio continuity;
- breathing room;
- restrained forced beat sync;
- less aggressive transition density.

CTA/product-first rules apply only if the Brief requires them.

---

## 9. Reference-style overlay

A user reference video may seed project-local style observations:

- shot-duration distribution;
- cut density;
- framing transitions;
- caption density;
- music/cut relationship;
- energy curve;
- transition frequency.

These observations bias policy only for the project/style context.

Reference media remains analysis-only unless explicitly imported as editable footage.

---

## 10. UserStyleProfile

Repeated user behavior can become local preference evidence.

Examples:

- repeatedly extend reaction shots;
- remove dissolves;
- prefer fewer subtitles;
- choose wider crop;
- replace energetic BGM with quieter track;
- lock natural source sound.

Promotion into UserStyle should require repeated evidence and remain:

- inspectable;
- resettable;
- exportable where practical;
- separated from global skill versions.

Never silently modify global CommercialSkill from one user’s edits.

---

## 11. No magic global weights

Do not freeze arbitrary constants such as:

```text
semantic=.31
action=.19
continuity=.17
```

Preferred lifecycle:

```text
define interpretable features
→ qualitative priors
→ benchmark comparisons
→ pairwise human preference labels
→ fit/tune interpretable weights
→ version release
```

A provisional implementation weight is a baseline calibration, not Domain truth.

---

## 12. Pairwise preference calibration

Preferred annotation:

```text
For this same EditSlot, A or B?
A / B / tie / neither
```

and:

```text
For the same Brief, which full edit is better?
A / B / tie
+ dimension reason codes
```

Feature differences can train/tune a simple interpretable ranking/preference model before considering heavier ML.

---

## 13. Feature normalization

Features have different scales.

Separate:

### absolute constraints/penalties

- invalid range;
- rights violation;
- duration outside hard bound;
- technical defect.

### relative candidate features

- semantic percentile;
- visual-quality rank;
- novelty relative to available alternatives;
- transition quality relative to current sequence.

Normalization version is part of the policy/model provenance.

---

## 14. Reviewer rubric vs Resolver weights

They are related but not identical.

Resolver asks:

> Which available candidate sequence should we choose?

Reviewer asks:

> Did the resulting edit satisfy Brief and craft goals?

A PerformanceAd review may score dimensions such as:

- Brief/fact adherence;
- Hook;
- product/brand clarity;
- value/proof;
- CTA;
- pacing;
- continuity;
- music fit;
- watchability.

Vlog rubric may emphasize naturalness/emotion/speech continuity instead.

---

## 15. Version update process

```text
new official guidance / research / benchmark evidence
→ proposed skill revision
→ benchmark A/B
→ human review
→ versioned release
```

Old projects keep the skill version they used for reproducibility.

A model cannot self-modify production policy silently.

---

## 16. Campaign performance data

Optional user-provided metrics such as retention/CTR/conversion may inform future calibration, but they are confounded by audience, targeting, offer, placement and budget.

Do not treat raw campaign outcome as a clean label that one edit decision was correct.

Initial calibration prioritizes controlled pairwise editorial preference.

---

## 17. Benchmarks

- pairwise candidate agreement;
- pairwise transition agreement;
- full-edit human win rate;
- user override/undo rate;
- dimension-specific Review scores;
- commercial fact/coverage success;
- API cost at equal human preference;
- cross-user generalization vs UserStyle benefit.

---

## 18. Not frozen here

- initial numeric weights;
- exact skill schema;
- exact platform rule values;
- how many preference labels are enough;
- learning/ranking algorithm;
- automatic UserStyle promotion threshold.
