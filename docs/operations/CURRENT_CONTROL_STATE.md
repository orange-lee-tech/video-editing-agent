# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-18
current_phase: R0.12
phase_state: STAGE_A_PRODUCT_GATE_CLOSURE_ACTIVE
active_work_order: R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001
accepted_code_baseline: 1e90e2dd3d235271ef48bb7a708a1899ce5b87a4
control_plane_baseline: 79be7b863d1802ad4f92474b25a357d215ec0dec
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: ENGINEERING_PASS_PRODUCT_HUMAN_OPEN
core_2_editing_product_gate: ENGINEERING_PASS_PRODUCT_HUMAN_OPEN
previous_work_order: R0.12-PRODUCT-FLOW-ORCHESTRATION-001
previous_work_order_result: PASS
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Routing truth

The accepted two-core architecture remains unchanged:

- Planning-only: `Brief → ScriptPlan → ShootingPlan`;
- Editing-only: `Brief/editorial intent + user local footage → Editing Core`;
- Combined: exact Planning revisions optionally enrich the same Editing Core.

Current accepted production-code baseline:

`1e90e2dd3d235271ef48bb7a708a1899ce5b87a4`

This baseline contains the accepted ProductFlow implementation plus its bounded Engineering evidence and the evidence-backed DeepSeek Director scalar-schema prompt repair.

## Stage-A completion truth

Structural progress remains **90%**.

- Stage-A completion gate: OPEN.
- Planning: Engineering mechanism PASS; Product Probe / Human Gate OPEN.
- Editing: Engineering mechanism PASS; Product Probe / Human Gate OPEN.

Engineering evidence or launcher implementation does not authorize 100%. Stage-A 100% remains forbidden until both real ordinary-user Product Gates and the global gate are PASS.

## Closed R0.12 boundaries

Accepted/closed productization boundaries include:

- GStreamer primary Preview;
- Stage-A Product I/O Contract;
- mixed source-audio / VoiceTreatment / audible QC;
- Reference URL acquisition;
- rights-aware public music acquisition;
- minimum Review / repair;
- Windows Environment Doctor;
- ProductFlow orchestration Engineering closure.

ProductFlow closure evidence:

`docs/validation/R0.12_PRODUCT_FLOW_ORCHESTRATION_CLOSURE.md`

Accepted ProductFlow Engineering evidence:

- Windows run `32046190310` — PASS;
- exact-head Quality Gate `32046499144` — PASS;
- direct second-process exact canonical EDL reload — PASS;
- real FFmpeg MP4 with video + audio — PASS;
- original source hash preservation — PASS;
- Review — PASS.

These facts are Engineering evidence only.

## Current active boundary — Stage-A Product Gate closure

`R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001` is ACTIVE.

Ordinary-user surface audit:

`docs/validation/R0.12_STAGE_A_PRODUCT_SURFACE_AUDIT.md`

Audit result: **IMPLEMENTATION REQUIRED**.

The accepted mechanisms work, but the product surface still lacks the complete reference-guidance bridge and a practical ordinary Windows launch/presentation layer.

### Audit-proven gaps

- ordinary Planning input does not expose accepted authoritative facts/references;
- ProductFlow / ProjectWorkspace drop existing `ReferenceStyleGuidance` before Script/Shooting workflows;
- current ProductFlow launch requires hand-written JSON;
- Editing exposes model/TransNet/tool plumbing as launch arguments;
- no ordinary Windows launcher/file chooser exists;
- Planning exact results are not directly presented to the user;
- progress events exist but are not observable live;
- Editing folder selection convenience is absent;
- Environment Doctor lacks mandatory Shot-detection runtime readiness.

### Frozen implementation direction

Reuse the existing owner chain. Add only:

1. product-facing reference input → accepted reference-only acquisition/analysis → `ReferenceStyleGuidance` plumbing;
2. authoritative-fact/reference ProductFlow support;
3. optional live `ProductFlowEvent` observation;
4. reviewed runtime defaults/TransNet auto-resolution + minimal Doctor coverage;
5. a thin ordinary Windows launcher/presentation layer;
6. readable exact Planning outputs and discoverable Editing result.

No new Editing architecture, NLE timeline or media authority is authorized.

## Codex/resource policy

The audit crossed the threshold for one complex local batch.

Codex: **ACTIVE RELEASE — SINGLE COMPLEX BATCH** for the exact implementation surface frozen in `CURRENT_WORK_ORDER.md` and `R0.12_STAGE_A_PRODUCT_SURFACE_AUDIT.md`.

Complex-batch single-writer rule is active:

- Codex owns this implementation surface until it commits/pushes and stops;
- ChatGPT must not concurrently modify the same source area;
- ChatGPT may continue remote observation and independent governance only;
- after Codex stops, ChatGPT independently reobserves GitHub/CI before acceptance.

## Product evidence boundary

Synthetic hosted Engineering media cannot close either Product Gate.

After the Codex batch is accepted and `main` is green, closure requires real user conditions and Human Gate evidence on the ordinary Windows surface.

Do not loosen Planning Review, Resolver grounding, EDL authority, Review policy or commercial constraints merely to obtain a PASS.

## Immediate corridor

1. Codex implements the bounded Stage-A product surface batch and stops;
2. ChatGPT reobserves exact `main`, diff and CI;
3. repair only concrete implementation defects;
4. run real Planning Product Probe + Human Gate;
5. run real Editing automatic-final-MP4 Product Probe + Human Gate;
6. set both core gates and Stage-A gate to PASS, and structural progress to 100%, only if all hard evidence passes.

## Constitutional constraints

- canonical EDL remains sole exact timeline authority;
- Renderer executes; Review classifies/routes only;
- Preview remains playback-only;
- Planning-only / Editing-only / Combined remain legitimate parallel entry modes;
- reference-only media remains Resolver-ineligible;
- originals remain protected;
- no LLM-generated source timestamps or internal IDs as authority;
- no Product/Human PASS inferred from Engineering Probe success;
- no progress bump merely for adding a UI shell.
