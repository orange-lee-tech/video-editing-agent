# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL CONSTRUCTION  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** ACTIVE — `R0.12-EDLBUILDER-001`  
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

## R0.12 EDL foundation accepted

`ff343833deb9296c1df0b6fc944735388d5c8296` — typed tracks, deterministic composition and structured validation.

## R0.12 EDL automation/serialization accepted

Accepted code baseline:

`4b2522ae1a6838517baf4c5bcf36d30026f86912` — `feat: add exact EDL automation serialization`.

Verified:

- remote `ci/quality-gate-diagnostic` success;
- exact rational spatial/audio automation types;
- deterministic EDL v0.2 codec and stable round-trip;
- schema-version fail-closed behavior;
- automation track compatibility and keyframe/source↔timeline validation;
- upstream SpatialComposer/AudioEditorial references retained as provenance;
- reported Engineering Probe `5/5 PASS`, focused tests `21 PASS`, full Quality Gate `505 tests` plus Ruff/mypy/import contracts/build/diff check.

## Active R0.12 frontier

`R0.12-EDLBUILDER-001` creates the deterministic assembly boundary from already-approved EditPlan/Resolution/Spatial/Audio decisions into canonical EDL v0.2.

The builder may allocate exact timeline placement from grounded ordered selections, but it may not redo source selection, framing or audio editorial policy.

Renderer remains blocked until this decision-to-EDL bridge is green.
