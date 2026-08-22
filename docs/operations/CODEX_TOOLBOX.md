# Codex Toolbox

Compact route index for bounded repository work. This file is not a default reading assignment;
open only the section selected by foreman or concrete evidence.

## Work tools

- Preflight current release + generate L0: `powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 preflight`.
- Locate symbols/files: `rg "pattern"` and `rg --files`.
- Inspect repository health: `powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 doctor`.
- Run focused tests: `uv run pytest <focused paths>`.
- Run the full local gate: `powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 verify`.
- Generate L0 only: `powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 foreman`.
- Generate a local handoff: `powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 handoff -Output .private/handoff.md`.

The full local gate includes repository doctor, Ruff format/check, mypy, pytest, import-linter,
build, `git diff --check` and launcher smoke. A dirty working tree is valid during pre-commit
verification; use `-RequireClean` only at a boundary that explicitly requires cleanliness.
`-SkipLauncherSmoke` is a diagnostic/headless escape hatch, not GUI acceptance evidence.

## Collaboration responsibility boundary

The repository uses four cooperating layers. Preserve this division to avoid wasting AI execution
capacity on the wrong task.

### ChatGPT: engineering control tower

Responsible for:

- product intent, architecture interpretation and scope decisions;
- current-state observation and work-order routing;
- selecting what should be done by ChatGPT, GitHub, PowerShell or Codex;
- low-risk deterministic repository maintenance;
- reviewing Codex evidence rather than accepting reports blindly;
- defining bounded implementation instructions.

Do not delegate pure architecture understanding, product-direction decisions or simple repository
maintenance to Codex merely because Codex can read code.

### Codex: local engineering executor

Use Codex for work that benefits from local execution loops:

- multi-file implementation;
- GUI changes;
- substantial refactors;
- debugging requiring runtime feedback;
- build/test/repair cycles.

Do not use Codex as the default project historian, architecture decision maker, or low-value
repository explorer. Read current control documents first and provide only bounded execution work.

### PowerShell: local evidence layer

Use PowerShell for:

- Windows workspace state;
- local runtime verification;
- build/test evidence;
- environment-specific checks.

### GitHub: long-term project memory

Use GitHub documents, commits, CI and status files as the durable source of project context. Avoid
repeatedly transferring large historical context through chat when it can be stored and routed here.

## Architecture/contract ambiguity

Stop guessing. Open only the CAP/ADR/contract section named by the active work order or the symbol's
ownership boundary. Escalate when two authorities materially conflict.

## Code-location uncertainty

Use targeted `rg`/`rg --files`, then open the smallest implementation and focused-test surface.
Do not broaden into repository history merely to find a symbol.

## Test/quality failure

Read the first focused failure and relevant code, repair the mechanism, rerun the focused check,
then run the canonical full Quality Gate. Do not weaken the gate.

## Git/repository-state issue

Stop writes. Inspect `git status --short --branch`, `git diff`, HEAD, branch and upstream. Preserve
user changes; use only non-destructive recovery unless broader authority is explicit.

## External/license/provider uncertainty

Fail closed. Open the smallest relevant provider/release/research evidence. Do not download,
bundle, attest rights, select a license or incur paid/API cost without authority.

## Destructive/high-risk operation

Resolve exact targets and stop for the required ChatGPT/User gate. Do not infer permission for
deletion, history rewrite, irreversible external writes or meaningful scope expansion.
