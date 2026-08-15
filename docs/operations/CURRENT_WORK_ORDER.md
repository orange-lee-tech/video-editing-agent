# Current Work Order

**ID:** `R0.12-SUBTITLE-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — structured subtitle execution audit closure  
**Owner/writer:** Codex

## Objective

Finish the existing structured-subtitle boundary by resolving the remaining execution-authority audit guards without broadening scope. Preserve the accepted body of the `12e4049c53a9597fba2a6654701d779d496b9433` candidate; do not advance into another R0.12 subsystem until subtitle execution is fail-closed and faithful to canonical EDL semantics.

## Read

1. `docs/capabilities/CAP-08_EDL_RENDER_PREVIEW_SUBTITLE.md`
2. `src/video_editing_agent/domain/edl/subtitle.py`
3. `src/video_editing_agent/domain/edl/validation.py`
4. `src/video_editing_agent/render/edl_ffmpeg.py`
5. `tests/unit/test_r0_12_subtitle_execution.py`
6. `tools/probes/r0_12_subtitle_live.py`

Use foreman `architecture` only if exact EDL→backend timing/layer ownership is genuinely ambiguous. Use `quality` only after a concrete verification failure. Do not preload unrelated R0.12 areas.

## Accepted candidate body

The implementation candidate already provides the intended Stage-A shape and should not be redesigned without evidence:

- approved `StructuredSubtitleCue` → canonical `EDLSubtitleCue` without fake media Assets;
- exact rational cue ranges retained in canonical EDL;
- language, optional speaker reference, bounded emphasis and upper/lower safe-zone intent;
- deterministic EDL schema v3 codec with v2 backward reading;
- validator diagnostics for duplicate IDs, track/range/text/language/layout/emphasis/overlap errors;
- deterministic ASS/libass burn-in through the existing EDL-driven Renderer;
- escaped subtitle text, typed process invocation and `shell=False`;
- English + Chinese region-pixel Engineering Probe with no unsupported semantic-glyph claim;
- living Resolver → EDLBuilder → Renderer smoke remains green.

## Required audit closure delta

- **Exact-time execution:** canonical EDL remains exact rational authority. The ASS backend must not silently `round()` arbitrary cue boundaries and thereby retime them. Either preserve exact semantics through an explicitly supported backend representation, or detect cue times that cannot be represented by the current ASS baseline and fail closed with a stable structured diagnostic before invocation. Do not change canonical cue timing to make the backend happy.
- **Subtitle track/layer semantics:** the Stage-A baseline must have one explicit deterministic rule for multiple SUBTITLE tracks. Either map supported EDL subtitle track/layer ordering into backend layer semantics without losing authority, or explicitly reject unsupported multi-track/layer input. Do not silently flatten distinct canonical layers into one ASS layer.
- **Path-escaping evidence:** keep the current escaping implementation if correct, but make the live/contract evidence exercise punctuation in the actual ASS filter path (for example a controlled parent directory containing comma/apostrophe) rather than treating a punctuated final MP4 filename as proof of filter-path escaping.
- Preserve the current v2 backward-read behavior and canonical v3 round-trip.
- Preserve the multilingual glyph limitation honestly: render/pixel evidence is engineering evidence; semantic glyph correctness remains a separate font/environment/Human-Gate question.
- Rerun focused subtitle tests/probe, the living integration smoke, and the full repository Quality Gate after the bounded closure repair.

## Hard boundaries

- EDL remains sole exact executable timeline authority.
- Renderer may encode supported backend syntax; it may not retime, relayer, rewrite or repair canonical subtitle decisions silently.
- Do not redesign the subtitle model, add a general typography engine, or expand EDL beyond a concrete closure blocker.
- No ASR rewriting/translation, karaoke, font redistribution, Graphics/CTA/price cards, transitions, Preview, Proxy/cache, hardware routing, packaging or UI.
- No new third-party dependency unless a concrete blocker proves it necessary.

## Verification

Focused subtitle/EDL/Renderer tests must cover non-centisecond rational cue timing and multi-SUBTITLE-track/layer behavior explicitly. Run the multilingual subtitle Engineering Probe, the living Resolver → EDLBuilder → Renderer smoke, the full repository Quality Gate, import contracts and `git diff --check`.

## Stop gate

Stop when the existing subtitle candidate is faithful or explicitly fail-closed for backend time/layer representability, the actual ASS filter-path punctuation case is exercised, all required checks are green, changes are committed/pushed, and the working tree is clean.

Do not continue into Graphics, transitions, Preview, Proxy/cache or another roadmap phase. Await Product Owner direction after subtitle closure.
