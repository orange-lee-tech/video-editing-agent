# Maintenance Micro-Tools

Small, non-authoritative tools for repetitive repository construction/maintenance work.

They are intentionally boring. They inspect state, generate local handoff context or wrap existing verification. They do **not** decide product policy, architecture or Human Gates.

## Repository doctor

```powershell
uv run python tools/maintenance/repo_doctor.py
```

Checks machine-verifiable governance invariants, including:

- required navigation/README/control-plane files exist;
- retired documents stay under `docs/archive/`;
- `CURRENT_CONTROL_STATE.md`, `CURRENT_WORK_ORDER.md` and `CURRENT_PHASE_STATUS.md` point to the same phase;
- an ACTIVE Work Order ID matches `active_work_order` in control state;
- accepted code baseline is a full commit SHA;
- structural progress remains within 0–100 and synchronized with live phase state;
- Stage-A progress cannot be 100 unless the Stage-A completion gate and both core Product Gates are `PASS`;
- documentation entry points route to the canonical live-state trio and Stage-A gate;
- local/private/cache/noise paths are not tracked.

The doctor prevents stale pointers and false completion claims. It does not decide whether a Product Probe deserves PASS; semantic/product acceptance remains a ChatGPT + Human Gate responsibility.

The same doctor runs automatically in `.github/workflows/repository-governance.yml` when relevant documentation/maintenance files change.

Use locally after governance/archive/navigation changes and before a handoff when repository structure changed materially.

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

Routes point into `docs/operations/CODEX_TOOLBOX.md` without copying target content. Contradictions remain blockers with a nonzero exit. Foreman never fetches, edits source/state, commits or pushes.

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

Dynamic Markdown should be minimized and machine-checked. Stable entry documents should route to live state rather than copy rapidly changing snapshots.