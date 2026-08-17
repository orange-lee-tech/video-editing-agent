# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-17
current_phase: R0.12
phase_state: PRODUCT_FLOW_ENGINEERING_PROBE_ACTIVE
active_work_order: R0.12-PRODUCT-FLOW-ORCHESTRATION-001
accepted_code_baseline: db8db211e6c662cdfc7ad2afe385ee766ce1a240
control_plane_baseline: 00228b928ff0a6e4ebbf31bb06679a38beee629c
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

`db8db211e6c662cdfc7ad2afe385ee766ce1a240`

This baseline contains the product-facing Planning / Editing request surface and reusable orchestration composition in addition to the earlier accepted R0.12 foundations.

## Stage-A completion truth

Structural progress remains **90%**.

- Stage-A completion gate: OPEN.
- Planning Product Gate: foundation accepted, ordinary-user flow open.
- Editing Product Gate: foundation accepted, ordinary-user automatic final-MP4 flow open.

100% remains forbidden until both Product Gates and the overall Stage-A gate are PASS.

Engineering Probe completion by itself does not authorize a structural-progress bump.

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

### Product-flow implementation — IMPLEMENTATION ACCEPTED

Accepted baseline:

`db8db211e6c662cdfc7ad2afe385ee766ce1a240`

Accepted facts:

- ordinary structured Planning and Editing request surfaces exist;
- request parsing rejects internal source-time/Resolver/EDL authority fields;
- Planning composes the accepted Brief/Script/Shooting owners;
- Editing composes local ingest/understanding → Director/EditPlan → grounded Resolver → canonical EDL → Renderer → Review;
- canonical EDL is persisted through the project workspace before render acceptance;
- source-audio treatment preserves Resolver-owned source ranges;
- deterministic repository gates and architecture contracts passed on the merged baseline.

This is not yet Work Order closure evidence and is not a Product Gate/Human Gate PASS.

## Current active boundary — Engineering Probe closure

`R0.12-PRODUCT-FLOW-ORCHESTRATION-001` remains ACTIVE.

The remaining engineering work is intentionally narrow.

### Planning Engineering Probe

```text
ordinary Planning request
→ Brief
→ persisted ScriptPlan
→ persisted ShootingPlan
→ exact persisted refs
```

### Editing Engineering Probe

```text
ordinary Editing request
→ real valid media
→ actual ingest / understanding
→ Director / EditPlan
→ grounded retrieval / Resolver
→ canonical EDL
→ persisted exact EDL
→ actual FFmpeg MP4
→ Review
```

Fake media bytes or a fake Renderer remain unit/composition evidence only and cannot satisfy this mechanism probe.

### EDL durability evidence wording

The existing Windows SQLite Persistence Probe directly proves separate-process persistence only for the entities it actually seeds/resumes.

Do not claim direct canonical EDL cross-process durability unless bounded evidence explicitly performs:

```text
process 1: save exact EDL revision
→ exit
→ process 2: load the same exact EDL revision
→ verify exact payload / lineage
```

No persistence redesign is required merely to add this evidence.

## Codex quota constraint

Approximately **9% Codex quota remains**.

ChatGPT + GitHub remain primary for remote state, workflow evidence, small deterministic probe/workflow changes and governance.

Codex: **NO ACTIVE RELEASE** by default. Release only for a genuine Windows/media multi-file runtime defect that materially benefits from local iterative execution.

## Immediate corridor after active work

1. Planning product-flow Engineering Probe;
2. Editing real-media / real-FFmpeg Engineering Probe;
3. bounded EDL second-process proof only if closure claims cross-process EDL durability;
4. close `R0.12-PRODUCT-FLOW-ORCHESTRATION-001` after Engineering evidence passes;
5. real Planning Product Probe + Human Gate;
6. real Editing automatic-final-MP4 Product Probe + Human Gate;
7. evidence-backed repair only;
8. Stage-A 100% only after all hard gates genuinely pass.

## Constitutional constraints

- canonical EDL remains sole exact timeline authority;
- Preview remains playback-only;
- Renderer has no editorial authority;
- Review has no edit/render mutation authority;
- Planning-only / Editing-only / Combined remain parallel legitimate entries;
- originals remain protected from overwrite;
- untrusted media/provider text cannot become executor authority;
- no structural-progress bump for Engineering Probe completion alone.
