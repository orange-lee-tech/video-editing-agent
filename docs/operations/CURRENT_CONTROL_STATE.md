# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-31
current_phase: R0.13
phase_state: RELEASE_POLISH_ACTIVE
active_work_order: R0.13-RELEASE-POLISH-001
active_construction_branch: work/r013-release-polish
accepted_code_baseline: e59cab8475a615d29003c03497ddcdaf862476a6
accepted_engineering_baseline: e59cab8475a615d29003c03497ddcdaf862476a6
current_main_baseline: fa3b1b50cd9b0896dec7c6cacebbc66ea994c9d5
latest_human_gate_candidate: e59cab8475a615d29003c03497ddcdaf862476a6
structural_progress_percent: 100
stage_a_completion_gate: PASS
core_1_planning_product_gate: PASS
core_2_editing_product_gate: PASS
windows_release_delivery_gate: PASS
codex_release: CLOSED
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: RELEASE_ENGINEERING
writer: chatgpt
---

## Current accepted truth

Stage-A remains complete at **100%** with accepted core baseline:

`e59cab8475a615d29003c03497ddcdaf862476a6` / version `0.1.5`.

R0.13 is a bounded post-Stage-A release-engineering phase. It does not reopen Planning or Editing unless a material regression appears.

## Active R0.13 work

Work order:

`R0.13-RELEASE-POLISH-001`

Approved scope:

1. installer remaining-time estimate/countdown;
2. Windows DPI-aware typography and clearer Chinese text;
3. persisted Day / Comfort / Night appearance modes;
4. verified component/file patch updates with rollback, while retaining the full Setup.exe as bootstrap/recovery fallback.

## Release boundary

Final `1.0.0` packaging is not authorized while R0.13 is active.

No advanced creative capability work belongs in this phase.

## Required invariants

R0.13 changes must preserve:

- accepted Planning/Editing behavior;
- external Workspace/original-media safety;
- public update discovery;
- packaged H.264 encode verification;
- guided installer lifecycle;
- fail-open network/update checks;
- explicit user consent for applying an update.

Byte-level binary delta algorithms are out of scope; component/file replacement with cryptographic verification and rollback is the chosen 1.0 update strategy.
