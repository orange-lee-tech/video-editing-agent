# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-16
current_phase: R0.12
phase_state: R0_12_NEXT_WORK_SELECTION_PENDING
active_work_order: NONE
accepted_code_baseline: 500c8563e3686a5aaef055ffb5301553aa999fd9
control_plane_baseline: dc4b1fa132ea7e6dff8483d2ecf6a71517ab0b75
previous_work_order: R0.12-EDITING-DIRECTOR-ENTRY-001
previous_work_order_result: PASS
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Routing truth

`ADR-009_TWO_CORE_WORKFLOWS_PARALLEL_ENTRY.md` remains the accepted workflow architecture:

- Planning-only may end at persisted ScriptPlan/ShootingPlan;
- Editing-only is independently activatable from Brief/editorial intent + user local footage;
- Combined is composition using the same Editing Core, with Planning artifacts as optional exact-revision context rather than an activation license.

The Domain compatibility correction `R0.12-EDITPLAN-COMPAT-001` is CLOSED.

The upstream production entry correction `R0.12-EDITING-DIRECTOR-ENTRY-001` is also CLOSED at accepted code baseline `500c8563e3686a5aaef055ffb5301553aa999fd9`.

## Accepted Editing Director/Application baseline

Production now provides:

`exact persisted Brief + eligible persisted local Shot/ShotAnalysis evidence + optional exact Planning context`
`→ provider-neutral Director proposal`
`→ validated production Director workflow`
`→ persisted revisioned EditPlan`
`→ existing Retrieval/CandidateWindow/Resolver kernel`

Accepted structural facts:

- Editing-only does not fabricate ScriptPlan/ShootingPlan;
- Combined preserves exact optional Planning provenance;
- an independent `ProjectWorkspace.editing_runtime(...)` exists without dummy preproduction provider requirements;
- EditPlan is now durably persisted in SQLite schema v6 with immutable exact revision identity and lineage;
- DeepSeek is only a replaceable adapter behind the neutral Director port;
- provider content does not receive or commit Shot/Asset/source-time/EDL authority;
- malformed provider scalar/time values and one-sided duration bounds fail closed;
- unique slot IDs remain required, while equal `order` values remain legal under the existing deterministic ordering semantics;
- generated EditPlan slots enter the existing Retrieval/CandidateWindow/Resolver path;
- Resolver, CandidateWindow, retrieval algorithms, EDLBuilder, Renderer and other STOP-scope production systems were not materially redesigned.

Formal closure evidence:

`docs/validation/R0.12_EDITING_DIRECTOR_ENTRY_CLOSURE.md`

## Review/CI truth

Primary implementation candidate `38f3ea6...` passed CI but independent ChatGPT review found bounded fail-closed defects. Those defects were corrected by `68b2f47...`.

Final semantic review then removed an over-strict slot-order uniqueness rule through `500c856...`, preserving the pre-existing Domain contract rather than expanding it without authority.

Human Gate local evidence included full repository quality gates (`563 passed` after hardening), Director 6/6 engineering probe and existing R0.12 living smoke 10/10. Final accepted commit `500c856...` was independently re-observed with exactly two changed files/eight deletions and remote `ci/quality-gate-diagnostic = success`.

## Current active boundary

There is **no active implementation Work Order**.

Do not begin substantive production-code construction until a new bounded Work Order is activated after re-observing current roadmap dependencies.

Known remaining R0.12 terrain:

1. bounded Stage-A Graphics + minimal transitions;
2. Preview backend benchmark/ADR using real Windows evidence;
3. Proxy/cache with exact source-time mapping and affected-only invalidation;
4. remaining Renderer operational controls such as progress/cancellation/diagnostics and controlled execution routing where structurally required.

These items are not authorized concurrently merely because they are all listed.

## Codex routing

Current Codex release decision: **NO ACTIVE RELEASE**.

The prior one-session release was consumed by `R0.12-EDITING-DIRECTOR-ENTRY-001` and is closed.

For the next Work Order, perform a fresh Codex 放行审查:

- deterministic control/docs/schema or small bounded changes → ChatGPT/GitHub + User PowerShell preferred;
- real Windows preview/player/proxy/runtime integration, repeated modify→run→observe loops, GPU/player/backend diagnostics or coherent broad multi-file execution → Codex may be justified.

## Next gate

Re-observe the exact R0.12 roadmap and dependency order before choosing the next Work Order.

Preview backend selection remains a prerequisite for later GUI/desktop commitment. Stage-A 100% still requires ordinary-user Planning-only, Editing-only and Combined product paths and a real final MP4 through the actual user-facing workflow; this accepted Director entry is necessary engineering foundation, not that final product gate.
