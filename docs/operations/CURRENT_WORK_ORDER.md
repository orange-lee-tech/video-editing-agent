# Current Work Order

**ID:** `R0.12-RENDERER-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — EDL-driven FFmpeg render foundation  
**Owner/writer:** Codex

## Objective

Create the first deterministic Renderer boundary that consumes canonical EDL v0.2 as its sole timeline authority and produces a locally verifiable MP4 through FFmpeg without inventing, repairing or reinterpreting editorial decisions.

## Read

1. `src/video_editing_agent/domain/edl/`
2. `src/video_editing_agent/render/spatial_plan_ffmpeg.py`
3. `docs/capabilities/CAP-08_EDL_RENDER_PREVIEW_SUBTITLE.md`

Use foreman trigger `location` only if existing artifact/path/runtime conventions are not obvious. Use `architecture` only for a genuine ownership ambiguity. Use `external` if a concrete FFmpeg distribution/license/provider uncertainty is encountered; do not preload release research.

## Required delta

- Add a typed application Renderer boundary or equivalent request/result contract with explicit `OutputSpec`, `RenderArtifact` and structured failure diagnostics. Renderer receives a canonical EDL plus explicit local Asset-to-media resolution; it must not consult Resolver/SpatialComposer/AudioEditorial as alternate authority.
- Implement an FFmpeg-backed deterministic renderer for the current builder-emitted EDL surface. Validate the EDL before execution and fail closed on unsupported track families, automation kinds, time mappings, missing assets or impossible execution semantics.
- Preserve exact rational source/timeline authority through planning. Convert rational values to backend adapter syntax deterministically at the FFmpeg boundary; binary floating-point must not become timeline authority.
- Execute VIDEO segments at their EDL source ranges and exact timeline order. Support current EDL spatial HOLD/LINEAR crop automation by compiling the EDL automation itself. Reuse safe R0.11 compiler ideas where useful, but do not keep `SpatialTransformPlan` as Renderer authority.
- Execute the current builder-emitted SOURCE_AUDIO/BGM semantics, including MUTE-vs-PRESERVE distinction and only those gain/fade/duck/loop mappings that are deterministic from typed EDL. Unsupported audio semantics must return structured diagnostics rather than guess.
- Build FFmpeg invocation as deterministic argv/filter-graph data; do not use model/provider shell fragments and do not require `shell=True`.
- Keep output settings explicit. The Stage-A baseline may use a narrow local MP4 profile suitable for Engineering Probe evidence, but codec/container choices must not be mistaken for a commercial distribution decision and no third-party binary may be bundled/downloaded in this batch.
- Produce one small deterministic Engineering Probe using synthetic/local generated media that actually renders MP4 and verifies the artifact with ffprobe. The probe should demonstrate at minimum: timeline order/duration, expected canvas, spatial execution, and an observable audio-policy case. Keep generated media/artifacts under ignored private/temp paths.
- Add focused deterministic unit/integration tests for planning, fail-closed behavior and subprocess argument construction, then run the full repository Quality Gate.

## Hard boundaries

- EDL is the sole exact executable timeline authority.
- Renderer executes; it does not repair, move, rescore, reframe, remix or fill missing editorial decisions.
- Existing `spatial_plan_ffmpeg.py` is an earlier execution adapter, not a competing timeline authority. Preserve useful deterministic math or migrate it behind the EDL-driven renderer as appropriate.
- No direct LLM/provider-generated commands or timing.
- No automatic stock/generative media fallback for missing assets.
- No bundled FFmpeg binary or commercial codec/license conclusion in this batch.
- Do not implement Subtitle, Graphics, Preview, Proxy/cache, hardware routing, packaging or UI in this batch.

## Verification

Run focused Renderer tests and the actual synthetic Engineering Probe, verify the resulting MP4 with ffprobe, then run the repository full Quality Gate. Preserve import contracts and `git diff --check`.

## Stop gate

Stop after canonical EDL v0.2 can deterministically produce and verify the bounded local MP4 baseline, with unsupported semantics failing closed, all required checks green, changes committed/pushed and the working tree clean. Do not continue into Subtitle, Preview, Proxy/cache or later Renderer refinement.
