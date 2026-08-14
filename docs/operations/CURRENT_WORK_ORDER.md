# Current Work Order

**ID:** `CONTROL-PLANE-001`  
**Status:** ACTIVE  
**Owner/writer:** Codex  
**Purpose:** Compress Codex startup/control instructions before R0.12 product construction.

## Objective

Create a deterministic "foreman" helper that turns current repository state + current control documents into one concise local Codex briefing.

The helper must reduce repeated prompt text without becoming a new product/architecture authority.

## Read

1. `docs/operations/CURRENT_CONTROL_STATE.md`
2. `docs/operations/CODEX_EXECUTION_ENTRY.md`
3. `docs/operations/CHATGPT_GITHUB_CODEX_COLLABORATION.md`
4. `tools/maintenance/repo_doctor.py`
5. `tools/maintenance/handoff_snapshot.py`
6. `scripts/maintain.ps1`

Read other files only if needed to implement/test this work order.

## Allowed scope

Preferred implementation surface:

- `tools/maintenance/foreman.py` (new, if this is the cleanest shape);
- `scripts/maintain.ps1`;
- existing maintenance helpers when reuse is materially cleaner than duplication;
- focused tests for the maintenance/control-plane behavior;
- concise operations docs needed to make the entry flow unambiguous.

Do not touch product implementation under `src/video_editing_agent/` except if an import/test fixture genuinely requires a mechanical change; otherwise stop and report.

## Required behavior

A command equivalent to:

```powershell
powershell -File scripts/maintain.ps1 foreman
```

must:

1. verify local repository basics needed for a safe Codex batch (repository, branch, status, HEAD, upstream/fetch state when available);
2. read `CURRENT_CONTROL_STATE.md` and `CURRENT_WORK_ORDER.md`;
3. validate obvious control contradictions (phase/work-order mismatch, missing referenced control files, malformed required metadata);
4. generate `.private/codex_brief.md`;
5. keep the generated brief concise and task-oriented;
6. list only the task-specific read set from the active work order, plus the two current control files;
7. surface stop/block reasons clearly instead of guessing;
8. never modify product source or Git state as part of brief generation.

The generated brief should include at minimum:

- active phase/state;
- active work-order ID;
- accepted implementation baseline;
- actual local HEAD/branch/cleanliness;
- work-order objective;
- allowed scope;
- forbidden scope;
- required read set;
- validation/stop gate;
- any detected contradiction/blocker.

## Authority boundary

The foreman is a deterministic assistant, not an architect.

It may:

- inspect;
- validate consistency;
- summarize already-recorded state;
- generate a briefing;
- route to existing maintenance/verification commands.

It may not:

- invent product decisions;
- silently rewrite `CURRENT_CONTROL_STATE.md`;
- change phase/work-order status;
- decide that CI is green without evidence;
- make source edits;
- auto-commit/push.

Remote GitHub/CI observation remains primarily ChatGPT's control-plane responsibility.

## Prompt compression target

After this batch, a normal Codex construction prompt should usually be approximately:

```text
Sync main and confirm clean state.
Read docs/operations/CURRENT_CONTROL_STATE.md.
Run: powershell -File scripts/maintain.ps1 foreman
Follow .private/codex_brief.md and execute the active work order to its stop gate.
Run required verification, commit/push the bounded reusable changes, then report.
```

Do not require a 100+ line task prompt unless the active work order itself is genuinely novel/high-risk.

## Verification

Add focused deterministic tests for at least:

- valid control state/work order -> brief generated;
- missing/malformed control metadata -> fail closed;
- phase/work-order mismatch -> fail closed;
- dirty tree is surfaced prominently;
- `.private/codex_brief.md` is untracked/ignored;
- brief does not expand by copying whole durable documents.

Run the repository's normal Quality Gate.

## Stop gate

Stop when:

- foreman command works;
- generated brief is concise and deterministic;
- focused tests pass;
- full Quality Gate is green;
- reusable changes are committed/pushed;
- working tree is clean.

Do not start R0.12 product feature implementation in this batch.
