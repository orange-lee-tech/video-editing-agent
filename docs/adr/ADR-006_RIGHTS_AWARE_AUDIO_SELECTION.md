# ADR-006 — Rights-Aware Coarse-to-Fine Music Selection

**Status:** ACCEPTED  
**Date:** 2026-08-11

## Context

Music fit depends on semantics, mood, energy, duration and temporal structure, but a technically excellent track is unusable if its commercial/project/platform rights are incompatible. A short video also needs a specific moment from a longer track, not merely a track ID.

## Decision

Music selection uses:

```text
rights-compatible candidate pool
→ cheap provider metadata/tag retrieval
→ optional semantic audio-text retrieval
→ Top-K
→ BeatMap/temporal reranking
→ grounded CandidateMusicWindow
→ MusicSelectionDecision
```

A rights/license snapshot is attached before final selection/EDL use.

Audio mixing/ducking/fades are planned structurally and executed deterministically by local tools.

## Consequences

- remote/public audio remains constitutionally separate from forbidden remote visual sourcing;
- `royalty-free` alone is not treated as universal license proof;
- model/checkpoint license is independent of code license;
- large CLAP-like models are optional and benchmark-gated rather than mandatory.
