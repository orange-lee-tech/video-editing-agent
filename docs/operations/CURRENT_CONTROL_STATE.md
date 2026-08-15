# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-15
current_phase: R0.12
phase_state: PRODUCT_IMPLEMENTATION_EDITING_DIRECTOR_ENTRY_ACTIVE
active_work_order: R0.12-EDITING-DIRECTOR-ENTRY-001
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

`ADR-009_TWO_CORE_WORKFLOWS_PARALLEL_ENTRY.md` is ACCEPTED. `R0.12-EDITPLAN-COMPAT-001` is CLOSED at accepted code baseline `1abc185a793d6a73ea55824bd2a036a1a134151a`: Editing-only `EditPlan` values can carry exact Brief provenance without fabricated Planning artifacts while Combined provenance remains representable.

The subsequent Application audit confirms the remaining upstream production gap:

- current `ApplicationRuntime` exposes preproduction/media only;
- current `ProjectWorkspace.runtime()` requires preproduction provider ports and therefore is not an independent Editing composition root;
- current `editing/director/` contains candidate-window/retrieval helpers but no production Director workflow that creates EditPlan from Brief + persisted media understanding;
- R0.9 Product Probe correctly validated the grounded retrieval/resolution kernel but manually constructed EditSlots/EditPlan before entering it;
- current SQLite schema v5 has no EditPlan persistence because no production EditPlan producer previously existed.

Architecture Contract v0.2 treats EditPlan as a top-level durable Domain Entity and requires durable stages to support pause/revision/resume semantics. Therefore persistence becomes justified in the same bounded work that introduces a production Director producer.

## Current active boundary

`R0.12-EDITING-DIRECTOR-ENTRY-001` is ACTIVE.

Its bounded goal is:

`exact Brief + persisted eligible local footage understanding + optional exact Planning context`
`→ provider-neutral Director proposal`
`→ production Director validation/owner workflow`
`→ persisted EditPlan`
`→ existing Retrieval/CandidateWindow/Resolver kernel`

The work must not create a second editing engine or reopen R0.9.

Expected structural additions include:

- provider-neutral Director request/proposal port;
- production Director service/workflow;
- first official EditPlan repository/codec and SQLite v6 table/migration;
- independent Editing composition surface that does not require dummy Planning providers;
- replaceable DeepSeek Director adapter;
- bounded engineering CLI generate/show path;
- offline living integration proving generated slots enter the existing Resolver path;
- optional/live provider probe where credentials are available.

## Stop boundary

Material redesign/duplication of Resolver, CandidateWindow, retrieval algorithms, EDLBuilder, Canonical EDL, Renderer, subtitle, SpatialComposer, music/audio editorial, VisualUnderstanding, Preview, Proxy/cache, Graphics/transitions, Review, packaging or GUI is outside the active Work Order and requires STOP/re-audit.

Do not expand current EditSlot fields to the full future CAP-04 vocabulary merely to make the provider richer. This work uses the currently implemented intent surface.

## Execution routing

Current Codex release decision: **YES — ONE BOUNDED SESSION**.

Reason: this is now a coherent multi-file structural implementation spanning SQLite migration/persistence, Application ports/workflow, workspace composition, provider parsing/wiring, CLI and migration/integration tests. It is beyond the efficient scope of manual PowerShell patching, while architecture and boundaries are already pre-converged.

ChatGPT must independently re-observe the resulting commit, CI and critical code before acceptance. Codex PASS is evidence, not authority.

User PowerShell remains the preferred channel for simple deterministic local Windows/live-provider verification after a candidate commit exists.

Normal Foreman routing remains trigger-first:

- code location unclear -> `location`;
- architecture/ownership ambiguity -> `architecture`;
- test failure -> `quality`;
- Git state issue -> `git`;
- license/provider uncertainty -> `external`;
- destructive/high-risk operation -> `high-risk`.

## Next gate

Do not activate Graphics/Preview/Proxy/Renderer productization work concurrently with this cross-cutting entry correction.

After this Work Order closes, resume remaining R0.12 terrain: bounded Graphics/minimal transitions, Preview backend benchmark, Proxy/cache and remaining Renderer operational controls.

Final Stage-A closure still requires real Planning-only, Editing-only and Combined end-to-end workflows through an ordinary Windows user-facing path; this Director entry is necessary but not sufficient for Stage-A 100%.
