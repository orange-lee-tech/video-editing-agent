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

- Planning Engineering/Product/Human Gate: PASS.
- Editing subsystem mechanisms: substantially built/validated.
- Editing ordinary ProductFlow integration gap: OPEN.
- Review-before-final-output publication gap: OPEN.
- Editing Product Probe: NOT GATE-READY until both gate-path defects are repaired.
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

## Editing Product Gate — two gate-path corrections before further attempt

Real Editing-only Windows probes have crossed input validation, local-media understanding and Director boundaries, exposing and repairing several concrete runtime defects. The most recent same-day cloud failure was an explicit Gemini HTTP 429/provider quota condition; it did not authorize silent provider/model switching.

A 2026-08-19 static ProductFlow audit then found two more fundamental gate blockers.

### 1. Required editing-expression families are not all wired into ordinary ProductFlow

Frozen Stage-A contract:

```text
understanding / Director / grounded Resolver
→ music/rhythm + spatial/audio + subtitle/graphics/minimal transitions
→ canonical EDL
→ Renderer / Review
→ final MP4
```

Current ordinary `build_editing_product_flow()` reaches grounded ResolutionDecision and builds canonical EDL with a conservative source-audio mix, but does not yet compose the already-developed R0.10 Music/Audio and R0.11 Spatial families into that route and has not product-integrated the required Subtitle/Graphics/minimal-transition floor.

Therefore a plain-cut/source-audio MP4 is useful mechanical evidence but **cannot close Stage A**.

### 2. Current flow renders to the user final path before Review

Current `EditingProductFlow.run()` order is effectively:

```text
canonical EDL
→ render(request.output_path)
→ Review
→ if non-PASS: result.final_output_path = None
```

The result object hides the path on correction, but the MP4 may already exist at the destination the user chose. That destination itself is a product-level “final output” signal and may also overwrite a previous non-source output because the FFmpeg backend uses overwrite semantics.

Required product meaning:

```text
canonical EDL
→ controlled render candidate
→ Review
→ PASS: publish/promote to requested final destination
→ non-PASS: no user-final publication
```

Review still only classifies/routes; publication is a product/artifact lifecycle step, not Review editorial authority.

Durable incidents:

- `R0.12 Stage-A ordinary Editing integration gap — OPEN`;
- `R0.12 Review-before-final-output publication defect — OPEN`;

in `docs/logs/INCIDENT_LEDGER.md`.

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

Codex is **closed for this wave because execution quota is exhausted**. Do not recreate the candidate or pull over its uncommitted working tree.

## Current execution mode

`LOCAL UX CANDIDATE FINALIZATION → EDITING INTEGRATION/PUBLICATION REPAIR → PRODUCT/HUMAN GATE`

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

### Step 2 — bounded Editing gate-path repair

Compose already-approved decision owners into the ordinary path and correct final-output publication:

- R0.10 Music/Audio Editorial;
- R0.11 Spatial/Auto Reframe;
- structured Subtitle path;
- bounded title/CTA/price-card graphics and minimal-transition semantics required by Stage A;
- controlled render candidate → Review → PASS-only final publication.

The repair must prove decision → canonical EDL → rendered execution alignment and keep:

- Resolver as source-time owner;
- EDLBuilder as assembler, not editor;
- EDL as exact timeline authority;
- Renderer execution-only;
- Review classification/routing-only;
- publication as product/artifact lifecycle, not editorial mutation.

### Step 3 — real Editing Product/Human Gate

Only after Step 2 is accepted:

1. ordinary multi-select local footage; Combined unchecked for Editing-only proof;
2. record source SHA-256 hashes;
3. run the real automatic chain including the Stage-A expression floor;
4. render to controlled candidate;
5. Review PASS;
6. publish/promote to requested final MP4;
7. verify sources unchanged;
8. user watches the final MP4 and completes Human Gate;
9. Stage A reaches 100 only if every completion invariant passes.

## Parallel productization backlog — important but not mixed into the gate repair

Durable preparation exists for:

- UI/design system: `docs/product/DESKTOP_UI_DESIGN_SYSTEM_V0.1.md`;
- Provider-neutral product binding: `docs/architecture/PROVIDER_NEUTRAL_PRODUCT_BINDING_PLAN.md`;
- Windows packaging: `docs/operations/WINDOWS_DESKTOP_PACKAGING_READINESS.md`;
- product health: `docs/roadmap/PRODUCT_RED_BLACK_BOARD.md`;
- history: `docs/logs/PROJECT_CHRONICLE.md`;
- risk audit: `docs/logs/COMMERCIAL_DESKTOP_RISK_AUDIT_2026-08-19.md`;
- open-source UI/product research: `docs/research/DESKTOP_PRODUCT_UI_REFERENCE_REVIEW_2026-08-19.md`.

These proceed as separate bounded waves after the gate-critical route is truthful. Do not combine Provider refactoring, UI decoration, packaging and Editing integration into one giant change.

## Frozen authority rules

- Planning remains independently usable;
- Editing remains independently activatable;
- Combined remains optional enrichment;
- canonical EDL remains sole exact timeline authority;
- Resolver owns source-time grounding;
- Renderer has no editorial authority;
- Review has no edit/render mutation authority;
- render candidate is not user-final output before Review PASS;
- reference-only media remains Resolver-ineligible;
- final commercial visuals come from user-selected local footage;
- originals remain protected;
- no silent provider switching;
- no fabricated replacement visuals;
- no plaintext API-secret profiles;
- no Product/Human PASS inferred from tests alone;
- no Editing PASS from a route that omits the Stage-A editing-expression floor;
- no final-output publication before Review PASS.
