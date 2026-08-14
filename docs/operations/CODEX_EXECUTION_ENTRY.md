# Codex Execution Entry

Purpose: enter the active construction state with the minimum safe model-visible context.

## Normal startup

```text
git status
git fetch
git switch main
git pull --ff-only
confirm clean working tree
```

Then run foreman. On this Windows host, use process-local bypass if required:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 foreman
```

Read `.private/codex_brief.md` and act on L0.

Do **not** automatically read `CURRENT_CONTROL_STATE.md`, `CURRENT_WORK_ORDER.md`, architecture documents, CAPs, ADRs or project history. Foreman may machine-parse them. Open secondary sources only when an L0 trigger or concrete implementation evidence requires them.

## Execution rules

- GitHub `main` is committed implementation truth; local state must be inspected before writing.
- Execute only the active bounded work order.
- Use targeted search before broad reading.
- Use toolbox/trigger routes when blocked; do not guess missing authority.
- Keep private media/models/cache/output untracked unless explicitly authorized.
- Run required focused checks and the repository Quality Gate.
- Commit/push bounded reusable changes and stop at the active gate.

## Interruption recovery

After a disconnect, inspect `git status` and `git diff`; resume unfinished work rather than replaying the original prompt.
