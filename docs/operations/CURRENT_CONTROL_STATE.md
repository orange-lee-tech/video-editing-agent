# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-19
current_phase: R0.12
phase_state: STAGE_A_EDITING_INTEGRATION_GAP_OPEN
active_work_order: R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001
accepted_code_baseline: af5865df14b9f1cceaa9e6c1fe4dadf14cc60058
control_plane_baseline: 79c3be540f335477699223292580f32f6bb3c807
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: PASS
core_2_editing_product_gate: INTEGRATION_PUBLICATION_OUTPUT_PROFILE_GAPS_OPEN_PRODUCT_HUMAN_OPEN
previous_work_order: R0.12-PRODUCT-FLOW-ORCHESTRATION-001
previous_work_order_result: PASS
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Routing truth

Frozen product architecture remains unchanged:

- Planning-only: `Brief → ScriptPlan → ShootingPlan`;
- Editing-only: `Brief/editorial intent + user local footage → Editing Core`;
- Combined: exact Planning revisions optionally enrich the same Editing Core;
- source-time grounding remains Resolver-owned;
- the user-visible/typed Output Profile supplies the target canvas/fps used by Spatial and rendering; platform may suggest a default but must not invisibly own the final canvas;
- approved Music/Audio/Spatial/Subtitle/Graphics/transition decisions belong upstream of EDL assembly;
- canonical EDL remains the sole exact timeline authority;
- Renderer executes only;
- Review classifies/routes only;
- a render candidate becomes the user's **final output only after Review PASS and product-layer publication/promotion**.

## Accepted production baseline

`af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`

Exact-head CI:

`32145822611` — `ci/quality-gate-diagnostic = success`.

This remains the accepted **remote production-code** baseline until the currently preserved Windows UX candidate is committed, pushed, reviewed and green in CI.

## Gate truth

### Planning

**Product/Human Gate: PASS**.

Durable evidence:

`docs/validation/R0.12_STAGE_A_PLANNING_PRODUCT_GATE.md`

### Editing

**Engineering mechanisms exist / ordinary ProductFlow integration + publication + output-profile gaps: OPEN / Product Probe: NOT GATE-READY / Human Gate: OPEN**.

The 2026-08-19 audit found three gate-path blockers/prerequisites in the ordinary Editing route.

#### A. Editing-expression integration gap

Frozen contracts require `music/rhythm + spatial/audio + subtitle/graphics/minimal transitions` before canonical EDL. Current `EditingProductCapabilities` / `build_editing_product_flow()` wires media understanding, Director, Resolver, conservative source audio, EDLBuilder, Renderer and Review, but does not yet wire the full required Music/Spatial/Subtitle/Graphics/minimal-transition floor into the ordinary product route.

Therefore a plain-cut MP4 from the current abbreviated ProductFlow cannot close Stage A.

#### B. Review-before-final-output publication gap

Current `EditingProductFlow.run()` renders directly to `request.output_path` **before** Review. If Review returns `CORRECTION_REQUIRED`, the product result correctly exposes no final path, but the rendered MP4 may already exist at the user-selected final destination.

Required publication boundary:

`canonical EDL → controlled render candidate → Review → PASS → publish/promote to requested final destination`.

A non-PASS candidate may remain internal evidence only if policy permits; it must not overwrite or masquerade as an accepted final output.

#### C. Fixed 1920×1080@30 output profile gap

Current `EditingProductCapabilities` defaults every ordinary render to `1920 × 1080 @ 30 fps`; `EditingForm` only asks for an output MP4 path. Brief contains a platform string, but no explicit user-visible Output Profile controls aspect/resolution/fps.

This must be corrected before ordinary R0.11 Spatial/Auto-Reframe integration: target canvas is a required spatial input, and silently composing for fixed 16:9 can make a technically valid reframe solve the wrong product geometry.

Required direction:

`user-visible typed Output Profile → target canvas/fps → SpatialComposer → canonical EDL/Render provenance`.

Platform may propose a default; user-visible output profile remains the actual product authority.

Durable incident records in `docs/logs/INCIDENT_LEDGER.md`:

- `R0.12 Stage-A ordinary Editing integration gap — OPEN`;
- `R0.12 Review-before-final-output publication defect — OPEN`;
- `R0.12 fixed output-profile / aspect-ratio gap — OPEN`.

These findings do not reopen accepted R0.8/R0.9/R0.10/R0.11 subsystem evidence and do not authorize a core redesign.

## Preserved local UX candidate

The user-authorized Stage-A UX stabilization wave exists as a **Windows local, still-uncommitted candidate** after Codex execution quota was exhausted.

Observed local evidence before the final Splash micro-edits:

- Ruff / mypy / import contracts / build / repo doctor: PASS;
- pytest: `713 passed`;
- launcher smoke: PASS;
- manual UI smoke for placeholder, single multi-select media input, export, localization, profiles, responsiveness and protected API-secret storage: PASS.

