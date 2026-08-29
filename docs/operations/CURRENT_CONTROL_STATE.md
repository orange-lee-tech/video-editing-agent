# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-30
current_phase: R0.12
phase_state: STAGE_A_FINAL_INSTALLER_HUMAN_GATE
active_work_order: R0.12-STAGE-A-FINAL-CLOSURE-002
active_construction_branch: NONE
accepted_code_baseline: 71d7b7b46fa819f87aba785cefcc2bcf97ab7a46
accepted_engineering_baseline: 71d7b7b46fa819f87aba785cefcc2bcf97ab7a46
current_main_baseline: c8bbc88309bcb975987a3bce0bf6ad6f73889ede
latest_human_gate_candidate: 71d7b7b46fa819f87aba785cefcc2bcf97ab7a46
structural_progress_percent: 95
stage_a_completion_gate: OPEN_FINAL_ORDINARY_USER_HUMAN_GATE
core_1_planning_product_gate: FINAL_0_1_1_HUMAN_REGRESSION_PENDING
core_2_editing_product_gate: FINAL_0_1_1_HUMAN_GATE_PENDING
windows_release_delivery_gate: ENGINEERING_PASS_FINAL_HUMAN_GATE_PENDING
codex_release: CLOSED
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Current accepted truth

The installed-product defects found in the 0.1.0 Human Gate were repaired in application source:

`71d7b7b46fa819f87aba785cefcc2bcf97ab7a46`

Application version: **0.1.1**.

The replacement Windows RC completed engineering verification successfully:

- Windows Release Candidate run: `33262066851`;
- exact release source: `71d7b7b46fa819f87aba785cefcc2bcf97ab7a46`;
- installer: `VideoEditingAgent-Setup-0.1.1.exe`;
- installer SHA-256: `fc93f83b0543a1163a44796c7f430dcc68ff5f7a5c9112134b84f5dd15cae6ea`;
- private prerelease tag: `v0.1.1-rc-71d7b7b`;
- release asset ID: `535433505`;
- durable release asset: uploaded;
- installer lifecycle smoke: **PASS**.

The previous 0.1.0 installer remains historical evidence only and must not be used for final Stage-A acceptance.

## 0.1.1 repair boundary accepted by engineering

The replacement candidate includes:

- shared Windows no-console child-process policy for FFmpeg/ffprobe/media subprocesses while preserving diagnostics;
- one bounded same-EDL automatic rerender attempt;
- correct handling of selected video clips without source audio;
- actionable renderer/QC failure presentation;
- one authoritative user-facing application version, displayed as v0.1.1;
- asynchronous fail-open update discovery and explicit Check for Updates UI;
- public source-free stable update metadata at:
  `https://orange-lee-tech.github.io/homepages/video-editing-agent/stable/latest.json`.

## Automated Windows evidence

Run `33262066851` passed:

1. exact selected-source checkout and source recording;
2. pinned CPython 3.12.13 packaging environment;
3. Windows onedir build, static inspection, Doctor/runtime probe and packaged windowed-GUI smoke;
4. verified Inno Setup 7.1.0 acquisition;
5. guided Setup.exe compilation;
6. Planning-only installation and launcher assertions;
7. Planning-only → Full upgrade;
8. Full launcher assertions;
9. same-version Full repair;
10. uninstall and external Workspace preservation;
11. durable private prerelease publication.

The run's ordinary Actions artifact is supplementary. The GitHub Release asset is the durable candidate authority.

## Remaining Stage-A gate

Only the final ordinary-user Human Gate remains. Test this exact 0.1.1 installer and confirm:

- v0.1.1 is visibly identifiable;
- normal Editing does not flash terminal windows;
- representative Planning still succeeds without weakening factual safety;
- representative real-footage Editing produces an approved final MP4;
- update discovery is understandable and non-blocking;
- Workspace/original media remain safe.

Structural progress intentionally remains **95%** until that exact Human Gate passes. If it passes without a material blocker, move directly 95% → 100% and close R0.12.

## Deferred / non-blocking 1.0 items

- advanced source-speech separation/reconstruction;
- sentence-preserving dialogue editing;
- translated/bilingual subtitles;
- cross-language narration/TTS;
- Remote Reference URL;
- delta/Web Setup updater;
- unrelated cosmetic redesign.

## Release-management note

The installer uses Inno Setup 7.1.0. Commercial-use licensing policy remains to be resolved before commercial distribution; it does not block the current engineering RC/Human Gate.
