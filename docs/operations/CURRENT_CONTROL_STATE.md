# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-19
current_phase: R0.12
phase_state: STAGE_A_EDITING_INTEGRATION_GAP_OPEN
active_work_order: R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001
accepted_code_baseline: c6bd96116e3ab00f76aeb87ee63ad1037ba84980
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
- typed/user-visible Output Profile supplies target canvas/fps used by Spatial and rendering;
- approved Music/Audio/Spatial/Subtitle/Graphics/transition decisions belong upstream of EDL assembly;
- canonical EDL remains the sole exact timeline authority;
- Renderer executes only;
- Review classifies/routes only;
- render candidate becomes user-final output only after Review PASS and product-layer publication/promotion.

## Accepted production baseline

`c6bd96116e3ab00f76aeb87ee63ad1037ba84980`

Exact-head CI:

`32205777259` — `ci/quality-gate-diagnostic = success`.

Accepted UX stabilization stack:

- `3df11e826bb672217528d7655ca02fc4701976d1` — `feat: stabilize Stage A desktop UX`;
- `b01978ed931dbf508e7d4b840017cac06d2a6421` — first Linux-mypy portability repair attempt; CI exposed Ruff B009;
- `c6bd96116e3ab00f76aeb87ee63ad1037ba84980` — final DPAPI typing repair; CI green.

The accepted UX change set remains limited to product adapter/UI/support/tests. Resolver, canonical EDL, Renderer and Review ownership were not modified.

## UX stabilization outcome — ACCEPTED

Windows local evidence before push:

- Ruff / mypy / import contracts / build / repo doctor: PASS;
- pytest: `713 passed`;
- launcher smoke: PASS;
- manual UI smoke: placeholders, single multi-select Media Files surface, output scrollbar/export, bilingual presentation, responsive background execution, profiles, Windows-protected API credentials and visible Splash: PASS;
- profile plaintext-secret smoke: PASS.

Remote review confirmed exactly seven intended UX/test files in the main feature commit. Linux CI then caught a Windows-only `ctypes.windll/WinError` typing portability defect that Windows mypy could not expose; the final typed-ignore repair passed exact-head CI.

## Gate truth

### Planning

**Product/Human Gate: PASS**.

Durable evidence:

`docs/validation/R0.12_STAGE_A_PLANNING_PRODUCT_GATE.md`

### Editing

**Ordinary ProductFlow integration + publication + output-profile gaps: OPEN / Product Probe: NOT GATE-READY / Human Gate: OPEN**.

Three gate-path issues remain:

1. ordinary Editing ProductFlow does not yet compose the complete Stage-A expression floor (`Music/Audio/Spatial/Subtitle/Graphics/minimal transitions`) before canonical EDL;
2. current flow renders directly to the user-selected final path before Review, instead of candidate → Review → PASS-only publication;
3. current ordinary output geometry is still a hidden `1920×1080@30` default instead of an explicit typed/user-visible Output Profile feeding Spatial/EDL/Render provenance.

Durable incident records are in `docs/logs/INCIDENT_LEDGER.md`.

These findings do not reopen accepted R0.8/R0.9/R0.10/R0.11 subsystem evidence and do not authorize a core redesign.

## Current execution corridor

`STAGE-A EDITING INTEGRATION/PUBLICATION/OUTPUT-PROFILE REPAIR → REAL PRODUCT/HUMAN GATE`

### 1. Bounded gate-path repair

- define the smallest typed Output Profile needed by Stage A and expose/propagate target width/height/fps;
- integrate existing R0.10 Music/Audio owners upstream of EDL assembly;
- integrate existing R0.11 Spatial/Auto-Reframe owners against the selected target canvas;
- integrate structured subtitle path;
- add only the bounded Stage-A title/CTA/price-card graphics and minimal-transition semantics required by the completion gate;
- render to a controlled candidate artifact;
- Review candidate;
- only Review PASS publishes/promotes to the requested final path;
- prove Output Profile / decision → EDL → render → Review → publication alignment with regressions and full Quality Gate.

### 2. Real Editing Product/Human Gate

Only after the repair is accepted and provider/runtime are available:

1. ordinary multi-select local footage, Combined unchecked for Editing-only proof;
2. select/confirm intended Output Profile;
3. record source SHA-256 hashes;
4. run actual ingest / shot detection / visual understanding / Director / grounded Resolver;
5. execute Stage-A expression floor through canonical EDL against the selected target canvas;
6. render controlled candidate;
7. Review PASS;
8. publish/promote reviewed candidate to final MP4 destination;
9. verify source hashes unchanged;
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
- UX stabilization: ACCEPTED.
- Editing Product/Human Gate: OPEN.
- Editing expression integration gap: OPEN.
- Review-before-final-publication gap: OPEN.
- explicit Output Profile gap: OPEN.

No UI polish, plain-cut MP4, subsystem-only evidence or packaging work may raise progress to 100 by itself.
