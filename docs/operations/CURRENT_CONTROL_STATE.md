# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-29
current_phase: R0.12
phase_state: STAGE_A_FINAL_HUMAN_GATE_FAILED_PATCH_ACTIVE
active_work_order: R0.12-STAGE-A-FINAL-CLOSURE-002
active_construction_branch: NONE
accepted_code_baseline: 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38
accepted_engineering_baseline: 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38
current_main_baseline: 3633bdeded19458a2572dfa3549c40f4eec27f0d
latest_human_gate_candidate: 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38
structural_progress_percent: 95
stage_a_completion_gate: HUMAN_FAIL_PATCH_REQUIRED
core_1_planning_product_gate: HUMAN_RUN_RECOVERED_AFTER_NETWORK_RESTART
core_2_editing_product_gate: HUMAN_FAIL_RENDER_AND_DESKTOP_PROCESS_DEFECTS
windows_release_delivery_gate: PATCH_AND_REPLACEMENT_RC_REQUIRED
codex_release: CLOSED
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Current accepted truth

The 0.1.0 installer built from:

80ab920b19c1ed1aebef4fa9b7eab05d6a509f38

passed automated Windows lifecycle engineering, but **failed the real ordinary-user Human Gate** on 2026-08-29.

Do not report Stage-A complete and do not continue distributing this installer as the final acceptance build.

## Human Gate observations

### Planning

The first Planning attempt was rejected by the factual-safety reviewer because the generated proposal implied portability/going-out suitability from only a 350 ml capacity fact. That rejection is expected safety behavior rather than a release defect.

After the machine restart and restored network conditions, the Product Owner reports that Planning generated successfully.

### Editing

The installed Full product reached real media analysis, public-music rights acquisition, edit decision, real-material resolution, EDL assembly, audio/subtitle preparation and render/review stages.

Material failures remain:

1. the ordinary GUI repeatedly flashes child terminal windows during media processing/rendering;
2. the final Editing run ended in rerender_same_edl instead of a deliverable PASS;
3. the user-facing correction message does not expose the underlying renderer diagnostic and can misleadingly imply that rendering itself completed successfully;
4. the current product does not visibly identify its installed version or provide an update-discovery path for already distributed installations.

## Code-level findings already established

- the packaged main GUI is windowed, but internal FFmpeg/ffprobe subprocess calls do not suppress Windows child console creation;
- multiple media/render/review adapters use ordinary subprocess.run / subprocess.Popen without a shared Windows no-console process policy;
- rerender_same_edl is emitted only for retryable renderer execution/output-verification failures;
- the Review contract allows one same-EDL repair attempt, but the current product flow does not actually execute that automatic retry;
- source-audio assembly currently assumes every grounded video selection has canonical source audio even though ingest metadata records whether an asset has audio channels; this must be reproduced and corrected if it is the observed FFmpeg failure;
- pyproject.toml and installer build inputs currently duplicate application version 0.1.0, while the GUI displays no version and there is no update manifest/check path.

## Required patch boundary

The next patch must remain bounded to final ordinary-user release blockers:

- suppress Windows console windows for child media/runtime processes without hiding diagnostics;
- preserve captured stdout/stderr and typed diagnostics;
- make same-EDL retry behavior executable and bounded as already defined by Review policy;
- expose the real renderer/QC diagnostic when Editing cannot deliver;
- correctly handle selected source clips that have no audio stream, if reproduction confirms the current unconditional source-audio mapping defect;
- establish one authoritative application version source and display the installed version in the desktop UI;
- add non-blocking update discovery suitable for a private source repository and already distributed Windows installers;
- build a replacement installer version greater than 0.1.0 and repeat automated lifecycle + ordinary-user Human Gate.

Structural progress remains **95%**. A replacement RC and successful Human Gate are required before 100%.

## Update-distribution boundary

The source repository is private, so ordinary users must not need GitHub repository credentials to discover updates.

The stable update path should use a public, source-free release metadata endpoint containing at minimum:

- version;
- publication timestamp;
- release notes URL/text;
- installer/download location or controlled distribution page;
- installer SHA-256;
- mandatory/recommended update flag.

The application should check this endpoint asynchronously and fail open when offline. Update-check failure must never block Planning or Editing.

Silent/background self-installation is not required for this patch.

## Deferred / non-blocking 1.0 items

- advanced source-speech separation/reconstruction;
- sentence-preserving dialogue editing;
- translated/bilingual subtitles;
- cross-language narration/TTS;
- Remote Reference URL;
- delta/Web Setup updater;
- exact UI-language override for a Brief written in another language.

## Release-management note

The current installer path uses Inno Setup 7.1.0. Its commercial-use licensing policy remains to be resolved before commercial distribution.
