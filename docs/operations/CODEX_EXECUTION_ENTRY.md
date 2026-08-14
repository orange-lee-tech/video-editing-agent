# Codex Execution Entry

Purpose: give Codex the shortest reliable path into the current construction state.

## Normal startup

```text
git status
git fetch
git switch main
git pull --ff-only
confirm clean working tree
```

Then read:

1. `docs/operations/CURRENT_CONTROL_STATE.md`
2. `docs/operations/CURRENT_WORK_ORDER.md`

If the foreman helper is available, run:

```powershell
powershell -File scripts/maintain.ps1 foreman
```

Then follow:

```text
.private/codex_brief.md
```

Read only the additional task-specific references listed by the active work order/brief.

## Expand the read set only when needed

Read Product Constitution / Architecture Contract / CAP / ADR / validation history beyond the listed references only if:

- the active work order explicitly requires it;
- the foreman reports a contradiction;
- implementation evidence conflicts with current control state;
- the task changes an architecture/product authority boundary.

Do not reread the entire project history for routine bounded work.

## Execution rules

- `main` is routine development branch.
- GitHub `main` is live committed implementation truth.
- During a complex Codex batch, Codex is the single writer for that implementation surface.
- Execute the active work order, not adjacent backlog items.
- Run the required focused tests and full Quality Gate named by the work order/repository scripts.
- Do not silently loosen acceptance criteria to make probes green.
- Keep private media, downloaded models, `.private/`, local outputs and caches untracked unless a work order explicitly says otherwise.
- Commit/push only reusable bounded changes.
- Stop at the work-order stop gate and report exact evidence.

## Network interruption recovery

If a session disconnects, do not restart the batch from the original prompt.

First inspect current:

```text
git status
git diff
```

Resume only unfinished implementation/verification.

## Bootstrap exception

If `foreman` is not implemented yet, `CURRENT_CONTROL_STATE.md` + `CURRENT_WORK_ORDER.md` are sufficient to execute the control-plane bootstrap work order.
