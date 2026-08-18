# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-18
current_phase: R0.12
phase_state: STAGE_A_PRODUCT_GATE_EXECUTION_ACTIVE
active_work_order: R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001
accepted_code_baseline: b6572602c0f7faaa22383dab9fffa361fb946e75
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

The frozen two-core architecture remains unchanged:

- Planning-only: `Brief → ScriptPlan → ShootingPlan`;
- Editing-only: `Brief/editorial intent + user local footage → Editing Core`;
- Combined: exact Planning revisions optionally enrich the same Editing Core.

Canonical EDL remains sole exact timeline authority.

## Accepted production baseline

Current accepted production-code baseline:

`b6572602c0f7faaa22383dab9fffa361fb946e75`

Exact-head CI:

`32127020333` — `ci/quality-gate-diagnostic = success`.

## Planning Product Gate — PASS

Durable evidence:

`docs/validation/R0.12_STAGE_A_PLANNING_PRODUCT_GATE.md`

On 2026-08-18 the ordinary Windows launcher completed a real reference-assisted Planning run through:

`project_ready → input_validation → ingest_understanding → ScriptPlan generation → ShootingPlan generation → completed`.

The launcher presented exact persisted ScriptPlan and ShootingPlan revisions. The user explicitly judged the script acceptable, the shooting plan acceptable and identified no blocking problem in the accepted result.

Therefore:

- Planning Engineering mechanism: PASS;
- Planning real Product Probe: PASS;
- Planning Human Gate: PASS;
- `core_1_planning_product_gate: PASS`.

The successful gate does not imply feature completeness. Ordinary-user follow-up feedback is preserved in:

`docs/roadmap/PRODUCT_UX_BACKLOG.md`.

Important known non-blocking follow-up: with empty authoritative facts/reference inputs, a separate Planning attempt generated unsupported concrete product claims and the semantic reviewer correctly rejected them, but the product currently terminates instead of automatically repairing/regenerating a safe claim-free proposal. The reviewer must remain strict; robustness should be improved through bounded repair and localized explanation.

## Stage-A completion truth

Structural progress remains **90%** because Editing Product/Human Gate remains OPEN.

- Stage-A completion gate: OPEN.
- Planning Product/Human Gate: PASS.
- Editing Engineering mechanism: PASS; Product Probe / Human Gate OPEN.

No UI polish, backlog item or Planning PASS authorizes Stage-A 100% before a real Editing final MP4 and Human Gate PASS.

## Current active boundary — Editing Product Gate

`R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001` remains ACTIVE with mode:

`PRODUCT PROBE → HUMAN GATE`

There is **no active Codex release**.

The immediate remaining work is:

1. synchronize current `main` to the real Windows workspace;
2. run Editing-only through the ordinary launcher with real user-selected local footage;
3. provide real editing intent and a real output MP4 destination;
4. execute actual ingest / shot detection / understanding / Director / grounded Resolver / canonical EDL / Renderer / Review;
5. verify original local media remains untouched;
6. obtain and watch the real final MP4 on Review PASS;
7. complete the ordinary Editing Human Gate;
8. repair only evidence-backed blockers;
9. set Stage-A gate and structural progress to 100 only if Editing also passes and all completion invariants remain true.

## Product UX backlog boundary

`docs/roadmap/PRODUCT_UX_BACKLOG.md` records current ordinary-user feedback including:

- output scrollbar and TXT export;
- UI-aligned localization;
- safe local profile/API credential persistence;
- required/optional placeholder guidance;
- bounded reference-share-link handling;
- no-facts safe creative repair;
- opt-in public-material guidance and similar-example research;
- startup splash/progress polish.

These items do not reopen Planning PASS. They should not preempt the active Editing Product Gate unless one directly blocks that gate.

## Resource policy

Codex quota is reserved for a proven nontrivial code defect only.

Do not use Codex for environment setup, API-secret configuration, routine launcher use, documentation/governance, deterministic provider compatibility fixes, or cosmetic backlog work.

Prefer user-run PowerShell for the local Windows target and ChatGPT/GitHub for observation, evidence review and governance.

## Product evidence boundary

Synthetic hosted Engineering media cannot close Editing Product Gate.

Editing Product Gate requires real user-selected local footage through the ordinary launcher, actual automatic processing to a real final MP4 on Review PASS, original-media protection and Human judgment of the resulting video/workflow.

## Failure classification

Before changing code, classify any failure as:

1. environment/configuration;
2. provider/network/input condition;
3. product-surface usability defect;
4. implementation/architecture defect;
5. Human Gate quality failure.

Only category 4, or a clearly nontrivial category 3, can justify a bounded Codex release.

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
- no LLM-generated timestamps or internal IDs as authority;
- no silent stock/generated replacement visuals;
- no silent provider switching;
- no Product/Human PASS inferred from Engineering evidence;
- no structural-progress bump before both real gates pass.
