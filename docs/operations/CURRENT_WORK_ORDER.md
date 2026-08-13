# Current Work Order

**Status:** ACTIVE

**Phase:** R0.9A — Edit Intent → Hybrid Retrieval → Grounded CandidateWindows

**Goal:** build the first inspectable automatic-editing decision boundary: structured EditSlot intent must retrieve eligible real Shots and produce bounded source-time CandidateWindows with explainable provenance, then export local diagnostic previews for human inspection.

## Entry

1. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
2. Read `docs/roadmap/CURRENT_PHASE_STATUS.md`.
3. Read this file.
4. Read `docs/capabilities/CAP-04_RETRIEVAL_DIRECTOR_RESOLVER.md` sections 1–10 and 17–20.
5. Read `docs/adr/ADR-003_LOCAL_HYBRID_RETRIEVAL_BASELINE.md`.
6. Inspect only the current planning/ShotIndex/temporal-evidence contracts and the empty `editing/director` / `editing/resolver` seams needed for this batch.

Do not reread unrelated historical material and do not implement R0.10+ capabilities.

## 1. Edit intent ownership

Implement provider-neutral canonical `EditPlan` / `EditSlot` value/domain contracts sufficient for R0.9 retrieval.

An EditSlot may express story/edit intent such as:

- stable slot identity and order;
- narrative role / purpose;
- desired subject/action/semantic query;
- target duration range using rational MediaTime;
- pacing / continuity hints;
- reuse policy;
- importance/intelligence budget.

It must not contain or accept authoritative source file paths, Shot IDs selected by a model, or source timestamps invented by a model.

Keep this boundary compatible with future Director model proposals but do not require a paid/live LLM call to prove R0.9A.

## 2. Hard eligibility

Before ranking, remove candidates that are definitely illegal for the Slot using already-authoritative project facts where available. At minimum enforce exact current Shot/source-range validity and existing usage-role/source eligibility semantics. Add narrow hooks/contracts for other hard constraints without inventing unavailable facts.

Ineligible candidates leave the search space; they are not merely assigned a low score.

## 3. Hybrid retrieval

Reuse the existing lexical/CJK index and R0.8 dense representations. Do not create competing Shot authorities.

Implement deterministic RRF-like rank fusion over lexical and dense candidate ranks. Requirements:

- lexical and dense raw scores are not treated as directly comparable;
- deterministic tie ordering;
- representation provenance remains rebuildable/non-authoritative;
- structured hard eligibility happens before final candidate exposure;
- retrieval output remains high-recall candidates only;
- fusion parameters are versioned strategy/configuration, not Domain truth.

No vector database/ANN server.

## 4. CandidateWindow generation

For each plausible Shot, generate a small bounded set of legal source windows from authoritative evidence rather than enumerating arbitrary timestamp pairs.

Inputs may use:

- exact Shot begin/end;
- speech phrase boundaries and VAD/silence;
- coarse/fine temporal anchors;
- action onset/peak/settle;
- target Slot duration;
- explicit user/source locks when already represented.

CandidateWindow must preserve at least:

- exact `shot_ref`;
- exact rational source range;
- Slot reference;
- anchor/evidence refs that justify IN/OUT/window;
- duration;
- confidence/evidence quality summary;
- stable deterministic identity/provenance.

Rules:

- every window must lie wholly inside the authoritative Shot source range;
- no free-form timestamp generation from LLM text;
- no cross-Shot window;
- no invalid/negative/zero duration;
- avoid combinatorial millisecond enumeration;
- deterministic evidence + policy must reproduce the same windows.

## 5. Explainability

For each surfaced candidate, retain enough information to answer:

- why this Shot was retrieved;
- which retrieval channels contributed;
- why this IN/OUT window exists;
- which evidence/anchors constrain it;
- what was filtered by hard eligibility.

Do not collapse everything into one opaque score.

## 6. Local real-media Engineering/Product bridge probe

Reuse the gitignored `example/` corpus and its tracked manifest. Reuse R0.8 runtimes/caches; no model reinstall or new paid API.

Create one reusable R0.9A probe under `tools/probes/` that constructs a small deterministic EditPlan/EditSlot set against the existing product footage and demonstrates:

1. lexical-only candidates;
2. dense-only candidates;
3. hybrid RRF candidates;
4. an ineligible candidate is excluded before ranking exposure;
5. stable deterministic rank/tie behavior;
6. CandidateWindows remain inside exact Shot/source boundaries;
7. at least one local-action Slot receives a window near real R0.8 temporal action evidence;
8. a low-motion/negative case does not fabricate an action window;
9. restart/reopen or deterministic rebuild preserves provenance;
10. no model/provider can inject arbitrary Shot IDs or timestamps.

Report candidate counts, broad Top-K, per-channel ranks, window ranges/durations, evidence refs and CPU latency.

## 7. Human-inspectable local preview artifacts

The user must be able to inspect what R0.9A thinks is worth cutting.

For the probe only, export diagnostic preview clips for the top CandidateWindows under:

`example/probe-output/r0_9a/`

Also write a local JSON report in that directory mapping:

`EditSlot → Shot → CandidateWindow → preview filename → evidence/retrieval reasons`.

Rules:

- these files remain gitignored/local-only;
- use FFmpeg only to trim/mux/copy or safely transcode the already-grounded source window;
- preview generation has zero creative authority;
- do not introduce EDL timeline placement, transitions, music, spatial composition or final-render semantics;
- failure to create a preview must not mutate candidate authority.

## Regression / Quality gates

Add deterministic tests for the domain and failure boundaries, including:

- EditSlot cannot carry authoritative invented source timestamps/IDs;
- hard eligibility dominates ranking;
- RRF fusion deterministic and stable under tie;
- lexical/CJK baseline unchanged;
- dense provenance semantics unchanged;
- CandidateWindow cannot leave Shot bounds or cross Shot identity;
- unsupported/missing evidence fails closed or yields fewer windows rather than guessed timestamps;
- exact evidence + policy reproduces identical CandidateWindow identities.

Run the complete repository Quality Gate plus the R0.9A live probe.

## Completion

If all gates pass:

- make one coherent code/test/probe commit on `main` and push;
- keep diagnostic media/report local and gitignored;
- report starting/ending HEAD, changed files, named gates, candidate/window metrics, preview output directory and major-stage wall-clock time;
- classify `ENGINEERING BASELINE ADEQUATE`, `MATERIAL DEFECT` or `BLOCKED`;
- stop at R0.9A. Do not begin Resolver/optimizer implementation in this batch.
