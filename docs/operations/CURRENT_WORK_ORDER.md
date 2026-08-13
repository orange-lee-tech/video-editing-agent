# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.8F — Seeded Subject/Product Tracking Baseline  
**Updated:** 2026-08-13

## Goal

Add a CPU/local, provider-neutral seeded tracker that propagates an explicitly supplied target region through an exact Shot/range and persists auditable tracking evidence.

This is the remaining tracking foundation required by R0.8. It is not object detection, semantic action recognition, or edit selection.

## Required reading

1. `docs/operations/CODEX_EXECUTION_ENTRY.md`
2. `docs/roadmap/CURRENT_PHASE_STATUS.md`
3. `docs/capabilities/CAP-03_MEDIA_UNDERSTANDING_SPEECH_TEMPORAL.md` sections on tracking / provider tiers / TemporalEvidence
4. Current visual-motion/refinement implementation and tests

## Implementation boundary

Prefer the existing optional OpenCV 4.13 runtime and existing FFmpeg exact-range decoding. Do not add a new heavy dependency merely for the baseline.

A suitable first mechanism is a seeded sparse-LK tracker: initialize trackable points inside a normalized seed rectangle, propagate with pyramidal LK, robustly estimate target-region motion, update the region, and fail explicitly when support is insufficient. Codex may choose an equivalent existing-OpenCV mechanism if it preserves the gates below and requires no unjustified dependency expansion.

Keep provider output behind an application Port and local owner. No OpenCV/NumPy types enter Domain state.

Persist rich trajectory/samples as a content-addressed durable-derived Artifact; persist low-density provider-neutral TemporalEvidence referencing exact Shot revision, analyzed source range, seed identity/geometry, provider revision and Artifact. Do not create a new top-level Domain entity.

All source time is rational original-Asset `MediaTime`. Geometry persisted across provider boundaries should be provider-neutral and normalized to frame dimensions.

Tracker loss, occlusion, insufficient features, target exit and decode failure must be explicit. Never hallucinate trajectory through unsupported gaps.

## Engineering gates

Controlled Windows fixtures must cover at least:

- static camera + moving seeded target: trajectory follows target;
- camera pan + independently moving seeded target: target remains tracked without confusing whole-frame motion for target motion;
- temporary/full occlusion: explicit loss or bounded recovery policy, never invented long-gap trajectory;
- target exits frame: explicit termination/unavailable state;
- distractor / nearby texture: tracker does not silently switch identity in the controlled fixture;
- non-zero Shot start and bounded analyzed range: no cross-Shot tracking;
- persistence/reopen: exact trajectory Artifact/evidence/provenance survives restart;
- deterministic rerun: same fixture/config produces stable identities and materially equivalent trajectory;
- optional OpenCV absent/wrong version: clean unavailable behavior;
- existing R0.8C–E motion/refinement regressions remain green.

Report quantitative center/box error against controlled ground truth and tracker survival/loss timing. Use fixture-derived acceptance gates; do not weaken them merely to obtain PASS.

## Completion boundary

If the mechanism and all repository Quality Gates pass, run a reusable Windows live probe, make one coherent commit on `main`, push, and stop at the end of R0.8F.

Do **not** continue into dense embeddings/R0.8G, paid Product Probe, Director, Resolver, EDL, music or Auto Reframe in this work order.

## Expected report

Only report repository HEAD/commit state, named tracking gates, key accuracy/loss metrics, persistence/restart result, Quality Gate, material repairs, remaining risks and classification.
