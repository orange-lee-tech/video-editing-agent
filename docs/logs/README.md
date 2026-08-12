# Engineering Logs

Status: non-authoritative engineering memory

This directory is a compact, repository-local memory layer for debugging, handoff, probe history, and repeated failure analysis. It is deliberately **not** a sixth authority pack.

## Authority boundary

When sources disagree, use this order:

1. current GitHub `main` implementation and CI/probe evidence for live implementation facts;
2. the five external authority-pack documents `00`–`04` for project governance and accepted architecture;
3. accepted repository architecture/roadmap/validation documents;
4. files in `docs/logs/` only as working memory and investigation history.

A log entry must never silently redefine Domain authority, Roadmap scope, product constitution, or phase closure.

## Files

- `INCIDENT_LEDGER.md` — durable symptom → mechanism → subsystem → invariant → fix/evidence history.
- `PROBE_LEDGER.md` — paid and material engineering/product probe history, including what new information each run produced.
- `R0.7B_WORKING_CACHE.md` — compact current-state cache for an active investigation; expected to be replaced as the investigation advances.

## Logging rules

Record only information that is expensive to rediscover or useful for discriminating future root causes. Prefer links/SHAs/run IDs over copied logs.

For bugs, use the chain:

```text
symptom
→ mechanism
→ subsystem
→ shared invariant
→ affected surfaces
→ systematic fix
→ verification evidence
```

For probes, record before execution:

```text
question
candidate root causes it can distinguish
expected new evidence
cost class
```

Then record the observed result after execution. A paid Product Probe must not be run when a red result would fail to distinguish at least two plausible root causes.

## What not to commit

Do not commit:

- API keys, tokens, secrets, private user footage, local absolute paths, or sensitive raw provider payloads;
- giant CI logs that are already retained by GitHub Actions;
- hidden model reasoning / chain-of-thought;
- repeated test output with no new diagnosis;
- speculative conclusions presented as fact.

## Retention

`INCIDENT_LEDGER.md` and `PROBE_LEDGER.md` are append-oriented durable history. `R0.7B_WORKING_CACHE.md` is replaceable working state and may be rewritten when its investigation closes. Phase closure evidence belongs in `docs/validation/`, not here.
