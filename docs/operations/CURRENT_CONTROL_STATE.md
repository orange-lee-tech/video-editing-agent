# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-16
current_phase: R0.12
phase_state: PREVIEW_BACKEND_BENCHMARK_ACTIVE
active_work_order: R0.12-PREVIEW-BACKEND-BENCHMARK-001
accepted_code_baseline: 500c8563e3686a5aaef055ffb5301553aa999fd9
control_plane_baseline: 4bfd58cb0938db41ca212e8ffdb6d920edf3be75
previous_work_order: R0.12-EDITING-DIRECTOR-ENTRY-001
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
- Combined: Planning artifacts optionally enrich the same Editing Core.

Accepted code baseline remains `500c8563e3686a5aaef055ffb5301553aa999fd9`. No new production code is authorized by the current benchmark Work Order.

## Current active boundary

`R0.12-PREVIEW-BACKEND-BENCHMARK-001` is ACTIVE.

Goal:

`real Windows environment + standardized media corpus`
`→ GStreamer D3D11 / approved LGPL libmpv / libVLC evidence`
`→ Preview backend ADR`

The benchmark exists to unblock later interactive Preview integration and downstream desktop/frontend decisions without giving any playback library EDL/timeline authority.

## Tool routing

### ChatGPT + GitHub

Primary control/analysis channel:

- current official candidate/license/runtime verification;
- benchmark design;
- evidence interpretation;
- ADR/governance writes;
- final acceptance.

### User PowerShell

Primary execution channel:

- Windows environment inventory;
- controlled candidate install after source approval;
- local media generation/use;
- playback/seek/resource measurements;
- logs and runtime evidence.

### Codex

**NO ACTIVE RELEASE.**

Remaining Plus/Codex quota is intentionally preserved. Do not spend Codex on environment discovery, package installation, benchmarking or ADR reasoning.

Reconsider Codex only after a backend winner exists and a later bounded integration task actually benefits from coherent multi-file execution or repeated modify→run→observe loops.

## Constitutional constraints

- EDL remains sole exact timeline authority.
- PreviewBackend is playback-only.
- final rendering remains canonical EDL → Renderer; preview/proxy media is not quality authority.
- original user media is never overwritten.
- CPU-only remains a supported baseline; GPU acceleration is optional routing.
- no unreviewed third-party binary is adopted for product distribution.
- GUI/desktop framework remains undecided during this benchmark.

## Current next action

Stage 0 only: collect the user's Windows/hardware/runtime inventory before installing any Preview candidate.

After inventory, ChatGPT will verify current official sources and prepare candidate-specific installation/benchmark commands.

## STOP boundary

Do not concurrently implement Graphics/transitions, Proxy/cache, Renderer operational controls, GUI/desktop frontend, packaging or EDL redesign while the benchmark is active.

## Remaining R0.12 terrain after Preview decision

- bounded Stage-A Graphics + minimal transitions;
- Preview integration based on the selected backend;
- Proxy/edit-friendly media + range-aware cache;
- Renderer progress/cancellation/diagnostics and controlled execution routing.

The order after the Preview ADR will be re-evaluated from actual evidence rather than assumed now.