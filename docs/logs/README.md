# Engineering Logs

**Last updated:** 2026-08-22  
**Status:** non-authoritative engineering memory

This directory stores durable debugging/probe/collaboration knowledge that is expensive to rediscover. It is not an authority pack and it is not the active project-state surface.

## Authority / live-state boundary

When facts conflict:

1. current GitHub `main` + current CI/probe evidence for live implementation facts;
2. accepted product/architecture/capability/Roadmap documents;
3. `docs/logs/` only as historical engineering memory.

Active state belongs in:

- `docs/operations/CURRENT_CONTROL_STATE.md`
- `docs/roadmap/CURRENT_PHASE_STATUS.md`
- `docs/operations/CURRENT_WORK_ORDER.md`

Do not create phase-specific working-cache files when those live control files can carry the current state.

## Files

- `PROJECT_CHRONICLE.md` — 简体中文、按自然日索引的项目编年史；把 GitHub 提交、validation、真实 Product/Human Gate 与关键失败重新串成可读时间线。
- `INCIDENT_LEDGER.md` — durable symptom → mechanism → invariant → fix/evidence history.
- `PROBE_LEDGER.md` — material Engineering/Product Probe history and information gained.
- `COLLABORATION_LESSONS.md` — durable lessons about ChatGPT/User/GitHub/Codex orchestration.
- `REPOSITORY_GOVERNANCE_LESSONS.md` — durable repository hygiene, archive and navigation lessons.
- dated audit files — static evidence snapshots for a specific risk/impact question; they do not become live authority.

## Chronicle rule

The chronicle uses **one natural day as the minimum history unit**. A day may summarize multiple commits/PRs/waves, but different dates should not be collapsed into one ambiguous entry.

The chronicle records why the project changed direction and what was actually proven. It should not duplicate every commit message or every CI run.

## What deserves a log entry

Record only information likely to prevent future rediscovery, such as:

```text
symptom → mechanism → subsystem → shared invariant → fix → verification
```

or a material probe/workflow lesson that established a reliable practice or exposed a repeatable failure mode.

Do not log ordinary green CI runs, repeated command output, routine formatter fixes, or every local experiment.

## Probe rule

Before a paid Product Probe, record the question, competing hypotheses it can distinguish, evidence needed, why deterministic tests are insufficient, and expected cost. No paid run is justified merely to obtain another wording example.

## Never commit

Secrets, private footage, machine-specific absolute paths, giant CI logs already retained by Actions, hidden model reasoning/chain-of-thought, or speculative conclusions presented as fact.

## Retention

Ledgers are append/curate-oriented durable memory and may be compacted when details are duplicated by formal closure evidence. Formal phase closure belongs in `docs/validation/`; active instructions belong in `docs/operations/`; retired documents belong in `docs/archive/`.
