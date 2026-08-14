# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.12 — activation / control-plane hardening before product implementation  
**Engineering state:** ACTIVE — `CONTROL-PLANE-001`  
**Updated:** 2026-08-14

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.
- R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.
- R0.11 — Spatial Composition / Auto Reframe.

## R0.11 closure

Accepted implementation baseline:

`d06592560dbeb764666592effa00f7d5537715ef` — `fix: make spatial QC interpolation-aware`

Remote `ci/quality-gate-diagnostic` for the accepted code baseline: success.

Final technical evidence:

- movement RAW containment `40/40`, 41 keyframes, max path velocity 240 px/s;
- movement STABILIZED containment `40/40`, 14 keyframes, max path velocity 195 px/s;
- occlusion RAW containment `96/96`, 99 keyframes, max path velocity 600 px/s;
- occlusion STABILIZED containment `96/96`, 14 keyframes, max path velocity 450 px/s;
- recovery `47/30 → 133/30`, latency about 2.8667 s;
- recovered identity remained the intended seeded subject;
- canonical `SpatialTransformPlan.evaluate_crop()` is shared by QC and Renderer semantics;
- no fabricated lost geometry;
- source/aspect validation green.

Final Human Gate:

- movement: `stabilized` preferred; natural; subject normal;
- occlusion/recovery: `stabilized` preferred; minor visible micro-jump;
- classification: `PASS_WITH_MINOR_DEFECT`.

The recovery micro-jump is a recorded known limitation, not a reason to keep retuning R0.11 without broader Product Probe evidence.

Release/distribution note:

- MediaPipe recovery runtime remains optional;
- EfficientDet Lite0 model remains external and SHA-pinned;
- model redistribution/commercial artifact terms remain `RELEASE_LICENSE_PENDING`;
- local/product engineering acceptance is closed;
- any future bundled distribution path must resolve or fail closed on this license gate.

Canonical closure record:

`docs/validation/R0.11_FINAL_CLOSURE.md`

## Current gate before R0.12 product work

The project control plane has accumulated duplicated state/explanation across ChatGPT prompts and repository docs.

Before EDL/Renderer/Subtitle/Preview/Proxy productization begins, execute `CONTROL-PLANE-001`:

- establish one compact `CURRENT_CONTROL_STATE.md` routing manifest;
- keep `CURRENT_WORK_ORDER.md` delta-only;
- add deterministic foreman/preflight briefing generation;
- keep durable rules in Product/Architecture/CAP/ADR docs instead of copying them into each Codex prompt;
- preserve ChatGPT as remote GitHub/CI control plane and Codex as local complex-batch writer.

R0.12 product implementation has **not** begun yet.
