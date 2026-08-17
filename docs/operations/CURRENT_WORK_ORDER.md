# Current Work Order

**ID:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A ordinary-user Product Gate closure  
**Mode:** PRODUCT PROBE + HUMAN GATE  
**Accepted production-code baseline:** `1e90e2dd3d235271ef48bb7a708a1899ce5b87a4`  
**Activated:** 2026-08-18  
**Codex release:** NO

## Previous Work Order result

`R0.12-PRODUCT-FLOW-ORCHESTRATION-001` — **PASS / CLOSED**.

Closure evidence:

`docs/validation/R0.12_PRODUCT_FLOW_ORCHESTRATION_CLOSURE.md`

Accepted Windows Engineering Probe:

`32046190310` — PASS.

Exact-head deterministic CI after the accepted Engineering evidence merge:

`32046499144` — PASS.

The accepted production baseline is:

`1e90e2dd3d235271ef48bb7a708a1899ce5b87a4`

## Why this Work Order exists

The repository has now proved the Planning and Editing mechanisms through real owner chains, including real media, live provider adapters, grounded Resolver decisions, persisted canonical EDL, actual FFmpeg render, Review, and exact EDL reload from a second Python process.

That Engineering proof does not satisfy Stage-A completion by itself.

The remaining structural question is:

> Can an ordinary Windows user practically use both core products through the real product path and judge the outputs useful enough, without repository editing or hand-authoring internal objects?

This Work Order closes that final Stage-A boundary as one coherent product batch rather than inventing multiple micro-phases.

## Canonical gate

Source of truth:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Structural progress stays at **90%** until both core Product Gates and the overall Stage-A gate pass.

## Scope A — ordinary-user surface audit

Before building a new frontend, inspect current repository surfaces and prove what is already usable.

Audit at minimum:

### Common

- project create/open;
- Environment Doctor / runtime diagnostics;
- workflow launch;
- progress/failure presentation;
- result/output discovery.

### Planning

- user can provide a real planning goal;
- reference/high-performing/commercial context can enter the product path;
- user does not need repository editing;
- generated ScriptPlan can be inspected;
- generated ShootingPlan can be inspected/used;
- failure is understandable rather than a raw internal trace.

### Editing

- user can choose local media files/folder;
- user can provide editing intent;
- user can choose/identify final output destination;
- provider/runtime configuration is not exposed as editorial meaning;
- user can start the actual automatic flow;
- progress/failure is understandable;
- final MP4 is discoverable;
- original source files remain protected.

The audit must inspect existing CLI/launcher/UI code before choosing a new toolkit.

## Scope B — minimum Stage-A Windows product surface

Implement only gaps proven by the audit.

A visually plain launcher/UI is acceptable. A feature-rich NLE is explicitly out of scope.

The minimum surface should make ordinary operation possible without requiring the user to write JSON by hand or understand:

- AssetRef / ShotRef;
- CandidateWindow / ResolutionDecision;
- source timestamps;
- EDL internals;
- model/runtime plumbing that belongs to product configuration.

The product surface may call the already accepted ProductFlow application owners. It must not duplicate or bypass them.

## Planning Product Gate

Required final evidence:

```text
real user planning goal / reference / commercial target
→ ordinary Windows product surface
→ Brief
→ real Planning workflow
→ persisted inspectable ScriptPlan
→ usable ShootingPlan
→ Human Gate
```

Human Gate questions should be ordinary and decision-oriented, for example:

- Is the script usable for the intended video?
- Is the shooting plan actually shootable with your stated resources?
- What is obviously wrong or missing?

Do not ask the user to invent a professional scoring rubric.

## Editing Product Gate

Required final evidence:

```text
user-selected real/private local footage
+ editing intent / output destination
→ ordinary Windows product surface
→ real automatic media-understanding/editing chain
→ canonical EDL
→ Renderer
→ Review / bounded repair where needed
→ real final MP4
→ Human Gate
```

Human Gate questions should center on the actual output:

- Is the final video usable/watchable for the stated purpose?
- Are there obvious bad cuts, missing material, bad text/audio, or other unacceptable defects?
- Can the user locate the result and understand any failure/correction guidance?

A Product Probe failure must be classified before repair as engineering/provider failure, semantic veto, product-quality veto, or human acceptance pending.

## Combined mode preservation

Combined remains composition of the same owners:

```text
Planning output
→ optional exact ScriptPlan/ShootingPlan revisions
→ same Editing Core
```

Do not make Planning mandatory for Editing and do not fabricate Planning artifacts to satisfy the gate.

## Deterministic acceptance requirements

Any implementation required by the usability audit must preserve:

- ordinary-request authority boundaries;
- source-time grounding;
- canonical EDL sole timeline authority;
- Renderer execution-only ownership;
- Review classify/route-only ownership;
- original media protection;
- Planning-only / Editing-only / Combined semantics;
- repository architecture contracts and Quality Gate.

Add regression coverage for every concrete product-surface defect discovered during Product Probe/Human Gate.

## Codex/resource policy

ChatGPT + GitHub should first complete the audit, architecture decision, exact scope and remote evidence work.

Codex remains **NO ACTIVE RELEASE** by default.

Release Codex only if the audit reveals a coherent multi-file Windows product-surface implementation or runtime defect that materially benefits from local `inspect → edit → test → repair` iteration. If released, one bounded complex batch should cover the complete agreed implementation surface and stop for ChatGPT review.

## Exit gate

This Work Order may close only when:

1. the ordinary-user Stage-A surface is practical on Windows;
2. Planning Product Probe passes on a real user planning target;
3. Planning Human Gate is PASS;
4. Editing Product Probe produces a real final MP4 from user-selected real footage;
5. Editing Human Gate is PASS;
6. Planning-only / Editing-only / Combined semantics remain valid;
7. the ordinary-user compatibility/diagnostic floor is satisfied;
8. latest accepted `main` is green;
9. closure evidence records exact code/runtime/product evidence and known limitations.

Only then may the control plane set:

```text
core_1_planning_product_gate: PASS
core_2_editing_product_gate: PASS
stage_a_completion_gate: PASS
structural_progress_percent: 100
```

## STOP boundary

Do not build a feature-rich NLE/timeline editor.

Do not reopen Preview backend benchmarking.

Do not redesign persistence, Resolver, EDL or Renderer without concrete Product Probe evidence.

Do not loosen semantic/commercial Review or grounding rules merely to turn a Product Probe green.

Do not use hosted synthetic Engineering media as Product Gate evidence.

Do not claim Human Gate PASS without the user's actual judgment.

Do not bump structural progress for a launcher/UI implementation alone.
