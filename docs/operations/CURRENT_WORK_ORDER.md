# Current Work Order

**Status:** ENGINEERING BASELINE ADEQUATE

**Phase:** R0.10B — Beat Structure → Music-Window Rerank → Natural Mix Quality

**Goal:** turn the R0.10A audible foundation into a quality-bearing deterministic local audio path suitable for the later R0.10 Product Probe.

**Technical result:** PASS on 2026-08-13. `audioop` was removed, automation track roles
were separated from EditSlot identities, and the deterministic local path passed measured
BeatMap confidence, feature-ranked windows, bounded looping, natural duck ramps, PCM QC and
audible A/B gates. Product Probe/R0.11 work was not started.

## Entry

1. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
2. Read `docs/roadmap/CURRENT_PHASE_STATUS.md`.
3. Read this file.
4. Read `docs/capabilities/CAP-06_MUSIC_AUDIO_EDITORIAL.md` sections 9–19 and Roadmap V2 R0.10.
5. Inspect only R0.10A music/audio code, R0.8 speech/VAD evidence and current FFmpeg execution seams.

Do not add a paid/network music provider, CLAP/heavy audio model, final EDL authority, subtitle/render productization or R0.11 work.

## Mandatory preflight

Before quality expansion:

- replace the R0.10A `audioop` dependency with a supported deterministic implementation compatible with the repository's declared Python range; do not narrow project support merely to keep `audioop`;
- resolve `AudioAutomationIntent.target_slot_ids` semantics: role tokens such as `bgm` must not masquerade as EditSlot IDs. Use real slot IDs where slot-scoped, or introduce an explicit track/role targeting field while preserving one canonical authority;
- keep R0.10A regression behavior green.

Do not stop after preflight.

## BeatMap quality

Evolve the local CPU baseline without inventing unsupported structure.

- preserve exact rational source time and provider provenance;
- retain beats/tempo/energy and add only structure that can be measured reliably (for example accent/energy-envelope or coarse sections if evidence supports it);
- estimate confidence from actual signal quality/periodicity rather than a universal constant;
- fail soft on weak/non-periodic material;
- no BeatMap field may create video-cut authority.

Avoid new heavyweight runtime dependencies. A small local implementation or existing FFmpeg-compatible path is preferred.

## Music-window scoring and selection

R0.10A gave every CandidateMusicWindow the same score. Replace that placeholder with deterministic, inspectable feature contributions derived from available evidence and MusicIntent.

At minimum consider where honestly measurable:

- boundary/beat alignment;
- energy fit and trajectory;
- target-duration completeness;
- narration/speech conflict;
- rights confidence;
- loop feasibility.

Persist score and confidence separately with reasons/alternatives. Rights gates remain hard constraints. Do not force a later/high-energy window to win; report the actual result.

Support an explicit beat/structure-aligned multi-segment loop plan only when target duration requires it and the source has a defensible boundary. Otherwise prefer a natural contiguous window or return a warning/unresolved result.

## Natural AudioEditorial

Upgrade the diagnostic mix intent and executor bridge while keeping FFmpeg non-authoritative.

- represent duck attack/release ramps around real VAD/speech ranges rather than abrupt rectangular attenuation;
- merge/clip overlapping automation safely inside timeline bounds;
- preserve source audio unless policy says otherwise;
- make fade semantics explicit enough to describe the intended ramp, not only a constant gain;
- add deterministic local peak/loudness/silence QC from rendered audio where available, but do not claim delivery-standard loudness unless actually measured/calibrated;
- warnings remain explicit when speech evidence or reliable QC is unavailable.

## Probe

Create/extend one reusable R0.10B live probe. Reuse local caches and rights-safe local media. Synthetic rhythmic audio is valid for Engineering Probe only.

Exercise at least two materially different musical structures/windows so ranking is non-trivial, then render:

`example/probe-output/r0_10b/baseline_mix_preview.mp4`
`example/probe-output/r0_10b/structured_mix_preview.mp4`
`example/probe-output/r0_10b/comparison.json`

The structured preview must be audibly derived from the canonical MusicSelectionDecision + AudioMixDecision.

## Named gates

Prove at least:

1. `PYTHON_SUPPORT_COMPATIBLE`
2. `AUTOMATION_TARGET_SEMANTICS`
3. `BEATMAP_REAL_CONFIDENCE`
4. `WEAK_RHYTHM_FAILS_SOFT`
5. `WINDOW_FEATURES_INSPECTABLE`
6. `WINDOW_RANKING_DETERMINISTIC`
7. `RIGHTS_HARD_GATE_PRESERVED`
8. `STRUCTURAL_LOOP_BOUNDED_OR_REFUSED`
9. `DUCK_RAMPS_BOUNDED`
10. `AUDIO_QC_INSPECTABLE`
11. `AUDIBLE_A_B_RENDERED`
12. `R0_10A_REGRESSION`

Add focused regressions for the shared invariants. Run the R0.10A regression/live probe, R0.10B live probe and full repository Quality Gate.

## Completion

If green:

- coherent commit + push `main`;
- keep generated media local/gitignored;
- classify `ENGINEERING BASELINE ADEQUATE`, `MATERIAL DEFECT` or `BLOCKED`;
- report HEAD, preflight repairs, BeatMap metrics/confidence, window feature ranking, mix/QC evidence, A/B preview paths and major-stage wall-clock;
- stop at R0.10B. Do not begin the R0.10 Product Probe or R0.11 in this batch.
