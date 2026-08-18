# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-18
current_phase: R0.12
phase_state: STAGE_A_PRODUCT_GATE_EXECUTION_ACTIVE
active_work_order: R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001
accepted_code_baseline: af5865df14b9f1cceaa9e6c1fe4dadf14cc60058
control_plane_baseline: 79c3be540f335477699223292580f32f6bb3c807
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: PASS
core_2_editing_product_gate: ENGINEERING_PASS_PRODUCT_HUMAN_OPEN
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
- canonical EDL remains sole exact timeline authority.

## Accepted production baseline

`af5865df14b9f1cceaa9e6c1fe4dadf14cc60058`

Exact-head CI:

`32145822611` — `ci/quality-gate-diagnostic = success`.

This baseline includes the accepted Director proposal repair and Gemini provider-aware retry-delay repair discovered through real Windows Product Probes.

## Gate truth

### Planning

**Product/Human Gate: PASS**.

Durable evidence:

`docs/validation/R0.12_STAGE_A_PLANNING_PRODUCT_GATE.md`

The ordinary Windows launcher completed a real Planning run and the user judged both ScriptPlan and ShootingPlan acceptable with no blocking issue.

### Editing

**Engineering mechanism: PASS / Product Probe: IN PROGRESS / Human Gate: OPEN**.

Real Editing-only probes have reached local-media understanding and Director boundaries, exposing and repairing several evidence-backed defects. The latest same-day probe is currently blocked by the user's Gemini free-tier quota after legitimate real-product requests. Persistent provider quota exhaustion must fail explicitly and does not authorize silent provider/model switching.

## Temporary UX stabilization boundary

The user explicitly chose to use the provider-quota reset interval to consolidate already-recorded ordinary-user UX/robustness work.

Current execution mode:

`PRODUCT PROBE → TEMPORARY UX STABILIZATION → HUMAN GATE`

Active Codex release:

`OPEN — BOUNDED UX STABILIZATION WAVE ONLY`

Execution spec:

`docs/operations/STAGE_A_UX_STABILIZATION_WAVE.md`

Primary wave includes:

- responsive Tkinter background execution;
- output scrollbar and UTF-8 TXT export;
- UI-aligned localization;
- honest ETA/progress with at least 30-second recalculation;
- one Editing source-selection mechanism: multi-select `Media Files`; remove ordinary `Media Folder` UI;
- first-run required/optional placeholders;
- local form/API profile files with Windows-protected API secrets;
- bounded Planning no-facts repair without weakening factual review;
- bounded share-text HTTPS extraction without platform scraping;
- real-milestone startup splash;
- localized provider/quota UX;
- focused regression tests and Windows manual smoke.

The `公共素材` / `类似方案` concepts remain backlog-only until real replaceable research/material adapters exist; do not ship decorative controls that do nothing.

## Structural progress

Remain at **90%**.

- Stage-A completion gate: OPEN.
- Planning Product/Human Gate: PASS.
- Editing Product/Human Gate: OPEN.

The UX wave cannot raise progress or close the gate.

## Return path after UX acceptance/provider reset

1. reobserve and accept exact UX implementation commit + CI;
2. synchronize accepted `main` to Windows;
3. use the single multi-select media-file mechanism;
4. record non-empty source SHA-256 hashes;
5. run Editing-only with Combined unchecked;
6. execute ingest / shot detection / understanding / Director / grounded Resolver / canonical EDL / Renderer / Review;
7. produce final MP4 only on Review PASS;
8. verify source hashes unchanged;
9. user watches the MP4 and completes the ordinary Editing Human Gate;
10. set Stage A to 100 only if every completion invariant passes.

## Constitutional constraints

- Planning remains optional for Editing;
- Planning-only / Editing-only / Combined remain legitimate;
- reference-only media remains Resolver-ineligible;
- commercial final visuals come from user-selected local footage;
- source-time grounding remains Resolver-owned;
- canonical EDL remains sole exact timeline authority;
- Renderer executes only;
- Review classifies/routes only;
- originals remain protected;
- no LLM-generated timestamps/internal IDs as authority;
- no silent stock/generated visual replacement;
- no silent provider switching;
- no plaintext API-secret profiles;
- no Product/Human PASS inferred from tests alone;
- no structural-progress bump before both real gates pass.
