# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE

**Current phase:** R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer

**Active boundary:** R0.9A — Edit Intent → Hybrid Retrieval → Grounded CandidateWindows

**Date:** 2026-08-13

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.

R0.8 closure baseline:

`6257586310e266ef271ea67f8eda1cc5434e6df1` — `test: close r0.8 media evidence phase`

R0.8H passed all ten named Product Probe gates on the anonymous local real-media corpus plus a deterministic local TTS speech fixture mixed with captured ambient audio. Closure evidence and limitations are recorded in `docs/validation/R0.8_FINAL_CLOSURE.md`.

## Active — R0.9A

R0.9 begins the core automatic-editing brain. The first construction boundary must convert structured editorial intent into grounded, inspectable candidate source windows without allowing an LLM to invent media IDs or timestamps.

R0.9A covers in one coherent batch:

- canonical `EditPlan` / `EditSlot` intent contracts owned by Director-side Domain/Application code;
- hard eligibility before ranking;
- existing lexical/CJK + dense representation retrieval combined through deterministic RRF-like rank fusion;
- bounded `CandidateWindow` generation from authoritative Shot/source ranges and persisted temporal evidence/anchors;
- stable provenance/explainability for every candidate;
- local diagnostic preview clips for human inspection of CandidateWindows.

The preview clips are non-authoritative probe artifacts only. They may trim/copy already-grounded source windows for inspection but must not introduce EDL, timeline placement, creative rendering decisions or R0.10+ authority.

## After R0.9A

The next boundary is Resolver + deterministic sequence optimizer: unary/pairwise/global scoring, uncertainty, alternatives and one-slot-to-multiple-selection `ResolutionDecision` support.

R0.9 closes only after the real-footage phase Product Probe demonstrates a grounded exact source-selection plan. Do not enter R0.10 before that closure.

## Operational control

Codex reads `CODEX_EXECUTION_ENTRY.md`, this file, then `CURRENT_WORK_ORDER.md`.
