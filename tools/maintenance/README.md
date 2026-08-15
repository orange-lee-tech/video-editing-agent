# Maintenance Micro-Tools

Small, non-authoritative tools for repetitive repository construction/maintenance work.

They are intentionally boring. They inspect state, generate local handoff context or wrap existing verification. They do **not** decide product policy, architecture or Human Gates.

## Repository doctor

```powershell
uv run python tools/maintenance/repo_doctor.py
```

Checks:

- required navigation/README/control-plane files exist;
- retired documents stay under `docs/archive/`;
- current phase and work-order phase pointers agree;
- local/private/cache/noise paths are not tracked.

Use after governance/archive/navigation changes and before a handoff when repository structure changed materially.

## Handoff snapshot

Print a snapshot:

```powershell
uv run python tools/maintenance/handoff_snapshot.py
```

Write one to an ignored local file:

```powershell
uv run python tools/maintenance/handoff_snapshot.py --output .private/handoff.md
```

The snapshot is orientation only. The receiving ChatGPT must still reobserve GitHub/main and CI.

## Foreman brief

```powershell
powershell -File scripts/maintain.ps1 foreman
```

Validates control pointers and local Git facts, then writes L0-only `.private/codex_brief.md`.
Secondary routes are exposed one at a time, for example:

```powershell
powershell -File scripts/maintain.ps1 foreman -Trigger quality
```

Routes point into `docs/operations/CODEX_TOOLBOX.md` without copying target content. Contradictions
remain blockers with a nonzero exit. Foreman never fetches, edits source/state, commits or pushes.

## Unified PowerShell wrapper

```powershell
powershell -File scripts/maintain.ps1 doctor
powershell -File scripts/maintain.ps1 foreman
powershell -File scripts/maintain.ps1 handoff -Output .private/handoff.md
powershell -File scripts/maintain.ps1 verify
```

`verify` delegates to the existing `scripts/verify.ps1`; there is no duplicate Quality Gate implementation.

## Design rule

Add another micro-tool only when a task is repeated, deterministic, cheap to verify and likely to prevent real mistakes. Do not automate subjective editorial judgment or create a second authority path.
