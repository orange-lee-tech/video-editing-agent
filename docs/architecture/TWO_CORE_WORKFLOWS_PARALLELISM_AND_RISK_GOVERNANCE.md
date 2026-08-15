# Two Core Workflows Parallelism and Risk Governance

**Status:** SUPERVISORY ARCHITECTURE GUIDANCE — non-normative until explicitly adopted  
**Date:** 2026-08-15  
**Repository:** `orange-lee-tech/video-editing-agent`  
**Observed baseline:** `d84a99cafdad6ac552a9521ba593e65560a3e033`  
**Authority boundary:** This document does **not** supersede `docs/product/PRODUCT_CONSTITUTION_V1.0.md`, accepted Architecture Contracts, capability specifications, ADRs, or active Work Orders. It records a product-alignment correction and risk-control guidance for later explicit adoption.

---

## 0. Why this document exists

The project has exactly two primary product capabilities:

1. **Pre-production creation** — user goal/reference → structured ScriptPlan → executable ShootingPlan.
2. **Post-production editing** — user-supplied local footage → understanding → editorial decisions → EDL → render → first cut/revision.

The Product Constitution already defines them as two primary capabilities, and the Stage-A 100% gate now separately requires the planning core and editing core to be genuinely operable through an ordinary user-facing path.

However, the current Architecture Contract still presents one durable product workflow as a single sequence:

```text
Brief
→ ScriptPlan
→ ShootingPlan
→ user footage
→ Understanding
→ Director / Resolver
→ EDL
→ Renderer
→ Review
→ Final output
```

That sequence is valid as the **combined full-lifecycle mode**, but it should not be interpreted as the only legal product entry path.

A concrete implementation-level coupling remains in the current `EditPlan` model: `script_plan_ref` and `shooting_plan_ref` are mandatory. That makes planning artifacts behave like prerequisites for editing, even though the product definition requires post-production editing to be independently usable on unordered user footage.

The correction therefore is **not** a full-stack redesign. It is a bounded removal of an unnecessary upstream dependency while preserving all valuable downstream authority boundaries, provenance, determinism and safety.

---

# 1. Target product structure: two entries, one editing kernel, optional composition

The durable product structure should be understood as:

```text
                       User Goal
                          │
                        Brief
                   ┌──────┴──────┐
                   │             │
                   ▼             ▼
            Planning Core    Editing Core
            AI Director      AI Video Editor
                   │             │
             ScriptPlan      User Footage
                   │             │
            ShootingPlan     Understanding
                   │             │
                   └── optional ─┤
                         context │
                                 ▼
                              EditPlan
                                 ↓
                      Retrieval / Resolver
                                 ↓
                  Music / Reframe / Audio
                                 ↓
                                EDL
                                 ↓
                             Renderer
                                 ↓
                              Review
```

The key invariant is:

> **Planning may enrich Editing, but Planning must not be the activation license for Editing.**

The product should support three legitimate modes:

### 1.1 Planning-only mode

```text
Goal / reference / commercial constraints
→ Brief
→ ScriptPlan
→ ShootingPlan
```

The user may stop here, shoot manually, or hand the plan to another editor.

### 1.2 Editing-only mode

```text
Goal / lightweight Brief
+ unordered local footage
→ Media Understanding
→ Director / Resolver
→ Music / Spatial / Audio
→ EDL
→ Renderer
→ Final MP4
```

The user must not be forced to fabricate ScriptPlan or ShootingPlan artifacts merely to satisfy schema requirements.

### 1.3 Combined mode

```text
Goal / reference
→ Brief
→ ScriptPlan
→ ShootingPlan
→ user shoots
→ same Editing Core
→ Final MP4
```

Combined mode is composition of the two cores, not a third editing implementation and not the only supported workflow.

---

# 2. Shared root: Brief, not ScriptPlan

The safest common root for both primary capabilities is the existing `Brief` concept.

`Brief` already carries the information both modes need:

- objective;
- audience;
- platform;
- core message;
- target duration;
- product/topic;
- authoritative commercial facts;
- style/emotion;
- success criteria;
- prohibited content;
- brand constraints;
- notes;
- references.

This makes it a suitable shared intent authority for both Planning and Editing.

A user entering Editing-only mode may provide a lightweight request such as:

```text
30 seconds
Douyin product ad
highlight fast heating
young, energetic style
```

The system may normalize that into a Brief and proceed directly into Editing Core.

The architecture must avoid the opposite failure mode: removing Script/Shooting dependencies and then allowing Editing to operate with no explicit editorial intent at all. Parallelism must not become “upload footage and let the model guess the product goal.”

