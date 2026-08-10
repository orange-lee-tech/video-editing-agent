# ADR-003 — Project-Local Hybrid Retrieval Before Vector-Database Infrastructure

**Status:** PROVISIONAL  
**Date:** 2026-08-11

## Context

The first desktop product operates on project-local Shot collections measured in hundreds/thousands, not internet-scale corpora. Retrieval needs both exact lexical matches and semantic paraphrase/cross-language recall.

## Decision

First implementation baseline:

```text
SQLite durable Shot/analysis records
+
lexical/CJK retrieval
+
local multilingual text embeddings
+
exact in-memory vector scan
+
RRF-like rank fusion
→ broad Top-K
```

Embeddings belong to rebuildable `ShotIndex` infrastructure.

Do not require a vector-database server for v1 desktop operation.

## Benchmark gate

Compare:

- lexical only;
- dense only;
- hybrid;
- candidate multilingual models;
- exact scan latency/RAM.

Escalate to sqlite-vec/FAISS/ANN only when measured scale/latency requires it.

## Consequences

- simpler Windows deployment;
- no duplicate database authority;
- easy index rebuild when embedding model changes;
- first model choice remains replaceable and evidence-driven.
