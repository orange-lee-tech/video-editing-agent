# ADR-005 — ASS/libass as Standard Subtitle Rendering Baseline

**Status:** PROVISIONAL  
**Date:** 2026-08-11

## Context

Commercial short-form video needs deterministic multilingual subtitles, timing, font/style emphasis, outline/shadow and safe positioning. Raw `drawtext` filtergraphs become difficult to manage for complex text/escaping/layout.

## Decision

Use structured subtitle cues as product semantics and target:

```text
SubtitleCue[]
→ ASS representation
→ libass / approved FFmpeg subtitle backend
```

for standard captions/emphasis.

Use a separate deterministic motion-graphics capability for complex CTA/price/chart/title animation.

## Consequences

- normal subtitles do not depend on a browser/UI renderer;
- subtitle semantics stay separate from backend file format;
- complex graphics do not force ASS to become a universal motion-graphics language.

## Gates

Benchmark multilingual shaping, Windows font discovery/embedding strategy, render fidelity and safe-zone behavior before final styling presets are frozen.
