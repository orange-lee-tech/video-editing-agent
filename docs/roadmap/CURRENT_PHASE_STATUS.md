# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Review / runtime productization  
**Engineering state:** STAGE_A_PRODUCT_GATE_CLOSURE_ACTIVE  
**Updated:** 2026-08-18

## Progress meaning

The structural percentage measures real end-to-end product usability, not module count, test count, workflow count, probe count or UI polish.

The hard 100% contract remains:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Current Product Gate state:

- Planning Engineering mechanism: PASS; real Product Probe / Human Gate: OPEN.
- Editing Engineering mechanism: PASS; real automatic-final-MP4 Product Probe / Human Gate: OPEN.
- Stage-A completion gate: OPEN.

Therefore structural progress remains **90%**.

## Current accepted production-code baseline

`1e90e2dd3d235271ef48bb7a708a1899ce5b87a4`

Exact-head deterministic CI:

`32046499144` — PASS.

## ProductFlow orchestration — PASS / CLOSED

Work Order:

`R0.12-PRODUCT-FLOW-ORCHESTRATION-001`

Closure evidence:

`docs/validation/R0.12_PRODUCT_FLOW_ORCHESTRATION_CLOSURE.md`

Bounded Windows Engineering Probe:

`32046190310` — PASS.

Accepted mechanism evidence includes:

- ordinary structured Planning and Editing request surfaces;
- live Planning provider/review path to persisted ScriptPlan + ShootingPlan;
- real-media ingest / understanding / Director / grounded Resolver path;
- canonical EDL persistence;
- actual FFmpeg MP4 with video + audio;
- second-process exact canonical EDL revision reload and lineage;
- original source hash preservation;
- explicit Review PASS.

This is Engineering evidence, not real Product Gate/Human Gate evidence.

## Active Work Order

`R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001` is ACTIVE.

The final Stage-A construction boundary is ordinary-user Product Gate closure, not more backend construction.

### Ordinary-user surface audit — COMPLETE

Audit evidence:

`docs/validation/R0.12_STAGE_A_PRODUCT_SURFACE_AUDIT.md`

Audit result: **IMPLEMENTATION REQUIRED**.

Confirmed gaps include:

- ordinary Planning input lacks accepted authoritative-fact/reference inputs;
- existing `ReferenceStyleGuidance` is not fully plumbed into both Planning owners;
- current ProductFlow launch requires hand-written JSON;
- Editing exposes runtime/model/TransNet weight-path/tool arguments to the launcher path;
- no ordinary Windows launcher/file chooser exists;
- Planning results are not directly presented as readable exact plans;
- progress events are not observable live;
- folder selection convenience is absent;
- Environment Doctor lacks mandatory Shot-detection runtime readiness coverage.

### Planning Product Gate target

```text
real user intent / reference / commercial target
→ ordinary Windows product surface
→ real Planning workflow
→ persisted inspectable ScriptPlan
→ usable ShootingPlan
→ Human Gate
```

### Editing Product Gate target

```text
user-selected real local footage
+ editing intent / output destination
→ ordinary Windows product surface
→ actual automatic media understanding / editing chain
→ canonical EDL / Renderer / Review
→ real final MP4
→ Human Gate
```

### Ordinary-user floor

The surface may be visually plain and should remain small. It must be practical and understandable; a feature-rich NLE timeline is explicitly unnecessary.

Normal operation must not require:

- repository-file editing;
- hand-authored EditPlan / ResolutionDecision / EDL;
- developer-only knowledge of Domain IDs or source timestamps.

## Product Probe boundary

Synthetic Engineering fixtures do not close Product Gates.

The final probes must use real user conditions. For Editing, user-selected/private local footage and Windows runtime are valid required evidence boundaries. For Planning, use a real planning target/reference/commercial intent that the user can judge as actually useful and shootable.

Human Gate should ask ordinary judgments such as usable/unusable, obvious problems, or where the output fails — not require the user to invent professional scoring rubrics.

## Frozen authority rules

- Planning remains independently usable;
- Editing remains independently activatable;
- Combined uses optional exact Planning revisions;
- canonical EDL remains sole exact timeline authority;
- source-time grounding remains Resolver-owned;
- Renderer has no editorial authority;
- Review has no edit/render mutation authority;
- commercial/production Review rules remain fail-closed;
- no optional music/spatial asset is fabricated simply to obtain PASS;
- no structural-progress bump for UI shell completion alone.

## Immediate corridor

1. Codex implements the already-frozen ordinary-user product-surface batch and stops;
2. focused tests, full deterministic repository gates and bounded Windows launcher smoke must pass as far as the environment allows;
3. ChatGPT independently reobserves exact `main`, diff and CI after Codex stops;
4. repair only evidence-backed implementation defects;
5. run real Planning Product Probe + Human Gate;
6. run real Editing Product Probe + Human Gate;
7. declare Stage-A 100% only if both core gates and the global completion gate genuinely PASS.
