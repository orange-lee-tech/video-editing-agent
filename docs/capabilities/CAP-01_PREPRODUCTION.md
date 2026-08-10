# CAP-01 — Pre-production: Brief, ScriptPlan, ShootingPlan

**Status:** CANDIDATE CAPABILITY SPEC  
**Architecture:** `ARCHITECTURE_CONTRACT_V0.2.md`  
**Scope:** User intent → executable ScriptPlan → practical ShootingPlan → coverage expectations

---

## 1. Purpose

Pre-production exists to make the final edit possible before the user presses Record.

The product is not merely an editor that reacts to whatever footage happens to exist. It should help an ordinary user capture enough purposeful coverage that the later Resolver has real choices without remote/generated visual fallback.

---

## 2. Ownership

```text
BriefService      → Brief
ScriptPlanner     → ScriptPlan
ShootingPlanner   → ShootingPlan / ShotRequirement
CoverageService   → derived CoverageState
```

LLM/Agent implementations produce proposals only.

```text
model
→ Proposal DTO
→ schema validation
→ deterministic/product validation
→ owner commit
```

---

## 3. Brief

Brief captures:

- objective;
- product/topic;
- platform/output context;
- audience;
- target duration;
- core message;
- authoritative facts/claims/prices/specifications;
- style/emotion;
- success criteria;
- prohibited content;
- brand constraints;
- user notes;
- references.

Brief must not contain source timestamps or executable editing state.

Authoritative commercial facts are protected downstream and cannot be silently rewritten by Director/Reviewer.

---

## 4. Reference material

Reference videos/copy may be used to analyze:

- hook strategy;
- narrative structure;
- pacing;
- shot-duration distribution;
- framing/transition patterns;
- caption density;
- music/cut relationship;
- energy curve;
- reusable production technique.

A reference video defaults to `reference_analysis_only` and is not Resolver-eligible source footage unless the user explicitly reclassifies/imports it for editable use and records rights intent.

Reference analysis should imitate technique/structure, not protected expression.

---

## 5. ScriptPlan

ScriptPlan is an executable production document, not one prose paragraph.

A NarrativeSection should be capable of expressing:

```text
narrative role
information goal
spoken narration/dialogue
visual requirement
target duration
subtitle/on-screen text intent
emotion
pacing
music intent
editing intent
importance
locks/protected facts
```

The exact schema may evolve, but distinct semantics must remain separate rather than compressed into generic prompt text.

---

## 6. Script revision and locking

Natural-language revision creates a new structured revision.

Examples:

- strengthen first three seconds;
- remove one claim;
- shorten total duration;
- use younger wording;
- preserve section 2 exactly.

Locked approved sections survive later automatic planning unless the user explicitly unlocks them.

---

## 7. ShootingPlan

ShootingPlan converts narrative need into production requirements.

Before planning, use known production constraints where relevant:

- phone/camera;
- tripod/stabilizer;
- lighting;
- microphones;
- number of people;
- available location/time;
- user skill level.

Default language should be executable by ordinary users.

Prefer:

> Move the phone close to the product, hold for about two seconds, then move slowly left to right.

rather than unexplained cinematography jargon.

---

## 8. ShotRequirement

A requirement describes what should be captured, not which actual Shot will be used.

Conceptual dimensions:

```text
purpose
subject/action
environment
framing/camera motion
target/minimum duration
audio/dialogue requirement
continuity hint
visual constraints
priority
backup intent
```

Priorities support at least:

```text
required
recommended/preferred
optional
backup
```

Visual `remote_allowed`, `remote_only`, `generated_allowed` are not valid active source policies in v0.2.

---

## 9. Coverage strategy

ShootingPlan SHOULD deliberately request:

- extra handles before/after action;
- alternate angle;
- wide/medium/close coverage when useful;
- clean product shot;
- backup take;
- room tone/source sound where relevant.

The goal is not minimum shot count. The goal is enough editable alternatives at reasonable shooting effort.

---

## 10. CoverageState

After ingest/analysis, CoverageService evaluates each requirement using actual eligible user footage.

Suggested states:

```text
unmatched
weak
satisfied
overcovered
```

A required unmet visual requirement becomes a user-visible production gap.

Preferred response:

```text
what is missing
why current footage is insufficient
what extra shot to capture
practical reshoot instruction
```

No automatic public stock/generative visual substitution.

---

## 11. Existing-footage mode

The default causality is:

```text
Brief → ScriptPlan → ShootingPlan → Footage
```

But users may already have footage.

In that case the Planner may inspect existing coverage and adapt production advice while keeping the same ownership model:

- existing footage does not rewrite Brief facts;
- useful unplanned footage may later be used by Director/Resolver;
- Script/Shooting plans remain semantic plans, not direct source selectors.

---

## 12. AI cost discipline

Text planning is usually cheap relative to video analysis.

Reference-video analysis should still be coarse-to-fine:

```text
local probe / shot summary
→ targeted reference observations
→ structured style/strategy evidence
→ planning model
```

Do not repeatedly upload the same reference video on every wording revision when cached structure evidence is sufficient.

---

## 13. Review gates

### Script review

Check:

- Brief coverage;
- protected facts;
- target duration plausibility;
- hook/value/proof/CTA logic as applicable;
- narrative coherence;
- missing production assumptions.

### Shooting review

Check:

- executable with declared equipment;
- all required sections have coverage plan;
- adequate handles/alternatives;
- no impossible/unexplained camera requirement;
- no unconstitutional visual fallback.

---

## 14. Product benchmarks

Useful benchmark tasks:

- Brief → Script pairwise human preference;
- Script factual fidelity;
- estimated vs actual spoken duration;
- ordinary-user shooting-plan executability;
- post-shoot required-coverage success rate;
- reshoot rate;
- percentage of final EDLSegments supported by planned vs useful unplanned coverage;
- user override/lock behavior.

---

## 15. Not frozen here

- exact text model/provider;
- prompt wording;
- NarrativeSection field names;
- how many alternate takes to request;
- platform-specific hook durations;
- autonomy approval matrix.

Those belong to provider configs, CommercialSkill, benchmarks and Autonomy Policy.
