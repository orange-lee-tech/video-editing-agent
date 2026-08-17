# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-17
current_phase: R0.12
phase_state: PRODUCT_FLOW_ORCHESTRATION_ACTIVE
active_work_order: R0.12-PRODUCT-FLOW-ORCHESTRATION-001
accepted_code_baseline: 914dd7dcc72595d418d7d3bf0cb05e356dd021b9
control_plane_baseline: 764bf7f38fce81d06303f376b3e5919ae0471155
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
core_2_editing_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
previous_work_order: R0.12-WINDOWS-ENVIRONMENT-DOCTOR-001
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

Current accepted production-code baseline:

`914dd7dcc72595d418d7d3bf0cb05e356dd021b9`

## Stage-A completion truth

Structural progress remains **90%**.

- Stage-A completion gate: OPEN.
- Planning Product Gate: foundation accepted, ordinary-user flow open.
- Editing Product Gate: foundation accepted, ordinary-user automatic final-MP4 flow open.

100% remains forbidden until both Product Gates and the overall Stage-A gate are PASS.

## Closed control boundaries

### Preview — PASS/CLOSED

- GStreamer primary;
- accepted baseline `4ca3b83bfac50923bdcf15f1ad08d90b397daa23`;
- Windows production run `32030024748` — PASS;
- playback-only; backend benchmark closed.

### Product I/O Contract — PASS/CLOSED

`docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

### Mixed source-audio / VoiceTreatment / audible QC — PASS/CLOSED

`docs/validation/R0.12_MIXED_SOURCE_AUDIO_QC_CLOSURE.md`

### Reference URL acquisition — PASS/CLOSED

`docs/validation/R0.12_REFERENCE_URL_ACQUISITION_CLOSURE.md`

### Rights-aware public music — PASS/CLOSED

- `docs/validation/R0.12_PUBLIC_MUSIC_ACQUISITION_EVIDENCE.md`
- accepted baseline `72ec275c1e72e876c4bcf828a44e7852208bab29`;
- Windows run `32026331114` — PASS.

### Minimum Review / repair — PASS/CLOSED

- `docs/validation/R0.12_MINIMUM_REVIEW_REPAIR_CLOSURE.md`
- accepted baseline `2cfeb664552769ade09f58bc2905ab531733a66a`;
- Windows real-media run `32033179672` — PASS.

### Windows Environment Doctor — PASS/CLOSED

- Work Order `R0.12-WINDOWS-ENVIRONMENT-DOCTOR-001`;
- closure `docs/validation/R0.12_WINDOWS_ENVIRONMENT_DOCTOR_CLOSURE.md`;
- accepted baseline `914dd7dcc72595d418d7d3bf0cb05e356dd021b9`;
- Quality Gate `32034737393` — PASS;
- Windows production Doctor run `32035192895` — PASS.

Environment Doctor provides project-independent typed machine/tool/provider/runtime readiness and sanitized repair guidance. It does not install dependencies or mutate creative state.

## Current active boundary — product flow orchestration

`R0.12-PRODUCT-FLOW-ORCHESTRATION-001` is ACTIVE.

### Audit truth

The repository owns the major capability pieces, but no application coordinator yet represents the ordinary-user end-to-end product flows.

Current seams:

```text
ProjectWorkspace.runtime()
→ Planning + low-level media operations

ProjectWorkspace.editing_runtime()
→ Director → persisted EditPlan

R0.12 living smoke
→ manually composes Resolver → EDLBuilder → Renderer

R0.9 product probe
→ previously proved retrieval → temporal evidence → CandidateWindows → Resolver
  but composition remains Probe-only
```

### Frozen product request boundary

Ordinary product input may contain project/input/output locations, Brief/editorial intent, policy/production constraints, audio/voice intent and optional exact Planning refs.

Ordinary product input must not require AssetRef/ShotRef/CandidateWindow/ResolutionDecision/source timestamps/EDL internals.

Runtime/provider/model configuration belongs to composition/configuration, not editorial request meaning.

### Product progress boundary

Application-level projections must surface project ready, input validation, ingest/understanding, planning/editing decision, resolving, EDL assembly, render, Review/QC, completed and failed states.

These are not new Domain authorities.

### Retrieval / Resolver boundary

- lexical retrieval is a valid minimal production baseline after indexed ShotAnalysis;
- dense retrieval remains optional enhancement;
- CandidateWindows come from exact Shot boundaries or persisted TemporalAnchors/Evidence;
- no LLM-generated timestamps;
- fallback remains inside exact Shot source range and explicitly evidences boundary grounding;
- unresolved remains fail-closed.

### Downstream authority

- audio treatment remains grounded per Resolver selection;
- optional music/spatial assets are not fabricated;
- EDLBuilder alone assembles canonical timeline;
- Renderer executes canonical EDL;
- Review classifies and routes correction only.

## Codex quota constraint

Approximately **9% Codex quota remains**.

ChatGPT + GitHub are primary for this bounded orchestration/integration work.

Codex: **NO ACTIVE RELEASE** unless a genuine Windows/media multi-file runtime defect cannot be closed efficiently with connector-first work and hosted evidence.

## Immediate corridor after active work

1. complete reusable Planning + Editing product flow orchestration;
2. real Planning Product Probe + Human Gate;
3. real Editing automatic-final-MP4 Product Probe + Human Gate;
4. evidence-backed repair only;
5. Stage-A 100% only after all hard gates genuinely pass.

## Constitutional constraints

- canonical EDL remains sole exact timeline authority;
- Preview remains playback-only;
- Renderer has no editorial authority;
- Review has no edit/render mutation authority;
- Planning-only / Editing-only / Combined remain parallel legitimate entries;
- originals remain protected from overwrite;
- untrusted media/provider text cannot become executor authority;
- no structural-progress bump for orchestration abstraction alone.
