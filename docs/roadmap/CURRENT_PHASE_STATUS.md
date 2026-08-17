# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Review / runtime productization  
**Engineering state:** PRODUCT_FLOW_ENGINEERING_PROBE_ACTIVE  
**Updated:** 2026-08-17

## Progress meaning

The structural percentage measures real end-to-end product construction, not file count, backend count, benchmark completion or test count.

The hard 100% contract is `STAGE_A_COMPLETION_GATE.md`.

Current Product Gate state remains:

- Planning foundation accepted; ordinary-user Planning Product Gate still open.
- Editing foundation accepted; ordinary-user automatic-final-MP4 Product Gate still open.

Stage-A 100% remains forbidden until both core Product Gates are PASS.

## Current accepted production-code baseline

`db8db211e6c662cdfc7ad2afe385ee766ce1a240`

This baseline includes the production Windows Environment Doctor foundation, durable canonical EDL persistence, and the product-facing Planning / Editing flow surface now merged to `main`.

Exact-head deterministic CI for this baseline passed after the ProductFlow merge.

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

### Product-flow implementation surface — IMPLEMENTATION ACCEPTED

Accepted production baseline:

`db8db211e6c662cdfc7ad2afe385ee766ce1a240`

Accepted implementation now provides:

- structured `video-editing-agent run planning --request ...` and `run editing --request ...` entry surfaces;
- strict ordinary-request schema that does not expose ShotRef, CandidateWindow, ResolutionDecision, source timestamps or EDL internals;
- reusable ProjectWorkspace Planning and Editing composition;
- local ingest → Shot/understanding → Director/EditPlan → grounded Resolver → canonical EDL → Renderer → Review composition;
- conservative Resolver-grounded source-audio treatment;
- exact EDL persistence through `workspace.edls`;
- deterministic unit/composition coverage.

This is **Engineering implementation evidence**, not a Product Gate or Human Gate PASS.

## Active Work Order

`R0.12-PRODUCT-FLOW-ORCHESTRATION-001` remains ACTIVE.

The implementation portion is accepted. The remaining exit gate is bounded Engineering Probe evidence.

### Planning Engineering Probe required

```text
ordinary Planning request
→ Brief
→ persisted ScriptPlan
→ persisted ShootingPlan
→ exact persisted refs
```

The probe must enter through the product-facing request surface rather than hand-authoring Domain internals.

### Editing Engineering Probe required

```text
real valid media
→ actual ingest / understanding
→ Director / persisted EditPlan
→ grounded retrieval / Resolver
→ canonical EDL
→ persisted exact EDL revision
→ actual FFmpeg MP4
→ Review
```

The probe must not use fake media bytes or a fake Renderer for the final mechanism claim.

### EDL durability wording rule

The existing Windows SQLite Persistence Probe directly proves cross-process persistence for its current Asset / Shot / ShotAnalysis path. It must **not** be described as direct canonical-EDL cross-process proof unless the bounded probe explicitly performs:

```text
process 1: EDLRepository.save(exact revision)
→ process exit
→ process 2: load same exact EDL revision
→ equality / lineage verification
```

Unit/reopen tests remain valid implementation evidence, but are a lower evidence class than this bounded cross-process probe.

## Immediate corridor after active work

1. pass Planning Engineering Probe through the ordinary request surface;
2. pass Editing real-media Engineering Probe through actual FFmpeg Renderer / Review;
3. include bounded EDL exact-revision cross-process evidence if closure wording claims it;
4. close `R0.12-PRODUCT-FLOW-ORCHESTRATION-001` only after those Engineering gates pass;
5. run real Planning Product Probe + Human Gate;
6. run real Editing automatic-final-MP4 Product Probe + Human Gate;
7. repair only evidence-backed defects;
8. Stage-A 100% only if both ordinary-user gates and the global completion gate genuinely PASS.

## Frozen authority rules

- user request does not contain CandidateWindow, ResolutionDecision, source timestamps or EDL internals;
- lexical retrieval may be the minimum always-available production retrieval baseline; dense remains optional enhancement;
- Shot-boundary fallback is permitted only as exact grounded evidence when stronger TemporalAnchors are absent;
- unresolved slots remain explicit and fail closed;
- optional music/spatial assets are not invented;
- source audio is conservatively grounded per resolved selection;
- canonical EDL remains sole exact timeline authority;
- Renderer executes; Review classifies/routes only;
- Planning-only / Editing-only / Combined remain parallel legitimate entries;
- structural progress remains 90% until real Product Gate evidence justifies a change.
