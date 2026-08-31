# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-31
current_phase: R0.13
phase_state: RELEASE_POLISH_ACTIVE
active_work_order: R0.13-RELEASE-POLISH-001
active_construction_branch: work/r013-release-polish
accepted_code_baseline: e59cab8475a615d29003c03497ddcdaf862476a6
accepted_engineering_baseline: 111b50f13d1b19670dfe0e0a68bfa2da00212a5f
current_main_baseline: 7ffbf2d3b27833003c6b9b9a74a7be6959cddd0f
latest_human_gate_candidate: 111b50f13d1b19670dfe0e0a68bfa2da00212a5f
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
4. verified component/file patch updates with rollback, while retaining the full Setup.exe as bootstrap/recovery fallback;
5. bilingual installer Software License and User Agreement with explicit interactive acceptance;
6. header consolidation so update checking lives inside Settings plus a sibling Declaration control;
7. visible product branding as `有岐` with slogan `创作有岐，表达有路`, while compatibility-sensitive internal identifiers remain stable.

## Release boundary

Final `1.0.0` packaging is not authorized while R0.13 is active.

No advanced creative capability work belongs in this phase.

Execution discipline: direct bounded repository edits are preferred for deterministic work; Codex is reserved for genuinely complex/local Windows iteration. The accepted Planning and Editing paths are protected invariants and any regression blocks R0.13 closure.

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


## Current R0.13 engineering candidate

Version `0.1.6`, exact source `111b50f13d1b19670dfe0e0a68bfa2da00212a5f`, completed Windows RC run `33379570088` with **SUCCESS**.

Installer SHA-256:

`f6a90b2a8b484806e893d0bbcc369adf5ced83425a14e887bc6f65954528796b`

This candidate supersedes the earlier `6a6bb6f` Human-review candidate after Product Owner feedback found three UI regressions: inaccessible profile Import / Export / Save / Delete actions in the fixed-height Settings dialog, premature developer-homepage exposure, and appearance selection that did not visibly apply on selection. The remediation preserves both form/API profile actions in a resizable scrollable Settings surface, replaces developer-homepage navigation with the temporary-closure notice, and applies Day / Comfort / Night preview immediately with cancel restore and persisted apply behavior.

Engineering verification is complete for the remediated candidate. R0.13 remains open only for Product Owner visual/interaction acceptance, including display-scaling review, before any final 1.0.0 authorization.
