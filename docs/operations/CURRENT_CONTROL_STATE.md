# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-30
current_phase: R0.12
phase_state: STAGE_A_FINAL_INSTALLER_HUMAN_GATE
active_work_order: R0.12-STAGE-A-FINAL-CLOSURE-002
active_construction_branch: NONE
accepted_code_baseline: eadbaa74c686f9fe526cb1d3eab64dde21c94d84
accepted_engineering_baseline: eadbaa74c686f9fe526cb1d3eab64dde21c94d84
current_main_baseline: 8bd4644fba34d4a97bf35cf14e7db67be2c6cb9f
latest_human_gate_candidate: eadbaa74c686f9fe526cb1d3eab64dde21c94d84
structural_progress_percent: 95
stage_a_completion_gate: OPEN_FINAL_ORDINARY_USER_HUMAN_GATE
core_1_planning_product_gate: HUMAN_PASS_ON_0_1_1_FINAL_0_1_2_REGRESSION_PENDING
core_2_editing_product_gate: FINAL_0_1_2_HUMAN_GATE_PENDING
windows_release_delivery_gate: ENGINEERING_PASS_FINAL_HUMAN_GATE_PENDING
codex_release: CLOSED
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Current accepted truth

The 0.1.1 ordinary-user Human Gate established that Planning works in the installed product, but representative Editing was interrupted during visual understanding by a retryable Gemini HTTP 503 high-demand response.

The visual-provider adapter already classified the condition correctly as `VisualProviderTransientError` and already retried transient errors, but the production default budget was too short for a real provider-demand spike: 3 attempts with only 0.3 / 0.6 second local delays when no provider RetryInfo was supplied.

That resilience defect is repaired in exact application source:

`eadbaa74c686f9fe526cb1d3eab64dde21c94d84`

Application version: **0.1.2**.

The replacement Windows RC completed engineering verification successfully:

- Windows Release Candidate run: `33265346143`;
- exact release source: `eadbaa74c686f9fe526cb1d3eab64dde21c94d84`;
- installer: `VideoEditingAgent-Setup-0.1.2.exe`;
- installer SHA-256: `32838e2748ae60f0059d461cccadbc5dc971ae3a9d2fc49922f3d9d8821f8c43`;
- private prerelease tag: `v0.1.2-rc-eadbaa7`;
- release asset ID: `535517911`;
- durable release asset: uploaded;
- installer lifecycle smoke: **PASS**.

The 0.1.1 installer remains useful historical engineering evidence but is superseded for final Stage-A acceptance.

## 0.1.2 transient-resilience patch

The replacement candidate changes only explicit transient visual-provider handling:

- default maximum attempts: 5;
- local backoff without provider guidance: 2 / 4 / 8 / 16 seconds;
- provider RetryInfo still overrides a shorter local delay;
- non-retryable provider/schema failures are not retried;
- exhausted retry budget preserves `VisualProviderTransientError` and original provider context;
- final error explicitly records that automatic retry budget was exhausted.

This patch does not change factual visual validation, edit selection, source provenance, Renderer semantics or Planning policy.

## Human evidence already retained

The Product Owner reports that installed Planning completed successfully on 0.1.1.

The 0.1.1 Editing attempt progressed through local media import and several successful Gemini visual-understanding calls before a later request returned retryable HTTP 503. Therefore the observed failure is not evidence of a local ingest/FFmpeg/Renderer regression.

## Remaining Stage-A gate

Test the exact 0.1.2 installer and confirm:

- v0.1.2 is visibly identifiable;
- representative Planning remains acceptable;
- representative real-footage Editing can pass through visual understanding and produce an approved final MP4;
- no terminal windows flash during ordinary media processing/rendering;
- temporary Gemini high-demand responses are tolerated by the bounded retry budget when they clear within the retry window;
- if provider demand persists beyond the bounded budget, the resulting diagnostic remains clear rather than hanging indefinitely;
- update discovery is understandable and non-blocking;
- Workspace/original media remain safe.

Structural progress intentionally remains **95%** until the final Human Gate passes.

## Stable update metadata

`https://orange-lee-tech.github.io/homepages/video-editing-agent/stable/latest.json`

currently advertises 0.1.2 and its exact installer SHA-256.

## Deferred / non-blocking 1.0 items

- advanced source-speech separation/reconstruction;
- sentence-preserving dialogue editing;
- translated/bilingual subtitles;
- cross-language narration/TTS;
- Remote Reference URL;
- delta/Web Setup updater;
- unrelated cosmetic redesign;
- broad task-resume/deduplicating Workspace checkpoint redesign.

## Release-management note

The installer uses Inno Setup 7.1.0. Commercial-use licensing policy remains to be resolved before commercial distribution; it does not block the current engineering RC/Human Gate.