Final Splash repaint + dependency-free Canvas pixel mark were repaired manually and the user confirmed the startup icon is visible. Because those edits happened after the 713-test gate, a fresh complete local Quality Gate remains mandatory before commit/push.

No remote production source file should be edited from GitHub until this candidate is safely committed/rebased/pushed.

## Codex state

Codex execution quota is exhausted for this wave.

**No further Codex execution is currently authorized or required.**

## Current execution corridor

`LOCAL UX CANDIDATE FINALIZATION → STAGE-A EDITING INTEGRATION/PUBLICATION/OUTPUT-PROFILE REPAIR → REAL PRODUCT/HUMAN GATE`

### 1. Finalize the preserved UX candidate

- rerun complete local Quality Gate after final Splash edits;
- commit the local product-adapter/UI/test changes before integrating remote docs;
- fetch/rebase onto latest docs-only `origin/main`;
- rerun required checks;
- push; ChatGPT inspects exact commit/diff/CI before changing accepted code baseline.

### 2. Repair the Stage-A Editing gate path

Use existing capability ownership wherever implemented:

- add the smallest typed user-visible Output Profile needed by Stage A; feed its target canvas/fps consistently into Spatial/EDL/Render provenance;
- Resolver remains grounded source-window owner;
- R0.10 Music/Audio decisions are integrated upstream of EDL assembly;
- R0.11 Spatial/Auto-Reframe decisions are integrated for resolved selections against the selected target canvas;
- structured subtitle path is integrated into canonical EDL;
- Stage-A minimum graphics/title/CTA/price-card and transition vocabulary receives small explicit typed semantics;
- EDLBuilder assembles approved decisions only;
- Renderer remains execution-only;
- Review remains classification/routing only;
- rendering targets a controlled candidate/staging artifact first;
- only Review PASS triggers product-layer publication/promotion to the requested final path;
- existing accepted final output must not be overwritten by a candidate that later fails Review.

This remains one bounded integration repair, not a new microphase or monolithic Effects Engine.

### 3. Resume the real Editing Product/Human Gate

Only after the repair is accepted and provider/runtime are available:

1. ordinary multi-select local footage, Combined unchecked for Editing-only proof;
2. select/confirm the intended Output Profile;
3. record source SHA-256 hashes;
4. run actual ingest / shot detection / visual understanding / Director / grounded Resolver;
5. execute the Stage-A editing-expression floor against the selected target canvas through canonical EDL;
6. render to controlled candidate;
7. Review PASS;
8. publish/promote the reviewed candidate to the user final MP4 destination;
9. source hashes remain unchanged;
10. user watches final MP4 and completes Human Gate.

## Parallel commercial-product preparation

Documented but not mixed into the gate-critical repair:

- `docs/product/DESKTOP_UI_DESIGN_SYSTEM_V0.1.md`;
- `docs/architecture/PROVIDER_NEUTRAL_PRODUCT_BINDING_PLAN.md`;
- `docs/operations/WINDOWS_DESKTOP_PACKAGING_READINESS.md`;
- `docs/operations/WINDOWS_RUNTIME_DEPENDENCY_INVENTORY.md`;
- `docs/roadmap/PRODUCT_RED_BLACK_BOARD.md`;
- `docs/logs/PROJECT_CHRONICLE.md`;
- `docs/logs/COMMERCIAL_DESKTOP_RISK_AUDIT_2026-08-19.md`;
- `docs/research/DESKTOP_PRODUCT_UI_REFERENCE_REVIEW_2026-08-19.md`.

## Structural progress

Remain at **90%**.

- Stage-A completion gate: OPEN.
- Planning Product/Human Gate: PASS.
- Editing Product/Human Gate: OPEN.
- Editing ordinary ProductFlow integration gap: OPEN.
- Review-before-final-output publication gap: OPEN.
- fixed output-profile/aspect-ratio gap: OPEN.

Neither a polished GUI, a successful plain-cut MP4, subsystem closure evidence nor packaging work may raise progress to 100 by itself.

## Constitutional constraints

- Planning remains optional for Editing;
- Planning-only / Editing-only / Combined remain legitimate;
- reference-only media remains Resolver-ineligible;
- commercial final visuals come from user-selected local footage;
- source-time grounding remains Resolver-owned;
- output canvas/fps is explicit product input/configuration, not hidden provider authority;
- canonical EDL remains sole exact timeline authority;
- Renderer executes only;
- Review classifies/routes only;
- render candidate is not final output before PASS;
- originals remain protected;
- no LLM-generated timestamps/internal IDs as authority;
- no silent stock/generated visual replacement;
- no silent provider switching;
- no plaintext API-secret profiles;
- no Product/Human PASS inferred from tests alone;
- no Stage-A Editing PASS from a route that omits the required editing-expression floor;
- no final-output publication before Review PASS;
- no structural-progress bump before both real gates pass.
