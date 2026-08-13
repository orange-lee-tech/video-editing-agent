# Current Work Order

**Status:** ACTIVE

**Phase:** R0.10 Product Probe + Phase Closure

**Goal:** prove or falsify the R0.10 product claim on a real short-form project using real rights-attested local music, then stop for Human Gate.

## Entry

1. Read `docs/operations/CODEX_EXECUTION_ENTRY.md`.
2. Read `docs/roadmap/CURRENT_PHASE_STATUS.md`.
3. Read this file.
4. Read Roadmap V2 R0.10 Product Probe/Exit Gate and only the accepted R0.10A/B implementation needed for the probe.

Do not add a new R0.10 feature module, external paid/network music provider, heavyweight audio model, final EDL authority or R0.11 work.

## Mandatory preflight

Make `compile_audio_execution()` derive duck gain relationships entirely from `AudioMixDecision`. Remove the hidden fixed `-10 dB` base-gain assumption and add a regression where changing base gain changes the compiled duck multiplier correctly. Continue through the Product Probe after this bounded fix.

## Real Product-Probe inputs

Synthetic rhythmic fixtures are Engineering-Probe-only and must not be used for product preference claims.

Use:

- one existing real short-form local video/project from the managed `example/` corpus;
- real R0.8 speech/VAD evidence where available for narration/source-audio intelligibility;
- at least two materially different real local music files for which the user can explicitly attest usage rights.

Prefer a gitignored local directory such as `example/product-probe-music/`. Do not commit music bytes or private paths.

Do not invent rights. If fewer than two real rights-attested music candidates are locally available, stop cleanly as `NEEDS_REAL_MUSIC_INPUT` and report the exact directory/file requirement. Do not download arbitrary music or substitute synthetic tracks.

## Product comparison

Run the accepted rights → BeatMap → CandidateMusicWindow → MusicSelectionDecision → AudioMixDecision → execution/QC path for both real music candidates.

Produce three human A/B questions with controlled variables:

1. **Music candidate:** same video/mix policy, candidate A vs candidate B using each candidate's own best grounded window.
2. **Music moment:** same chosen track and same mix policy, a transparent baseline legal window vs the feature-ranked selected window.
3. **Mix:** same chosen track/window, basic/baseline mix vs structured decision-derived duck/fade mix.

Do not force the structured version to win. Preserve honest ties/regressions.

## Technical evidence

Report and gate at least:

- rights status/provenance for each candidate;
- BeatMap metrics/confidence for each candidate;
- generated windows, feature contributions, selected exact source segments and alternatives;
- selected segments actually executed by the compiler;
- AudioMixDecision automation actually compiled;
- deterministic rerun equality;
- post-mix peak/RMS/silence/clipping for every human-review preview;
- source/narration audio remains present when policy is preserve;
- provider/API cost (expected zero for the local-only baseline);
- R0.10A/R0.10B regressions and full Quality Gate remain green.

## Human-review artifacts

Write local-only artifacts under:

`example/probe-output/r0_10_product/`

At minimum:

- `candidate_a_preview.mp4`;
- `candidate_b_preview.mp4`;
- `moment_baseline_preview.mp4`;
- `moment_ranked_preview.mp4`;
- `mix_baseline_preview.mp4`;
- `mix_structured_preview.mp4`;
- `comparison.json`;
- `HUMAN_REVIEW.md`.

`HUMAN_REVIEW.md` must give a simple rubric and explicitly allow `A`, `B`, `tie/inconclusive`, plus a short defect note. Do not require the user to invent a professional rating scale.

## Completion

If technical acceptance passes:

- commit/push all non-private code/test/probe/doc changes coherently;
- keep music and previews local/gitignored;
- classify `READY_FOR_HUMAN_ACCEPTANCE`;
- stop before marking R0.10 CLOSED and before R0.11.

If required real music is absent, classify `NEEDS_REAL_MUSIC_INPUT`. If a bounded R0.10 mechanism defect appears, repair the shared mechanism, add regression coverage and rerun this same Product Probe when practical.

Final report: HEAD, preflight result, real candidate identities without private paths, rights state, BeatMap/window/selection metrics, executed source segments, post-mix QC, preview directory/files, provider cost, Quality Gate and major-stage wall-clock.
