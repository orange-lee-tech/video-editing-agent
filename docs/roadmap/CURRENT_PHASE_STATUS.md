# Current Roadmap Phase Status

**Planning baseline:** ACCEPTED / FROZEN  
**Roadmap V2 operational status:** ACTIVE  
**R0.7A:** CLOSED  
**R0.7B:** CLOSED  
**Current phase:** R0.8 — Media Evidence Foundation  
**Date:** 2026-08-12

## Authority

The active planning order remains:

```text
Product Constitution v1.0
→ Architecture Contract v0.2
→ Capability Specs CAP-01 ... CAP-10
→ ADRs
→ Upstream Ledger / Policy V2
→ Roadmap V2
→ implementation
```

A0 was explicitly accepted by the user before R0.7A implementation began.

## R0.7A closure retained

R0.7A — Architecture v0.2 Migration Foundation remains closed after canonical rational media-time migration, persistence/evidence ownership migration, exact-time TransNetV2 validation, full Engineering Quality Gates, Windows probes, and a private real-phone-footage Product Probe.

The retained real-footage quality guard is that correct Shot count is not sufficient by itself: temporal boundary error must remain visible and future changes must not silently regress beyond the measured baseline without explicit evidence.

See:

```text
docs/validation/R0.7A_FINAL_CLOSURE.md
```

## R0.7B closure

R0.7B — Pre-production Planning + Commercial Skill Foundation is closed after implementing and validating the executable product pillar:

```text
Brief → ScriptPlan → ShootingPlan
```

Closure evidence includes:

- structured Brief/Script/Shooting models and revision ownership;
- Script duration assessment and section locks;
- production constraints and structured ProductionLocation identity;
- required/recommended/optional/backup coverage and reshoot routing;
- `Performance Product Ad` and `Natural Vlog` CommercialSkill paths;
- provider-neutral DeepSeek planning/review seams;
- shared Commercial Authority across generation and review;
- veto-only semantic review without Domain ownership;
- deterministic Quality Gate success on `48ecafcf45a299ced4d9abafd5501e2b9031f4a3`;
- Product Probe run `31610613082` (#16) with both cases `ready_for_human_acceptance` and all automated semantic/product gates accepted;
- Human Gate acceptance on usefulness, shooting-plan executability, factual fidelity, and expected shooting coverage.

The Product Ad result estimated 23 seconds against a 30-second Brief target. This is retained as a non-blocking quality note rather than hidden or converted into a false engineering failure.

See:

```text
docs/validation/R0.7B_FINAL_CLOSURE.md
```

## Active next phase — R0.8

R0.8 builds the grounded media evidence required by later Resolver/Director work.

Primary scope from Roadmap V2:

### Speech

- CPU-capable ASR provider baseline;
- word/segment timestamps;
- VAD/silence evidence;
- transcript persistence;
- phrase/time mapping.

### Visual temporal evidence

- camera/global motion estimation;
- camera-compensated residual motion;
- coarse-to-fine event regions;
- motion onset/peak/settle anchors;
- seeded subject/product tracking baseline;
- provider-neutral TemporalEvidence/Anchor storage.

### Retrieval representation

- derived visual-semantic/speech embedding representations;
- local multilingual embedding provider prototype;
- index provenance/version;
- exact project-local vector scan.

R0.8 must not leapfrog into R0.9 Director/Resolver authority, R0.10 music editorial, R0.11 Auto Reframe, or R0.12 renderer productization.

## R0.8 exit direction

The phase must prove that real user footage can produce a useful grounded candidate-time evidence set without requiring a high-end GPU.

Engineering/Product evidence must include timestamp provenance, Shot-boundary isolation, camera-motion compensation behavior, persistence/rebuild semantics, and real-footage quality observations.

## Development gate

The discipline remains:

```text
observe current state
→ audit
→ plan one coherent batch
→ implement behind existing ownership seams
→ deterministic/local verification
→ atomic commit to main
→ free Quality Gate
→ Engineering Probe
→ Product Probe only when usefulness is genuinely being claimed
→ evidence/docs
→ next batch
```

If `main` becomes red, feature work freezes until repaired.

Before Codex, first decide whether the work genuinely requires complex cross-file construction/exploration. Before a paid Product Probe, state what new information the run can discriminate and why deterministic verification cannot answer it.
