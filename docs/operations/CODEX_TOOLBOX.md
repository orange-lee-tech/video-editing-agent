# Codex Toolbox

Compact route index for bounded repository work. This file is not a default reading assignment;
open only the section selected by foreman or concrete evidence.

## Work tools

- Locate symbols/files: `rg "pattern"` and `rg --files`.
- Inspect repository health: `powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 doctor`.
- Run focused tests: `uv run pytest <focused paths>`.
- Run the full gate: `powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 verify`.
- Generate L0: `powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 foreman`.
- Generate a local handoff: `powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 handoff -Output .private/handoff.md`.

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
