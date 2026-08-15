# Current Work Order

**ID:** `R0.12-SUBTITLE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — structured subtitle execution  
**Owner/writer:** Codex

## Objective

Build one complete deterministic subtitle path in which approved structured cues become canonical exact-time EDL execution data and are burned into a real MP4 through the existing EDL-driven FFmpeg Renderer using an ASS/libass baseline. Prove timing, escaping, layout intent and multilingual execution without moving subtitle wording policy or creative decisions into Renderer.

## Read

1. `docs/capabilities/CAP-08_EDL_RENDER_PREVIEW_SUBTITLE.md`
2. `src/video_editing_agent/domain/edl/model.py`
3. `src/video_editing_agent/domain/edl/codec.py`
4. `src/video_editing_agent/domain/edl/validation.py`
5. `src/video_editing_agent/render/edl_ffmpeg.py`

Use foreman `location` only if existing speech/transcript or EDL codec interfaces are unclear. Use `architecture` only for a genuine ownership ambiguity. Use `external` if FFmpeg/libass/font distribution licensing becomes a release-boundary question; do not block local engineering merely because a redistributable font is not yet selected.

## Required delta

- Add a small typed structured subtitle cue value/model sufficient for current CAP-08 semantics: stable cue identity, exact `MediaTimeRange`, text, language, optional speaker/ref, bounded emphasis spans/tokens and deterministic layout/safe-zone intent. Do not create a new top-level Domain Entity.
- Preserve the rule that ASR transcript is evidence/input, not automatically final subtitle wording. This batch consumes approved/structured cue text; it does not invent rewriting, translation or summarization policy.
- Extend canonical EDL only as much as required to make subtitle execution truth self-contained. Do **not** fake subtitle cues as media `EDLSegment`s with invented `asset_ref`/`source_range`. Prefer a subtitle-specific typed execution payload associated with an `EDLTrackFamily.SUBTITLE` track and exact EDL timeline ranges.
- Extend deterministic EDL v0.2 serialization/deserialization and validation for the subtitle payload. Canonical serialize → deserialize → canonical serialize must remain stable. Preserve rational time; no binary-float timing authority.
- Validator must diagnose rather than repair: duplicate cue IDs, invalid/unknown subtitle track, illegal timeline ranges, malformed emphasis spans, invalid language/layout data, unsupported overlap/shape semantics selected for this baseline, and any other locally provable invariant.
- Add a deterministic subtitle builder/compiler boundary that maps approved structured cues into canonical EDL subtitle execution data without changing cue wording or timing unless an explicit deterministic layout/splitting rule is owned there. If no splitting is needed for the baseline, keep it out rather than inventing policy.
- Extend the existing FFmpeg Renderer so it consumes canonical EDL subtitle data, emits a deterministic ASS artifact/filter invocation, and burns captions into the final MP4. Renderer may format/escape execution syntax; it must not rewrite text, retime cues or choose editorial emphasis.
- ASS generation must safely escape user text and paths so braces, backslashes, commas, colons, quotes, line breaks or shell-like text cannot escape typed execution. Keep `shell=False`; no raw model/provider shell fragments.
- Implement a bounded safe-zone/layout mapping and bounded keyword-emphasis representation consistent with CAP-08. Avoid a general typography engine, karaoke engine or motion-graphics system.
- Add deterministic unit/contract tests for cue model, EDL codec round-trip, validation, ASS escaping/timing and Renderer compilation.
- Add one small local Engineering Probe that generates/uses controlled video, burns at least English + Chinese structured cues, runs FFmpeg/libass, ffprobes the result, and proves captions altered pixels in the intended subtitle region at expected cue times. The probe may accept/use an explicitly supplied local Windows font if necessary; do not commit or redistribute proprietary font files. Record missing font/glyph support honestly rather than substituting OCR or claiming semantic glyph correctness from a render-success code alone.
- Keep the existing living Resolver → EDLBuilder → Renderer smoke green. Do not force subtitles into that smoke unless the integration is natural and low-cost; the living smoke should remain cheap.

## Hard boundaries

- EDL remains sole exact executable timeline authority.
- Subtitle builder/planner owns structured caption preparation; Renderer owns execution only.
- Do not use fake media Assets for text cues.
- Do not add Graphics/CTA/price cards, transitions, Preview, Proxy/cache, hardware routing, packaging or UI in this batch.
- Do not implement ASR transcription, translation, LLM rewriting, caption summarization, broad style recommendation, karaoke animation or a monolithic Effects Engine.
- No new third-party dependency unless a concrete blocker requires it; FFmpeg/libass baseline should use the existing toolchain where possible.
- Do not bundle a font or alter project licensing in this batch.

## Verification

Run focused subtitle/EDL/Renderer tests, the multilingual subtitle Engineering Probe, the existing living integration smoke if practical under the configured local toolchain, and the full repository Quality Gate. Preserve import contracts and `git diff --check`.

## Stop gate

Stop when structured cues → canonical exact-time EDL subtitle payload → deterministic ASS/libass Renderer → real MP4 is reproducible and green; deterministic codec/validation tests pass; multilingual probe evidence is recorded honestly; full Quality Gate passes; bounded reusable changes are committed/pushed; and the working tree is clean. Do not continue into Graphics, transitions, Preview or Proxy/cache.
