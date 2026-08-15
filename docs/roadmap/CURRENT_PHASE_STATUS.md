# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL CONSTRUCTION  
**Current phase:** R0.12 — EDL / Renderer / Subtitle / Preview / Proxy Productization  
**Engineering state:** AUDIT HOLD — `R0.12-SUBTITLE-001` candidate implemented, closure guards remain  
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

## Accepted R0.12 structural baselines

- `ff343833deb9296c1df0b6fc944735388d5c8296` — typed EDL tracks, deterministic composition and structured validation.
- `4b2522ae1a6838517baf4c5bcf36d30026f86912` — exact rational spatial/audio automation plus deterministic EDL codec/round-trip.
- `b6c5684a9b07d79f20a10d28886cd087eaeecf10` — deterministic grounded decision-to-EDL assembly.
- `83fc2999297023f828fa77719cd357fe82eab5de` — deterministic EDL-driven FFmpeg Renderer.
- `9f06386f9f311fe241f250f4679fa6b2042699b0` — living Resolver → EDLBuilder → Renderer → ffprobe/final-pixel integration smoke.

## Subtitle implementation candidate

`12e4049c53a9597fba2a6654701d779d496b9433` — `feat: add structured subtitle execution`.

Independent review confirms substantial success:

- one bounded fast-forward commit and remote `ci/quality-gate-diagnostic` success;
- structured approved cues compile into subtitle-specific canonical EDL payload rather than fake media segments;
- EDL artifact schema advances to v3 while v2 artifacts remain readable;
- canonical round-trip preserves exact rational cue ranges, text, language, speaker reference, emphasis and layout intent;
- validation diagnoses duplicate ID, invalid track/range/text/language/layout/emphasis and same-track overlap without repair;
- Renderer consumes canonical cues, emits deterministic ASS and burns them through FFmpeg/libass with typed argv and `shell=False`;
- live Engineering Probe reports 7/7 PASS, with English lower-safe and Chinese upper-safe region pixel changes and zero change between cues;
- the probe explicitly does not claim semantic Chinese glyph correctness and redistributes no font;
- reported full Quality Gate: Ruff, mypy 184 files, 538 tests, import contracts, build and diff check all pass; living integration smoke remains 10/10 PASS.

## Subtitle audit guards before closure

Two items are structural execution guards, not Stage-B polish:

1. **ASS time representability.** Canonical EDL stores exact rational cue times, but the current ASS writer converts them with `round(time * 100)` to centiseconds. The existing probe uses centisecond-aligned cue boundaries, so it does not expose this. Renderer must not silently retime a non-representable rational boundary; the backend must preserve it or fail closed explicitly.
2. **Multiple subtitle tracks/layers.** EDL supports typed tracks with composition layers; validation currently rejects overlap per subtitle track, while ASS generation flattens all cues into `Layer 0`. Until a deterministic layer mapping exists, unsupported multi-track/layer subtitle input must fail closed rather than silently lose EDL composition semantics.

One additional evidence gap is smaller: the live output filename contains comma/apostrophe, but the generated ASS artifact path does not. The filter-path escaping implementation is plausible and Windows drive-colon execution is real, but punctuation in the actual subtitle filter path should be exercised before claiming that part fully proven.

The default/fallback font and semantic correctness of multilingual glyph shapes remain downstream environment/release/product-quality concerns unless broader evidence turns them into a structural blocker.

## Hold state

Do not start Graphics, transitions, Preview, Proxy/cache or further Renderer expansion while this audit hold is open. No new downstream work order is activated here.

The next Product Owner decision may choose how to sequence the remaining R0.12 surfaces, but subtitle closure should first remove the small execution-authority ambiguity above.

## Downstream structural constraints

R0.16 one-click execution must use actual VisualUnderstanding evidence in Retrieval/Resolver; a visual-only automatic-BGM promise requires a concrete rights-aware provider path; Stage A needs a bounded minimum editing-expression/effects floor without a monolithic Effects Engine; and the final Reference/B爆款 → Script Product Probe must show downstream speech/temporal/music/subtitle/transition evidence feeding back into Script/ShootingPlan planning.

These are integration requirements, not Stage-B polish.
