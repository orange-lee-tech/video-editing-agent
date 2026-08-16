# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-16
current_phase: R0.12
phase_state: PREVIEW_BACKEND_BENCHMARK_ACTIVE
active_work_order: R0.12-PREVIEW-BACKEND-BENCHMARK-001
accepted_code_baseline: 500c8563e3686a5aaef055ffb5301553aa999fd9
control_plane_baseline: 21abe0130dce6d0ccdfefd52f181babb18aa33b9
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
core_2_editing_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
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

Accepted code baseline remains `500c8563e3686a5aaef055ffb5301553aa999fd9`. No new production code is authorized beyond the active benchmark Work Order.

## Stage-A completion truth

Structural progress is currently **90%**.

This percentage is not allowed to reach 100 merely because backend modules, tests or a GUI exist. The hard closure contract is:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Live gate state:

- `stage_a_completion_gate: OPEN`;
- Core 1 Planning: foundation is structurally accepted, but the ordinary-user product flow is still open;
- Core 2 Editing: foundation is structurally accepted, but the ordinary-user automatic final-MP4 product flow is still open.

At 100%, both core gates must be `PASS`. Repository governance must reject a false 100% state.

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

- architecture/product boundary decisions;
- current GitHub/CI observation;
- small deterministic repository/governance writes;
- official dependency/license/runtime verification;
- benchmark design and evidence interpretation;
- Work Order activation/closure and durable validation records;
- final semantic acceptance after Codex reports.

### User PowerShell

Primary machine/environment evidence channel:

- Windows environment/runtime/hardware observation;
- private media and credentials;
- controlled installation/runtime probes;
- local synchronization;
- deterministic commands where the user's actual machine is the evidence source.

Do not turn PowerShell into manual CI when GitHub/Codex can perform the same deterministic repository verification more efficiently.

### Codex

**NO ACTIVE RELEASE** for the current Preview evidence/ADR work.

Remaining Plus/Codex quota is intentionally preserved. Do not spend Codex on environment discovery, package installation, benchmarking, GitHub observation, documentation or already-known small fixes.

Reconsider Codex only for a bounded implementation batch that materially benefits from coherent multi-file local execution and repeated edit → test → repair loops.

## Final-10-percent execution corridor

The final structural corridor is deliberately narrow. Do not open these concurrently unless a dependency requires it.

1. **Finish R0.12 productization floor**
   - evidence-backed Preview backend ADR, then thin Preview integration;
   - bounded Stage-A Graphics + minimal transitions;
   - Proxy/edit-friendly media + range-aware cache where required for practical preview;
   - Renderer progress/cancellation/diagnostics and controlled execution routing.

2. **Close the minimum Review/repair loop**
   - deterministic technical QC first;
   - machine-actionable findings routed to the smallest owner/range;
   - avoid whole-project recompute for local defects.

3. **Make the Windows runtime ordinary-user operable**
   - Environment Doctor/capability report;
   - product-owned/private dependencies where practical;
   - understandable degraded/failure states;
   - no normal requirement for repository-file editing, global developer PATH setup or manual Domain construction.

4. **Integrate the two real product cores through a plain product-facing surface**
   - Planning-only product path to persisted visible ScriptPlan + ShootingPlan;
   - Editing-only product path from selected local footage to real final MP4;
   - Combined path reuses the same Editing Core;
   - basic, practical UI is sufficient; extensibility and clarity matter more than visual richness.

5. **Run Stage-A closure Product Probes / Human Gate**
   - real planning target/reference/commercial input;
   - real user footage;
   - actual automatic chain, no hand-authored EditPlan/ResolutionDecision/EDL;
   - real final MP4 and visible plans;
   - Windows usability evidence;
   - only then may structural progress become 100%.

## Constitutional constraints

- EDL remains sole exact timeline authority.
- PreviewBackend is playback-only.
- final rendering remains canonical EDL → Renderer; preview/proxy media is not quality authority.
- original user media is never overwritten.
- CPU-capable/degraded behavior remains part of the supported product strategy; GPU acceleration is optional routing.
- no unreviewed third-party binary is adopted for product distribution.
- GUI/desktop framework remains undecided during the Preview benchmark.
- no temporary integration shortcut may fabricate Planning artifacts, source timestamps, Domain decisions or a final-product PASS.

## Current environment evidence

The first Preview benchmark machine is a Lenovo-class low-end/legacy Windows environment with Intel hardware ID `VEN_8086&DEV_1916`, but Windows currently loads `Microsoft Basic Display Adapter` instead of a vendor Intel display driver. An `OrayIddDriver` virtual display device is also present.

Treat it as **Class A degraded/fallback evidence**, not as the sole performance basis for D3D11/hardware-acceleration choice.

The repository owns an FFmpeg runtime under `.tools`; absence of global `ffmpeg`/`ffprobe` on PATH is not by itself a product defect and reinforces the private-runtime deployment direction.

## Documentation synchronization rule

Dynamic state is canonical only in:

- `docs/operations/CURRENT_CONTROL_STATE.md`;
- `docs/operations/CURRENT_WORK_ORDER.md`;
- `docs/roadmap/CURRENT_PHASE_STATUS.md`.

Stable navigation/authority files must point to those live documents instead of duplicating fragile phase snapshots.

`tools/maintenance/repo_doctor.py` + `repository-governance` are responsible for machine-checkable consistency. A phase/work-order/control-state transition is incomplete until the corresponding governance checks pass.

## STOP boundary

Do not concurrently implement Graphics/transitions, Proxy/cache, Renderer operational controls, GUI/desktop frontend, packaging or EDL redesign while the current Preview benchmark is active unless the Work Order is explicitly revised.

The next implementation writer is chosen per batch: ChatGPT/GitHub for exact low-risk changes; Codex for complex local iteration; PowerShell for genuine local-machine evidence.