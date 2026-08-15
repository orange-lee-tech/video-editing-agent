# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-15
current_phase: R0.12
phase_state: PRODUCT_IMPLEMENTATION_EDITPLAN_COMPAT_CLOSED_HANDOFF
active_work_order: R0.12-EDITPLAN-COMPAT-001
accepted_code_baseline: 1abc185a793d6a73ea55824bd2a036a1a134151a
control_plane_baseline: 1012f239aa95899e914ba6091c3b825dfc6302fe
previous_work_order: R0.12-EDITPLAN-COMPAT-001
previous_work_order_result: PASS
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Routing truth

`ADR-009_TWO_CORE_WORKFLOWS_PARALLEL_ENTRY.md` is ACCEPTED: Planning Workflow and Editing Workflow are parallel primary-capability entries, while Combined Workflow is their composition. `Brief` is the common intent root; Planning may enrich Editing but is not an activation license for Editing.

`R0.12-EDITPLAN-COMPAT-001` is accepted and CLOSED at code baseline `1abc185a793d6a73ea55824bd2a036a1a134151a`.

The accepted Domain boundary now allows explicit Brief-rooted Editing-only `EditPlan` values without fabricated ScriptPlan/ShootingPlan, preserves exact Planning provenance in Combined mode, intentionally retains the prior complete ScriptPlan+ShootingPlan shape for compatibility, and fails closed on broken provenance. Resolver and EDLBuilder authority remains independent of Planning provenance once EditSlots/grounded decisions are fixed.

No production redesign occurred in Resolver, CandidateWindow generation, Retrieval, EDLBuilder, Canonical EDL, Renderer, Media Understanding, subtitle, spatial, music or audio. No fictitious EditPlan persistence migration was added.

Durable validation: `docs/validation/R0.12_EDITPLAN_PARALLEL_ENTRY_CLOSURE.md`.

## Verification truth

Accepted local evidence includes 20 focused PASS, full pytest 551 PASS, Ruff format PASS, Ruff lint PASS, mypy 184 source files PASS, import-linter 3 contracts kept, build PASS, diff-check PASS and the existing living Resolver → EDLBuilder → Renderer smoke 10/10 PASS with verified MP4 output.

Remote GitHub independently confirms `ci/quality-gate-diagnostic = success` at `1abc185a793d6a73ea55824bd2a036a1a134151a`.

The first semantic commit exposed a process defect rather than a product defect: local acceptance had omitted the CI formatter gate. Future full local acceptance must include `uv run ruff format --check .` as well as `uv run ruff check .` before code is declared green.

## Current gate

There is intentionally no active downstream implementation task. `CURRENT_WORK_ORDER.md` is CLOSED, so Foreman should block until the next bounded work order is prepared.

The next cross-cutting structural surface to pre-process is a real Editing Application entry/orchestration boundary. It must accept Brief/editorial intent + user footage, permit optional Planning context, and reuse the same existing Editing Core. An empty wrapper, hand-authored EditPlan shortcut, or duplicate Resolver/EDLBuilder/Renderer path is not acceptable closure.

After that bounded correction, continue the remaining R0.12 productization terrain: Graphics/minimal transitions, Preview backend benchmark, Proxy/cache, and Renderer operational controls.

Final Stage-A closure still requires real Planning-only, Editing-only and Combined workflows through an ordinary Windows user-facing path.

## Execution routing

Current Codex release decision: **NO ACTIVE CODEX TASK**.

Use GitHub for deterministic governance/audit, User PowerShell for simple local deterministic execution, and only release Codex when a bounded task actually requires complex multi-file/runtime/debug iteration.

Normal Foreman routing remains trigger-first:

- code location unclear -> `location`;
- architecture/ownership ambiguity -> `architecture`;
- test failure -> `quality`;
- Git state issue -> `git`;
- license/provider uncertainty -> `external`;
- destructive/high-risk operation -> `high-risk`.
