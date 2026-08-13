# Current Work Order

**Status:** ACTIVE

**Phase:** R0.9 Product Probe + Phase Closure

**Goal:** prove or falsify R0.9 on the existing local real-media corpus by comparing retrieval/selection baselines, then stop for a real Human Gate before phase closure.

## Entry

1. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
2. Read `docs/roadmap/CURRENT_PHASE_STATUS.md`.
3. Read this file.
4. Read Roadmap V2 R0.9 Product Probe/Exit Gate and only the R0.9A/R0.9B implementation needed for the comparison.

Do not restart model research, add a new R0.9 feature module, or begin R0.10.

## Product Probe

Reuse the gitignored `example/` real-media corpus, existing manifest, R0.8 evidence, R0.9A retrieval/window pipeline and R0.9B Resolver/optimizer. Reuse local runtimes/caches.

Run one deterministic comparison over the same EditPlan/eligible media/evidence:

1. lexical-only baseline;
2. hybrid lexical+dense retrieval baseline;
3. hybrid + grounded Resolver/sequence optimizer.

Hard eligibility and authoritative Shot/source-time rules are identical across variants. No variant may invent Shot IDs or timestamps.

Measure/report at least:

- eligible/retrieved Shot and CandidateWindow counts;
- intended-slot/candidate recall where the existing human-confirmed corpus evidence permits honest scoring;
- selected exact source ranges and trim-window differences;
- lexical vs hybrid rank changes;
- Resolver score/confidence/reasons/alternatives/evidence refs;
- sequence legality, reuse and unresolved behavior;
- deterministic rerun equality;
- CPU wall-clock for each variant.

Do not fabricate unavailable human ground truth. The current real product corpus is sufficient to test the R0.9 exit question; broader style/corpus diversity remains a documented limitation rather than a reason to create another engineering phase.

## Human-inspectable outputs

Write local-only artifacts under:

`example/probe-output/r0_9_product/`

At minimum produce:

- `lexical_only_preview.mp4`;
- `hybrid_retrieval_preview.mp4`;
- `grounded_resolver_preview.mp4`;
- `comparison.json` mapping EditSlots, candidates, source ranges, ranks, decisions and preview segments;
- a short local `HUMAN_REVIEW.md` telling the user exactly what to judge: candidate relevance/recall, trim quality/completeness and sequence preference.

These are diagnostic previews only; no EDL/final-render authority is introduced.

## Technical acceptance

The technical Product Probe is adequate only if:

- all three variants use the same legal grounded search space;
- hybrid retrieval does not regress required candidate recall relative to lexical-only on the scored fixture;
- Resolver selections are exact existing CandidateWindows;
- hard constraints dominate all scores;
- optimizer output is deterministic and legal;
- unresolved remains explicit where evidence is insufficient;
- comparison/provenance is inspectable and restart/rebuild safe;
- R0.9A and R0.9B regressions plus repository Quality Gate stay green.

If a bounded R0.9 defect appears, repair the shared mechanism, add regression coverage and rerun this same Product Probe in the same work order when practical. Do not create R0.9C/R0.9D.

## Completion boundary

If technical acceptance passes:

- commit/push all non-private code/test/probe/doc changes coherently;
- keep media/previews local and gitignored;
- classify `READY_FOR_HUMAN_ACCEPTANCE`;
- stop before marking R0.9 CLOSED and before R0.10 implementation.

If the technical probe fails materially, classify `MATERIAL R0.9 DEFECT`; if an actual external/runtime blocker exists, classify `BLOCKED`.

Final report must include HEAD, three-variant metrics/source ranges, preview directory/files, Quality Gate and major-stage wall-clock time.
