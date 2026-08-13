# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.8 — Media Evidence Foundation  
**Active boundary:** R0.8H — Real-Footage Product Probe + Phase Closure  
**Date:** 2026-08-13

## Completed engineering baselines

- R0.7A — Architecture v0.2 Migration Foundation: CLOSED.
- R0.7B — Pre-production Planning + Commercial Skill Foundation: CLOSED.
- R0.8 Speech: CPU ASR, timestamps, VAD/silence, transcript persistence, phrase/time mapping.
- R0.8 Visual temporal evidence: camera/global motion, compensated residual motion, event regions, coarse/fine anchors, seeded tracking.
- R0.8 Retrieval representation: multilingual local embedding prototype, explicit provenance, rebuildable dense Artifacts, selective refresh/invalidation and deterministic project-local exact vector scan.
- R0.8H local media corpus manifest: anonymous, stable metadata/hash tracking for the gitignored `example/` corpus.

R0.8G accepted implementation baseline:

`ae67be32c3f8726399fecfc20173a7effa06ef34` — `fix: harden dense retrieval provenance`

R0.8H corpus tooling baseline:

`b1f45a98619d192afbdfaa7fbac7d8189e05b305` — `test: track anonymized local media corpus`

The existing real captured `example/` corpus covers handheld product demo, camera motion/pan, hand-object interaction, low motion and weak/noisy/blurred footage. Its original audio contains no useful scored speech.

## Active — R0.8H Closure Sprint

No new R0.8 feature module is planned.

The closure requirement is to prove that the already-built speech, temporal, tracking and retrieval evidence mechanisms produce useful grounded candidate-time evidence on the local real-media corpus.

### Speech fixture policy

Do not require the user to speak or to perform a physical acoustic re-recording merely to satisfy the closure gate.

For the remaining speech-path Product Probe, Codex may create a **local-only derived speech fixture** from one of the existing real captured `example/` videos by:

- synthesizing a deterministic short TTS script locally;
- inserting an explicit known pause suitable for VAD/cut scoring;
- mixing the TTS with the clip's original captured ambient audio when practical;
- muxing the result onto the real captured video without changing the authoritative source-time semantics used by the probe;
- keeping the generated media gitignored/local-only.

Prefer built-in/local Windows speech synthesis and existing FFmpeg tooling; do not introduce a paid/network TTS dependency for this closure task.

This fixture is valid for R0.8 speech timestamp/VAD/phrase/cut integration because the speech content and pause ground truth are deterministic while the carrier video and ambient recording remain real captured media.

Do **not** overclaim the result: natural spontaneous human speech, real microphone speech acoustics and talking-head visual behavior remain an explicit Product Probe limitation. Those limitations do not block R0.8 closure if the speech evidence mechanism, real visual temporal evidence, tracking, retrieval and restart/provenance gates all pass.

## Closure rule

Treat R0.8H as one closure sprint, not a chain of new subphases.

If a bounded defect appears in an already-owned R0.8 mechanism, repair it, add regression coverage and rerun the same Product Probe in this work order.

If all R0.8H acceptance gates pass:

1. write `docs/validation/R0.8_FINAL_CLOSURE.md` with anonymized evidence/metrics and explicit limitations;
2. mark R0.8 CLOSED;
3. set the roadmap active phase to R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer;
4. stop before R0.9 implementation.

Do not commit local media, generated TTS media, absolute local paths, raw private transcripts or identifying content.

## Operational control

Codex reads, in order:

1. `docs/operations/CODEX_EXECUTION_ENTRY.md`
2. this file
3. `docs/operations/CURRENT_WORK_ORDER.md`

`CURRENT_WORK_ORDER.md` is the single active implementation/probe boundary.
