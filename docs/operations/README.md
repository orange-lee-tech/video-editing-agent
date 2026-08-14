# Operations

Dynamic collaboration/execution state lives here. These files are intentionally small and change more often than product/architecture authority.

## Files

- `CHATGPT_GITHUB_CODEX_COLLABORATION.md` — stable role split and handoff protocol among user, ChatGPT, GitHub and Codex.
- `CODEX_EXECUTION_ENTRY.md` — minimal behavior/read-order for local Codex implementation.
- `CURRENT_WORK_ORDER.md` — the single active implementation boundary or `HANDOFF_READY` resume blueprint.

Related live phase state:

- `../roadmap/CURRENT_PHASE_STATUS.md`

## Work-state semantics

- `ACTIVE` means the current boundary may be executed.
- `HANDOFF_READY` means the project is deliberately ready for a new coordinating ChatGPT conversation to reobserve GitHub and activate/refresh the preserved boundary. It is **not** a lock.
- `PAUSED` means no implementation should proceed until the user changes that state.

Codex must never resurrect an obsolete work order from old chat history. ChatGPT owns work-order activation after observing current GitHub truth.

## Authority boundary

Operations documents coordinate work but cannot override:

`Product Constitution → Architecture Contract → Capability Specs → ADRs → Roadmap`

Do not store design essays, incident histories or phase closure evidence here; use the appropriate canonical directory instead.
