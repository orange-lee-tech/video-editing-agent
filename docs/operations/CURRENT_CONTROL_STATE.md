# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-26
current_phase: R0.12
phase_state: STAGE_A_FINAL_SOURCE_CONSOLIDATION_AND_INSTALLER
active_work_order: R0.12-STAGE-A-FINAL-CLOSURE-002
active_construction_branch: NONE
accepted_engineering_baseline: c2c959239cf8842388ac661777c19f20f64a6a90
current_main_baseline: 153a7686aef3700c2a992542884a33dc135225cc
latest_human_gate_candidate: 153a7686aef3700c2a992542884a33dc135225cc
structural_progress_percent: 95
stage_a_completion_gate: OPEN
core_1_planning_product_gate: OPEN_QUALITY_HARDENING_REQUIRED
core_2_editing_product_gate: LOCAL_VISUAL_FIRST_PASS_PENDING_ACCEPTED_SHA
windows_release_delivery_gate: OPEN_SETUP_EXE_REQUIRED
codex_release: CLOSED_PENDING_LOCAL_PATCH_ACCEPTANCE
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Accepted engineering foundation

The accepted runtime/packaging foundation remains PR #20 at:

`c2c959239cf8842388ac661777c19f20f64a6a90`.

It proved the exact engineering runtime inventory and packaged execution machinery, including:

- LGPL-only FFmpeg/ffprobe 8.1;
- `transnetv2-pytorch==1.0.5` + `torch==2.13.0+cpu` + reviewed weights;
- `faster-whisper==1.2.1` + CTranslate2/PyAV + pinned local model as an engineering-proven speech component;
- exact CPython 3.12.13 packaging baseline;
- runtime manifest/NOTICE/hash evidence, Doctor, real TransNet/ASR probes, GUI launcher and external Workspace smoke.

Current remote main is:

`153a7686aef3700c2a992542884a33dc135225cc`.

The latest Human Gate executed a focused uncommitted local repair based on that SHA. Because that repair is not yet an accepted GitHub commit, the front-matter candidate remains anchored to its remote base SHA and the successful local observations below must not be mistaken for accepted-main proof.

## Latest Human Gate truth

### Planning

The previous factual failure is mechanically repaired in the focused local candidate: the 350 ml scenario completed without unsupported bag-fit / one-hand-operability claims escaping semantic review.

The Product Owner nevertheless rejected release quality. The plan was too sparse and repetitive, with generic hook language, duplicate fact copy, static visual guidance and weak role-specific shooting coverage. Planning therefore remains OPEN for quality hardening while factual safety stays non-negotiable.

### Editing

Real local Human Gate runs completed automatic visual-first Editing for both Chinese-speaking and English-speaking footage after a focused cross-language retrieval repair. This locally demonstrates the intended visual chain:

`local footage → visual understanding → Director → Resolver → EDL → Renderer/Review → final output`.

The previously observed false missing-coverage failure was caused by a language mismatch between footage evidence and a purely lexical internal retrieval query. The focused repair prevents Director retrieval fields from silently translating away from the evidence language.

This local success does not become accepted main truth until the dirty local work is preserved, verified, committed, pushed and passed through normal CI.

### Speech / multilingual voice production scope

The Product Owner decided on 2026-08-26 that speech-continuity reconstruction requires a future dual-track audio/video design and must not distort 1.0 visual editing authority.

Therefore source-speech separation/reconstruction, sentence-preserving dialogue editing, translated/bilingual subtitles and cross-language narration/TTS are deferred to 2.0. Unfinished controls must be hidden in 1.0.

The previously proven speech runtime remains useful future engineering evidence but is no longer a default 1.0 release payload requirement.

### Provider quota behavior

A real English run hit Gemini HTTP 429 with an explicit retry delay and then succeeded when repeated later. The transport already classifies that condition as transient. The final source consolidation should consume provider-directed bounded wait/retry information rather than immediately failing the whole ordinary-user task on the first retryable quota response.

## Final source consolidation boundary

Before installer freeze, preserve the current local repair and complete only the remaining coherent 1.0 source set:

- Planning quality hardening without weakening factual review;
- direct independent configuration actions instead of select-scope-then-import UI;
- hide unfinished/deferred speech/translated-subtitle/TTS interfaces;
- bounded provider quota/wait UX;
- retain visual-first Editing semantics and user-local source authority.

Do not reopen 2.0 audio reconstruction, Remote Reference URL or unrelated architecture work.

## Windows release delivery gate

The Product Owner has explicitly rejected raw ZIP/onedir extraction as the normal release experience. Stage-A / 1.0 release closure requires a guided Windows `Setup.exe` path with application-owned runtime management.

The release design must support, at minimum:

- normal install and uninstall without repository/Python/uv/Git knowledge;
- upgrade/repair of application-owned components;
- license/agreement presentation where applicable;
- user-selectable desktop shortcut;
- install-complete option to launch the application;
- safe handling of existing application-owned runtime/component conflicts;
- Project Workspace, Profiles and user originals remaining outside the install tree and surviving uninstall/upgrade;
- capability-oriented delivery so Core/Planning does not have to acquire Editing runtime components when they are not needed.

For 1.0 the default release component model is now:

- Core App / Planning;
- Media Runtime (FFmpeg/ffprobe);
- Scene Detection Runtime (TransNet/CPU Torch/weights).

Speech Runtime is deferred from the default 1.0 payload with the advanced speech line.

## Final gate boundary

Structural progress remains **95%**. Stage-A 100% is forbidden until all of the following are true:

1. Planning-only passes factual review and the Product Owner's ordinary-user quality bar;
2. the focused visual-first Editing repair exists on an accepted green GitHub SHA and real Chinese/English footage remains usable;
3. Combined semantics remain valid;
4. 1.0 hides unfinished/deferred interfaces and keeps originals, credentials and Workspace ownership protected;
5. provider-directed transient waits are bounded and understandable;
6. normal Windows delivery is a tested guided `Setup.exe` install/upgrade-or-repair/uninstall path rather than a raw large ZIP;
7. final evidence records the exact release candidate and Human observations.
