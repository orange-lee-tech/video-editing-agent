# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-29
current_phase: R0.12
phase_state: STAGE_A_REPLACEMENT_INSTALLER_RC_REQUIRED
active_work_order: R0.12-STAGE-A-FINAL-CLOSURE-002
active_construction_branch: NONE
accepted_code_baseline: 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38
accepted_engineering_baseline: 7753e5bbee93ca743152a7e2319c3f6739faff60
current_main_baseline: 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38
latest_human_gate_candidate: 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38
structural_progress_percent: 95
stage_a_completion_gate: OPEN_REPLACEMENT_INSTALLER_RC_AND_FINAL_HUMAN_GATE
core_1_planning_product_gate: POST_HUMAN_GATE_SOURCE_REPAIR_ACCEPTED_INSTALLER_PENDING
core_2_editing_product_gate: POST_HUMAN_GATE_SOURCE_REPAIR_ACCEPTED_INSTALLER_PENDING
windows_release_delivery_gate: REPLACEMENT_RC_REQUIRED
codex_release: CLOSED
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Current accepted truth

The previous automated Windows RC was built from:

`7753e5bbee93ca743152a7e2319c3f6739faff60`.

That installer passed its automated lifecycle, but the subsequent ordinary-user desktop Human Gate exposed material usability/packaging defects. Those defects have now been repaired on `main`.

The current accepted source candidate is:

`80ab920b19c1ed1aebef4fa9b7eab05d6a509f38`.

Ordinary repository CI for this source is green. The latest source repairs include:

- split windowed GUI and console diagnostics executable;
- installer pre-initialization defect removal;
- packaged GUI smoke that waits for real process completion;
- editable forms during background work from immutable task snapshots;
- localized task-local AI token usage telemetry;
- review-blocked rendered output retained and clearly labelled as a candidate rather than final output;
- clearer localized failure/correction presentation;
- public-music candidate naming during rights checks;
- mouse-wheel scrolling on the active product page.

## Replacement Windows release candidate required

The old Setup.exe hash

`9ba68f361f2d4c7881e1192b82e2fb3d750332d8844796829224a9dd1912033e`

belongs to the superseded `7753e5b...` source and must **not** be used for final Stage-A acceptance.

The next required engineering action is a manual `Windows Release Candidate` workflow run using exact source ref:

`80ab920b19c1ed1aebef4fa9b7eab05d6a509f38`.

The workflow must again pass staging/package smoke plus install/upgrade/repair/uninstall lifecycle checks and upload a new SHA-addressed Setup.exe artifact.

## Final gate boundary

Structural progress remains **95%**.

If the replacement Setup.exe built from `80ab920...` passes automated Windows lifecycle verification, the Product Owner should perform one final ordinary-user install/run check on that exact artifact. Only then may Stage-A move directly from 95% to 100%.

Do not invent intermediate percentages.

## Deferred / non-blocking 1.0 items

- source-speech separation/reconstruction;
- sentence-preserving dialogue editing;
- translated/bilingual subtitles;
- cross-language narration/TTS;
- Remote Reference URL;
- Web Setup / delta updater;
- exact UI-language override for a Brief written in another language.

## Release-management note

The Windows RC path currently uses Inno Setup 7.1.0. Its commercial-use licensing policy must be resolved before commercial distribution. This does not invalidate engineering/Human Gate work.
