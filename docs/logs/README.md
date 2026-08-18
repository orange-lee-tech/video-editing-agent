# Engineering Logs

**Status:** non-authoritative engineering memory

This directory stores durable debugging/probe/collaboration knowledge that is expensive to rediscover. It is not an authority pack and it is not the active project-state surface.

## Authority / live-state boundary

When facts conflict:

1. current GitHub `main` + current CI/probe evidence for live implementation facts;
2. accepted product/architecture/capability/Roadmap documents;
3. `docs/logs/` only as historical engineering memory.

Active state belongs in:

- `docs/roadmap/CURRENT_PHASE_STATUS.md`
- `docs/operations/CURRENT_WORK_ORDER.md`

Do not create phase-specific working-cache files when those two dynamic files can carry the current state.

## Files

- `PROJECT_CHRONICLE.md` — 简体中文项目编年史；把 GitHub 提交、validation、真实 Product/Human Gate 与关键失败重新串成可读时间线。
- `INCIDENT_LEDGER.md` — durable symptom → mechanism → invariant → fix/evidence history.
- `PROBE_LEDGER.md` — material Engineering/Product Probe history and information gained.
- `COLLABORATION_LESSONS.md` — durable lessons about ChatGPT/User/GitHub/Codex orchestration.
- `REPOSITORY_GOVERNANCE_LESSONS.md` — durable repository hygiene, archive and navigation lessons.
- `STAGE_A_PRODUCT_IO_IMPACT_AUDIT_2026-08-16.md` — Stage-A product input/output impact audit snapshot.
- `COMMERCIAL_DESKTOP_RISK_AUDIT_2026-08-19.md` — static evidence-backed audit of Provider, Windows desktop, packaging, filesystem, runtime and commercial-release risks.

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
