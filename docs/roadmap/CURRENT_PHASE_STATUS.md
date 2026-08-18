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
- Editing Engineering mechanism: PASS; real Product Probe: IN PROGRESS after provider-aware retry repair; Human Gate: OPEN.
- Stage-A completion gate: OPEN.

Therefore structural progress remains **90%**.

## Current accepted production-code baseline

`af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`

Exact-head deterministic CI:

`32145822611` — PASS (`ci/quality-gate-diagnostic = success`).

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

The real Editing-only Windows probe uses real local MP4 footage with the Combined checkbox left unchecked.

An earlier run reached `editing_decision` and exposed an invalid DeepSeek `minimum_duration` proposal. Accepted baseline `c61c7e5abc8b7b388e0e92ad9ae533d094a27707` added strict Director proposal guidance, specific exact-time diagnostics and exactly one bounded local-contract repair proposal without coercing provider values.

After that repair was synchronized and a fresh Windows process was launched, a later real run reached local-media `ingest_understanding` and received a genuine Gemini HTTP 429 response reporting:

`generate_content_free_tier_requests, limit: 20, model: gemini-3.6-flash; Please retry in 10.577272831s`.

Audit found the visual retry decorator still waited only 0.3 and 0.6 seconds, so it ignored the provider's explicit recovery window. Accepted baseline `af5865df14b9f1cceaa9e6c1fe4dadf14cc60058` now:

- carries optional validated provider retry hints on transient visual errors;
- extracts Google `RetryInfo.retryDelay`, with bounded message fallback;
- waits for the greater of local backoff and provider-required delay;
- keeps the maximum attempt count at three;
- preserves fail-closed behavior, provider identity and real error reporting;
- has regression coverage for RetryInfo propagation and provider-directed waiting.

Exact-head CI run `32145822611` is green.

The same real Editing-only probe must now be rerun. A true account-level/quota exhaustion may still fail after bounded retries and remains a provider condition, not grounds for silent fallback. This Engineering repair does not constitute Editing Product/Human PASS.

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

For the gate-closing rerun, use one unambiguous source-selection mode instead of simultaneously filling both explicit files and a source folder, record source hashes before/after, and allow the application to honor short provider-directed retry waits rather than manually restarting the run.

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
- bounded deterministic provider proposal/retry repair;
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

1. synchronize current `main` to the Windows workspace;
2. launch a fresh ordinary product process and configure user-owned API credentials;
3. open the `自动剪辑` tab and keep Combined unchecked;
4. select real footage through one source-selection method and preserve before-run SHA-256 hashes;
5. rerun Editing-only and allow bounded provider-directed 429 waits to complete;
6. continue through Director / Resolver / canonical EDL / Renderer / Review;
7. inspect the actual final MP4 if Review PASSes;
8. verify source hashes remain unchanged;
9. complete Editing Human Gate;
10. classify and repair any further evidence-backed failure;
11. set Stage-A to 100% only if Editing Product/Human Gate PASSes and `STAGE_A_COMPLETION_GATE.md` is fully satisfied.
