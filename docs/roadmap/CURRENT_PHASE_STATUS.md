# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Review / runtime productization  
**Engineering state:** STAGE_A_PRODUCT_GATE_EXECUTION_ACTIVE  
**Updated:** 2026-08-18

## Progress meaning

The structural percentage measures real end-to-end product usability, not module count, test count, workflow count, probe count or UI polish.

The hard 100% contract remains:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Current Product Gate state:

- Planning Engineering mechanism: PASS; Product Probe: PASS; Human Gate: PASS.
- Editing Engineering mechanism: PASS; real Product Probe: IN PROGRESS after Director proposal repair; Human Gate: OPEN.
- Stage-A completion gate: OPEN.

Therefore structural progress remains **90%**.

## Current accepted production-code baseline

`c61c7e5abc8b7b388e0e92ad9ae533d094a27707`

Exact-head deterministic CI:

`32139988645` — PASS (`ci/quality-gate-diagnostic = success`).

## Planning Product Gate — PASS

Durable evidence:

`docs/validation/R0.12_STAGE_A_PLANNING_PRODUCT_GATE.md`

A real ordinary-user Windows Planning run completed end-to-end with a user-selected local reference, real planning intent, user-owned configured APIs and no repository editing or hand-authored internal plans.

The launcher produced and presented exact ScriptPlan and ShootingPlan revisions. The user explicitly judged the ScriptPlan acceptable, the ShootingPlan acceptable and identified no blocking defect in the accepted result.

Planning-only is therefore proven usable for Stage A.

Known product refinements from the same session are preserved in:

`docs/roadmap/PRODUCT_UX_BACKLOG.md`.

These refinements do not reopen Planning PASS.

## Real Editing Product Probe — in progress

The first real Editing-only Windows probe used real local MP4 footage with the Combined checkbox left unchecked and reached:

`project_ready → input_validation → ingest_understanding → editing_decision`.

It then failed at the DeepSeek Director/EditPlan proposal boundary with `DeepSeekPlanningResponseError: invalid minimum_duration`.

Audit found that DeepSeek JSON mode produced a provider proposal that still had to satisfy the stricter local exact-time/EditSlot contract. The Director adapter previously had no bounded repair path for a syntactically valid JSON proposal that failed local contract validation.

Accepted repair through `c61c7e5abc8b7b388e0e92ad9ae533d094a27707`:

- adds a complete valid Director JSON example to the prompt;
- explicitly constrains exact duration `value` / `scale`, positive scale/value and max/min ordering;
- keeps local `MediaTime` and EditSlot validation strict;
- never silently coerces invalid provider durations;
- allows exactly one second Director proposal only after a locally invalid first proposal, carrying the specific local validation reason as repair feedback;
- fails closed after the second invalid proposal;
- adds precise exact-time diagnostics and bounded-repair regression coverage.

The pre-format repair run had 696 tests, mypy, import contracts and build passing with only two Ruff line-length findings. The exact accepted head is fully green in run `32139988645`.

The same real Editing-only probe must now be rerun. This Engineering repair does not constitute Editing Product/Human PASS.

## Active Work Order

`R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001` remains ACTIVE, with execution mode:

`PRODUCT PROBE → HUMAN GATE`

There is **no active Codex writer**.

The active closure target remains the **real Editing Product Gate**.

## Editing Product Gate target

```text
user-selected real local footage
+ editing intent / output destination
→ ordinary Windows launcher
→ actual ingest / shot detection / understanding / Director
→ grounded Resolver
→ canonical EDL / Renderer / Review
→ real final MP4
→ Human Gate
```

Required evidence remains:

- real local source media or source folder;
- real editing intent and output MP4 destination;
- Editing-only must work independently of Planning;
- actual automatic production chain, not hand-authored EditPlan/ResolutionDecision/EDL;
- final MP4 only on Review PASS;
- original user media unchanged;
- user watches the result and judges usefulness/obvious defects/workflow clarity.

For the gate-closing rerun, use one unambiguous source-selection mode instead of simultaneously filling both explicit files and a source folder, and record source hashes before/after.

## Current ordinary-user feedback backlog

`docs/roadmap/PRODUCT_UX_BACKLOG.md` records:

- scroll/export improvements for long output;
- real-data runtime ETA to the minute, recalculated at least every 30 seconds;
- full UI-aligned localization of plans/progress/user-facing diagnostics;
- safe local profile persistence and OS-protected API-secret persistence;
- first-run required/optional placeholders;
- bounded share-text/reference-URL handling without scraper-first platform coupling;
- safe repair/regeneration when no authoritative facts/reference exist and the model proposes unsupported claims;
- opt-in public-material guidance and similar-example research while preserving rights/reference boundaries;
- startup splash/progress polish.

Only a backlog item that blocks the Editing Product Probe should preempt the current gate.

## Runtime readiness strategy

Use the actual Windows host and repository Doctor. Repair environment/configuration with PowerShell or the product Settings surface before considering source changes.

Do not spend Codex quota on:

- FFmpeg/GStreamer/TransNet installation;
- PATH repair;
- API-secret configuration;
- launcher operation;
- ordinary deterministic checks;
- bounded deterministic provider proposal repair;
- documentation/governance maintenance;
- cosmetic backlog work.

Codex may be re-released only for a concrete nontrivial implementation defect after ChatGPT classifies the failure.

## Human Gate

Editing Human Gate stays ordinary and product-centered:

- Is the final video usable as the Stage-A automatic result?
- Are there obvious wrong shots/cuts/audio/subtitle/content problems?
- Was the workflow understandable from source selection to final MP4?

Do not ask the user to invent a professional scoring rubric.

## Frozen authority rules

- Planning remains independently usable;
- Editing remains independently activatable;
- Combined uses optional exact Planning revisions;
- canonical EDL remains sole exact timeline authority;
- source-time grounding remains Resolver-owned;
- Renderer has no editorial authority;
- Review has no edit/render mutation authority;
- reference-only media remains Resolver-ineligible;
- commercial final visuals come from user-selected local footage;
- originals remain protected;
- no silent provider switching or fabricated replacement visual assets.

## Immediate corridor

1. synchronize the accepted Director repair to the Windows workspace;
2. launch the ordinary product surface and configure user-owned API credentials;
3. open the `自动剪辑` tab and keep Combined unchecked;
4. select real footage through one source-selection method and record before-run SHA-256 hashes;
5. rerun Editing-only with real editing intent and a real MP4 destination;
6. inspect the actual final MP4 if Review PASSes;
7. verify source hashes remain unchanged;
8. complete Editing Human Gate;
9. classify and repair any further evidence-backed failure;
10. set Stage-A to 100% only if Editing Product/Human Gate PASSes and `STAGE_A_COMPLETION_GATE.md` is fully satisfied.
