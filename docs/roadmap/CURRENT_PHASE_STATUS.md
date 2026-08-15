# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** ACTIVE — `R0.12-EDL-002`  
**Updated:** 2026-08-15

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.
- R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.
- R0.11 — Spatial Composition / Auto Reframe (`PASS_WITH_MINOR_DEFECT`).

## Control-plane baseline

`1012f239aa95899e914ba6091c3b825dfc6302fe` — trigger-first foreman v2. Further control-plane refinement is demand-driven only.

## R0.12 EDL foundation accepted

Accepted code baseline:

`ff343833deb9296c1df0b6fc944735388d5c8296` — `feat: add typed EDL validation foundation`.

Verified from GitHub:

- remote `ci/quality-gate-diagnostic` success;
- typed EDL track families and deterministic composition ordering;
- deliberate v0.1 built-in track compatibility view;
- structured deterministic diagnostics for duplicate identities, unknown tracks, duration mismatch and illegal same-track overlap;
- rational `MediaTimeRange` semantics preserved;
- deterministic Engineering Probe present with 5 named gates.

Reported local gate: Ruff, mypy, 499 tests, import contracts, build and diff check green; working tree clean and synchronized.

## Active R0.12 frontier

`R0.12-EDL-002` adds the remaining execution semantics needed before an EDL-driven Renderer is justified:

- exact typed time-varying spatial automation;
- typed audio automation for current R0.10 execution needs;
- deterministic rational EDL v0.2 serialization/round-trip;
- automation validation and Engineering Probe evidence.

Do not begin Renderer, Subtitle, Preview, Proxy/cache or UI in the same batch.
