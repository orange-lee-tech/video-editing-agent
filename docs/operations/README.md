# Operations

**Last updated:** 2026-08-21

Dynamic collaboration/execution state lives here. These files change more often than product/architecture authority and are part of the repository control plane, not decorative documentation.

## Read order

For current execution state use:

1. `../DOCUMENT_REGISTRY.json` — compact repository/document map and attention classes.
2. `CURRENT_CONTROL_STATE.md` — machine-readable high-level live control state, accepted baseline and Stage-A gates.
3. `CURRENT_WORK_ORDER.md` — exact currently authorized implementation/evidence boundary.
4. `../roadmap/CURRENT_PHASE_STATUS.md` — human-readable live phase position and remaining terrain.
5. `CODEX_EXECUTION_ENTRY.md` only when local Codex execution is actually released.

Stable supporting files:

- `DOCUMENT_CONTROL_POLICY.md` — update-date, lifecycle, placement, archive and registry rules.
- `CHATGPT_GITHUB_CODEX_COLLABORATION.md` — role split and handoff protocol.
- `CODEX_EXECUTION_ENTRY.md` — minimal local Codex startup/read-order.
- `CODEX_TOOLBOX.md` — bounded escalation/tool routes.
- `CONTROL_PLANE_ARCHITECTURE.md` — control-plane design.
- `WINDOWS_DESKTOP_PACKAGING_READINESS.md` — Windows packaging/release-readiness boundary.
- `WINDOWS_RUNTIME_DEPENDENCY_INVENTORY.md` — active runtime/component packaging inventory.

Completed/superseded wave notes must not remain active entry points merely because they were once useful. Preserve meaningful closure evidence in `../validation/` or `../logs/`; archive only when the semantic archive rule is met.

## Live-state synchronization contract

The canonical dynamic trio is:

```text
docs/operations/CURRENT_CONTROL_STATE.md
docs/operations/CURRENT_WORK_ORDER.md
docs/roadmap/CURRENT_PHASE_STATUS.md
```

A phase/work-order transition is not complete merely because one Markdown file changed.

`tools/maintenance/repo_doctor.py` and `.github/workflows/repository-governance.yml` machine-check deterministically enforceable invariants, including:

- live phase pointers agree;
- an ACTIVE Work Order matches `active_work_order` in control state;
- required entry files exist and remain routed;
- Stage-A structural progress cannot be 100 unless both core Product Gates and the completion gate are PASS;
- private/cache/noise files remain untracked;
- document registry/attention governance remains present.

`tools/maintenance/document_registry.py` and `.github/workflows/document-registry.yml` generate the exhaustive tracked-document inventory without requiring agents to recursively browse the repository.

Human semantic review remains necessary for architecture/product truth; automation prevents stale pointers and false completion claims from silently becoming baseline.

## Work-state semantics

- `ACTIVE` — current boundary may be executed.
- `HANDOFF_READY` — ready for a new coordinating ChatGPT conversation to reobserve GitHub and activate/refresh the boundary; not a lock.
- `PAUSED` — no implementation should proceed until the user changes that state.
- `CLOSED — PASS` — historical/accepted; `active_work_order` must not still point to it.

Codex must never resurrect an obsolete Work Order from old chat history. ChatGPT owns Work Order activation after observing current GitHub truth.

## Attention rule

Root `AGENTS.md` is binding for agent navigation. In particular, `docs/archive/**`, `.private/**`, `.tools/**`, `.uv-cache*/**`, `.venv/**`, `build/**` and `dist/**` are default-excluded from ordinary discovery.

Archive is opened only for a concrete historical/provenance, backward-compatibility or legal need.

## Stage-A completion rule

`../roadmap/STAGE_A_COMPLETION_GATE.md` is the stable 100% gate.

A visually polished UI, green Engineering Probe, hand-authored EditPlan/EDL, Python wheel/sdist, or CLI-only workflow cannot substitute for the real user outcomes and deployment floor.

## Packaging boundary

Packaging work may implement:

- private/distributable runtime layout;
- thin bootstrap and resource/runtime locator;
- release/runtime manifest;
- fresh-Windows smoke;
- installer/update strategy after the onedir proof.

It must not:

- smuggle unresolved-license binaries/models into distribution;
- move user-writable project/profile data into the install directory;
- make a successful package substitute for Product/Human evidence;
- introduce a second composition path that bypasses the ordinary product runtime;
- hard-wire a provider/model/runtime into Domain authority.

## Authority boundary

Operations documents coordinate work but cannot override:

`Product Constitution → Architecture Contract → Capability Specs → ADRs → Roadmap`

Do not store broad product-design essays here. Operational release/readiness documents are appropriate only when they coordinate execution rather than redefine product/architecture policy.
