# Current Roadmap Phase Status

**Planning baseline:** ACCEPTED / FROZEN  
**Roadmap V2 operational status:** ACTIVE  
**R0.7A:** CLOSED  
**Current phase:** R0.7B — Pre-production Planning + Commercial Skill Foundation  
**Date:** 2026-08-11

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

## R0.7A closure

R0.7A — Architecture v0.2 Migration Foundation is closed after:

- canonical rational media-time migration;
- Asset origin / usage-role and rights seams;
- SQLite v2 migration with v1 read compatibility;
- Derived Evidence / cache / index ownership cleanup;
- future authority contracts for Resolver, SpatialComposer, MusicSelection, AudioEditorial, Review and EDL;
- exact-time TransNetV2 migration closure;
- full Engineering Quality Gates;
- Windows engineering probes;
- one private real-phone-footage Product Probe.

The private Product Probe detected the correct three-shot structure on the tested composite. Practical boundary deltas relative to independently probed source-clip cumulative durations were approximately 91 ms and 142 ms early. The user judged that error range barely acceptable and explicitly does not want larger regressions.

This observation is a quality guard, not a universal fixed threshold. Later benchmark work must annotate acceptable cut ranges directly on final test assets and score boundary accuracy separately from Shot-count accuracy.

See:

```text
docs/validation/R0.7A_6_ENGINEERING_CLOSURE.md
```

## Active next phase — R0.7B

R0.7B makes the first product pillar real:

```text
Brief → ScriptPlan → ShootingPlan
```

The phase must build an executable pre-production workflow rather than generic LLM chat.

Primary scope:

- structured Brief creation/revision;
- authoritative commercial facts;
- ScriptPlan / NarrativeSections;
- natural-language structured revision and locks;
- reference-video structural/style analysis without source eligibility;
- ShootingPlan and production-constraint intake;
- required/recommended/optional/backup coverage;
- coverage-gap and reshoot guidance;
- initial CommercialSkill / PlatformProfile foundation;
- at least one Product Ad and one Natural Vlog policy path.

R0.7B must not silently expand into R0.8 media-evidence work, R0.10 music systems, R0.11 Auto Reframe or R0.12 renderer productization.

## Development gate

The existing discipline remains active:

```text
observe current state
→ audit
→ plan one coherent batch
→ implement
→ quality gate
→ Engineering Probe
→ Product Probe when usefulness is claimed
→ evidence/docs
→ next batch
```

If `main` becomes red, feature work freezes until repaired.
