# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL CONSTRUCTION  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** ACTIVE — `R0.12-SMOKE-001`  
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

## Accepted R0.12 structural baselines

- `ff343833deb9296c1df0b6fc944735388d5c8296` — typed EDL tracks, deterministic composition and structured validation.
- `4b2522ae1a6838517baf4c5bcf36d30026f86912` — exact rational spatial/audio automation plus deterministic EDL v0.2 codec/round-trip.
- `b6c5684a9b07d79f20a10d28886cd087eaeecf10` — deterministic grounded decision-to-EDL assembly.
- `83fc2999297023f828fa77719cd357fe82eab5de` — deterministic EDL-driven FFmpeg Renderer.

Renderer verification from GitHub/source audit:

- remote `ci/quality-gate-diagnostic` success;
- EDL is sole timeline/spatial/audio execution authority;
- missing media, ambiguous Asset mappings, timeline gaps and unsupported semantics fail closed;
- deterministic argv, `shell=False`;
- live probe executes EDLBuilder → Renderer → actual MP4 → ffprobe;
- observed output: 2.000 s, 180×320, 30 FPS; PRESERVE contains audio, MUTE does not;
- reported focused tests 22 PASS and full gate 522 tests plus Ruff/mypy/import contracts/build/diff check.

Current known integration evidence gap: spatial live-probe proof checks the generated LINEAR crop/filter semantics rather than final-frame pixel motion. This is carried into the living smoke path, not treated as a reason to reopen the Renderer foundation.

## Active R0.12 frontier

`R0.12-SMOKE-001` establishes a durable bounded integration regression path using actual Resolver/optimizer output → EDLBuilder → EDL-driven Renderer → ffprobe.

This smoke must use real module outputs at each linked boundary rather than hand-authoring downstream truth, but it remains controlled Engineering Probe evidence. It must not be mislabeled as the later R0.16 real one-click Product Probe.

After the smoke path is green, continue R0.12 Subtitle/Graphics/Preview/Proxy productization without expanding EDL/Renderer internals unless a concrete blocker appears.

## Downstream structural constraints

The R0.16 one-click chain must eventually use actual VisualUnderstanding evidence in Retrieval/Resolver; a visual-only automatic-BGM promise requires a concrete rights-aware provider path; Stage A needs a bounded minimum editing-expression/effects floor without a monolithic Effects Engine; and the final Reference/B爆款 → Script Product Probe must show downstream speech/temporal/music/subtitle/transition evidence feeding back into Script/ShootingPlan planning.

These are integration requirements, not Stage-B polish.
