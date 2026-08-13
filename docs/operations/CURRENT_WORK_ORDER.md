# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.8H — Real-Footage Product Probe + Phase Closure  
**Goal:** finish the remaining R0.8 Product Probe using the existing local real-media corpus plus a deterministic local speech fixture, then close R0.8 in this same work order if the gates pass.

## Entry

1. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
2. Read `docs/roadmap/CURRENT_PHASE_STATUS.md`.
3. Read this file.
4. Inspect only the existing R0.8 implementations/probes and the tracked R0.8H corpus manifest needed for closure.

Do not restart model research and do not start R0.9 implementation.

## Local media

- `example/` remains the gitignored real captured media corpus.
- Validate/update `tests/fixtures/media/r0_8h/corpus_manifest.json` with the existing manifest tool before the closure run.
- Never commit media files, generated speech media, absolute local paths, raw transcripts or identifying content.

The existing corpus already covers the visual R0.8H cases: handheld product demo, camera motion/pan, hand-object interaction, low motion and weak/noisy/blurred footage.

## Deterministic speech fixture — no user speech required

The prior requirement for a real speaker/camera acoustic recapture is removed; it was an unnecessary closure constraint, not a Domain requirement.

Create one local-only derived speech-bearing clip from an existing real `example/` video.

Preferred path:

1. Generate TTS locally with existing Windows facilities (prefer built-in SAPI/System.Speech when available; no paid/network TTS).
2. Use a short deterministic script with a known pause, for example:
   - `The bottle is standing on the table.`
   - approximately 1 second pause
   - `Now the bottle is picked up and turned slowly.`
3. Mix the synthesized speech with the selected clip's original captured ambient audio at a level that keeps speech intelligible while retaining some real recording noise, when practical.
4. Mux to a new gitignored/local-only video under `example/` or `.private/r0_8h/`; never alter the original corpus media in place.
5. Keep local machine-readable ground truth for the exact script and intended pause/range so ASR/VAD/phrase/cut gates can be scored deterministically.
6. Update/check the anonymized corpus manifest if the generated fixture is intentionally included in the local corpus view; generated coverage must be clearly distinguishable from human-confirmed real visual coverage.

If the built-in local TTS facility is unavailable, use another already-available local synthesis path. Do not install a large new runtime or call a paid API solely for this fixture. Stop only if no reasonable local synthesis path exists.

This fixture validates speech timestamp/VAD/phrase/cut integration. Closure must explicitly state that natural spontaneous human speech, real microphone speech acoustics and talking-head visual behavior were not product-validated in this R0.8 baseline.

## Closure probe

Create or extend one reusable R0.8H probe under `tools/probes/`. Reuse existing R0.8 services/providers/runtimes/caches.

Exercise, as applicable:

- Asset/Shot source-time identity;
- ASR transcript timestamps;
- VAD/silence and phrase/time mapping;
- camera/global and residual motion;
- coarse/fine temporal anchors;
- seeded tracking on a real product/subject clip;
- visual-semantic/speech dense representation and exact local retrieval sanity;
- persistence/reopen with provenance.

Do not introduce Director, Resolver, CandidateWindow, RRF production fusion, music or other R0.9 authority.

## Product acceptance gates

Report independent PASS/FAIL/NOT_APPLICABLE gates with useful metrics:

1. `REAL_FOOTAGE_SOURCE_TIME`
2. `SPEECH_TIMESTAMP_USEFULNESS`
3. `SPEECH_CUT_QUALITY`
4. `PAN_FALSE_LOCAL_ACTION`
5. `LOCAL_ACTION_RECALL`
6. `LOW_MOTION_FALSE_POSITIVE`
7. `NOISY_BLURRED_FAIL_SAFE`
8. `TRACKING_REAL_FOOTAGE`
9. `RETRIEVAL_REAL_PROJECT_SANITY`
10. `R0_8_RESTART_PROVENANCE`

For speech gates, score against the deterministic TTS script/pause ground truth. For visual gates, score only against the real captured footage and human-confirmed coarse coverage; do not let the synthetic speech track substitute for visual Product Probe evidence.

The exit question remains:

> Can the system produce a useful grounded candidate-time set for real footage without a high-end GPU?

## Repair policy

If a bounded R0.8 defect appears:

- diagnose the mechanism;
- repair the shared invariant;
- add deterministic regression coverage;
- rerun the affected Engineering Probe and the same R0.8H Product Probe;
- continue toward closure in this same work order when practical.

Do not create R0.8I/R0.8J for routine repair.

## Quality and closure

Run the complete repository Quality Gate after code changes and confirm the current CI baseline remains green.

If all required gates are adequate:

1. create `docs/validation/R0.8_FINAL_CLOSURE.md` with anonymized corpus description, environment, named gates, metrics, known limitations and accepted baseline commits;
2. update `docs/roadmap/CURRENT_PHASE_STATUS.md` to mark R0.8 CLOSED and R0.9 ACTIVE;
3. replace this file with `R0.8 CLOSED — awaiting R0.9 work order` state;
4. commit/push all non-private code/docs changes coherently;
5. stop before R0.9 implementation.

Final classification:

- `R0.8 CLOSED`;
- `MATERIAL R0.8 DEFECT`;
- `BLOCKED`.

Report major-stage wall-clock time when observable, but optimize for useful progress per unit time.
