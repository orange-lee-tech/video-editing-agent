# Current Work Order

**Status:** READY_FOR_HUMAN_ACCEPTANCE

**Phase:** R0.9 Product Probe evidence hardening + Phase Closure

**Goal:** repair the Product Probe evidence chain so the R0.9 Human Gate is based on actual end-to-end retrieval/window/resolution behavior over the local real-media corpus, not probe-preselected answers.

**Technical result:** PASS on 2026-08-13. The hardened Probe executes the real lexical/E5
indexes, persisted OpenCV evidence/event reduction, canonical CandidateWindow generation and
grounded Resolver. Local review artifacts are under `example/probe-output/r0_9_product/`.
R0.9 remains open pending a real human verdict.

## Entry

1. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
2. Read `docs/roadmap/CURRENT_PHASE_STATUS.md`.
3. Read this file.
4. Inspect only the current R0.8 evidence/retrieval persistence plus R0.9A/R0.9B pipeline/probes needed for this rerun.

Do not add a new R0.9 feature module and do not begin R0.10.

## Mandatory repair

Replace the current product comparison's preconstructed decision inputs with the real implementation path.

The Product Probe may fix:

- EditPlan/EditSlot intent;
- separate human-known expected semantic/event labels or coarse scoring windows;
- deterministic strategy/configuration.

It must **not** feed the answer into the system by hardcoding:

- winning `ShotCandidate` identities/ranks;
- final `CandidateWindow` identities;
- selected source ranges used as pipeline input.

Candidates/ranks must come from the actual lexical and dense retrieval/index path over local project data. CandidateWindows must come from actual persisted/generated R0.8 speech/temporal evidence and anchors through the canonical R0.9 CandidateWindow generator. Resolver/optimizer must consume only those generated windows.

Use the existing gitignored `example/` corpus and existing local runtimes/caches. Reuse persisted evidence when trustworthy; regenerate through existing owners when needed. Do not fabricate ShotAnalysis or temporal evidence merely to force the expected result. Human-confirmed corpus coverage may be used as scoring ground truth, not as source-selection authority.

## Comparison

Run the same three variants over the same legal real-media search space:

1. lexical-only;
2. hybrid lexical+dense;
3. hybrid + grounded Resolver/optimizer.

Report actual retrieved Shot IDs/ranks, actual generated CandidateWindows, selected exact source ranges, recall where honestly scoreable, unresolved behavior, provenance and deterministic rerun equality.

Do not require hybrid to beat lexical by construction. Report an honest tie/regression/improvement from the real corpus.

## Local review artifacts

Replace/regenerate the local-only artifacts under:

`example/probe-output/r0_9_product/`

including:

- `lexical_only_preview.mp4`;
- `hybrid_retrieval_preview.mp4`;
- `grounded_resolver_preview.mp4`;
- `comparison.json`;
- `HUMAN_REVIEW.md`.

The previews must be rendered only from source ranges produced by the repaired real pipeline.

## Acceptance

Technical acceptance requires:

- no preselected candidate/window/source-range answers in probe inputs;
- real lexical+dense retrieval execution;
- real evidence/anchor → CandidateWindow execution;
- Resolver selections are exact generated CandidateWindows;
- hard constraints dominate;
- explicit unresolved where unsupported;
- deterministic repeat/provenance;
- R0.9A/R0.9B regressions and full Quality Gate green.

If a bounded mechanism defect is exposed, repair it with regression coverage and rerun this same Product Probe in this work order.

If technical acceptance passes, commit/push non-private changes and classify `READY_FOR_HUMAN_ACCEPTANCE`; stop before R0.9 closure/R0.10. If the real local corpus genuinely cannot supply an honest scored path, classify the smallest concrete evidence/corpus gap rather than substituting scripted answers.

Final report: HEAD, actual pipeline stages exercised, real retrieved IDs/ranks, real CandidateWindows/source ranges, three preview files, named gates, Quality Gate and major-stage wall-clock.
