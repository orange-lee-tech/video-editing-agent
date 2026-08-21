# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 95%  
**Current phase:** R0.12 — Stage-A final closure / compatibility / packaging  
**Engineering state:** STAGE_A_FINAL_CLOSURE_REFERENCE_COMPATIBILITY_AND_PACKAGING  
**Updated:** 2026-08-21

## Progress truth

Structural percentage measures real ordinary-user end-to-end usability, not module/test/UI count.

Hard 100% contract:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Current gate state:

- Planning Product/Human Gate: PASS.
- Editing no-speech ordinary Human baseline: PASS with real final MP4.
- source audio preservation + rights-safe BGM: HUMAN PASS on the accepted real run.
- no-speech subtitle behavior: PASS (`SKIPPED` / no fabricated captions).
- speech-bearing original-voice + basic trusted subtitles: engineering seam present; approved/pinned runtime/model + real Human evidence still OPEN.
- ordinary Bilibili reference-page compatibility: OPEN bounded adapter gap.
- Windows distributable proof without Python/uv/repository execution: OPEN.
- Stage-A completion gate: OPEN.

Therefore structural progress is **95%**, not 100%.

## Accepted production-code baseline

`6ba297bf28f36aa7e56da9babb5f27d941965913`

This is the main merge of PR #11 after exact-head CI passed for implementation head `836b5401a428f57e89efbc65e9cf1534450cff05`.

Durable Editing evidence:

`docs/validation/R0.12_EDITING_AUDIO_SUBTITLE_CLOSURE_2026-08-21.md`

## What is now proven

The ordinary Editing path has real evidence for:

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

The accepted implementation also retains typed provider-neutral seams for future speech synthesis and audio separation without pretending those deferred backends are already available.

## Remaining 1.0 closure terrain

### A. Planning reference compatibility

A real ordinary Bilibili page URL was rejected because static bounded webpage discovery did not expose a direct HTTPS video source.

This is an adapter compatibility gap, not authorization for unbounded site crawling.

Target direction:

```text
ReferenceAcquisitionPort
├─ direct HTTPS media adapter
├─ bounded generic webpage media adapter
└─ bounded provider-specific adapter(s), beginning with a Bilibili proof
```

Planning Domain must remain independent of provider/site mechanics.

### B. Basic speech/subtitle retained capability

Production synthetic voice/TTS is deferred, but original human speech + basic trusted subtitles remains a retained 1.0 capability.

The speech runtime/model must become a deliberate, pinned, diagnosable runtime capability and pass a real simple spoken-video Human Gate before final closure. Advanced source separation/noise handling is not required for 1.0.

### C. Compatible Windows packaging

Packaging must progress from Python wheel/sdist to a real Windows distributable engineering proof:

- ordinary target does not need Python, uv or repository checkout;
- thin bootstrap/resource/runtime location outside Domain authority;
- user-writable data outside install directory;
- providers/models/renderers remain replaceable;
- current 1.0 runtime dependencies are closed deliberately rather than accidentally copied from a developer machine;
- fresh/clean Windows smoke proves launch and retained core path diagnostics.

### D. Final closure

After A-C:

- run retained ordinary Product/Human evidence;
- verify required full quality gates;
- verify exact-head CI;
- synchronize live control documents;
- set Stage-A 100% only if every machine/human completion invariant actually passes.

## Active Work Order

`R0.12-STAGE-A-FINAL-CLOSURE-002`

The next implementation wave must stay bounded to the current closure terrain and obey root `AGENTS.md` plus `docs/operations/DOCUMENT_CONTROL_POLICY.md`.
