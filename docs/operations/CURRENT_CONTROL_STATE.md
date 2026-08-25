# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-25
current_phase: R0.12
phase_state: STAGE_A_HUMAN_GATE_REPAIR_ACTIVE
active_work_order: R0.12-STAGE-A-FINAL-CLOSURE-002
active_construction_branch: NONE
accepted_engineering_baseline: c2c959239cf8842388ac661777c19f20f64a6a90
current_main_baseline: 1015096fc4c5b2b9138e98cbe713fc4cc1770c07
latest_human_gate_candidate: 1015096fc4c5b2b9138e98cbe713fc4cc1770c07
structural_progress_percent: 95
stage_a_completion_gate: OPEN
core_1_planning_product_gate: REOPENED_UNSUPPORTED_CLAIM_REPAIR_REQUIRED
core_2_editing_product_gate: REOPENED_DIRECTOR_RESOLVER_GROUNDING_REQUIRED
windows_release_delivery_gate: OPEN_SETUP_EXE_REQUIRED
codex_release: CLOSED_PENDING_FOCUSED_LOCAL_DIAGNOSTIC
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Accepted engineering foundation

The accepted runtime/packaging foundation remains PR #20 at:

`c2c959239cf8842388ac661777c19f20f64a6a90`.

It proves the exact application-owned Windows runtime inventory and packaged execution machinery, including:

- LGPL-only FFmpeg/ffprobe 8.1;
- `transnetv2-pytorch==1.0.5` + `torch==2.13.0+cpu` + package-owned weights;
- `faster-whisper==1.2.1` + CTranslate2/PyAV + pinned local model, CPU/int8/local-files-only;
- exact CPython 3.12.13 packaging baseline;
- runtime manifest/NOTICE/hash evidence, Doctor, real TransNet/ASR probes, GUI launcher and external Workspace smoke.

PR #21 merged at current main:

`1015096fc4c5b2b9138e98cbe713fc4cc1770c07`.

It added one bounded Resolver -> Director EditPlan recovery and improved Planning proposal repair without weakening commercial-fact safety. Main CI and the Windows packaging candidate for this SHA passed.

## Latest Human Gate truth

The 2026-08-25 Product Owner run on the exact `1015096...` candidate reopened two product gates:

1. **Planning-only FAIL.** After bounded repair, Script generation still introduced unsupported fit/operability implications (for example fitting in a bag or being held in one hand) that were not supported by the authoritative fact set. The semantic reviewer correctly vetoed the proposal. Planning must therefore not remain marked PASS.
2. **Editing-only FAIL.** The new bounded recovery executed as designed, but the revised EditPlan still requested multiple semantic beats that the real local footage could not ground. The flow correctly stopped before EDL/render instead of fabricating or substituting public visuals. The next repair must be grounded in the persisted shot-analysis/EditPlan evidence, not prompt guessing.

The bounded recovery mechanism itself is therefore mechanically proven; the remaining defect is Director/Resolver grounding quality and recovery policy.

Ordinary no-speech Editing evidence, Workspace separation, credential protection and runtime packaging evidence remain valid unless a later regression disproves them.

## Engineering-loop correction

Human Gate repair iterations are now **patch-first and evidence-first**:

- do not rebuild or ask the Product Owner to download the ~769 MB compressed / ~1.88 GB extracted onedir artifact after every small source repair;
- collect focused local evidence from the external Workspace (`project.sqlite3`, logs and only other narrowly requested state), keeping private media outside GitHub;
- investigate the actual persisted Brief / shot analyses / EditPlan revisions / resolver evidence before changing Editing behavior;
- use focused patches plus local repository tests and local GUI/product runs for repair iterations;
- run ordinary CI on code changes, but reserve the full Windows packaging candidate for an explicit release-candidate checkpoint;
- run the final ordinary-user Human Gate only after the repair set and Windows installer delivery are stable.

A developer terminal is allowed for this engineering feedback loop. It remains forbidden as a requirement of the ordinary-user product path.

## Windows release delivery gate

The Product Owner has explicitly rejected raw ZIP/onedir extraction as the normal release experience. Stage-A / 1.0 release closure now requires a guided Windows `Setup.exe` path with application-owned runtime management.

The release design must support, at minimum:

- normal install and uninstall without repository/Python/uv/Git knowledge;
- upgrade/repair of application-owned components;
- license/agreement presentation where applicable;
- user-selectable desktop shortcut;
- install-complete option to launch the application;
- clear handling of existing application-owned runtime/component conflicts, with consent before destructive replacement/reconfiguration;
- Project Workspace and user originals remaining outside the install tree and surviving uninstall/upgrade;
- componentized delivery so Planning-only does not have to acquire every heavy Editing/speech runtime when it is not needed.

Inno Setup, NSIS, Velopack and bootstrapper approaches are implementation references, not product authority. Do not reinvent installer mechanics that established tooling already provides.

## Final gate boundary

Structural progress remains **95%**. Stage-A 100% is forbidden until all of the following are true:

1. Planning-only passes ordinary inputs without fabricating unsupported commercial facts;
2. Editing-only can adapt to real available local footage or fail with an honest, useful missing-coverage explanation, and the retained clear-speech path reaches final MP4 with original voice + trusted subtitles;
3. Combined semantics remain valid;
4. originals, credentials and Workspace ownership remain protected;
5. the normal Windows delivery is a tested guided `Setup.exe` install/upgrade/uninstall path rather than a raw large ZIP;
6. final evidence records the exact release candidate and Human observations.
