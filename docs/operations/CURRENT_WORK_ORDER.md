# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.10 — source-audio policy/execution repair → real-music Product Probe / Human Gate / closure  
**Updated:** 2026-08-14

## Current evidence

Remote implementation baseline before this work order refresh:

`5644c22211d43cba10b5cdae0575316a32a49a89` — `fix: derive audio ducking from mix decision`

Observed evidence:

- fixed-base-gain assumption removed from `compile_audio_execution()`;
- focused R0.10A/R0.10B tests passed;
- full Quality Gate passed on remote CI;
- real-music Product Probe did not run because `example/product-probe-music/` had `0/2` required real local music candidates;
- classification was correctly `NEEDS_REAL_MUSIC_INPUT`.

## Why this boundary changed

The user clarified a durable product/editorial preference: routine short-form editing should not drag noisy camera audio through the workflow merely because it is muxed with the video. Original source media must remain intact, but visual processing and source-audio processing should be separable, and routine output may mute source audio unless dialogue/ambience/meaningful action sound is intentionally needed.

This matches the existing R0.10 Roadmap deliverable `source audio preserve/mute policy`; it is not a new phase.

A code audit also shows a real execution gap:

- `AudioMixDecision` already carries `SourceAudioPolicy`;
- current basic planning effectively uses `PRESERVE`;
- current diagnostic audio compiler always consumes `[0:a]` and therefore does not make `source_audio_policy` authoritative.

## Coherent implementation boundary

1. Preserve the authoritative ingested video Asset unchanged. Do not destructively strip/rewrite source files.
2. Keep visual and source-audio lanes logically separate. Visual-only work must not depend on carrying audio. Reuse existing stream-selective FFmpeg decode where adequate; do **not** automatically materialize a large permanent PCM copy for every Asset.
3. If a reusable demuxed/decoded audio derivative materially reduces repeated ASR/VAD/audio-analysis work, implement it only as a provenance-preserving derived Artifact/cache with exact source-time mapping. Prefer the smallest architecture-consistent implementation; benchmark before making eager extraction mandatory.
4. Make `AudioMixDecision.source_audio_policy` affect canonical execution truth. At minimum, `MUTE` and `PRESERVE` must produce observably different valid execution plans and rendered outputs. Give `DUCK` deterministic semantics only if existing ownership/model semantics support it cleanly; otherwise fail explicitly rather than inventing hidden behavior.
5. For routine short-form planning with no grounded need for camera audio, use `MUTE` as the normal default. Preserve/attenuate source audio only when grounded speech/ambience/critical action sound or explicit user/editorial intent requires it. Do not add expensive denoising merely to rescue unneeded camera audio.
6. When source speech or critical sound is intentionally retained, preserve its grounded time integrity. Reuse existing ASR/VAD/TemporalEvidence/CandidateWindow machinery rather than creating a second timestamp authority.
7. Add regressions proving decision mutation changes execution, including source-audio policy. Include a no-audio-input case and prevent accidental silent final output when an intentional BGM/voiceover/SFX lane exists.
8. Keep all R0.10A/R0.10B regressions and the full repository Quality Gate green.
9. When at least two materially different, rights-attested real local music tracks are available, resume the existing R0.10 Product Probe and produce the already-defined three controlled comparisons: music candidate, music moment, structured mix.
10. If real music is still unavailable after the engineering repair, stop with `NEEDS_REAL_MUSIC_INPUT`. If the Product Probe is technically green, stop at `READY_FOR_HUMAN_ACCEPTANCE`.

## Hard boundaries

- no destructive modification of user source Assets;
- no claim that a demuxed audio proxy is a new authoritative Asset;
- no second audio/timestamp authority outside `AudioMixDecision` → EDLBuilder/execution ownership;
- no arbitrary downloaded music or fabricated rights;
- no synthetic music as Product Probe evidence;
- no R0.11 work before R0.10 closes;
- no heavyweight denoising/audio model without a demonstrated benchmark need.

## Codex entry

Before coding:

1. sync clean `main` to current `origin/main`;
2. read `docs/operations/CODEX_EXECUTION_ENTRY.md`;
3. read `docs/roadmap/CURRENT_PHASE_STATUS.md` and this work order;
4. read `docs/capabilities/CAP-06_MUSIC_AUDIO_EDITORIAL.md`;
5. inspect only the relevant audio planning/execution, ASR/VAD decode path and tests;
6. execute the whole coherent boundary and stop at its stated gate.
