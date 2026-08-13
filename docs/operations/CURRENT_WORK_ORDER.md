# Current Work Order

**Status:** ACTIVE

**Phase:** R0.9B — Canonical Edit Contracts → Resolver → Deterministic Optimizer

**Goal:** converge R0.9A onto existing canonical Domain contracts, then implement the first deterministic grounded source-selection/sequence decision and a local resolved-sequence diagnostic preview.

## Entry

1. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
2. Read `docs/roadmap/CURRENT_PHASE_STATUS.md`.
3. Read this file.
4. Read `docs/capabilities/CAP-04_RETRIEVAL_DIRECTOR_RESOLVER.md` sections 11–20.
5. Read `docs/adr/ADR-004_LAYERED_BEAM_SEARCH_OPTIMIZER_BASELINE.md`.
6. Inspect the R0.9A implementation plus existing `domain/edit/model.py` and `domain/edit/resolution.py`.

Do not restart retrieval/model research and do not enter R0.10.

## Mandatory preflight — canonical convergence

Before adding Resolver code:

- evolve/reuse canonical `domain/edit/model.py::EditPlan/EditSlot`; remove or reduce the R0.9A Director duplicate to a non-authoritative import/re-export if needed;
- evolve/reuse canonical `domain/edit/resolution.py::CandidateWindow`; the generator must output that type rather than a competing definition;
- introduce an explicit rational min/max duration-constraint value using `MediaTime` semantics; do not overload `MediaTimeRange`, whose meaning remains exact media interval `[start,end)`;
- migrate R0.9A tests/probe without changing its proven retrieval/window behavior;
- add regressions preventing future duplicate authorities and duration-range misuse.

Routine naming/file-placement choices are autonomous. Do not stop after preflight; continue through the full R0.9B boundary if green.

## Resolver baseline

Use only eligible grounded CandidateWindows. Never invent Shot IDs or source timestamps.

Implement a deterministic, versioned resolver strategy with explainable contributions. At minimum support:

- unary suitability features available from current evidence/intent;
- pairwise transition/reuse compatibility available from current evidence;
- bounded global sequence features such as slot coverage, duration and reuse;
- hard feasibility before scoring;
- score and confidence stored separately;
- reasons / feature contributions / warnings / alternatives / evidence refs;
- explicit unresolved result when no legal/useful candidate exists;
- existing one-Slot → multiple `ResolvedSelection` Domain capability.

Do not pretend unavailable features are measured. Missing evidence should reduce confidence or remain neutral, not be fabricated.

## Deterministic sequence optimizer

Implement the ADR-004 first baseline as a small layered beam-search / DAG-style optimizer over ordered EditSlots and their bounded CandidateWindows.

Requirements:

- deterministic for identical evidence + strategy version;
- hard constraints always dominate score;
- obey slot order and reuse policy;
- support bounded Top-K/beam width as versioned strategy parameters;
- preserve enough state/reasons to explain why the chosen sequence beat alternatives;
- no EDL timeline authority and no arbitrary millisecond search.

## Probe and visible result

Reuse the gitignored `example/` real-media corpus and R0.9A outputs where valid. Create/extend one R0.9B local probe that exercises multiple ordered slots and proves at least:

1. canonical contract convergence;
2. hard-ineligible candidate cannot win;
3. higher editorial suitability can beat a merely higher retrieval rank;
4. deterministic repeat produces identical decisions;
5. reuse policy is enforced;
6. no-candidate case becomes `UNRESOLVED`;
7. score/confidence/reasons/alternatives remain inspectable;
8. one Slot can resolve to multiple selections when the fixture explicitly requires it;
9. selected ranges are exact existing CandidateWindows and remain inside Shot bounds;
10. optimizer produces a legal ordered sequence.

Write local-only artifacts under:

`example/probe-output/r0_9b/`

At minimum:

- `resolution_decisions.json`;
- `resolved_sequence_preview.mp4` built only by concatenating/copying/transcoding the already-selected grounded source ranges in optimizer order for human inspection.

The preview is diagnostic only, not EDL/final-render authority.

## Regression / Quality

Run focused tests, the R0.9A regression probe where relevant, the new R0.9B live probe and the complete repository Quality Gate.

If all green:

- coherent commit + push `main`;
- report starting/ending HEAD, canonical repairs, named probe gates, selected ranges/sequence, preview path and major-stage wall-clock;
- classify `ENGINEERING BASELINE ADEQUATE`, `MATERIAL DEFECT` or `BLOCKED`;
- stop at R0.9B. Do not begin the R0.9 phase-closure Product Probe or R0.10 in this batch.
