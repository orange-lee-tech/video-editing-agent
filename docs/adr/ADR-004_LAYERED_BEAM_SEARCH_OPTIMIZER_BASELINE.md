# ADR-004 — Layered Beam Search / DP as First Sequence-Optimizer Baseline

**Status:** PROVISIONAL  
**Date:** 2026-08-11

## Context

After retrieval and CandidateWindow generation, the remaining problem is a bounded sequence-selection task with unary, pairwise and global constraints. Asking an LLM to enumerate and time the full sequence is less deterministic, less explainable and more expensive.

## Decision

First optimizer family to prototype/benchmark:

```text
layered beam search / DAG-style dynamic programming
```

over EditSlots and bounded CandidateWindows.

Optimizer state can include current Slot, accumulated duration/music state, last candidate, used Shot neighborhoods, coverage and accumulated score.

The optimizer lives inside/behind the Resolver capability and does not own EDL timeline coordinates.

## Why not CP-SAT first

A general constraint solver remains a valid escalation path if future requirements include strongly coupled multi-track/global allocation constraints. Current short-form editing shape is naturally sequential and can start with a small transparent search.

## Evidence

Survey V2 found independent support from BEAT-style elastic alignment and EditIQ-style explicit sequence/energy optimization.

## Benchmark gate

Measure human sequence preference, runtime, pruning quality, VLM escalation count and sensitivity to beam width/Top-K.

Parameters are not frozen by this ADR.
