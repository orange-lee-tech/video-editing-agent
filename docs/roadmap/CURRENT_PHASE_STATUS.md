# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.11 — Spatial Composition / Auto Reframe  
**Engineering state:** ACTIVE — tracker recovery candidate found; current Human Gate invalidated by step-held preview execution; interpolation + extended-loss semantics next  
**Updated:** 2026-08-14

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.
- R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.

## Accepted R0.11 engineering foundations

- `ef0baa455c27c0ccb42ae74c4d24ede76e543a74` — deterministic static spatial composition foundation.
- `3ea89a51354fd3df62eed82e7959201969ec8b57` — deterministic source-time track paths.
- `ad4f47e5f659e108d34593675bc08177a2c2aff4` — deterministic motion-stability baseline.
- `66fc889094dd46dd51d5ccf028869c37658f648b` — canonical spatial-plan FFmpeg execution foundation.

At `66fc889`, remote `ci/quality-gate-diagnostic` is green. The implementation diff is bounded to the FFmpeg spatial-plan executor and focused tests; it does not alter `SpatialComposer`, the seeded tracker or stabilization constants.

## Movement Human Gate — invalidated by preview execution semantics

The user watched the generated `moving_occlusion2_landscape` previews.

Reported product behavior:

- CENTER is ordinary static framing and loses the moving person for part of the clip;
- RAW visibly jumps;
- STABILIZED also visibly jumps even though playback itself is smooth.

The current FFmpeg adapter is explicitly step-held: crop coordinates change only at canonical keyframe timestamps. Therefore the preview itself injects discrete framing jumps.

Classification:

`HUMAN_GATE_INVALID — STEP_HELD_PREVIEW_EXECUTION`

Do not use this Human Gate to tune SpatialComposer constants. First add explicit canonical interpolation semantics and rerender the same comparison.

## Tracker recovery benchmark — technical candidate found

Current Sparse-LK still loses at `29/30 s` and cannot reacquire.

### YOLOX-Nano + ByteTrack

Technically insufficient for this case because the returning intended person receives a new track ID and original identity continuity is not recovered.

### MediaPipe Object Detector + deterministic Sparse-LK reseed

Technically successful on the rights-attested occlusion clip:

- deterministic across three runs;
- recovers the originally seeded person without observed identity switch;
- main real occlusion loss at 1.565 s;
- recovery at 4.428 s;
- recovery latency 2.863 s;
- lost observations contain no geometry;
- CPU processing approximately 6.25–9.18 FPS;
- peak RSS approximately 127 MB.

Current classification:

`RECOVERY_CANDIDATE_TECHNICALLY_READY_LICENSE_PENDING`

## Long-loss contract exposed by real evidence

The existing path policy allows only a 1 s lost hold and current Composer returns unresolved once the loss gap exceeds that bound.

The real successful recovery arrives after 2.863 s. Therefore recovery-provider integration alone cannot complete the Product Probe.

R0.11 now needs an explicit bounded extended-loss/reacquisition state that:

- never invents subject geometry;
- preserves legal spatial decisions during the gap;
- records recovery-wait evidence/QC;
- permits bounded later reacquisition;
- fails closed outside the explicit recovery contract.

Do not silently turn the existing 1 s short-loss hold into unlimited stale framing.

## Active implementation gate

Next bounded engineering batch:

1. make interpolation an explicit canonical spatial-plan semantic owned upstream, not by Renderer;
2. replace step-held tracked preview execution with deterministic interpolation consumed from the canonical plan;
3. integrate the smallest provider-neutral recovery path based on the technically successful MediaPipe + deterministic reseed candidate;
4. add explicit extended-loss/reacquisition semantics supported by the real 2.863 s Product Probe gap;
5. rerun Quality Gate;
6. regenerate fair movement and occlusion A/B/C previews;
7. stop for Human Gate.

Do not tune dead-zone/velocity merely to compensate for the old renderer behavior.

## Open-source licensing state

The Product Owner has stated willingness to open-source the project.

The repository currently has no root `LICENSE` file and `pyproject.toml` has no project license declaration. Open-source license selection is therefore still a separate governance decision.

This means AGPL-family providers may be reconsidered in the future, but no AGPL adoption/relicensing is authorized implicitly by the open-source intent statement.

For the current MediaPipe candidate, exact downloaded model-artifact terms remain a release gate independent of the Apache-2.0 runtime/source license.

## R0.11 completion gate

R0.11 remains open until:

1. corrected interpolation-aware movement previews pass Human Gate;
2. a recovery-capable evidence path survives the real occlusion/recovery case under explicit long-loss semantics;
3. occlusion A/B/C previews pass Human Gate;
4. dependency/model release status is recorded clearly enough for the intended distribution path.

## Future audio-provider backlog

Automatic rights-aware music discovery/acquisition remains recorded separately in:

`docs/research/AUDIO_PROVIDER_CANDIDATES_2026-08-14.md`

It does not reopen R0.10 and is not part of R0.11.
