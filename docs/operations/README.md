# Operations

Dynamic collaboration/execution state lives here. These files change more often than product/architecture authority and are part of the repository control plane, not decorative documentation.

## Read order

For current execution state use:

1. `CURRENT_CONTROL_STATE.md` — machine-readable high-level live control state, active Work Order pointer, accepted baseline and Stage-A product gates.
2. `CURRENT_WORK_ORDER.md` — exact currently authorized implementation/evidence boundary.
3. `../roadmap/CURRENT_PHASE_STATUS.md` — human-readable live phase position and remaining terrain.
4. `CODEX_EXECUTION_ENTRY.md` / Foreman only when local Codex execution is actually released.

Stable supporting files:

- `CHATGPT_GITHUB_CODEX_COLLABORATION.md` — role split and handoff protocol among user, ChatGPT, GitHub and Codex.
- `CODEX_EXECUTION_ENTRY.md` — minimal local Codex startup/read-order.
- `CODEX_TOOLBOX.md` — bounded escalation/tool routes.
- `CONTROL_PLANE_ARCHITECTURE.md` — control-plane design.

## Live-state synchronization contract

The canonical dynamic trio is:

```text
docs/operations/CURRENT_CONTROL_STATE.md
docs/operations/CURRENT_WORK_ORDER.md
docs/roadmap/CURRENT_PHASE_STATUS.md
```

A phase/work-order transition is not complete merely because one Markdown file changed.

`tools/maintenance/repo_doctor.py` and `.github/workflows/repository-governance.yml` must machine-check the invariants that can be checked deterministically, including:

- live phase pointers agree;
- an ACTIVE Work Order matches `active_work_order` in control state;
- required live entry files exist and remain routed from documentation entry points;
- Stage-A structural progress cannot be 100 unless both core Product Gates and the Stage-A completion gate are PASS;
- private/cache/noise files remain untracked.

Human semantic review remains necessary for architecture/product truth; automation prevents stale pointers and false completion claims from silently becoming the baseline.

## Work-state semantics

- `ACTIVE` means the current boundary may be executed.
- `HANDOFF_READY` means the project is deliberately ready for a new coordinating ChatGPT conversation to reobserve GitHub and activate/refresh the preserved boundary. It is **not** a lock.
- `PAUSED` means no implementation should proceed until the user changes that state.
- `CLOSED — PASS` means the Work Order is historical/accepted and `active_work_order` must not still point to it.

Codex must never resurrect an obsolete Work Order from old chat history. ChatGPT owns Work Order activation after observing current GitHub truth.

## Stage-A completion rule

`../roadmap/STAGE_A_COMPLETION_GATE.md` is the stable 100% gate.

A visually polished UI, green Engineering Probe, hand-authored EditPlan/EDL, or CLI-only workflow cannot substitute for the two real user outcomes:

1. Planning core: real intent/reference → visible persisted ScriptPlan + usable ShootingPlan.
2. Editing core: selected local footage → actual automatic pipeline → final MP4.

## Authority boundary

Operations documents coordinate work but cannot override:

`Product Constitution → Architecture Contract → Capability Specs → ADRs → Roadmap`

Do not store design essays, incident histories or phase closure evidence here; use the appropriate canonical directory instead.