# ADR-002 — Grounded AI: Models Do Not Invent Authoritative Timestamps

**Status:** ACCEPTED  
**Date:** 2026-08-11

## Context

General LLM/VLM models are valuable at semantic/editorial judgment but unstable at arbitrary floating-point media timing. Local ASR, motion, Shot boundaries, tracking and BeatMap can produce real candidate anchors more cheaply and reproducibly.

## Decision

By default:

```text
local/model evidence
→ validated TemporalAnchors / CandidateWindows
→ AI may choose/label/rank grounded options
→ Resolver commits source decision
→ EDLBuilder commits exact timeline
```

A model may report a timestamp as observation evidence, but it cannot become authoritative merely because the provider returned it.

Prefer prompts such as:

> choose A/B/C/uncertain

over:

> invent the exact millisecond.

## Consequences

- source windows remain valid/benchmarkable;
- strong AI budget is spent on meaning instead of clocks;
- provider replacement becomes easier;
- exact trim quality depends on high-recall TemporalAnchor generation;
- targeted VLM re-analysis remains available when evidence is genuinely ambiguous.
