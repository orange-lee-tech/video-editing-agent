# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-29
current_phase: R0.12
phase_state: STAGE_A_FINAL_INSTALLER_HUMAN_GATE
active_work_order: R0.12-STAGE-A-FINAL-CLOSURE-002
active_construction_branch: NONE
accepted_code_baseline: 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38
accepted_engineering_baseline: 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38
current_main_baseline: 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38
latest_human_gate_candidate: 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38
structural_progress_percent: 95
stage_a_completion_gate: OPEN_FINAL_ORDINARY_USER_HUMAN_GATE
core_1_planning_product_gate: FINAL_INSTALLER_HUMAN_GATE_PENDING
core_2_editing_product_gate: ACCEPTED_SOURCE_FINAL_INSTALLER_HUMAN_GATE_PENDING
windows_release_delivery_gate: ENGINEERING_PASS_FINAL_HUMAN_GATE_PENDING
codex_release: CLOSED
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Current accepted truth

The accepted post-Human-Gate repaired 1.0 source is:

`80ab920b19c1ed1aebef4fa9b7eab05d6a509f38`.

This source contains the final ordinary-user desktop/release repairs discovered after the earlier installer candidate, including:

- true windowed GUI executable separated from the console diagnostics CLI;
- installer pre-initialization defect removal;
- packaged GUI smoke that waits for real process completion;
- editable forms during background work from immutable task snapshots;
- localized task-local AI token usage telemetry;
- review-blocked rendered output retained and clearly labelled as a candidate rather than final output;
- clearer localized failure/correction presentation;
- public-music candidate naming during rights checks;
- mouse-wheel scrolling on the active product page.

Ordinary repository CI for this source is green.

## Final Windows release candidate

Windows Release Candidate run `33243959576` completed successfully for exact source SHA:

`80ab920b19c1ed1aebef4fa9b7eab05d6a509f38`.

Final installer:

- file: `VideoEditingAgent-Setup-0.1.0.exe`;
- SHA-256: `15978b647dec198996b747ea41fdb77fce61c8fe59261cd983c26ae0c74e34da`;
- artifact: `VideoEditingAgent-Setup-80ab920b19c1ed1aebef4fa9b7eab05d6a509f38`;
- artifact ID: `9712373668`;
- artifact ZIP SHA-256: `973487969900b5f52a76b4e76aa216cba29ae955a24e0576937825838c9340da`;
- Inno Setup: 7.1.0, immutable release asset hash verified and Authenticode signer validated.

Automated Windows lifecycle evidence is PASS for:

- exact source checkout;
- pinned packaging environment;
- staged package inspection;
- packaged Doctor/runtime probe;
- windowed GUI packaged smoke;
- guided Setup.exe compilation;
- Planning-only install;
- Planning-only → Full upgrade;
- Full installed launcher;
- same-version repair;
- deferred 2.0 payload exclusion;
- external Workspace preservation;
- uninstall removal of application-owned files.

The previous `7753e5b...` RC remains historical engineering evidence only and is superseded for final acceptance.

## Final gate boundary

Structural progress remains **95%** until the Product Owner performs the ordinary-user Human Gate on this exact replacement Setup.exe.

The remaining gate is deliberately narrow:

1. install the exact `80ab920...` RC through the normal wizard;
2. launch without repository/Python/uv knowledge;
3. confirm installed Planning is ordinary-user acceptable;
4. confirm representative installed Full visual-first Editing works;
5. confirm the post-Human-Gate desktop repairs are materially acceptable;
6. confirm ordinary uninstall behavior and Workspace/original-media preservation.

If that Human Gate passes, Stage-A may move directly from 95% to 100%. Do not invent intermediate percentages.

## Deferred / non-blocking 1.0 items

- source-speech separation/reconstruction;
- sentence-preserving dialogue editing;
- translated/bilingual subtitles;
- cross-language narration/TTS;
- Remote Reference URL;
- Web Setup / delta updater;
- exact UI-language override for a Brief written in another language.

## Release-management note

The RC uses Inno Setup 7.1.0. Its commercial-use licensing policy must be resolved before commercial distribution. This does not invalidate the engineering RC or final Human Gate.
