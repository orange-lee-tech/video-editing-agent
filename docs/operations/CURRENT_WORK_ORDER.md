# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.8G — Retrieval Representation Hardening  
**Goal:** close the bounded provenance/invalidation defects found in post-implementation review of `ed3a08d`, rerun the existing Windows Engineering Probe, and stop at the true R0.8G boundary.

## Entry

1. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
2. Read `docs/roadmap/CURRENT_PHASE_STATUS.md`.
3. Read this file.
4. Inspect only the current dense retrieval implementation/tests/probe plus the existing ShotIndex representation ownership contract as needed.

Do not restart model research and do not reread unrelated historical material.

## Efficiency constraint

The prior R0.8G run already paid the first-time environment/model setup cost.

- Reuse the existing isolated Windows sentence-transformers/PyTorch runtime, local `intfloat/multilingual-e5-small` snapshot and repository-local uv/cache state if present and healthy.
- Do not reinstall PyTorch / sentence-transformers or redownload the model merely to rerun tests/probes.
- Recreate runtime/model files only if missing or demonstrably corrupt, and report that as exceptional setup cost.
- Keep sentence-transformers optional; do not add it or PyTorch to production dependencies.

## Defect 1 — preserve analysis revision semantics

`ShotIndexRepresentationDescriptor.analysis_revision` and `ShotCandidate.analysis_revision` must continue to mean ShotAnalysis revision. Do not overload them with speech transcript revision.

Represent dense source provenance with separate facts sufficient to bind:

- exact Shot revision;
- current ShotAnalysis revision used by retrieval candidate ownership;
- representation kind;
- representation source kind (`shot_analysis` / `speech_transcript` or equivalent provider-neutral identity);
- representation source revision;
- model id;
- model revision;
- dimension;
- normalization.

For `visual_semantic_text`, analysis revision and representation-source revision may be equal because ShotAnalysis is the source.

For `speech_text`, candidate `analysis_revision` must remain the current ShotAnalysis revision while transcript revision is recorded separately as the speech representation source revision.

If the dense Artifact schema must change, write a new schema version and either retain safe backward read of `r0.8g-dense-v1` or fail explicitly with a documented reason; do not silently reinterpret old speech provenance.

## Defect 2 — selective maintenance / invalidation

Add a narrow rebuildable maintenance seam so a single exact `(shot_ref, representation)` can be refreshed or invalidated without rebuilding unrelated representations.

Required behavior:

- changing only one ShotAnalysis revision rebuilds only that Shot's affected visual representation;
- changing only one speech transcript revision rebuilds only that Shot's `speech_text` representation;
- unrelated representation records/artifact identities remain unchanged;
- model id/revision change invalidates stale query/document compatibility and requires/rebuilds the applicable dense representation set;
- missing source text can remove/invalidate the affected representation cleanly;
- duplicate exact `(shot_ref, representation)` input fails closed before silently overwriting another record.

This remains rebuildable retrieval infrastructure, not Domain truth.

## Defect 3 — trustworthy provider identity

The sentence-transformers adapter must not report a hard-coded E5 model id independent of configured model identity.

Make model id explicit in provider configuration (or use an equally trustworthy mechanism) and validate non-empty model id/revision plus positive dimension. The probe candidate remains:

- runtime `sentence-transformers==5.6.0`;
- model `intfloat/multilingual-e5-small`;
- resolved model revision `614241f622f53c4eeff9890bdc4f31cfecc418b3` unless the existing local snapshot proves a different exact revision.

The adapter must continue using query/document intent correctly and local/offline inference for the Engineering Probe.

## Regression gates

Add deterministic tests proving at least:

1. visual representation candidate carries the correct ShotAnalysis revision;
2. speech representation candidate carries the correct ShotAnalysis revision while separately preserving transcript revision;
3. refreshing speech revision changes only speech representation identity/provenance;
4. refreshing visual analysis revision changes only the affected visual representation;
5. stale model id/revision fails closed at search;
6. configured model identity is what provider output reports;
7. duplicate representation identity fails closed;
8. restore/reopen preserves all revised provenance;
9. lexical/CJK index behavior remains unchanged;
10. R0.8F hardening regressions remain green.

## Windows Engineering Probe

Extend `tools/probes/r0_8g_retrieval_representation_live.py`; do not create another competing probe.

It must independently report PASS/FAIL for:

- English query → relevant Chinese document;
- Chinese query → relevant English document;
- deterministic exact-scan/tie ordering;
- visual analysis provenance;
- speech transcript provenance without corrupting candidate analysis revision;
- selective visual-source refresh;
- selective speech-source refresh;
- model-provenance mismatch rejection;
- restart/restore equality;
- offline inference.

Also report corpus size, indexing time and query latency. Report process memory if it is easy/reliable in the existing environment; absence of memory telemetry alone is not a blocker.

Do not count dependency/model installation time as inference latency. If no reinstall/redownload was needed, say so explicitly in the final report.

## Completion

Run the complete repository Quality Gate and the updated Windows Engineering Probe.

If all gates pass:

- make one coherent code commit on `main` and push;
- report starting/ending HEAD, files changed, named gates, actual repair, Quality Gate, probe timing and whether any environment/model setup was repeated;
- report coarse wall-clock time by stage when observable (`code/repair`, focused tests, live probe, full Quality Gate, environment/model setup) so future unit-time efficiency can be compared;
- classify only `ENGINEERING BASELINE ADEQUATE`, `MATERIAL DEFECT`, or `BLOCKED`;
- stop at R0.8G. Do not start R0.8H or R0.9.
