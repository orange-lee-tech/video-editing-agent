# Current Work Order

**ID:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Stage-A ordinary-user Product Gate closure  
**Mode:** PRODUCT PROBE → TEMPORARY UX STABILIZATION → HUMAN GATE  
**Accepted production-code baseline:** `af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`  
**Activated:** 2026-08-18  
**Codex release:** OPEN — ONE BOUNDED WINDOWS/TKINTER UX WAVE ONLY

## Objective

Close Stage A only through real ordinary-user evidence for the two frozen core product functions.

Planning Product/Human Gate is already **PASS**. Editing Engineering mechanism is **PASS**, while the real Editing Product/Human Gate remains **OPEN**.

On 2026-08-18 the real Editing probe became temporarily blocked by the user's Gemini free-tier quota after multiple legitimate real-product requests. The user explicitly chose to use the quota-reset interval to consolidate already-recorded ordinary-user UX/robustness work instead of repeatedly consuming provider quota.

This does **not** raise structural progress above 90%, does **not** close Editing Product Gate, and does **not** authorize product-core redesign.

## Frozen architecture

The following remain unchanged:

- Planning-only: `Brief → ScriptPlan → ShootingPlan`;
- Editing-only: `Brief/editorial intent + user local footage → Editing Core`;
- Combined: exact Planning revisions optionally enrich the same Editing Core;
- reference-only media remains Resolver-ineligible;
- final commercial visuals come from user-selected local footage;
- source-time grounding remains Resolver-owned;
- canonical EDL remains the sole exact timeline authority;
- Renderer executes only;
- Review classifies/routes only;
- originals remain protected;
- no silent provider switching or fabricated replacement media.

## Gate state

### Planning Product Gate

**PASS**.

Durable evidence:

`docs/validation/R0.12_STAGE_A_PLANNING_PRODUCT_GATE.md`

The ordinary Windows launcher completed a real Planning run and produced persisted ScriptPlan/ShootingPlan revisions. The user judged both acceptable with no blocking issue.

### Editing Product Gate

**ENGINEERING PASS / PRODUCT PROBE IN PROGRESS / HUMAN GATE OPEN**.

Real Windows probes have already crossed input validation and local-media understanding far enough to expose and repair:

1. Gemini model/API-contract migration defects;
2. exact `MediaTime` provider-presentation misuse;
3. missing bounded visual transient retry wiring;
4. malformed DeepSeek Director exact-duration proposals;
5. provider-aware Gemini retry-delay handling.

Accepted production-code baseline:

`af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`

Exact-head CI:

`32145822611` — `ci/quality-gate-diagnostic = success`.

A subsequent real Editing-only run reached `ingest_understanding` and failed with a genuine Gemini HTTP 429 after the account/project's current free-tier quota was exhausted. The provider condition is explicit and must not be bypassed by silent model/provider switching.

## Temporary execution boundary — ordinary-user UX stabilization

While the provider quota prevents a useful same-day Editing re-probe, execute exactly one bounded UX stabilization wave described in:

`docs/operations/STAGE_A_UX_STABILIZATION_WAVE.md`

The wave may touch the ordinary launcher, product adapter/controller/presentation seams, safe local profile support, provider-facing retry/status presentation, and directly related tests.

It must **not** refactor EDL/Resolver/Renderer/Review ownership, change provider authority, or broaden into a new application architecture.

### User-approved source-selection simplification

The Editing launcher shall expose **one** local footage input mechanism:

- keep `素材文件 / Media Files`;
- support multi-select in one chooser;
- remove the separate `素材文件夹 / Media Folder` field and button from the ordinary UI;
- do not silently scan unrelated files from a directory;
- preserve deterministic user-selected local-footage provenance.

Lower-level folder expansion may remain temporarily for compatibility if removing it would create unrelated churn, but it must no longer be an ordinary-user surface.

## Codex release boundary

This is a justified Codex release because the requested UX wave spans multiple files and requires local Windows/Tkinter behavior, background execution/responsiveness, safe Windows credential persistence, file dialogs, and regression tests.

Codex may:

- implement the exact UX wave;
- add/modify focused tests;
- perform small reversible refactors inside the product adapter/UI layer when required for testability;
- run formatter/lint/mypy/tests/build locally;
- commit/push one coherent implementation to `main` only after the local quality gate is green.

Codex must not:

- redesign product-core architecture;
- weaken factual review, Resolver grounding, EDL authority, Review policy, or original-media protection;
- add a brittle Douyin/platform scraper;
- store API keys in plaintext profile files;
- silently change provider/model to escape quota;
- invent fake progress percentages or fake ETA values;
- implement decorative controls that do nothing;
- create R0.12A/B/C-style microphases.

After Codex reports completion, ChatGPT must reobserve exact `origin/main`, diff, tests and CI before accepting the result.

## Return to Editing Product Gate

After the UX wave is accepted and provider quota is available again:

1. synchronize the accepted `main` to Windows;
2. launch the ordinary product surface;
3. select real footage through the single multi-select local-file mechanism;
4. record non-empty source SHA-256 hashes before the gate-closing run;
5. keep Combined unchecked for the Editing-only proof;
6. execute actual ingest / shot detection / understanding / Director / grounded Resolver / canonical EDL / Renderer / Review;
7. produce a real final MP4 only on Review PASS;
8. verify source hashes remain unchanged;
9. let the user watch the MP4 and complete the ordinary Editing Human Gate.

## Structural progress

Remain at **90%** until Editing Product/Human Gate also PASSes.

Stage A may reach 100% only when both core Product/Human Gates pass and `docs/roadmap/STAGE_A_COMPLETION_GATE.md` is fully satisfied.
