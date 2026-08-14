# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-14
current_phase: R0.12
phase_state: ACTIVATION_CONTROL_PLANE_HARDENING
active_work_order: CONTROL-PLANE-001
accepted_code_baseline: d06592560dbeb764666592effa00f7d5537715ef
previous_phase: R0.11
previous_phase_result: PASS_WITH_MINOR_DEFECT
writer: codex
---

## Purpose

This file is the one-page routing state for ChatGPT/Codex construction. It does not replace GitHub live truth, Product Constitution, Architecture Contract, CAPs, ADRs, or validation records.

Do not copy durable rules into prompts when they can be referenced from canonical documents.

## Live truth rule

Before writing, observe actual Git state. GitHub `main` remains implementation/integration truth.

`accepted_code_baseline` means the latest accepted implementation baseline, not necessarily the current docs-only HEAD.

## Current state

R0.11 Spatial Composition / Auto Reframe is closed for engineering/product development.

Human Gate:

- movement: `stabilized` preferred; natural; subject framing normal;
- occlusion/recovery: `stabilized` preferred; recovery accepted with minor visible micro-jump;
- classification: `PASS_WITH_MINOR_DEFECT`;
- the micro-jump is recorded, not an automatic retuning trigger.

Release note:

- MediaPipe runtime integration remains optional;
- EfficientDet Lite0 model remains external/uncommitted;
- exact redistribution/commercial model-artifact terms remain `RELEASE_LICENSE_PENDING`;
- this does not reopen R0.11, but a bundled release path must fail closed until the distribution decision is resolved.

## Current construction frontier

Before substantive R0.12 product implementation, compress the Codex control plane.

Target operating model:

1. `CURRENT_CONTROL_STATE.md` — current phase/work-order routing state.
2. `CURRENT_WORK_ORDER.md` — only the active bounded batch and its delta constraints.
3. durable Product/Architecture/CAP/ADR docs — read on demand, never recopied into every prompt.
4. `foreman` maintenance command — deterministic local preflight + concise Codex brief generator.
5. `.private/codex_brief.md` — generated local runtime brief; never committed.

## Default Codex read set

Always:

1. `docs/operations/CURRENT_CONTROL_STATE.md`
2. `docs/operations/CURRENT_WORK_ORDER.md`

Then only the task-specific files explicitly listed by the work order.

Do **not** reread the full project history or every architecture document unless:

- the work order requests it;
- the foreman detects a contradiction;
- implementation evidence conflicts with the current control state.

## Current gate

Execute `CONTROL-PLANE-001` only.

No R0.12 product implementation until that control-plane batch is green and reviewed.
