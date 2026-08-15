# Architecture Decision Records

**Status:** Candidate ADR set for Architecture Contract v0.2 / Roadmap V2

ADRs record important concrete choices that should not be hidden inside implementation code. They sit below the Product Constitution and Architecture Contract.

## Current ADRs

- `ADR-001_FFMPEG_PRIMARY_RENDER_BACKEND.md`
- `ADR-002_GROUNDED_AI_NO_FREEFORM_TIMESTAMPS.md`
- `ADR-003_LOCAL_HYBRID_RETRIEVAL_BASELINE.md`
- `ADR-004_LAYERED_BEAM_SEARCH_OPTIMIZER_BASELINE.md`
- `ADR-005_ASS_LIBASS_STANDARD_SUBTITLES.md`
- `ADR-006_RIGHTS_AWARE_AUDIO_SELECTION.md`
- `ADR-007_SPATIAL_COMPOSER_AUTO_REFRAME.md`
- `ADR-008_DEPENDENCY_LICENSE_CHAIN_GATE.md`
- `ADR-009_TWO_CORE_WORKFLOWS_PARALLEL_ENTRY.md`

## Status meanings

- **ACCEPTED** — architecture-level decision supported strongly enough to build around.
- **PROVISIONAL** — preferred first implementation/baseline, but benchmark can replace it behind the same capability seam.
- **DEFERRED** — consciously not selected yet.
- **SUPERSEDED** — replaced by a later ADR.

A PROVISIONAL ADR is not weak architecture: it freezes the seam and experiment method while keeping replaceable technology choices replaceable.