---

# 3. Safe restoration of parallelism: compatibility migration, not abrupt refactor

The current coupling is localized enough that the correction should have a small blast radius. The downstream architecture already largely works from `EditPlan`, `ResolutionDecision`, `Shot`, decisions, EDL and Renderer rather than directly depending on ScriptPlan/ShootingPlan.

Therefore, the migration should be staged and bounded.

## 3.1 Do not mix this correction with the active subtitle closure

The active subtitle frontier has independent execution-authority issues such as ASS time representability, subtitle layer semantics and path escaping evidence.

Do not modify EditPlan provenance semantics in the same Work Order or commit that closes subtitle execution guards.

Reason: if tests or probes fail, mixed changes make fault attribution difficult and enlarge the rollback surface.

## 3.2 Correct product/architecture semantics before broad implementation changes

After subtitle closure, explicitly distinguish three workflow meanings in architecture/control documentation:

- Planning Workflow;
- Editing Workflow;
- Combined Workflow.

The current single end-to-end diagram should be treated as Combined Workflow, not the unique legal entry path.

## 3.3 Evolve EditPlan with backward compatibility

Do **not** simply delete provenance fields.

Desired semantics are conceptually:

```text
EditPlan
├─ editing intent / Brief provenance       required
├─ script_plan_ref                         optional context
├─ shooting_plan_ref                       optional context
└─ slots                                   required
```

Exact field shape should be chosen by the implementation owner, but the semantic requirements are:

- Editing-only plans can exist without ScriptPlan/ShootingPlan.
- Combined-mode plans retain exact ScriptPlan/ShootingPlan revision references.
- Existing serialized EditPlan data remains readable.
- Historical revisions are not silently rewritten.
- New schema versions round-trip deterministically.
- Protected commercial facts and user locks remain enforceable downstream.

A versioned read adapter / migration path is preferable to destructive rewrite.

## 3.4 Two Application entry points, one Editing Core

Application orchestration should expose independent entry points such as:

```text
PlanningWorkflow
EditingWorkflow
```

A combined user journey may call PlanningWorkflow and then pass its resulting artifacts as context into EditingWorkflow.

Do not create separate Resolver, EDLBuilder or Renderer implementations for combined mode.

The single Editing Core should remain the reusable kernel.

## 3.5 Required workflow probes

Parallelism should be proven with three independent product-facing probes:

### Planning-only probe

```text
real user intent/reference/commercial constraints
→ real planning pipeline
→ persisted ScriptPlan
→ persisted executable ShootingPlan
```

### Editing-only probe

```text
lightweight Brief
+ unordered local footage
→ actual VisualUnderstanding/evidence
→ real Director / Retrieval / Resolver
→ music / spatial / audio as applicable
→ canonical EDL
→ real Renderer
→ final MP4
```

No hand-authored coverage text, ResolutionDecision or EDL may substitute for an automatic step the probe claims to validate.

### Combined probe

```text
Planning artifacts
→ same EditingWorkflow
→ final MP4
```

This probe must demonstrate reuse of the editing-only kernel rather than a second hidden implementation.

---

# 4. Long-chain risk amplification

The engineering chain is intentionally long because each stage owns a distinct kind of authority:

```text
Brief
→ Understanding
→ Retrieval
→ Resolver
→ Reframe
→ Music
→ Audio
→ EDL
→ Renderer
→ Review
```

The main systemic risk is not one module making one error. It is a small upstream error being repeatedly interpreted as certain by downstream stages until the final output is structurally valid but semantically wrong.

Typical failure cascade:

```text
VisualUnderstanding slightly wrong
→ Retrieval over-trusts observation
→ Resolver chooses wrong source
→ Reframe optimizes wrong subject
→ EDL remains perfectly valid
→ Renderer succeeds
→ final video is technically PASS but editorially wrong
```

The system therefore needs a hard rule:

> **Upstream uncertainty may propagate downstream, but downstream stages must not erase uncertainty and pretend it became fact.**

Where confidence/evidence is insufficient, allowed responses include:

- lower score;
- alternative candidate;
- targeted re-observation;
- fallback method;
- user approval;
- unresolved state.

The system must always retain the right to return `unresolved` rather than guess.

---

# 5. Safe redundancy: duplicate evidence and verification, not authority

Redundancy is useful only when it does not create competing sources of truth.

## 5.1 Good redundancy

### Evidence redundancy

Visual analysis, ASR, VAD, motion, tracking and user labels may corroborate one another.

### Provider redundancy

Multiple VLM/LLM providers may implement the same Port, with explicit provenance and capability reports.

### Execution verification redundancy

