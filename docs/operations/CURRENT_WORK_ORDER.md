# Current Work Order

**Status:** ACTIVE  
**Phase:** R0.10 — real-music Product Probe / Human Gate / closure  
**Activated:** 2026-08-14

## Meaning

This file is the active coherent construction boundary. It was activated after reobserving current `origin/main` and CI and confirming that the preserved R0.10 boundary still matches implementation reality.

No new product-policy decision is required to execute this boundary. If the user changes the goal or the repository materially changes, refresh the work order before continuing.

## Resume boundary

1. Mandatory preflight: make `compile_audio_execution()` derive duck/base-gain relationships entirely from `AudioMixDecision`; remove the hidden fixed `-10 dB` assumption and add a regression.
2. Use one real local short-form project and at least two materially different real local music files for which the user can attest local test/use rights.
3. Run the accepted rights → BeatMap → CandidateMusicWindow → MusicSelectionDecision → AudioMixDecision → execution/QC path.
4. Produce controlled human A/B comparisons for music candidate, music moment and structured mix. Ties/inconclusive are valid.
5. Every preview must execute canonical decisions and receive post-mix QC.
6. Keep R0.10A/R0.10B regressions and the full repository Quality Gate green.
7. If technically green, stop at `READY_FOR_HUMAN_ACCEPTANCE`; only the user/Human Gate can close R0.10.

If fewer than two suitable real local music candidates exist, report `NEEDS_REAL_MUSIC_INPUT`. Do not download arbitrary tracks, invent rights or substitute synthetic fixtures for product-quality claims.

## Not in scope

- no R0.11 Spatial/Auto Reframe implementation before R0.10 closes;
- no external paid/network music provider merely to complete the probe;
- no heavyweight audio model without a benchmark need;
- no final EDL/Renderer authority leap.

## Execution entry

Before coding:

1. reobserve local/remote state and confirm a clean `main` working tree;
2. read `docs/operations/CODEX_EXECUTION_ENTRY.md`;
3. read `docs/roadmap/CURRENT_PHASE_STATUS.md` and this file;
4. inspect only the R0.10 implementation/tests needed for this boundary;
5. execute the complete work order and stop at its stated gate.
