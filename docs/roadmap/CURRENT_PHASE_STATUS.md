# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 95%  
**Current phase:** R0.12 — Stage-A final closure / workspace UX / packaging  
**Engineering state:** STAGE_A_FINAL_CLOSURE_WORKSPACE_UX_AND_PACKAGING  
**Updated:** 2026-08-22

## Progress truth

Structural percentage measures real ordinary-user end-to-end usability, not module/test/UI count.

Hard 100% contract:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Current gate state:

- Planning Product/Human Gate: PASS on the supported Stage-A surface.
- local reference video: retained supported Planning input.
- remote reference URL: deliberately hidden and deferred to 2.0 provider-neutral `ReferenceObservation`; not a 1.0 blocker.
- bounded Bilibili acquisition fallback: Engineering PASS, not exposed as ordinary 1.0 product capability.
- Editing no-speech ordinary Human baseline: PASS with real final MP4.
- source audio preservation + rights-safe BGM: HUMAN PASS on the accepted real run.
- no-speech subtitle behavior: PASS (`SKIPPED` / no fabricated captions).
- speech-bearing original voice + basic trusted subtitles: engineering seam present; approved/pinned runtime/model + real Human evidence still OPEN.
- Project Workspace / desktop UX consolidation before packaging: OPEN.
- Windows distributable proof without Python/uv/repository execution: OPEN.
- Stage-A completion gate: OPEN.

Therefore structural progress remains **95%**, not 100%.

## Accepted production-code baseline

`756a30562dd512fba9868eeee43cf6422f60f642`

This is the squash merge of PR #13 after exact-head CI passed for implementation head `e8b09444e2f8402d267c670e841e8b9720418d20`.

Durable evidence:

- `docs/validation/R0.12_EDITING_AUDIO_SUBTITLE_CLOSURE_2026-08-21.md`
- `docs/validation/R0.12_REFERENCE_COMPATIBILITY_CLOSURE_2026-08-22.md`

## What is now proven

Ordinary Editing has real evidence for:

```text
real user footage
→ media understanding
→ rights-safe public BGM
→ EditPlan / grounded Resolver
→ canonical EDL
→ SOURCE_AUDIO preservation
→ capability-aware no-speech subtitle handling
→ Renderer / Review
→ final MP4
```

The Product Owner confirmed the final no-speech MP4 was normal, source audio was present, and BGM was present/natural.

Reference compatibility exploration also proved that a provider-specific Bilibili acquisition adapter can live behind the existing acquisition seam while preserving transport/security boundaries. However, because current visual providers are image-frame oriented rather than provider-neutral remote/video-native observers, ordinary remote-reference input is intentionally hidden for 1.0 instead of forcing a heavy download/parse path into the product.

## Remaining 1.0 closure terrain

### A. Project Workspace + desktop UX consolidation

Before packaging, make the existing desktop surface structurally coherent:

- one shared top-level `Project Workspace` context for Planning and Editing;
- project-specific cache/work/autosave/undo-redo/log/output ownership under that workspace;
- sensible project-local default output destination;
- unified main-window configuration import/export/save/delete interaction;
- form-level Clear / Undo / Redo;
- vertical collapsible sections instead of unnecessary horizontal width;
- replace the temporary pixel-camera mark with the approved feather identity if the real asset is recoverable;
- keep remote reference URL hidden.

Specification:

`docs/operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`

### B. Basic speech/subtitle retained capability

Production synthetic voice/TTS is deferred, but original human speech + basic trusted subtitles remains a retained 1.0 capability.

The speech runtime/model must be deliberate, pinned, diagnosable and pass a real simple spoken-video Human Gate before final closure. Advanced source separation/noise handling is not required for 1.0.

### C. Compatible Windows packaging

Packaging must progress from Python wheel/sdist to a real Windows distributable engineering proof:

- ordinary target does not need Python, uv or repository checkout;
- thin bootstrap/resource/runtime location outside Domain authority;
- user-writable data outside install directory;
- providers/models/renderers remain replaceable;
- current 1.0 runtime dependencies are closed deliberately rather than accidentally copied from a developer machine;
- fresh/clean Windows smoke proves launch and retained core-path diagnostics.

The current repository-local `.tools` FFmpeg locator is a development fallback, not the final packaging resource-location architecture.

### D. Final closure

After A-C:

- run retained ordinary Planning/local-reference evidence;
- rerun Editing no-speech baseline;
- run clear single-speaker original-voice + basic subtitle Human Gate;
- verify packaged launcher/diagnostics without repo/Python/uv;
- verify required full quality/governance gates and exact-head CI;
- synchronize live control documents;
- set Stage-A 100% only if every machine/human completion invariant actually passes.

## 2.0 deferred reference direction

Remote URLs may return only when a provider-neutral observation capability exists, e.g.:

```text
Reference URL
→ provider-neutral ReferenceObservation capability
→ remote/video-native observation when supported
→ provider upload-media observation when required
→ controlled image-only fallback when appropriate
→ structured reference observations
→ Planning/Director
```

Bilibili/Douyin/Xiaohongshu site mechanics must remain adapter concerns and must not own Planning Domain.

## Active Work Order

`R0.12-STAGE-A-FINAL-CLOSURE-002`

The next implementation wave must stay bounded to the current closure terrain and obey root `AGENTS.md` plus `docs/operations/DOCUMENT_CONTROL_POLICY.md`.
