# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-29
current_phase: R0.12
phase_state: STAGE_A_FINAL_INSTALLER_HUMAN_GATE
active_work_order: R0.12-STAGE-A-FINAL-CLOSURE-002
active_construction_branch: NONE
accepted_engineering_baseline: 7753e5bbee93ca743152a7e2319c3f6739faff60
current_main_baseline: bc413ff59da42e42cac3dc06b7ea2d6895613653
latest_human_gate_candidate: 7753e5bbee93ca743152a7e2319c3f6739faff60
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

The final 1.0 product source accepted for Windows release-candidate packaging is:

`7753e5bbee93ca743152a7e2319c3f6739faff60`.

That source includes the accepted Planning/Editing/UI repairs, including factual-review recovery, cross-language visual retrieval grounding, simplified configuration actions and 1.0 UI isolation of deferred capabilities.

Real Product Owner source-run evidence established:

- Chinese-speaking footage can complete visual-first automatic Editing;
- English-speaking footage can complete visual-first automatic Editing;
- the previous false missing-coverage defect was a cross-language lexical retrieval bug and is repaired;
- factual Planning review no longer allows unsupported bag-fit / one-hand-operability claims to escape;
- advanced speech continuity, translated/bilingual subtitles and cross-language narration/TTS are intentionally deferred to 2.0.

## Final Windows release candidate

Windows RC run #5 (`33140342038`) completed successfully for source SHA
`7753e5bbee93ca743152a7e2319c3f6739faff60`.

Final installer:

- file: `VideoEditingAgent-Setup-0.1.0.exe`;
- SHA-256: `9ba68f361f2d4c7881e1192b82e2fb3d750332d8844796829224a9dd1912033e`;
- size: 287,556,353 bytes;
- artifact: `VideoEditingAgent-Setup-7753e5bbee93ca743152a7e2319c3f6739faff60`;
- Inno Setup: 7.1.0, immutable release asset hash verified and Authenticode signer validated.

Automated Windows lifecycle evidence is PASS for:

- Planning-only install;
- Planning-only omission of Editing runtimes;
- installed Planning launcher;
- Planning-only → Full upgrade;
- Full Editing runtime presence;
- installed Full launcher;
- same-version repair;
- deferred 2.0 speech payload absence;
- external Workspace preservation through upgrade, repair and uninstall;
- uninstall removal of application-owned files.

Durable evidence:

`docs/validation/R0.12_WINDOWS_SETUP_RC_0.1.0.md`.

## Final gate boundary

Structural progress remains **95%** until the Product Owner performs the ordinary-user Human Gate on this exact Setup.exe.

The remaining gate is deliberately narrow:

1. install the exact RC through the normal wizard;
2. launch without repository/Python/uv knowledge;
3. confirm installed Planning is ordinary-user acceptable;
4. confirm representative installed Full visual-first Editing works;
5. confirm ordinary install/repair/uninstall behavior is acceptable.

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
