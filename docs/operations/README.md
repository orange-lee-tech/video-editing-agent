# Operations

Dynamic collaboration/execution state lives here. These files are intentionally small and change more often than product/architecture authority.

## Files

- `CODEX_EXECUTION_ENTRY.md` — stable minimal behavior/read-order for local Codex implementation.
- `CURRENT_WORK_ORDER.md` — the single active implementation boundary, or an explicit PAUSED state.

Related live phase state:

- `../roadmap/CURRENT_PHASE_STATUS.md`

## Pause semantics

If `CURRENT_WORK_ORDER.md` says `PAUSED` or `NO ACTIVE IMPLEMENTATION WORK`, agents must not infer an old work order from chat history, roadmap prose or historical validation files. Reobserve `origin/main` and wait for an explicit resumed work order.

## Authority boundary

Operations documents may coordinate work but cannot override:

`Product Constitution → Architecture Contract → Capability Specs → ADRs → Roadmap`

Do not store design essays, incident histories or phase closure evidence here; use the appropriate canonical directory instead.
