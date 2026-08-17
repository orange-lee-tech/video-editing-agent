# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Review / runtime productization  
**Engineering state:** PRODUCT_FLOW_ORCHESTRATION_ACTIVE  
**Updated:** 2026-08-17

## Progress meaning

The structural percentage measures real end-to-end product construction, not file count, backend count, benchmark completion or test count.

The hard 100% contract is `STAGE_A_COMPLETION_GATE.md`.

Current Product Gate state remains:

- Planning foundation accepted; ordinary-user Planning Product Gate still open.
- Editing foundation accepted; ordinary-user automatic-final-MP4 Product Gate still open.

Stage-A 100% remains forbidden until both core Product Gates are PASS.

## Current accepted production-code baseline

`914dd7dcc72595d418d7d3bf0cb05e356dd021b9`

This baseline includes the production Windows Environment Doctor foundation in addition to all earlier accepted R0.12 product corridors.

## Closed R0.12 productization boundaries

### Preview — PASS/CLOSED

- primary Stage-A backend: GStreamer;
- accepted production baseline `4ca3b83bfac50923bdcf15f1ad08d90b397daa23`;
- final bounded Windows production-adapter run `32030024748` — PASS;
- Preview remains playback-only and backend benchmarking remains closed.

### Product I/O Contract — PASS/CLOSED

`docs/product/STAGE_A_PRODUCT_IO_CONTRACT.md`

### Mixed source-audio / VoiceTreatment / audible QC — PASS/CLOSED

`docs/validation/R0.12_MIXED_SOURCE_AUDIO_QC_CLOSURE.md`

### Reference URL acquisition — PASS/CLOSED

- `docs/validation/R0.12_REFERENCE_URL_ACQUISITION_CLOSURE.md`
- accepted baseline `d15abf9258c0a080e37d666cd1112358723e823a`

### Rights-aware public music acquisition — PASS/CLOSED

- `docs/validation/R0.12_PUBLIC_MUSIC_ACQUISITION_EVIDENCE.md`
- accepted baseline `72ec275c1e72e876c4bcf828a44e7852208bab29`
- Windows provider run `32026331114` — PASS.

### Minimum post-render Review / bounded repair — PASS/CLOSED

- `docs/validation/R0.12_MINIMUM_REVIEW_REPAIR_CLOSURE.md`
- accepted production baseline `2cfeb664552769ade09f58bc2905ab531733a66a`
- final Windows real-media Review run `32033179672` — PASS.

Review classifies evidence and routes correction; it does not mutate EDL/editorial/render state.

### Windows Environment Doctor — PASS/CLOSED

- Work Order `R0.12-WINDOWS-ENVIRONMENT-DOCTOR-001`;
- closure `docs/validation/R0.12_WINDOWS_ENVIRONMENT_DOCTOR_CLOSURE.md`;
- accepted production baseline `914dd7dcc72595d418d7d3bf0cb05e356dd021b9`;
- deterministic Quality Gate `32034737393` — PASS;
- final Windows production Doctor run `32035192895` — PASS.

Accepted semantics:

- product-independent `video-editing-agent doctor` exists;
- Windows/Python and FFmpeg/ffprobe readiness are typed machine facts;
- Preview missing/private-runtime configuration is represented without backend switching;
- DeepSeek/Gemini/OpenAI credential presence is reported without exposing values;
- repair report is sanitized;
- Doctor creates no project/creative state;
- final installer technology remains unfrozen.

## Active Work Order

`R0.12-PRODUCT-FLOW-ORCHESTRATION-001` is ACTIVE.

### Audit-grounded starting point

The accepted owners exist, but ordinary product launch remains fragmented:

- `ProjectWorkspace.runtime()` composes Planning and low-level media operations;
- `ProjectWorkspace.editing_runtime()` composes Director → persisted EditPlan only;
- no application owner currently carries Editing through retrieval/Resolver → EDLBuilder → Renderer → Review;
- the R0.12 living integration smoke manually creates the downstream decisions;
- R0.9 already proved retrieval → temporal evidence → canonical CandidateWindows → grounded Resolver on real media, but that composition remains trapped in Probe code.

### Product route to close

```text
ordinary Planning request
→ existing Brief/Script/Shooting owners
→ exact persisted refs + progress/result

ordinary Editing request
→ local file ingest/understanding
→ Director/EditPlan
→ retrieval → grounded CandidateWindows → Resolver
→ approved audio/spatial/optional decisions
→ canonical EDL
→ Renderer
→ Review
→ final MP4 or typed correction route
```

### Frozen authority rules

- user request does not contain CandidateWindow, ResolutionDecision, source timestamps or EDL internals;
- lexical retrieval may be the minimum always-available production retrieval baseline; dense remains optional enhancement;
- Shot-boundary fallback is permitted only as exact grounded evidence when stronger TemporalAnchors are absent;
- unresolved slots remain explicit and fail closed;
- optional music/spatial assets are not invented;
- source audio is conservatively grounded per resolved selection;
- canonical EDL remains sole exact timeline authority;
- Renderer executes; Review classifies/routes only.

### Required product projections

Expose understandable progress from project/input through planning/editing, resolve, EDL, render, Review and terminal success/failure.

These are application projections, not new top-level Domain entities.

## Immediate corridor after active work

1. complete product-flow orchestration/integration;
2. run real Planning Product Probe + Human Gate;
3. run real Editing automatic-final-MP4 Product Probe + Human Gate;
4. repair only evidence-backed defects;
5. Stage-A 100% only if both ordinary-user gates and the global completion gate genuinely PASS.
