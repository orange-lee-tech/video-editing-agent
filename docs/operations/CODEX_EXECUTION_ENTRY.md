# Codex Execution Entry

**Purpose:** minimal dynamic entrypoint for local Codex implementation work.

## Read order

Before coding, read only what is needed in this order:

1. `docs/operations/CODEX_EXECUTION_ENTRY.md` — execution behavior.
2. `docs/roadmap/CURRENT_PHASE_STATUS.md` — current phase and completed/remaining boundaries.
3. `docs/operations/CURRENT_WORK_ORDER.md` — the single active implementation boundary and acceptance gates.
4. Only the capability/implementation/tests referenced by the current work order.

Do not reread the entire repository or historical validation archive unless the active work order requires it.

## Pause gate

If `CURRENT_WORK_ORDER.md` says `PAUSED`, `NO ACTIVE IMPLEMENTATION WORK`, or otherwise contains no active implementation boundary, **make no code changes and do not resurrect a previous work order**. Report the paused state and stop.

## Execution behavior

- Reobserve local/remote state first: clean tree, `main`, fetch, fast-forward only.
- Treat current `origin/main` as implementation truth.
- Work toward the **full current work-order boundary**, not the smallest imaginable subtask.
- Make routine local engineering decisions independently when they preserve frozen architecture and acceptance criteria.
- Do not stop for naming, file placement, obvious test construction, small refactors, deterministic threshold plumbing, or other reversible low-risk choices. Choose the most consistent existing pattern and continue.
- Stop only for a material architecture conflict, destructive/data-loss risk, unavailable required external dependency/runtime, paid action not already authorized, or evidence that the requested mechanism is invalid.
- When a mechanism fails, diagnose and repair the mechanism before weakening the acceptance gate.
- Keep providers behind ports/owners; model/provider proposals never gain Domain/editorial authority.
- Exact source time remains rational `MediaTime` / `MediaTimeRange`.
- Do not leap beyond the current Roadmap phase or beyond the active work-order completion boundary.

## Verification and commit

For code-bearing batches, unless the work order explicitly narrows this:

```text
uv sync --frozen
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
uv run lint-imports
uv build
git diff --check
```

Run the capability-specific live Engineering Probe when required by `CURRENT_WORK_ORDER.md`.

If all required gates pass, make one coherent commit on `main` and push. If commit/push approval is the only blocker, preserve the verified working tree/staging and report it; do not redo the implementation.

## Reporting

Keep the final report short:

- starting / ending HEAD;
- changed files and commit/push state;
- named acceptance gates with PASS/FAIL;
- material repairs made during the batch;
- remaining risks;
- classification.

Do not repeat architecture background already present in repository docs.

## Dynamic maintenance

This file and `CURRENT_WORK_ORDER.md` are operational policy/state, not product/architecture authority. ChatGPT may update them as collaboration practice and active work change. Product Constitution, Architecture Contract, capability specs and Roadmap remain higher authority.
