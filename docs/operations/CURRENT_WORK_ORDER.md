# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.8G — Retrieval Representation  
**Goal:** complete R0.8 engineering retrieval representation in one coherent batch, then stop before the real-footage closure gate.

## Read

- `docs/operations/CODEX_EXECUTION_ENTRY.md`
- `docs/roadmap/CURRENT_PHASE_STATUS.md`
- `docs/adr/ADR-003_LOCAL_HYBRID_RETRIEVAL_BASELINE.md`
- `docs/capabilities/CAP-04_RETRIEVAL_DIRECTOR_RESOLVER.md` sections 5–9
- `docs/validation/R0.7A_4_DERIVED_EVIDENCE_INDEX.md`
- existing `application/ports/shot_index.py`, `application/use_cases/shot_index.py`, `media/indexing/lexical.py` and their tests

Do not reread unrelated historical documents.

## Preflight hardening from R0.8F review

Before retrieval work, fix these deterministic tracking boundary gaps and continue in the same batch:

1. a well-supported tracked box that becomes even partially out of frame must terminate explicitly as `target_exit` rather than emit invalid normalized geometry and rely on owner rejection;
2. the tracking owner must fail closed on malformed provider output: non-empty provider identity, positive FPS/frame dimensions, non-empty samples beginning at relative time zero, supported status/reason semantics, non-negative integer support count and finite support ratio in `[0,1]`.

Add regressions. Do not rerun model-selection work or create a separate tracking phase.

## R0.8G implementation boundary

Reuse existing ShotIndex ownership. Never restore `embedding_ref` to `ShotAnalysis`.

Implement:

- provider-neutral local text-embedding Port with distinct query/document intent;
- deterministic retrieval-text projection for at least `visual_semantic_text` from current ShotAnalysis and `speech_text` from persisted transcript evidence where available;
- explicit provenance binding exact Shot revision, source analysis/transcript revisions, representation kind, model id/revision, dimension and normalization;
- rebuildable representation storage using existing artifact/lifecycle/index seams; cache state must remain replaceable and must not become Domain truth;
- deterministic project-local exact vector scan with L2-normalized embeddings and stable tie ordering;
- query embedding and dense candidate results that remain retrieval candidates only.

Engineering candidate for the Windows CPU probe:

- `sentence-transformers==5.6.0`
- `intfloat/multilingual-e5-small`
- pin and report the exact resolved model revision.

Keep this runtime isolated/optional initially; do not add it to production dependencies merely to run the Engineering Probe. If this candidate is materially unusable on the target Windows CPU, diagnose the mechanism and choose one comparably lightweight multilingual replacement rather than stopping for model-shopping.

## Required behavior

- exact source/provenance identity survives restart/rebuild;
- changing model id/revision rebuilds dense representation without changing ShotAnalysis identity;
- changing relevant ShotAnalysis or speech transcript revision invalidates/rebuilds only the affected representation;
- unknown dimension/model/normalization mismatch fails closed;
- optional embedding runtime absence is clean;
- no vector DB, ANN server, RRF production fusion, Director, Resolver or CandidateWindow work in this batch;
- lexical/CJK behavior must remain unchanged.

## Engineering Probe

Create a reusable local Windows CPU probe under `tools/probes/`.

It must independently report:

- English query → relevant Chinese document sanity;
- Chinese query → relevant English document sanity;
- dense exact-scan deterministic ranking/tie behavior;
- visual-semantic and speech-text representation provenance;
- model/source-revision rebuild behavior with unchanged ShotAnalysis identity where appropriate;
- restart/reopen or deterministic rebuild evidence;
- indexing time, query latency and corpus size; include memory if practical;
- no network after model availability is established for the actual inference/retrieval path.

Use a controlled project-local corpus sufficient to discriminate semantic retrieval from exact lexical matching. This is an Engineering Probe, not a product-quality claim.

No paid Product Probe.

## Verification / completion

Run the complete Quality Gate from `CODEX_EXECUTION_ENTRY.md` plus the Windows live Engineering Probe.

If all required gates pass, make one coherent commit on `main` and push. Routine reversible implementation choices are yours; continue to the full work-order boundary without stopping for naming, file placement or basic refactors.

Stop only at the R0.8G completion boundary. Do not start R0.8H real-footage Product Probe or R0.9.
