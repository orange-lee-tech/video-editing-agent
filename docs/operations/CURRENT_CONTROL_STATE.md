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

This baseline contains the accepted ProductFlow implementation plus the bounded Engineering Probe surface and the evidence-backed DeepSeek Director scalar-schema prompt repair.

## Stage-A completion truth

Structural progress remains **90%**.

- Stage-A completion gate: OPEN.
- Planning: Engineering mechanism PASS; Product Probe / Human Gate OPEN.
- Editing: Engineering mechanism PASS; Product Probe / Human Gate OPEN.

Engineering evidence does not authorize 100%. Stage-A 100% remains forbidden until both real ordinary-user Product Gates and the global gate are PASS.

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

The remaining problem is no longer whether the owner chain can execute. It is whether an ordinary Windows user can practically enter, understand and complete the two real product workflows without repository editing or hand-authoring internal objects.

### Planning Product Gate target

```text
real user intent / reference / commercial target
→ ordinary Windows product surface
→ Brief
→ persisted inspectable ScriptPlan
→ usable ShootingPlan
→ Human Gate judgment
```

### Editing Product Gate target

```text
user-selected real local footage
+ editing intent / output destination
→ ordinary Windows product surface
→ actual automatic Editing Core
→ canonical EDL / Renderer / Review
→ real final MP4
→ Human Gate judgment
```

### Minimum user-facing floor

Do not build a feature-rich NLE. Provide only what the Stage-A gate genuinely requires:

- create/open project;
- provide Planning inputs/references or select Editing footage;
- choose/identify output;
- start the workflow;
- see understandable progress/failure;
- inspect/locate plans and final MP4;
- avoid repository editing and manual Domain/EDL construction.

Before implementing a new frontend, audit and reuse any existing CLI/launcher/UI capability that already satisfies part of this floor.

## Product evidence boundary

Synthetic hosted Engineering media cannot close either Product Gate.

Product closure requires real user conditions and Human Gate evidence. The user machine/private-media boundary may therefore be used for the final Product Probes once the ordinary-user surface is ready.

Do not loosen Planning Review, Resolver grounding, EDL authority, Review policy or commercial constraints merely to obtain a PASS.

## Codex/resource policy

ChatGPT + GitHub remain primary for audit, control state, bounded deterministic changes and evidence review.

Codex: **NO ACTIVE RELEASE** by default. Release one coherent batch only if the ordinary-user-surface audit exposes a substantial multi-file implementation/runtime loop that materially benefits from local execution.

## Immediate corridor

1. audit current ordinary-user entry surface against `STAGE_A_COMPLETION_GATE.md`;
2. implement only the missing minimum Windows usability surface;
3. keep deterministic `main` green;
4. run real Planning Product Probe + Human Gate;
5. run real Editing automatic-final-MP4 Product Probe + Human Gate;
6. repair only evidence-backed defects;
7. set both core gates and Stage-A gate to PASS, and structural progress to 100%, only if all hard evidence passes.

## Constitutional constraints

- canonical EDL remains sole exact timeline authority;
- Renderer executes; Review classifies/routes only;
- Preview remains playback-only;
- Planning-only / Editing-only / Combined remain legitimate parallel entry modes;
- originals remain protected;
- no LLM-generated source timestamps or internal IDs as authority;
- no Product/Human PASS inferred from Engineering Probe success;
- no progress bump merely for adding a UI shell.
