# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-18
current_phase: R0.12
phase_state: STAGE_A_PRODUCT_GATE_EXECUTION_ACTIVE
active_work_order: R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001
accepted_code_baseline: 0134d0c4a741eb2babed7275c0aaef42045f2dc4
control_plane_baseline: 79c3be540f335477699223292580f32f6bb3c807
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

The frozen two-core architecture remains unchanged:

- Planning-only: `Brief → ScriptPlan → ShootingPlan`;
- Editing-only: `Brief/editorial intent + user local footage → Editing Core`;
- Combined: exact Planning revisions optionally enrich the same Editing Core.

Canonical EDL remains sole exact timeline authority.

## Accepted production baseline

Current accepted production-code baseline:

`0134d0c4a741eb2babed7275c0aaef42045f2dc4`

Implementation closure:

`docs/validation/R0.12_STAGE_A_PRODUCT_SURFACE_IMPLEMENTATION_CLOSURE.md`

Exact-head CI:

`32111192942` — `ci/quality-gate-diagnostic = success`.

The ordinary-user Stage-A product surface is accepted. The implementation includes the stdlib Tkinter launcher, user-semantic Planning/Editing inputs, reference-only guidance bridge, live progress observation, runtime discovery/diagnostics, exact Planning presentation, Editing result presentation, deterministic folder expansion, and safe optional same-session/same-project Combined enrichment.

## Stage-A completion truth

Structural progress remains **90%**.

- Stage-A completion gate: OPEN.
- Planning: Engineering mechanism PASS; Product Probe / Human Gate OPEN.
- Editing: Engineering mechanism PASS; Product Probe / Human Gate OPEN.

Engineering tests, CI and launcher smoke do not authorize 100%.

## Current active boundary — real Product Gates

`R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001` remains ACTIVE with mode:

`PRODUCT PROBE → HUMAN GATE`

There is **no active Codex release**.

The remaining work is:

1. synchronize this accepted state to the actual Windows workspace;
2. repair required runtime/provider capabilities using local PowerShell/configuration;
3. run a real Planning Product Probe through `video-editing-agent launch`;
4. complete the Planning Human Gate;
5. run a real Editing Product Probe using user-selected real/private local footage through the launcher;
6. complete the Editing Human Gate;
7. classify and repair only evidence-backed failures;
8. set both core gates and the global Stage-A gate to PASS, and structural progress to 100%, only if all hard evidence passes.

## Resource policy

Codex quota is reserved for a future **proven code defect only**.

Do not use Codex for:

- FFmpeg/GStreamer/TransNet installation;
- PATH repair;
- API-secret configuration;
- Environment Doctor execution;
- launcher operation;
- routine local verification;
- documentation/governance edits.

Prefer user-run PowerShell for local operations and ChatGPT/GitHub for observation/governance.

## Runtime evidence boundary

The actual Windows target must report the capabilities needed by the selected real probe.

Known capability classes:

- Windows/Python host runtime;
- FFmpeg + ffprobe;
- reviewed TransNetV2 runtime/package-owned weights;
- DeepSeek credential;
- one explicitly configured supported visual-understanding provider when reference-video analysis or Editing requires it;
- approved private GStreamer Preview runtime only when Preview evidence is required.

Secret values must not be committed, logged or pasted into governance evidence.

Planning without reference remains a valid independent path and may be probed before media-analysis runtime is fully ready.

## Product evidence boundary

Synthetic hosted Engineering media cannot close either Product Gate.

Planning Product Gate requires a real user target through the ordinary launcher and Human judgment of the resulting ScriptPlan/ShootingPlan usefulness and shootability.

Editing Product Gate requires real user-selected local footage through the ordinary launcher, actual automatic processing to a real final MP4 on Review PASS, original-media protection and Human judgment of the resulting video/workflow.

## Failure classification

Before changing code, classify any failure as:

1. environment/configuration;
2. provider/network/input condition;
3. product-surface usability defect;
4. implementation/architecture defect;
5. Human Gate quality failure.

Only category 4, or a clearly nontrivial category 3, can justify a new bounded Codex release.

## Constitutional constraints

- Planning remains optional for Editing;
- Planning-only / Editing-only / Combined remain legitimate;
- reference-only media remains Resolver-ineligible;
- commercial final visuals come from user-supplied local footage;
- source-time grounding remains Resolver-owned;
- canonical EDL remains sole exact timeline authority;
- Renderer executes only;
- Review classifies/routes only;
- originals remain protected;
- no LLM-generated timestamps or internal IDs as authority;
- no stock/generated replacement visuals;
- no silent provider switching;
- no Product/Human PASS inferred from Engineering evidence;
- no structural-progress bump before both real gates pass.
