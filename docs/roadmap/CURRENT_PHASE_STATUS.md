# Current Roadmap Phase Status

**Roadmap:** V2 ACTIVE  
**Current phase:** R0.8 — Media Evidence Foundation  
**Updated:** 2026-08-13

## Authority

```text
Product Constitution v1.0
→ Architecture Contract v0.2
→ Capability Specs / ADRs
→ Roadmap V2
→ current implementation
```

For live implementation facts, always reobserve current `origin/main`; do not treat a recorded SHA in historical evidence as current HEAD.

## Closed phases

- R0.7A — Architecture v0.2 Migration Foundation: CLOSED. See `docs/validation/R0.7A_FINAL_CLOSURE.md`.
- R0.7B — Pre-production Planning + Commercial Skill Foundation: CLOSED. See `docs/validation/R0.7B_FINAL_CLOSURE.md`.

## R0.8 completed engineering foundations

### Speech

- CPU Faster-Whisper baseline;
- word/segment timestamps;
- Silero VAD / silence evidence;
- transcript persistence and reopen;
- deterministic phrase/time mapping.

### Visual temporal evidence

- exact Shot-scoped camera/global motion measurement;
- camera-compensated residual motion;
- bounded-memory streaming frame-pair processing;
- durable motion Artifact + low-density measurement-set evidence;
- deterministic event-region reduction;
- coarse onset / peak / settle anchors;
- bounded high-rate refinement with exact analyzed-source-range provenance;
- v1 motion Artifact backward read + v2 range-aware write;
- persistence/restart and rational original-Asset time mapping.

The latest owner invariant requires provider-reported `analyzed_source_range` to equal the requested analysis range before any Artifact/evidence commit.

## R0.8 remaining planned work

1. **R0.8F — Seeded subject/product tracking baseline** — active next boundary.
2. **R0.8G — Retrieval representation** — multilingual dense representation + provenance + exact local vector scan.
3. **R0.8H — Real-footage Product Probe and phase closure** — talking head, handheld product demo, camera pan, hand/product interaction, low motion, noisy/blurred footage.

R0.8 must not leap into R0.9 Director / Resolver authority before these foundations and the real-footage evidence gate are complete.

## Operational entrypoints

- Codex behavior: `docs/operations/CODEX_EXECUTION_ENTRY.md`
- Active implementation boundary: `docs/operations/CURRENT_WORK_ORDER.md`
- Probe history: `docs/logs/PROBE_LEDGER.md`
- Incident/root-cause history: `docs/logs/INCIDENT_LEDGER.md`

The phase-status file is intentionally concise and may be rewritten as work advances. Historical detail belongs in validation/log documents, not here.
