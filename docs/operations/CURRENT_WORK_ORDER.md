# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.8H — Real-Footage Product Probe + Phase Closure  
**Goal:** prove or falsify R0.8 usefulness on private real footage and, if the gate passes, close R0.8 in this same work order.

## Entry

1. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
2. Read `docs/roadmap/CURRENT_PHASE_STATUS.md`.
3. Read this file.
4. Read Roadmap V2 section `R0.8 — Media Evidence Foundation` and only the R0.8 implementations/probes needed for the closure run.

Do not reread unrelated historical material and do not start R0.9 implementation.

## Private-media contract

Use `C:\Users\yulia\Desktop\video-editing-agent\.private\r0_8h\` as the default local-only probe root. `/.private/` is gitignored.

Never commit:

- private media;
- absolute media paths;
- raw private transcripts;
- extracted private frames/audio;
- secrets or user-identifying content.

Committed closure evidence must use anonymized clip IDs and aggregate/derived metrics only.

A single real clip may cover multiple categories. The real-footage set must collectively cover:

- talking head;
- handheld product demo;
- camera pan;
- hand/product interaction;
- low motion;
- noisy/blurred footage.

Prefer a small set of short clips over a large corpus. This is a phase closure probe, not a benchmark campaign.

## Ground-truth / manifest

Prefer `.private/r0_8h/manifest.json` when present. It may contain local-relative filenames, anonymous clip IDs/categories, a few expected speech phrase ranges and/or coarse motion-event ranges/negative controls needed to score the probe.

Do not require frame-perfect annotation. Coarse human-known event windows are enough to test whether grounded evidence is useful.

If real footage exists but the manifest is absent, inspect only this private probe directory, create a minimal local-only manifest/template from the available filenames and run every gate that can be scored honestly. Do not invent human ground truth.

If no usable real footage exists, stop with classification `NEEDS_REAL_FOOTAGE` and report the smallest missing set. Do not substitute synthetic fixtures and do not create another engineering subphase.

## Closure probe

Create or extend one reusable probe under `tools/probes/` for R0.8H. Reuse existing R0.8 services/providers and previously validated local runtimes/caches; do not reinstall models or redo model selection unless the environment is missing/corrupt.

For the private clips, exercise the relevant chain end-to-end as far as practical:

- Asset/Shot source-time identity;
- ASR transcript timestamps;
- VAD/silence and phrase/time mapping;
- camera/global and residual motion;
- coarse event regions/anchors;
- fine temporal refinement where applicable;
- seeded tracking on at least one explicit product/subject seed where the manifest provides one;
- visual-semantic/speech dense representation and exact local retrieval sanity where representation inputs are available;
- persistence/reopen with provenance.

Do not introduce Director, Resolver, CandidateWindow, RRF production fusion, music or R0.9 authority.

## Product acceptance gates

Report independent PASS/FAIL/NOT_APPLICABLE gates and enough metrics to judge usefulness, including:

1. `REAL_FOOTAGE_SOURCE_TIME` — evidence stays within exact Shot/source ranges and survives reopen;
2. `SPEECH_TIMESTAMP_USEFULNESS` — expected spoken phrases map to plausible source ranges;
3. `SPEECH_CUT_QUALITY` — phrase boundaries plus VAD/silence provide usable cut boundaries for annotated speech examples;
4. `PAN_FALSE_LOCAL_ACTION` — camera pan does not create material false residual-action evidence;
5. `LOCAL_ACTION_RECALL` — annotated hand/product or local-motion events receive nearby residual region/anchor candidates;
6. `LOW_MOTION_FALSE_POSITIVE` — low-motion real footage does not produce excessive event anchors;
7. `NOISY_BLURRED_FAIL_SAFE` — weak footage lowers/loses evidence cleanly rather than inventing confident events/tracks;
8. `TRACKING_REAL_FOOTAGE` — seeded track remains useful when visible and reports explicit loss/exit when not supportable;
9. `RETRIEVAL_REAL_PROJECT_SANITY` — available speech/visual semantic representation retrieves the intended clip for a small set of local semantic queries without changing ShotAnalysis authority;
10. `R0_8_RESTART_PROVENANCE` — persisted evidence/representations reopen with exact revisions/provenance.

Use tolerances derived from the evidence mechanism and human-known coarse windows. Do not weaken a gate merely to pass it. Record false positives and misses explicitly.

The Roadmap exit question is binary:

> Can the system produce a useful grounded candidate-time set for real footage without a high-end GPU?

## Repair policy

If a gate fails because of a bounded defect in an existing R0.8 mechanism:

- diagnose mechanism, not symptom;
- repair the shared invariant;
- add deterministic regression coverage;
- rerun the affected Engineering Probe and the same real-footage Product Probe;
- continue toward closure in this same work order when practical.

Do not create R0.8I/R0.8J merely for routine repair.

Stop only for a material architectural defect, missing real-footage/ground-truth needed for an honest Product Probe, unavailable required local runtime, or a failure that would require crossing into R0.9 authority.

## Quality and closure

Run the complete repository Quality Gate after any code changes. A probe-only closure with no code change still requires confirming current CI/quality baseline remains green and running the relevant local checks.

If the real-footage acceptance is adequate:

1. create `docs/validation/R0.8_FINAL_CLOSURE.md` with anonymized corpus description, environment, named gates, metrics, known limitations and accepted baseline commit(s);
2. update `docs/roadmap/CURRENT_PHASE_STATUS.md` to mark R0.8 CLOSED and R0.9 ACTIVE;
3. replace this file with a short `R0.8 CLOSED — awaiting R0.9 work order` state;
4. commit/push all non-private code/docs changes coherently;
5. stop before R0.9 implementation.

Final classification must be one of:

- `R0.8 CLOSED`;
- `MATERIAL R0.8 DEFECT`;
- `NEEDS_REAL_FOOTAGE`;
- `BLOCKED`.

Report wall-clock by major stage when observable, but optimize for useful progress per unit time rather than minimum elapsed time.
