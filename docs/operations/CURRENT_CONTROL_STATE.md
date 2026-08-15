# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-15
current_phase: R0.12
phase_state: PRODUCT_IMPLEMENTATION_EDITPLAN_COMPAT_ACTIVE
active_work_order: R0.12-EDITPLAN-COMPAT-001
accepted_code_baseline: 827b84941e1726bab374f2ffea9a746f49f6e570
control_plane_baseline: 1012f239aa95899e914ba6091c3b825dfc6302fe
previous_work_order: R0.12-SUBTITLE-001
previous_work_order_result: PASS
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Routing truth

`R0.12-SUBTITLE-001` remains accepted and closed at code baseline `827b84941e1726bab374f2ffea9a746f49f6e570`.

The subsequent supervisory architecture audit identified a localized product-semantic defect: current `EditPlan` requires `script_plan_ref` and `shooting_plan_ref`, which incorrectly makes Planning artifacts prerequisites for Editing-only entry even though the Product Constitution defines Planning Core and Editing Core as parallel primary capabilities.

`ADR-009_TWO_CORE_WORKFLOWS_PARALLEL_ENTRY.md` is now ACCEPTED. The Architecture Contract v0.2 Section 1 chain is interpreted as Combined Workflow, not the unique product path. Planning Workflow and Editing Workflow are independently legitimate; Combined mode composes them and reuses the same Editing Core.

## Current active boundary

`R0.12-EDITPLAN-COMPAT-001` is ACTIVE.

The migration is deliberately narrow:

- add explicit Brief-rooted Editing intent/provenance semantics to `EditPlan`;
- allow Editing-only plans without ScriptPlan/ShootingPlan;
- retain exact Planning provenance for Combined mode;
- preserve legacy combined construction where required for compatibility;
- fail closed on broken provenance shapes;
- add focused regression evidence that Planning context does not change Resolver/EDL authority for otherwise identical plans;
- do not invent an EditPlan database migration because the current repository has no persisted EditPlan table/codec.

Material modification of Resolver, CandidateWindow generation, EDLBuilder, Canonical EDL, Renderer, Media Understanding, subtitle, spatial or audio semantics is outside scope and is a stop/re-audit trigger.

## Execution routing

Current Codex release decision: **NO**.

The audited production change is small enough to attempt through ChatGPT-authored deterministic patch + User PowerShell application/verification. Escalate to Codex only on evidence of unexpected multi-file/type/import/runtime complexity.

Normal Foreman routing remains trigger-first:

- code location unclear -> `location`;
- architecture/ownership ambiguity -> `architecture`;
- test failure -> `quality`;
- Git state issue -> `git`;
- license/provider uncertainty -> `external`;
- destructive/high-risk operation -> `high-risk`.

## Next gate after this work order

After EditPlan compatibility closes, activate a separate bounded Application work order for a real Editing entry point that reuses the same Editing Core. Do not fake that closure with an empty wrapper or by duplicating Resolver/EDLBuilder/Renderer.

Final Stage-A closure still requires real Planning-only, Editing-only and Combined product probes through ordinary user-facing execution; fixtures or hand-authored internal decisions cannot substitute.
