# Architecture

## Active authority

The post-Survey V2 planning baseline was accepted on **2026-08-11**.

Authority order:

1. `docs/product/PRODUCT_CONSTITUTION_V1.0.md` — product-level authority.
2. `ARCHITECTURE_CONTRACT_V0.2.md` — **ACTIVE architecture baseline**.
3. `docs/capabilities/` — active capability specification set.
4. `docs/adr/` — active architecture decision records.
5. implementation / provider behavior.

Acceptance record: `docs/roadmap/A0_PLANNING_BASELINE_ACCEPTANCE.md`.

The `CANDIDATE` wording inside the original v0.2 draft header records its pre-acceptance drafting state. A0 supersedes that status label for current authority.

## Retired architecture contracts

The v0.1.x series is preserved centrally under `docs/archive/architecture/` as provenance only.

## Current construction state

The project is in **Stage A — Structural Construction**, currently R0.12.

Accepted R0.12 execution chain:

```text
EditPlan / grounded ResolutionDecision
+ authoritative Shot/Asset mappings
+ approved Spatial/Audio decisions
→ EDLBuilder
→ canonical EDL v0.2
→ EDL-driven Renderer
→ local MP4 artifact
```

Accepted Renderer baseline:

`83fc2999297023f828fa77719cd357fe82eab5de` — `feat: add deterministic EDL-driven renderer`.

The Renderer may compile backend syntax, but it may not consult Resolver, SpatialComposer or AudioEditorial as alternate execution authority. Missing or unsupported execution semantics fail closed rather than being repaired at render time.

See:

- `docs/roadmap/CURRENT_PHASE_STATUS.md`
- `docs/operations/CURRENT_WORK_ORDER.md`
- `docs/capabilities/CAP-08_EDL_RENDER_PREVIEW_SUBTITLE.md`

Core authority chain:

`Brief → ScriptPlan → ShootingPlan → user visual Assets/Shots → evidence → Music/BeatMap → EditPlan → ResolutionDecision → spatial/audio decisions → EDLBuilder → EDL → Renderer → Review`

External models/providers/upstreams contribute capability implementations only. They never override Domain ownership or Product Constitution policy.
