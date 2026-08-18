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
- `STAGE_A_UX_STABILIZATION_WAVE.md` — current bounded ordinary-user UX stabilization specification; it does not close Editing Product/Human Gate.
- `WINDOWS_DESKTOP_PACKAGING_READINESS.md` — operational preparation for a reproducible Windows desktop bundle/installer path; it is not a claim that release packaging is already approved.
- `WINDOWS_RUNTIME_DEPENDENCY_INVENTORY.md` — active packaging input that separates current mandatory runtime, gate-integration runtime, optional/advanced components and release/license unknowns.

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

## Packaging preparation boundary

Packaging work may prepare:

- private runtime/bundle layout;
- resource locator;
- release manifest;
- fresh-Windows smoke;
- installer/update strategy;

but it must not:

- smuggle unresolved-license binaries/models into distribution;
- move user-writable project/profile data into the install directory;
- make a successful installer substitute for Product/Human editing evidence;
- introduce a second composition path that bypasses the ordinary product runtime.

The runtime dependency inventory deliberately distinguishes “module exists in repository” from “must ship in the first installer”. Packaging may promote a dependency to mandatory only after the real ordinary product path proves it is required and its runtime/license closure is known.

## Authority boundary

Operations documents coordinate work but cannot override:

`Product Constitution → Architecture Contract → Capability Specs → ADRs → Roadmap`

Do not store broad product-design essays or phase closure evidence here; use the appropriate canonical directory. Operational release/readiness documents are appropriate only when they describe execution preparation rather than redefine product/architecture policy.
