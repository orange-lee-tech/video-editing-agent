# Current Work Order

**Status:** ACTIVE

**Phase:** R0.10B — execution-evidence bridge repair

**Goal:** make the R0.10B diagnostic execution consume the canonical music-selection and audio-mix decisions, then measure the actual rendered mix before Product Probe.

## Entry

1. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
2. Read `docs/roadmap/CURRENT_PHASE_STATUS.md`.
3. Read this file.
4. Inspect the existing R0.10B selection, AudioMixDecision and live-probe renderer only as needed.

Do not redesign BeatMap/window ranking, add external music providers, add final EDL authority, or begin R0.11.

## Mandatory repair

The structured diagnostic preview must execute canonical decisions rather than duplicate their answers in probe constants.

- compile `MusicSelectionDecision.source_segments` into the diagnostic FFmpeg music source path, including bounded repeated/loop segments when present;
- compile `AudioMixDecision.automation_intents` into the structured diagnostic filter plan; do not separately hardcode selected duck/fade/gain ranges in the probe;
- keep FFmpeg execution non-authoritative: changing the decision changes execution, execution does not mutate the decision;
- preserve rational source ranges and exact selected Asset revision;
- keep the baseline preview as a simple comparator if useful, but the structured preview must be decision-derived.

## Rendered-output QC

QC must describe the post-mix rendered audio, not the input music fixture.

Extract or render a PCM analysis artifact from the same final mixed audio path and report peak/RMS/silence/clipping from that output. Do not claim delivery-standard loudness without a calibrated implementation.

## Regression / gates

Add focused regressions proving at least:

1. selected music source segments, not `0:6` or another probe constant, determine the structured preview music input;
2. changing an AudioMixDecision automation range changes the compiled execution plan;
3. no duplicated hardcoded duck/fade answer remains in the structured probe path;
4. rendered-output QC measures the post-mix audio and detects a deliberately clipped control fixture;
5. R0.10A regression remains green;
6. all existing R0.10B BeatMap/window/rights/loop gates remain green.

Regenerate local artifacts under `example/probe-output/r0_10b/`, including `baseline_mix_preview.mp4`, `structured_mix_preview.mp4`, `comparison.json`, and a local rendered-audio QC artifact if useful.

Run focused tests, R0.10A live regression, repaired R0.10B live probe and full repository Quality Gate.

If all green:

- coherent commit + push `main`;
- classify `ENGINEERING BASELINE ADEQUATE`;
- report HEAD, decision→execution evidence, executed selected source segments, rendered-output QC, preview paths, named gates, Quality Gate and major-stage wall-clock;
- stop at the repaired R0.10B boundary. Do not begin Product Probe or R0.11 in this batch.

If the repair exposes a broader authority defect, classify `MATERIAL DEFECT`; only classify `BLOCKED` for a real external/runtime blocker.
