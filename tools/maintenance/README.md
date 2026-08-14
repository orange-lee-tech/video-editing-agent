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

Validates the current control state/work-order pointers and local Git facts, then writes the
concise, deterministic `.private/codex_brief.md`. Contradictions are recorded as blockers and
return a nonzero exit code. The helper only inspects state; it never fetches, edits product source,
changes control status, commits or pushes.

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
