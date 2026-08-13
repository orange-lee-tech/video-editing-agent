# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.8 — Media Evidence Foundation  
**Active boundary:** R0.8G — Retrieval Representation  
**Date:** 2026-08-13

## Completed

- R0.7A — Architecture v0.2 Migration Foundation: CLOSED.
- R0.7B — Pre-production Planning + Commercial Skill Foundation: CLOSED.
- R0.8 Speech: CPU ASR, word/segment timestamps, VAD/silence, transcript persistence and deterministic phrase/time mapping.
- R0.8 Visual temporal evidence: camera/global motion, camera-compensated residual motion, event regions, coarse anchors, fine temporal refinement and seeded subject/product tracking Engineering baselines.

R0.8F implementation baseline:

`1b5ac063d6be44929a159b7457a802077f0bf64f` — `feat: add seeded subject tracking evidence`

Its controlled Windows probe passed moving-target, pan+local, occlusion, target-exit, distractor, deterministic and persistence/reopen gates. Real-footage robustness remains deliberately unclaimed until the R0.8 Product Probe.

## Active — R0.8G Retrieval Representation

Finish the remaining engineering representation layer required by R0.8:

- derived visual-semantic and speech-text embedding representations;
- local multilingual embedding provider baseline;
- explicit model/revision/dimension/normalization and source-revision provenance;
- deterministic project-local exact vector scan;
- rebuild/invalidation when representation inputs or embedding model change;
- preserve `ShotAnalysis` identity and semantic authority.

Use the existing `ShotIndexRepresentationDescriptor`, ShotIndex ownership, lexical index and artifact-lifecycle seams. Embeddings are rebuildable retrieval state, never Domain semantic truth.

Do not implement R0.9 Director/Resolver authority or CandidateWindow generation in this phase.

## After R0.8G

R0.8H is the phase-level real-footage Product Probe / closure gate using talking-head, handheld product-demo, camera-pan, hand/product interaction, low-motion and noisy/blurred footage. It must measure grounded temporal usefulness and retrieval behavior before R0.8 can close.

## Operational control

Codex reads, in order:

1. `docs/operations/CODEX_EXECUTION_ENTRY.md`
2. this file
3. `docs/operations/CURRENT_WORK_ORDER.md`

`CURRENT_WORK_ORDER.md` is the single active implementation boundary. Historical validation/logs are consulted only when that work order points to them.