Preview and final Renderer may independently expose execution defects while reading the same canonical EDL.

### Validation redundancy

A producer validates its own output; critical consumers revalidate the invariants they depend on.

## 5.2 Bad redundancy

Do not create multiple competing timeline authorities:

```text
LLM timeline
Resolver timeline
Preview timeline
Renderer timeline
```

The durable authority should remain:

```text
ResolutionDecision
→ EDLBuilder / TimelineAllocator
→ Canonical EDL
→ Preview / Renderer
```

Preview and Renderer may implement different execution backends, but neither may silently invent editorial state that differs from canonical EDL.

---

# 6. Defect-by-defect improvement guidance

## 6.1 Core capabilities accidentally serialized into one dependency chain

**Risk:** Editing loses standalone value and real users with existing footage are forced through fake planning artifacts.

**Correction:** Use Brief/editorial intent as shared root; make ScriptPlan/ShootingPlan optional enrichment context for Editing; expose two independent entry points.

**Do not:** Build two different editing engines or remove provenance entirely.

---

## 6.2 Architecture complexity is high

**Risk:** Small feature work touches many layers, raises regression probability and increases cognitive load.

**Correction:** Keep the current intentionally small set of top-level Domain Entities. New discoveries should default to Value Objects, Derived Artifacts, Decisions or Ports unless durable identity/revision ownership truly requires entity status.

**Do not:** Add a new Entity/Subsystem for every new feature. In particular, this correction does not justify inventing `WorkflowModeEntity`, a second project model, or a duplicate pipeline hierarchy.

The solution to complexity is not removing useful boundaries. It is making those boundaries limit blast radius.

---

## 6.3 Long chain amplifies small errors

**Risk:** Wrong evidence becomes wrong selection, then a perfectly executable wrong final video.

**Correction:** Preserve confidence, uncertainty, evidence_refs and provenance across stage boundaries. Use hard eligibility before soft ranking. Permit targeted re-analysis, alternatives and unresolved outcomes.

**Do not:** Let downstream AI silently infer missing upstream facts.

---

## 6.4 Module PASS can be confused with product PASS

**Risk:** Every component is green while the real user flow is broken.

**Correction:** Maintain permanent living integration smoke tests and separate real Product Probes. Stage-A 100% must require both core workflows to operate through a normal user path.

**Do not:** Treat unit tests, isolated probes, hand-authored internal artifacts or synthetic fixtures as proof of one-click product behavior.

---

## 6.5 Integration risk appears late

**Risk:** Interfaces look compatible in isolation but fail when real artifacts are connected.

**Correction:** Grow one inexpensive “living spine” continuously:

```text
Resolver → EDL → Renderer
↓
Understanding → Resolver → EDL → Renderer
↓
Understanding + Music + Reframe + Subtitle
→ EDL → Renderer
↓
Review → smallest-owner repair → affected-only recompute
```

**Do not:** Wait until R0.16 to connect previously isolated modules for the first time.

Living Smoke protects engineering continuity. Product Probe validates actual product usefulness. They are complementary, not interchangeable.

---

## 6.6 AI/editorial quality is unstable

**Risk:** Technically correct output can still be aesthetically poor or commercially ineffective.

**Correction:** Treat most early quality defects first as evidence, policy, calibration, scoring, CommercialSkill, UserStyle or benchmark problems. Use Human preference and real-video benchmark history in Product Refinement.

**Do not:** Change architecture whenever a video “does not look good.” Promote a problem to an architecture change only when evidence proves current representation/authority boundaries cannot express the needed behavior.

Examples:

- subtitle aesthetics → style/policy/font/layout calibration first;
- weak pacing → CommercialSkill / sequence scoring / BeatMap weighting first;
- poor shot choice → locate whether failure is Understanding, Retrieval, CandidateWindow or Resolver before changing ownership.

---

## 6.7 FFmpeg/libass has representational limits

**Risk:** Backend limitations leak upward and corrupt canonical semantics.

**Correction:** Keep FFmpeg/libass as adapters. If a canonical EDL value cannot be represented faithfully by the selected backend, fail closed with stable diagnostics or explicitly route through an approved compatible representation.

**Do not:** Weaken Canonical EDL semantics to match FFmpeg/ASS convenience.

The subtitle centisecond issue is the correct governance example: exact rational EDL time must not be silently rounded merely because ASS uses centisecond timing.

Future backends may coexist:

```text
Canonical EDL
       │
 ┌─────┴─────┐
 ▼           ▼
FFmpeg    Future Renderer
```

The editing brain remains upstream and backend-neutral.

---

## 6.8 Preview and final render can diverge

