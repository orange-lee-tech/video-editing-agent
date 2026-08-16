# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 90%  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** PREVIEW LIBMPV LGPL GATE ACTIVE — production Preview implementation not yet authorized  
**Updated:** 2026-08-16

## Progress meaning

The structural percentage measures real end-to-end product construction, not file count or backend module completion.

The hard 100% contract is `STAGE_A_COMPLETION_GATE.md`.

Current Product Gate state remains:

- Planning foundation accepted; ordinary-user Planning product flow still open.
- Editing foundation accepted; ordinary-user automatic final-MP4 product flow still open.

Stage-A 100% remains forbidden until both core Product Gates are PASS.

## Accepted R0.12 structural baselines

- `ff343833deb9296c1df0b6fc944735388d5c8296` — typed EDL tracks and deterministic validation.
- `4b2522ae1a6838517baf4c5bcf36d30026f86912` — exact rational spatial/audio automation.
- `b6c5684a9b07d79f20a10d28886cd087eaeecf10` — grounded decision-to-EDL assembly.
- `83fc2999297023f828fa77719cd357fe82eab5de` — deterministic EDL-driven FFmpeg Renderer.
- `9f06386f9f311fe241f250f4679fa6b2042699b0` — living Resolver → EDLBuilder → Renderer smoke.
- `827b84941e1726bab374f2ffea9a746f49f6e570` — structured subtitle execution.
- `1abc185a793d6a73ea55824bd2a036a1a134151a` — EditPlan parallel-entry compatibility.
- `500c8563e3686a5aaef055ffb5301553aa999fd9` — real Editing Director/Application entry with SQLite v6 EditPlan persistence and generated EditPlan → existing Retrieval/CandidateWindow/Resolver integration.

Accepted production-code baseline remains `500c8563e3686a5aaef055ffb5301553aa999fd9`; current Preview work remains evidence/ADR-only.

## Parallel workflow architecture

Planning-only, Editing-only and Combined remain parallel legitimate product meanings. Brief is the shared intent root; Planning artifacts enrich Editing only when present.

## Active R0.12 Work Order

`R0.12-PREVIEW-BACKEND-BENCHMARK-001` is ACTIVE.

CAP-08 still defines PreviewBackend as interactive playback only. It has no EDL/timeline authority, does not repair EDL and does not define final-render quality.

### Accepted Preview evidence so far

- Windows Class-A environment/device capability: PASS;
- GStreamer 1.28.6 and VLC/libVLC 3.0.23 provenance/private runtimes: PASS;
- actual deterministic windowed playback for GStreamer + VLC: PASS;
- VLC Intel HD 520 D3D11VA decode proof: PASS;
- GStreamer actual `playbin3 → decodebin3 → d3d11h264dec → D3D11Memory/NV12 → d3d11videosink` hardware path: PASS;
- GstPlay + libVLC deterministic play/pause/eight-seek/resume/release control: PASS;
- three real phone HEVC files: GStreamer normal 3/3 PASS, libVLC normal 3/3 PASS;
- GStreamer explicit software decode fallback on the real HEVC corpus: 3/3 PASS;
- libVLC explicit software decode fallback: PASS using per-media `:avcodec-hw=none`; global-only `--avcodec-hw=none` is recorded as unreliable for the tested embedding path.

Durable Wave-3 evidence:

`docs/validation/R0.12_PREVIEW_WAVE3_REAL_MEDIA_SOFTWARE_FALLBACK_EVIDENCE.md`

Evidence gaps remain explicit:

- the real-phone corpus did not contain observed VFR behavior;
- Class-B ordinary-current-Windows host evidence is missing;
- Class-C newer-accelerated host evidence is missing;
- total no-GPU/no-presentation-device behavior was not simulated.

These gaps do not reopen already accepted hardware, control or real-HEVC/software-fallback evidence.

### Current sequence

1. **ACTIVE:** resolve auditable LGPL-configured libmpv Windows candidate or hard-gate exclusion;
2. compare GStreamer / libVLC / libmpv using hard gates and transparent trade-offs;
3. write and accept Preview ADR;
4. close Preview benchmark;
5. only then authorize bounded production Preview integration.

### Codex

NOT RELEASED for this benchmark. Preserve remaining quota for later production integration where local multi-file edit/test/repair creates real leverage.

## Preview STOP rule

After the Preview ADR, do not continue expanding player benchmarking merely because more tests are possible. The benchmark exists to choose a replaceable playback adapter, not to become the project.

The product priority immediately returns to the Stage-A input→black-box→output corridor after Preview closure.

## Remaining R0.12 / Stage-A corridor

After Preview closure, prioritize the bounded productization work needed for ordinary-user usefulness, including the already identified Product I/O gaps:

1. Stage-A Product I/O Contract;
2. mixed source-audio semantics + speech protection + audible QC;
3. reference URL acquisition;
4. rights-aware public music provider/acquisition;
5. remaining bounded R0.12 productization, including production Preview integration where justified;
6. minimum Review/repair loop;
7. ordinary-user Windows runtime / Environment Doctor;
8. practical product-facing integration for both real cores;
9. real Planning/Editing Product Probes + Human Gate.

Do not confuse later visual polish with structural closure. A basic interface is acceptable; a developer-only workflow is not.

## Stage-A 100% product-operability gate

Before structural construction reaches 100%:

- Planning core must run real reference/high-performing/commercial intent to persisted inspectable ScriptPlan + executable ShootingPlan through an ordinary-user path;
- Editing core must run user-selected local footage through the real automatic pipeline to canonical EDL/Renderer/Review and a real final MP4;
- Planning-only, Editing-only and Combined must all remain valid;
- normal Product Probes must not hand-author EditPlan/ResolutionDecision/EDL;
- an ordinary Windows user must be able to create/open a project, select inputs/output, provide intent, start, observe progress/failure and locate outputs without repository-file editing.

Desktop/frontend technology remains intentionally undecided until Preview/backend and later Windows packaging evidence justify a commitment.
