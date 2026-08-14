# Control Plane Architecture — Information Economy

**Status:** ACTIVE OPERATING MODEL  
**Updated:** 2026-08-14

## Goal

Optimize Codex for **execution efficiency, accuracy and necessity**. Prompt length is secondary.

Moving a long prompt into Markdown is not a solution if Codex must still read the same information before every task. Repository documents are an authority/tool store; they are not automatically model context.

## Model-read vs machine-read

The foreman may machine-parse rich repository state and work-order files. Codex should normally see only the smallest safe execution surface.

### L0 — always visible

Only information needed to start correctly:

- active task/phase;
- one-sentence objective;
- actual local Git state;
- immediate next action;
- hard blocker/stop conditions;
- named trigger routes.

### L1 — task-local expansion

Open only when needed: relevant implementation files, focused tests, exact tool command, or one targeted contract/reference.

### L2 — authority/evidence expansion

Open only when the task hits an architecture/product boundary, contradictory evidence, provider/license uncertainty, or a failed quality gate that cannot be resolved locally.

### L3 — historical/deep investigation

Project history, broad validation records, upstream research and old decisions are last-resort context, not startup context.

## Trigger-first rule

Secondary information is exposed by condition, not by completeness anxiety.

Examples:

- architecture ambiguity -> route to the smallest relevant CAP/ADR/contract section;
- symbol/code-location uncertainty -> targeted search first, not repository-wide reading;
- test failure -> focused failure evidence + quality tool route;
- Git-state problem -> repository recovery route;
- license/provider uncertainty -> release/research route and fail closed where required;
- destructive/high-risk operation -> stop for ChatGPT/User gate.

The route points to information or a tool. It does not copy the target into L0.

## Toolbox model

Maintain a compact Codex toolbox index with two families:

1. **work tools** — locate, inspect, test, verify, probe, build, handoff and repository-maintenance commands;
2. **blocked strategies** — what to do when state, architecture, evidence, licensing, network or destructive-operation blockers occur.

The toolbox should be complete enough to route work but should not be read in full on every task. Foreman exposes only the route relevant to the current trigger.

## Authority boundaries

- User: product intent, Human Gate, governance decisions.
- ChatGPT: work-order design, GitHub/CI review, phase/closure control.
- Codex: bounded local implementation and verification.
- Foreman: deterministic observation, validation and routing only.
- GitHub `main`: live committed implementation truth.
- Product Constitution / Architecture / CAP / ADR: durable authority opened only when triggered.

## Normal startup

The preferred steady-state flow is:

```text
sync main -> run foreman -> read L0 brief -> execute
                           -> trigger L1/L2 only if needed
```

Codex should not automatically read `CURRENT_CONTROL_STATE.md`, `CURRENT_WORK_ORDER.md`, Product Constitution, Architecture Contract, CAPs, ADRs or historical validation before routine bounded work. The foreman may parse control files on Codex's behalf.

## Success criterion

A good control plane does not maximize context. It keeps the automation chain and work relationships reliable while making the next correct action obvious.