**Risk:** User approves a preview but exported MP4 differs.

**Correction:** Preview and Renderer consume the same canonical EDL and source-time mapping. Add explicit preview↔final equivalence tests for representative timelines, spatial transforms, subtitles and audio behavior.

**Do not:** Let Preview maintain independent editorial timeline state.

---

## 6.9 External AI/API providers are unstable

**Risk:** Provider outage, latency, model drift or schema drift can break product behavior.

**Correction:** Keep provider-neutral Ports; persist provider/model/tool provenance; use timeout/retry/capability reporting; cache durable evidence where valid; define degraded fallback behavior.

**Do not:** Allow provider responses to directly become Domain Authority or mutate the timeline.

---

## 6.10 Increasing automation increases failure velocity

**Risk:** Full Auto can execute wrong decisions faster and with less visibility.

**Correction:** Keep locks, confidence thresholds, user approvals where risk warrants them, ReviewFindings, unresolved states and mode-specific autonomy policy.

**Do not:** Remove human gates simply to maximize automation percentage.

Product priority remains final video quality and controllability ahead of raw automation level/speed.

---

## 6.11 Schema evolution can break old projects

**Risk:** Making EditPlan provenance optional or adding new workflow semantics may make historical data unreadable or reinterpret its meaning.

**Correction:** Versioned schema, backward reader, deterministic round-trip, migration probes, immutable history/revision semantics.

**Do not:** Rewrite historical persisted artifacts in place merely to make them look like the new design.

---

## 6.12 Automatic Review can create new problems while fixing old ones

**Risk:** Reviewer fixes one visual defect by silently changing unrelated decisions or rebuilding the entire project.

**Correction:** `ReviewFinding → smallest responsible owner → affected-only stale/recompute`. Preserve locks and unaffected decisions.

**Do not:** Give Reviewer direct unrestricted authority to rewrite EDL or rerun every upstream capability.

---

## 6.13 Feature growth can turn the project into a generic media framework

**Risk:** Architecture construction becomes the product, while user-facing outcomes stagnate.

**Correction:** Every Stage-A feature must clearly serve either Planning Core, Editing Core, or the safe composition of both. Prefer bounded editing-expression floors over broad generic engines.

**Do not:** Build abstractions “because future editors may need them” without a current core-workflow requirement or measured benchmark.

---

# 7. Degradation ladders: every high-risk capability should fail safely

Each major AI/media capability should eventually define a preferred → degraded → manual → unresolved ladder.

## 7.1 Spatial / Auto Reframe example

```text
subject tracking
↓ failure / insufficient confidence
static semantic crop
↓ failure
non-generative layout/letterbox fallback
↓ failure
manual crop request or alternate Shot
↓ failure
unresolved
```

## 7.2 Music example

```text
rights-aware automatic provider
↓ unavailable
user-local music
↓ unavailable
valid no-BGM first cut / request music
```

## 7.3 Visual Understanding example

```text
primary VLM
↓ failure
alternate compatible provider / cached durable evidence
↓ failure
local coarse evidence
↓ insufficient
unresolved / user guidance
```

The critical safety rule is:

> A mature system is allowed to fail explicitly. It must never be forced to invent confidence because the pipeline design has no unresolved state.

---

# 8. Blast-radius control as the main answer to engineering complexity

The project should not aim to minimize the number of architectural layers at all costs.

Useful boundaries such as Evidence → Decision → EDL → Renderer are safety barriers.

The real optimization target is:

```text
change one owner
→ stale only its dependent artifacts
→ recompute only affected slots/ranges
→ preserve all unaffected approved state
```

For example, a SpatialComposer change should ideally invalidate ReframeDecision and dependent EDL transform execution for affected selections, not force ASR, ScriptPlanning and unrelated ResolutionDecisions to rerun.

This is why affected-owner / affected-slot / affected-range recompute and Review routing are strategically important in later roadmap phases.

---

# 9. UI should reinforce the architecture rather than accidentally re-serialize it

The minimum Windows product entry point should make both primary capabilities first-class choices.

Conceptually:

```text
What do you want to do?

[ Plan what to shoot ]
Goal / Reference → ScriptPlan → ShootingPlan

[ I already have footage ]
Footage + Goal → Auto Editing → MP4

[ Continue project ]
```

After Planning finishes, the UI may offer:

```text
Continue with this plan to editing
```

That action enters the **same Editing Core**.

Avoid implementing the product as one mandatory wizard that forces every user through Planning screens before Editing. UI structure can either preserve or destroy architectural parallelism.

---

# 10. Codex usage and implementation economy

