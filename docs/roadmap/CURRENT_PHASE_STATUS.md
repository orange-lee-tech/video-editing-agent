# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Review / runtime productization  
**Engineering state:** STAGE_A_EDITING_INTEGRATION_GAP_OPEN  
**Updated:** 2026-08-19

## Progress truth

Structural percentage measures real end-to-end ordinary-user usability, not module/test/UI count.

Hard 100% contract:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Current gate state:

- Planning Engineering: PASS; Product Probe: PASS; Human Gate: PASS.
- Editing subsystem mechanisms: substantially built/validated; ordinary ProductFlow integration gap: OPEN.
- Editing Product Probe: NOT GATE-READY until the required editing-expression floor is integrated.
- Editing Human Gate: OPEN.
- Stage-A completion gate: OPEN.

Therefore structural progress remains **90%**.

## Accepted production-code baseline

`af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`

Exact-head CI:

`32145822611` — PASS (`ci/quality-gate-diagnostic = success`).

This remains the accepted remote production-code baseline until the preserved local UX candidate is committed, pushed, reviewed and green in CI.

## Planning Product Gate — PASS

Durable evidence:

`docs/validation/R0.12_STAGE_A_PLANNING_PRODUCT_GATE.md`

A real ordinary-user Windows Planning run completed end-to-end, produced persisted ScriptPlan/ShootingPlan revisions, and the user judged both acceptable with no blocking issue.

Planning-only is proven usable for Stage A. Follow-up refinements do not reopen this PASS.

## Editing Product Gate — integration correction before further gate attempt

Real Editing-only Windows probes have crossed input validation, local-media understanding and Director boundaries, exposing and repairing several concrete runtime defects. The most recent same-day cloud failure was an explicit Gemini free-tier HTTP 429/provider quota condition; it did not authorize silent provider/model switching.

A subsequent 2026-08-19 static integration audit found a more important **product-gate correctness issue**:

The already-frozen Stage-A completion contract requires:

```text
user-selected local footage
→ understanding / Director / grounded Resolver
→ music/rhythm + spatial/audio + subtitle/graphics/minimal transitions
→ canonical EDL
→ Renderer / Review
→ final MP4
```

The Stage-A Product I/O contract likewise requires approved Music / Audio / Spatial / Subtitle / Graphics decisions before EDL assembly.

Current ordinary `build_editing_product_flow()` does not yet compose that entire floor. It currently reaches grounded ResolutionDecision and builds canonical EDL with a conservative source-audio mix, but it does not wire the already-developed Music/Audio and Spatial decision families into this ordinary route and has not yet product-integrated the required subtitle/graphics/minimal-transition floor.

Therefore:

> **The current ordinary Editing route is not gate-ready merely because it can eventually render an MP4. A plain-cut MP4 cannot close Stage A.**

Durable incident:

`docs/logs/INCIDENT_LEDGER.md` — `R0.12 Stage-A ordinary Editing integration gap — OPEN`.

This is an integration correction, not a new architecture. Resolver/EDL/Renderer/Review ownership remains frozen.

## Preserved local UX stabilization candidate

The bounded Windows/Tkinter UX wave has been implemented locally but is still uncommitted/unpushed because Codex execution quota ended before completion reporting.

Observed before final Splash micro-edits:

- Ruff: PASS;
- mypy: PASS;
- pytest: `713 passed`;
- import contracts: PASS;
- build/diff/repo doctor: PASS;
- launcher/Tk smoke: PASS;
- manual UI smoke for placeholder, multi-select media input, export, localization, profiles, responsiveness and protected API-secret persistence: PASS.

The final Splash repaint + dependency-free pixel mark were then repaired manually; the user confirmed the startup icon is visible.

Because those last edits happened after the 713-test run, a fresh complete Quality Gate is mandatory before commit/push.

Codex is now **closed for this wave because execution quota is exhausted**. The local candidate must be preserved and finalized via PowerShell; do not recreate it or pull over the uncommitted working tree.

## Current execution mode

`LOCAL UX CANDIDATE FINALIZATION → EDITING INTEGRATION REPAIR → PRODUCT/HUMAN GATE`

Active Work Order:

`R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`

Control documents:

- `docs/operations/CURRENT_CONTROL_STATE.md`
- `docs/operations/CURRENT_WORK_ORDER.md`
- `docs/operations/STAGE_A_UX_STABILIZATION_WAVE.md`
- `docs/roadmap/STAGE_A_COMPLETION_GATE.md`
- `docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

## Return corridor

### Step 1 — accept the existing local UX candidate

1. rerun full local quality/launcher checks after Splash edits;
2. commit locally before integrating remote docs;
3. fetch/rebase the local code commit onto latest `origin/main`;
4. rerun required checks;
5. push;
6. ChatGPT reobserves exact diff/CI and either accepts or rejects the new code baseline.

### Step 2 — bounded Editing integration repair

Compose already-approved decision owners into the ordinary path instead of inventing a second implementation:

- R0.10 Music/Audio Editorial;
- R0.11 Spatial/Auto Reframe;
- structured Subtitle path;
- bounded title/CTA/price-card graphics and minimal-transition semantics required by Stage A.

The repair must prove decision → canonical EDL → rendered execution alignment and keep:

- Resolver as source-time owner;
- EDLBuilder as assembler, not editor;
- EDL as exact timeline authority;
- Renderer execution-only;
- Review classification/routing-only.

### Step 3 — real Editing Product/Human Gate

Only after Step 2 is accepted:

1. use ordinary multi-select local footage, Combined unchecked for Editing-only proof;
2. record source SHA-256 hashes;
3. run the real automatic chain including the Stage-A expression floor;
4. obtain final MP4 only on Review PASS;
5. verify sources unchanged;
6. user watches the MP4 and completes Human Gate;
7. Stage A reaches 100 only if every completion invariant passes.

## Parallel productization backlog — important but not mixed into the gate repair

The user has additionally requested commercial productization. Durable preparation now exists for:

- UI/design system: `docs/product/DESKTOP_UI_DESIGN_SYSTEM_V0.1.md`;
- Provider-neutral product binding: `docs/architecture/PROVIDER_NEUTRAL_PRODUCT_BINDING_PLAN.md`;
- Windows packaging: `docs/operations/WINDOWS_DESKTOP_PACKAGING_READINESS.md`;
- product health: `docs/roadmap/PRODUCT_RED_BLACK_BOARD.md`;
- history: `docs/logs/PROJECT_CHRONICLE.md`;
- risk audit: `docs/logs/COMMERCIAL_DESKTOP_RISK_AUDIT_2026-08-19.md`.

These should proceed as separate bounded waves after the gate-critical integration path is made truthful. Do not combine Provider refactoring, UI decoration, packaging and Editing integration into one giant change.

## Frozen authority rules

- Planning remains independently usable;
- Editing remains independently activatable;
- Combined remains optional enrichment;
- canonical EDL remains sole exact timeline authority;
- Resolver owns source-time grounding;
- Renderer has no editorial authority;
- Review has no edit/render mutation authority;
- reference-only media remains Resolver-ineligible;
- final commercial visuals come from user-selected local footage;
- originals remain protected;
- no silent provider switching;
- no fabricated replacement visuals;
- no plaintext API-secret profiles;
- no Product/Human PASS inferred from tests alone;
- no Editing PASS from a route that omits the Stage-A editing-expression floor.
