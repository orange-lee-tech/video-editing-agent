# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL CONSTRUCTION  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** ACTIVE — `R0.12-SUBTITLE-001`  
**Updated:** 2026-08-15

## Progress meaning

Canonical stage model: `docs/roadmap/DEVELOPMENT_STAGE_MODEL.md`.

The current 0–100% project percentage measures **structural construction**: end-to-end capability closure with correct authority, extensibility, deterministic execution, compatibility and safe failure behavior.

Reaching 100% will begin a separate product-refinement stage; it will not mean commercial quality is already perfect.

## Closed

- R0.7A — Architecture v0.2 Migration Foundation.
- R0.7B — Brief → ScriptPlan → ShootingPlan + commercial-authority baseline.
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
- `9f06386f9f311fe241f250f4679fa6b2042699b0` — living Resolver → EDLBuilder → Renderer → ffprobe/final-pixel integration smoke.

## Living smoke accepted

Independent review confirms:

- `main` is exactly `9f06386f9f311fe241f250f4679fa6b2042699b0` and is one commit ahead of the previous docs baseline;
- remote `ci/quality-gate-diagnostic` is success;
- the probe invokes actual `optimize_sequence()` rather than hand-authoring final selections;
- selected source windows `1/4 + 1s` and `1/2 + 1s` survive unchanged into canonical EDL;
- final output is 2.000 s, 320×192, 30 FPS and contains source audio under PRESERVE;
- final-frame pixel sampling independently proves red → blue visual order in the rendered MP4;
- no ReframeDecision/Spatial automation is fabricated merely to enrich the gate;
- the five temporary `tmp-renderer-nav-sync*` branches are gone;
- reported full Quality Gate: 523 tests plus Ruff/mypy/import contracts/build/diff check.

This closes the previous Renderer final-image evidence gap for ordered clip execution. It does not claim a real VisualUnderstanding-driven one-click workflow.

## Active R0.12 frontier

`R0.12-SUBTITLE-001` establishes the first complete structured subtitle execution path.

CAP-08 requires structured cues before backend rendering, exact EDL timeline authority, ASS/libass baseline, safe-zone layout, keyword emphasis and multilingual coverage. The current EDL exposes a `SUBTITLE` track family but its media `EDLSegment` shape cannot carry cue text/language/layout semantics without inventing fake media source mappings. A narrowly scoped subtitle-specific canonical execution payload is therefore an allowed concrete EDL extension; do not generalize this into a broad overlay/effects framework.

After subtitle execution is green, continue Graphics, remaining Renderer operational work, Preview and Proxy/cache. The Stage-A minimum transition vocabulary remains a downstream R0.12/R0.16 structural requirement and must be closed before Stage-A completion, but it is not part of the subtitle batch.

## Downstream structural constraints

The R0.16 one-click chain must use actual VisualUnderstanding evidence in Retrieval/Resolver; a visual-only automatic-BGM promise requires a concrete rights-aware provider path; Stage A needs a bounded minimum editing-expression/effects floor without a monolithic Effects Engine; and the final Reference/B爆款 → Script Product Probe must show downstream speech/temporal/music/subtitle/transition evidence feeding back into Script/ShootingPlan planning.

These are integration requirements, not Stage-B polish.
