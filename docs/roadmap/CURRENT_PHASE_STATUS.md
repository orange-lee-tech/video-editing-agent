# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL CONSTRUCTION  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** ACTIVE — `R0.12-RENDERER-001`  
**Updated:** 2026-08-15

## Progress meaning

Canonical stage model: `docs/roadmap/DEVELOPMENT_STAGE_MODEL.md`.

The current 0–100% project percentage measures **structural construction**: end-to-end capability closure with correct authority, extensibility, deterministic execution, compatibility and safe failure behavior.

Reaching 100% will begin a separate product-refinement stage; it will not mean commercial quality is already perfect.

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Pre-production Planning + Commercial Skill Foundation.
- R0.8 — Media Evidence Foundation.
- R0.9 — Director → Retrieval → Resolver → Deterministic Optimizer.
- R0.10 — Music Selection + BeatMap + Audio Editorial.
- R0.11 — Spatial Composition / Auto Reframe (`PASS_WITH_MINOR_DEFECT`).

## Control-plane baseline

`1012f239aa95899e914ba6091c3b825dfc6302fe` — trigger-first foreman v2. Further control-plane refinement is demand-driven only.

## R0.12 EDL foundations accepted

- `ff343833deb9296c1df0b6fc944735388d5c8296` — typed tracks, deterministic composition and structured validation.
- `4b2522ae1a6838517baf4c5bcf36d30026f86912` — exact rational spatial/audio automation plus deterministic EDL v0.2 codec/round-trip.

## R0.12 EDLBuilder accepted

Accepted code baseline:

`b6c5684a9b07d79f20a10d28886cd087eaeecf10` — `feat: add deterministic EDL builder`.

Verified from GitHub:

- remote `ci/quality-gate-diagnostic` success;
- deterministic grounded selection → Shot/Asset → exact timeline assembly;
- approved spatial plan and music/audio decisions translate without new creative policy;
- missing/conflicting/unresolved/out-of-range/unsupported mappings fail closed with structured diagnostics;
- MUTE and PRESERVE produce observably different canonical track structures;
- Foreman read-reference fix is limited to accepting existing directory paths rather than only files;
- reported Engineering Probe `6/6 PASS`, focused verification `26 tests`, full Quality Gate `513 tests` plus Ruff/mypy/import contracts/build/diff check.

## Active R0.12 frontier

`R0.12-RENDERER-001` establishes the first canonical EDL-driven FFmpeg render path.

The structural target is deliberately concrete: a validated canonical EDL must produce an actual locally verifiable MP4 while unsupported execution semantics fail closed. Renderer may reuse deterministic R0.11 FFmpeg compilation ideas, but it may no longer treat `SpatialTransformPlan` or any upstream decision object as alternate timeline authority.

Subtitle, Graphics, Preview, Proxy/cache, hardware routing and packaging remain outside this batch.
