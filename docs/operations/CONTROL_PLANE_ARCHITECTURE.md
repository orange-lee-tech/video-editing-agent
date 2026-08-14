# Control Plane Architecture — ChatGPT / Codex / GitHub / Local Foreman

**Status:** ACTIVE OPERATING MODEL  
**Updated:** 2026-08-14

## Problem being solved

Long Codex prompts accumulated repeated architecture explanations, historical context, startup rules, validation requirements and stop conditions.

That is inefficient and increases instruction collision risk: task-specific objectives compete with repeated durable rules, while Codex spends effort reconstructing a state model that already exists in repository documents.

The control plane therefore separates **durable authority**, **current state**, **active delta**, and **runtime observation**.

## Four layers

### 1. Durable authority

Examples:

- Product Constitution;
- Architecture Contract;
- CAPs;
- ADRs;
- Engineering Operating Protocol;
- Chat/Codex execution policy.

These documents explain long-lived rules.

They must not be recopied into every Codex prompt.

### 2. Current routing state

`docs/operations/CURRENT_CONTROL_STATE.md`

Owns only:

- current phase;
- phase state;
- active work-order ID;
- latest accepted implementation baseline;
- current Human Gate/release notes relevant to routing;
- default read strategy;
- immediate gate.

It is compact and intentionally replaceable as the project advances.

It does not claim live GitHub HEAD authority.

### 3. Active work-order delta

`docs/operations/CURRENT_WORK_ORDER.md`

Owns only the current coherent batch:

- objective;
- required read set;
- allowed scope;
- forbidden scope;
- acceptance tests;
- stop gate.

Historical explanations belong in validation/research/ADR docs instead.

### 4. Runtime observation

Generated local file:

`.private/codex_brief.md`

Produced by the deterministic foreman helper from:

- actual local Git state;
- `CURRENT_CONTROL_STATE.md`;
- `CURRENT_WORK_ORDER.md`;
- minimal referenced task files/metadata.

The generated brief is ephemeral and never committed.

## Foreman role

The foreman is a deterministic local construction assistant.

It should:

- inspect local branch/HEAD/status;
- check obvious state/work-order consistency;
- generate a concise active briefing;
- route to existing verify/handoff maintenance commands;
- fail closed on contradictions.

It must not:

- decide product architecture;
- rewrite project state on its own;
- modify source;
- auto-commit/push;
- declare remote CI green without evidence;
- invent missing constraints.

ChatGPT remains the remote GitHub/CI control plane. Codex remains the local complex-batch writer.

## Read-on-demand rule

Normal Codex startup should read:

1. `CURRENT_CONTROL_STATE.md`;
2. `CURRENT_WORK_ORDER.md`;
3. only the task-specific references named by the work order.

Do not make every batch reread Product Constitution + Architecture Contract + Roadmap + all CAPs + all historical validation unless the task actually touches those authorities.

A contradiction or architecture-sensitive change is the trigger to expand the read set.

## Prompt budget rule

A normal ChatGPT → Codex prompt should be a launcher, not the complete construction manual.

Target shape:

```text
Sync main and confirm clean state.
Read docs/operations/CURRENT_CONTROL_STATE.md.
Run powershell -File scripts/maintain.ps1 foreman.
Follow .private/codex_brief.md and execute the active work order to its stop gate.
Run required verification, commit/push bounded reusable changes, then report.
```

Use a long inline prompt only when:

- a new architecture decision has not yet been recorded;
- an emergency repair depends on fresh evidence not yet captured in docs;
- a one-off destructive/risky operation requires explicit human constraints.

After the decision becomes durable, move it into the correct repository document and shrink subsequent prompts again.

## State ownership

- User: product intent / Human Gate / governance decisions.
- ChatGPT: current control state, work-order design, GitHub/CI review, closure records.
- Codex: bounded local implementation/test loop.
- Foreman: deterministic state briefing and preflight only.
- GitHub `main`: live committed implementation truth.

This architecture exists to reduce repeated reasoning, not to remove checks. The goal is **check once at the right layer, reference thereafter**.
