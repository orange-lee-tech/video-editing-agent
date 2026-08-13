# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.8 — Media Evidence Foundation  
**Active boundary:** R0.8G — Retrieval Representation Hardening  
**Date:** 2026-08-13

## Completed

- R0.7A — Architecture v0.2 Migration Foundation: CLOSED.
- R0.7B — Pre-production Planning + Commercial Skill Foundation: CLOSED.
- R0.8 Speech: CPU ASR, word/segment timestamps, VAD/silence, transcript persistence and deterministic phrase/time mapping.
- R0.8 Visual temporal evidence: camera/global motion, camera-compensated residual motion, event regions, coarse anchors, fine temporal refinement and seeded subject/product tracking Engineering baselines.
- R0.8F tracking boundary hardening: partial target exit now terminates explicitly; owner fails closed on malformed provider identity/sample/support output.

R0.8G implementation candidate:

`ed3a08dcd15d12dd7e7698f5b27fee32e2a8d8ee` — `feat: add dense retrieval representation`

The candidate establishes the intended local multilingual embedding mechanism, rebuildable dense Artifacts, exact project-local vector scan, stable tie ordering, offline Windows CPU inference and restart/restore behavior. Repository CI is green.

## Active — R0.8G Retrieval Representation Hardening

R0.8G is not yet accepted as complete because post-implementation review found remaining authority/provenance gaps:

1. `ShotIndexRepresentationDescriptor.analysis_revision` is currently overloaded with generic source revision. For `speech_text`, transcript revision therefore leaks into a field whose established meaning is ShotAnalysis revision, and dense `ShotCandidate.analysis_revision` can become semantically wrong.
2. Dense maintenance currently exposes full `rebuild()` but no explicit per-representation upsert/invalidate seam. The required behavior “changing only the relevant ShotAnalysis/transcript revision rebuilds only the affected representation” is therefore not yet proven.
3. The Windows Engineering Probe does not currently exercise source/model revision invalidation/rebuild despite the active work order requiring that gate.
4. Sentence-transformers provider provenance hard-codes `MODEL_ID=intfloat/multilingual-e5-small`; an arbitrary configured model path could therefore be reported under the wrong model identity.

These are bounded R0.8G defects. Do not restart model selection or repeat the initial environment installation.

## Efficiency rule for the hardening pass

Reuse the already validated local Windows runtime, model snapshot and repository-local caches when they are still present and healthy. Do not reinstall PyTorch / sentence-transformers or redownload the embedding model merely to rerun R0.8G. Recreate them only if the existing environment is missing or demonstrably corrupt.

The first R0.8G run paid a legitimate one-time environment/model setup cost; subsequent work should pay only incremental code/test/probe cost.

## After R0.8G

R0.8H remains the phase-level real-footage Product Probe / closure gate using talking-head, handheld product-demo, camera-pan, hand/product interaction, low-motion and noisy/blurred footage. It must measure grounded temporal usefulness and retrieval behavior before R0.8 can close.

Do not implement R0.9 Director/Resolver authority or CandidateWindow generation until R0.8H closes.

## Operational control

Codex reads, in order:

1. `docs/operations/CODEX_EXECUTION_ENTRY.md`
2. this file
3. `docs/operations/CURRENT_WORK_ORDER.md`

`CURRENT_WORK_ORDER.md` is the single active implementation boundary. Historical validation/logs are consulted only when that work order points to them.
