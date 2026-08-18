# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-18
current_phase: R0.12
phase_state: STAGE_A_PRODUCT_GATE_EXECUTION_ACTIVE
active_work_order: R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001
accepted_code_baseline: 49f14cc0a9b4a798491314f58b9d6df9120f350f
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

`49f14cc0a9b4a798491314f58b9d6df9120f350f`

Original Stage-A product-surface implementation closure:

`docs/validation/R0.12_STAGE_A_PRODUCT_SURFACE_IMPLEMENTATION_CLOSURE.md`

Current exact-head CI:

`32125492197` — `ci/quality-gate-diagnostic = success`.

The accepted Stage-A ordinary-user surface includes:

- Simplified Chinese / English launcher switching;
- a user-facing API Settings entry organized by product capability rather than environment-variable names;
- independent `思考指挥 / Reasoning & Direction` and `视觉理解 / Visual Understanding` credential slots;
- current supported provider disclosure: DeepSeek for reasoning/direction, Gemini or OpenAI for visual understanding;
- explicit notice that these APIs are used for understanding, reasoning, planning and editing decisions, not video generation;
- permission to enter the same key string in both capability slots, while warning that the selected visual API/model must actually support image input;
- session-local secret application only: keys are not written to project state, repository files or logs.

The existing provider adapters and ownership boundaries remain unchanged. The Settings adapter only maps user capability configuration onto the provider environment contract.

## Real Product Probe defect evidence — Gemini compatibility and transient transport

The real Windows Planning Product Probe with a user-selected local reference video has now exposed three sequential provider-path defects or robustness gaps after successfully reaching visual understanding.

First, `gemini-2.5-flash` returned provider `NOT_FOUND` for `generateContent` and directed new users to `gemini-3.6-flash`. The repair moved the Stage-A Gemini visual default to `gemini-3.6-flash` and preserved bounded provider HTTP error detail.

Second, the rerun reached `gemini-3.6-flash` but returned HTTP 400 because `generationConfig.responseFormat.text.mimeType` was sent as the legacy string `application/json`. The live provider contract requires the enum value `APPLICATION_JSON`; that contract is now locked in regression coverage.

Third, the next real rerun failed with `VisualProviderTransientError: Gemini request failed in transport`. The old transport collapsed `TimeoutError` and `URLError` into the same message, and the real Stage-A composition bypassed the repository's existing `RetryingVisualUnderstandingPort`, so a single transient visual-provider failure could abort the entire Planning run.

Accepted repair through `49f14cc0a9b4a798491314f58b9d6df9120f350f`:

- real Gemini and OpenAI visual-provider composition is wrapped by the existing retry decorator;
- only explicit `VisualProviderTransientError` is retried, up to the existing three-attempt policy; response/schema failures are not retried and no fake visual semantics or silent provider switching is introduced;
- Gemini timeout failures now report the configured timeout budget;
- Gemini `URLError` failures now preserve a bounded safe transport reason;
- the 60-second per-request timeout remains unchanged until a rerun provides evidence that the budget itself is inadequate;
- regression coverage verifies retry composition and the new transient transport diagnostics.

These repairs are Engineering PASS only. The same real Planning Product Probe must be rerun before any Product/Human Gate can pass.

## Stage-A completion truth

Structural progress remains **90%**.

- Stage-A completion gate: OPEN.
- Planning: Engineering mechanism PASS; real Product Probe remains in progress after provider-path repair; Human Gate OPEN.
- Editing: Engineering mechanism PASS; Product Probe / Human Gate OPEN.

Engineering tests, CI, launcher smoke, bilingual UI, API Settings or provider repairs do not authorize 100%.

## Current active boundary — real Product Gates

`R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001` remains ACTIVE with mode:

`PRODUCT PROBE → HUMAN GATE`

There is **no active Codex release**.

The remaining work is:

1. synchronize this accepted state to the actual Windows workspace;
2. use the product Settings surface for user-owned API credentials as needed;
3. rerun the same real Planning Product Probe through `video-editing-agent launch`;
4. complete the Planning Human Gate only after a real ScriptPlan/ShootingPlan is produced;
5. run a real Editing Product Probe using user-selected real/private local footage through the launcher;
6. complete the Editing Human Gate;
7. classify and repair only evidence-backed failures;
8. set both core gates and the global Stage-A gate to PASS, and structural progress to 100%, only if all hard evidence passes.

## Resource policy

Codex quota is reserved for a future **proven nontrivial code defect only**.

Do not use Codex for:

- FFmpeg/GStreamer/TransNet installation;
- PATH repair;
- API-secret configuration;
- Environment Doctor execution;
- launcher operation;
- routine local verification;
- deterministic provider-version compatibility updates;
- small deterministic provider composition/diagnostic repairs;
- documentation/governance edits.

Prefer user-run PowerShell for local operations and ChatGPT/GitHub for observation/governance.

## Runtime evidence boundary

The actual Windows target must report the capabilities needed by the selected real probe.

Known capability classes:

- Windows/Python host runtime;
- FFmpeg + ffprobe;
- reviewed TransNetV2 runtime/package-owned weights;
- user-owned DeepSeek credential for the current reasoning/direction provider;
- one explicitly configured supported visual-understanding provider when reference-video analysis or Editing requires it;
- approved private GStreamer Preview runtime only when Preview evidence is required.

Secret values must not be committed, logged or pasted into governance evidence.

Planning without reference remains a valid independent path and may be probed before visual-understanding capability is configured.

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
