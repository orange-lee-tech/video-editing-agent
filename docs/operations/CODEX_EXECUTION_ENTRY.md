# Codex Execution Entry

**Purpose:** minimal dynamic entrypoint for local Codex implementation work.

## Read order

Before coding, read only what is needed in this order:

1. `docs/operations/CODEX_EXECUTION_ENTRY.md` — execution behavior.
2. `docs/roadmap/CURRENT_PHASE_STATUS.md` — current phase and completed/remaining boundaries.
3. `docs/operations/CURRENT_WORK_ORDER.md` — the single active implementation boundary or handoff blueprint.
4. Only the capability/implementation/tests referenced by the current work order.

At a new ChatGPT/Codex handoff, the coordinating ChatGPT should also read `CHATGPT_GITHUB_CODEX_COLLABORATION.md` once. Codex does not need to reread collaboration/history documents every run.

Do not reread the entire repository or historical validation/archive unless the active work order requires it.

## Work-state gate

- `ACTIVE` — execute the stated boundary.
- `HANDOFF_READY` — resumable blueprint. Codex does **not** self-activate it from stale chat/history; the coordinating ChatGPT reobserves `origin/main` and activates/refreshes it.
- `PAUSED` / `NO ACTIVE IMPLEMENTATION WORK` — make no code changes unless the user explicitly changes the work state.

HANDOFF_READY is not a product freeze and should not be treated as permanent blocking state.

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

## Maintenance micro-toolbox

Use these when they reduce repeated work; they are helpers, not mandatory ceremony:

```powershell
powershell -File scripts/maintain.ps1 doctor
powershell -File scripts/maintain.ps1 handoff -Output .private/handoff.md
powershell -File scripts/maintain.ps1 verify
```

- `doctor` is useful after navigation/archive/control-plane changes.
- `handoff` creates a **local, non-authoritative** snapshot for conversation transfer.
- `verify` delegates to the existing canonical full Quality Gate.

Do not create a new automation for a one-off task. Do not let maintenance tools become product/editorial authority.

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

Run the capability-specific live Engineering/Product Probe when required by `CURRENT_WORK_ORDER.md`.

If all required gates pass, make one coherent commit on `main` and push. If commit/push approval is the only blocker, preserve the verified working tree/staging and report it; do not redo implementation.

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
