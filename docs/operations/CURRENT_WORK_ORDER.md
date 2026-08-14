# Current Work Order

**Status:** WAITING_INPUT  
**Phase:** R0.10 — real-music Product Probe / Human Gate / closure  
**Updated:** 2026-08-14

## Current evidence

Current accepted implementation baseline:

`6c5b70be39ab4188942787974a07fd1e2d0283ce` — `fix: enforce source audio mix policy`

Observed and reverified evidence:

- `AudioMixDecision.source_audio_policy` now controls canonical execution;
- `PRESERVE` consumes/mixes source audio when available;
- `MUTE` does not reference the source-audio input and retains intentional BGM output;
- missing source audio can still produce a valid audible BGM-only output;
- undefined source-audio `DUCK` fails closed rather than inventing semantics;
- routine planning with no grounded speech defaults to `MUTE`; grounded speech selects `PRESERVE` using the existing speech/VAD evidence path;
- existing VAD already uses stream-selective FFmpeg PCM decode, so no eager audio proxy was added without benchmark need;
- R0.10 focused/live regressions and full repository Quality Gate are green on remote CI.

## Why work is waiting

The R0.10 engineering boundary is complete enough to run the required Product Probe. The only current blocker is external/user input:

```text
NEEDS_REAL_MUSIC_INPUT
real local music candidates = 0 / required 2
```

Do not create substitute engineering work simply to keep the phase moving.

## Required user input

Provide at least two materially different real local music files under the gitignored local probe area, normally:

```text
example/product-probe-music/
```

The user must be able to attest that the tracks may be used for this local test/project. A simple explicit attestation is sufficient for the Product Probe evidence record; the software records the claim but does not certify its legal truth.

The tracks should be materially different enough to make the music-candidate comparison meaningful (for example different mood, rhythm, instrumentation or energy profile). Do not download arbitrary tracks merely to satisfy the count.

## Resume boundary once input exists

1. Sync clean `main` to current `origin/main` and reobserve the control plane.
2. Confirm at least two suitable local music files and record user rights attestation without fabricating license facts.
3. Use one real short-form project and run the accepted rights → BeatMap → CandidateMusicWindow → MusicSelectionDecision → AudioMixDecision → canonical execution/render/QC path.
4. Produce the three controlled comparisons already defined for R0.10:
   - music candidate: Track A vs Track B;
   - music moment: ordinary legal window vs feature-ranked selected window;
   - mix: basic mix vs structured duck/fade mix.
5. Every preview must consume canonical decisions and receive rendered-output QC.
6. Keep all R0.10A/R0.10B/source-audio-policy regressions and the full repository Quality Gate green.
7. If technically green, stop at `READY_FOR_HUMAN_ACCEPTANCE` and present the comparisons in ordinary human terms. Only the user/Human Gate can close R0.10.

## Hard boundaries

- no destructive modification of user source Assets;
- no arbitrary downloaded music or fabricated rights;
- no synthetic music as Product Probe evidence;
- no second audio/timestamp authority;
- no new audio proxy unless benchmark evidence justifies it;
- no new R0.10 micro-phase merely to avoid the input gate;
- no R0.11 work before R0.10 closes.

## Codex entry after input is ready

Read only:

1. `docs/operations/CODEX_EXECUTION_ENTRY.md`
2. `docs/roadmap/CURRENT_PHASE_STATUS.md`
3. this work order
4. `docs/capabilities/CAP-06_MUSIC_AUDIO_EDITORIAL.md`
5. the Product Probe implementation/tests actually needed

Then execute the complete remaining R0.10 Product Probe boundary and stop at its stated gate.
