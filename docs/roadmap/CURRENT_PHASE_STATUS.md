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
- Stage-A UX stabilization: ACCEPTED.
- Editing subsystem mechanisms: substantially built/validated.
- Editing ordinary ProductFlow integration gap: OPEN.
- Review-before-final-output publication gap: OPEN.
- explicit Output Profile / target-canvas gap: OPEN.
- Editing Product Probe: NOT GATE-READY until all three gate-path issues are repaired.
- Editing Human Gate: OPEN.
- Stage-A completion gate: OPEN.

Therefore structural progress remains **90%**.

## Accepted production-code baseline

`c6bd96116e3ab00f76aeb87ee63ad1037ba84980`

Exact-head CI:

`32205777259` — PASS (`ci/quality-gate-diagnostic = success`).

The accepted UX stack introduced responsive Tk execution, bilingual ordinary-user presentation, single multi-select media input, scroll/export, placeholders, local profiles, Windows-protected API credential persistence, bounded share-text HTTPS extraction, ETA/status and visible Splash. Windows local gate passed 713 tests plus launcher/manual UI smoke; Linux CI then exposed and closed a Windows-only ctypes typing portability defect.

## Planning Product Gate — PASS

Durable evidence:

`docs/validation/R0.12_STAGE_A_PLANNING_PRODUCT_GATE.md`

Planning-only is proven usable for Stage A.

## Editing Product Gate — three gate-path corrections before further attempt

### 1. Required editing-expression families are not all wired into ordinary ProductFlow

Frozen Stage-A contract requires:

```text
understanding / Director / grounded Resolver
→ music/rhythm + spatial/audio + subtitle/graphics/minimal transitions
→ canonical EDL
→ Renderer / Review
→ final MP4
```

Current ordinary ProductFlow still does not compose the already-developed R0.10 Music/Audio and R0.11 Spatial families plus the required Subtitle/Graphics/minimal-transition floor into the gate-closing path.

A plain-cut/source-audio MP4 cannot close Stage A.

### 2. Current flow renders to the user final path before Review

Required lifecycle:

```text
canonical EDL
→ controlled render candidate
→ Review
→ PASS: publish/promote to requested final destination
→ non-PASS: no user-final publication
```

Review remains classification/routing-only; publication is product/artifact lifecycle.

### 3. Output canvas/fps is still a hidden fixed `1920×1080@30`

Before R0.11 Spatial integration, the ordinary product route needs an explicit typed/user-visible Output Profile supplying target width/height/fps to Spatial/EDL/Renderer. Platform may suggest a default, but cannot invisibly own final geometry.

Durable incidents are recorded in `docs/logs/INCIDENT_LEDGER.md`.

## Current execution mode

`EDITING INTEGRATION/PUBLICATION/OUTPUT-PROFILE REPAIR → PRODUCT/HUMAN GATE`

Active Work Order:

`R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`

### Step 1 — bounded Editing gate-path repair

- typed/user-visible Output Profile;
- R0.10 Music/Audio Editorial integration;
- R0.11 Spatial/Auto Reframe integration against selected target canvas;
- structured Subtitle integration;
- bounded title/CTA/price-card Graphics and minimal-transition semantics required by Stage A;
- controlled render candidate → Review → PASS-only final publication;
- mutation/integration tests proving Output Profile / decision → EDL → render → Review → publication alignment;
- full Quality Gate.

### Step 2 — real Editing Product/Human Gate

Only after Step 1 is accepted:

1. ordinary multi-select local footage; Combined unchecked for Editing-only proof;
2. select/confirm intended Output Profile;
3. record source SHA-256 hashes;
4. execute the real automatic chain including Stage-A expression floor;
5. render controlled candidate;
6. Review PASS;
7. publish/promote to requested final MP4;
8. verify sources unchanged;
9. user watches final MP4 and completes Human Gate;
10. Stage A reaches 100 only if every completion invariant passes.

## Parallel productization backlog

Durable preparation exists for UI design, Provider-neutral product binding, Windows packaging/runtime inventory, project chronicle, product red/black board and commercial risk audit. These remain separate bounded waves; do not mix them into the gate-critical Editing repair.

## Frozen authority rules

- Planning remains independently usable;
- Editing remains independently activatable;
- Combined remains optional enrichment;
- output canvas/fps is explicit product input/configuration and visible to the user;
- Resolver owns source-time grounding;
- canonical EDL remains sole exact timeline authority;
- Renderer has no editorial authority;
- Review has no edit/render mutation authority;
- render candidate is not user-final output before Review PASS;
- final commercial visuals come from user-selected local footage;
- originals remain protected;
- no silent provider switching;
- no plaintext API-secret profiles;
- no Product/Human PASS inferred from tests alone;
- no final-output publication before Review PASS.
