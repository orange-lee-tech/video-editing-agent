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

The v0.1.x series is preserved centrally under:

`docs/archive/architecture/`

Those files are provenance only. Where a v0.1.x rule conflicts with Product Constitution v1.0 or accepted v0.2, it is historical and must not be implemented.

## Current construction state

R0.10 is **HANDOFF_READY** after accepted R0.10A/R0.10B engineering baselines. It is not closed; the next planned boundary is the real-music Product Probe / Human Gate.

See:

- `docs/roadmap/CURRENT_PHASE_STATUS.md`
- `docs/operations/CURRENT_WORK_ORDER.md`

Core authority chain:

`Brief → ScriptPlan → ShootingPlan → user visual Assets/Shots → evidence → Music/BeatMap → EditPlan → ResolutionDecision → spatial/audio decisions → EDL → Render → Review`

External models/providers/upstreams contribute capability implementations only. They never override Domain ownership or Product Constitution policy.
