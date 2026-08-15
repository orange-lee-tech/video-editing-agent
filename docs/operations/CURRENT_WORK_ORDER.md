# Current Work Order

**ID:** `R0.12-EDL-002`  
**Status:** ACTIVE  
**Phase:** R0.12 — EDL v0.2 automation + serialization  
**Owner/writer:** Codex

## Objective

Extend the canonical EDL with exact typed time-varying spatial/audio automation and deterministic rational v0.2 serialization/round-trip, while keeping existing R0.10/R0.11 decisions as upstream authority/provenance rather than reimplementing their editorial logic.

## Read

1. `src/video_editing_agent/domain/edl/model.py`
2. `src/video_editing_agent/domain/edl/validation.py`
3. `docs/capabilities/CAP-08_EDL_RENDER_PREVIEW_SUBTITLE.md`

Use foreman trigger `location` only if existing R0.10/R0.11 decision types, serialization conventions or EDL consumers are not obvious. Use `architecture` only for a real ownership ambiguity.

## Required delta

- Add canonical typed spatial automation sufficient to represent exact crop/scale/position-style execution over timeline/source time, with explicit deterministic interpolation semantics and rational keyframe time.
- Add canonical typed audio automation sufficient for current EDL execution needs such as gain/mute/fade/loop-style envelopes where already justified by R0.10 outputs; do not invent a DAW or duplicate AudioEditorial policy.
- Keep existing spatial/audio decision references as provenance/traceability where useful; executable automation belongs in EDL rather than Renderer guesswork.
- Add deterministic EDL v0.2 serialization/deserialization using exact rational media-time values and explicit schema/version semantics. No binary-float time authority.
- Preserve deliberate compatibility with existing EDL construction/persisted forms where practical; fail explicitly on unsupported or ambiguous legacy data rather than guessing.
- Extend deterministic validation for automation invariants: legal ranges, stable keyframe ordering/uniqueness, supported interpolation/value semantics, and segment/track compatibility where locally provable.
- Add focused deterministic tests and an Engineering Probe proving exact round-trip plus valid/invalid spatial/audio automation behavior.

## Hard boundaries

- EDL remains the sole exact executable timeline authority.
- SpatialComposer and AudioEditorial remain upstream decision owners; EDL records executable results, not new creative policy.
- Renderer will execute typed EDL later; do not implement Renderer productization now.
- No raw model/provider shell fragments or hidden timing decisions.
- No new dependency unless a concrete blocker triggers the external route.
- Do not implement Subtitle, Graphics, Preview, Proxy/cache or UI in this batch.

## Verification

Run focused EDL automation/serialization tests and Engineering Probe, then the repository full Quality Gate. Preserve import contracts and `git diff --check`.

## Stop gate

Stop after typed EDL automation + deterministic v0.2 serialization/round-trip are green, committed/pushed, and the working tree is clean. Do not continue into EDLBuilder/Renderer or other R0.12 deliverables.
