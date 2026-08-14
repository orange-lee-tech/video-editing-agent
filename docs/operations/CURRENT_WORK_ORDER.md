# Current Work Order

**Status:** HANDOFF_READY — RESUMABLE BLUEPRINT  
**Phase:** R0.10 — real-music Product Probe / Human Gate / closure  
**Handoff:** 2026-08-14

## Meaning

This file preserves the next coherent construction boundary for a new conversation. It is **not a pause lock** and it is not permission for Codex to invent work by itself.

A new coordinating ChatGPT conversation may, after reobserving current `origin/main`, change this status to `ACTIVE` and continue this boundary without asking for a new product-policy decision. If the user changes the goal or the repository has materially changed, refresh the work order first.

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

## New-conversation entry

Before activation:

1. reobserve `origin/main` and CI;
2. read `docs/README.md`;
3. read `docs/operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md`;
4. read `docs/roadmap/CURRENT_PHASE_STATUS.md` and this file;
5. inspect only the R0.10 implementation/tests needed to confirm the boundary still matches reality;
6. activate/update this work order, then give Codex a compact instruction pointing back to repository docs.