Because local Codex quota is scarce, architectural reasoning and migration design should be completed by the main ChatGPT/GitHub supervision path before Codex receives implementation work.

Codex is best reserved for:

- local multi-file EditPlan/schema compatibility changes;
- persistence migration/read compatibility;
- Windows runtime work;
- real media execution;
- tests and probes;
- FFmpeg/libass integration;
- iterative CI/runtime debugging.

Do not spend Codex quota on:

- rediscovering architecture intent;
- broad repo reading;
- deciding whether Planning and Editing should be parallel;
- rewriting governance documents;
- open-ended research.

A future bounded Codex Work Order should be implementation-ready before invocation.

---

# 11. Recommended execution sequence

To minimize systemic risk, the preferred order is:

1. Finish the active subtitle execution-authority closure without unrelated architecture changes.
2. Explicitly adopt the product semantic correction: Planning and Editing are independent primary workflows; Combined mode composes them.
3. Update architecture/capability wording narrowly so the existing full-chain diagram is not interpreted as the only legal entry path.
4. Design a versioned, backward-compatible EditPlan provenance evolution.
5. Implement the smallest code change needed to permit Editing-only plans while preserving Combined-mode provenance.
6. Add Planning-only, Editing-only and Combined workflow tests/probes.
7. Keep all existing Resolver, EDLBuilder and Renderer authority boundaries unless a failing test proves a real incompatibility.
8. Grow the living integration spine continuously as remaining R0.12–R0.16 capabilities are added.
9. Expose the two core workflows as independent paths in the minimum Windows user entry point.
10. At Stage-A 100%, require both workflows to pass real Product Probes through that ordinary user path.

---

# 12. Acceptance criteria for the parallelism correction

The correction should be considered structurally successful only if all of the following are true:

- Planning-only works without invoking Editing.
- Editing-only works without creating fake ScriptPlan/ShootingPlan artifacts.
- Combined mode retains exact planning provenance and uses the same Editing Core.
- A meaningful Brief/editorial intent remains required or derived explicitly for editing.
- Existing persisted EditPlan data remains readable.
- No historical revision is silently rewritten.
- Resolver ownership is unchanged unless evidence proves otherwise.
- EDLBuilder remains sole exact timeline constructor.
- Canonical EDL remains the unique executable timeline authority.
- Renderer remains an execution adapter and does not absorb editorial ownership.
- Existing protected facts, locks, rights/provenance and fail-closed behavior are preserved.
- New independent workflow probes pass.
- Full quality gate remains green.
- The change can be reverted or isolated without invalidating unrelated media/render infrastructure.

If the proposed correction requires a large rewrite of Resolver, EDL, Renderer, media understanding or storage unrelated to EditPlan provenance, stop and reassess: the blast radius is likely larger than justified by the actual defect.

---

# 13. Long-term supervisory checklist

For every future significant change, reviewers should ask:

1. Does this change serve Planning Core, Editing Core, or their safe composition?
2. Does it accidentally make one core workflow a prerequisite for the other?
3. Does it introduce a second authority for data that already has one owner?
4. Can upstream uncertainty remain visible downstream?
5. Is there a safe fallback or unresolved state?
6. What is the blast radius if this component is wrong?
7. Can repair/recompute be localized to the smallest responsible owner/slot/range?
8. Does the real integration spine exercise this capability, or only an isolated unit probe?
9. Is Engineering PASS being mistaken for Product PASS?
10. Is a backend/provider limitation leaking into Domain semantics?
11. Is schema evolution backward compatible and historically reproducible?
12. Is this architectural change genuinely necessary, or is the problem better solved by evidence/policy/calibration?
13. Is this worth spending Codex quota on, or can reasoning/research/governance be completed first outside Codex?

---

# 14. Final guidance

The current architecture is not fundamentally wrong. Its strongest properties should be preserved:

- grounded evidence before concrete source selection;
- provider-neutral AI;
- deterministic ownership boundaries;
- canonical rational media time;
- EDL as sole executable timeline authority;
- renderer as adapter rather than editorial brain;
- durable provenance/revision semantics;
- fail-closed execution;
- real Product Probes instead of fixture-based self-congratulation.

The required correction is narrower:

```text
OLD IMPLIED DEPENDENCY
Planning → Editing

TARGET RELATIONSHIP
Planning ── optional high-value context ──→ Editing
```

That change should increase product freedom without weakening engineering rigor.

The broader risk-governance principle is equally important:

> **Do not make a complex system safe by removing useful boundaries. Make it safe by keeping authority singular, uncertainty visible, fallbacks explicit, integration continuously exercised, and each modification's blast radius as small as possible.**
