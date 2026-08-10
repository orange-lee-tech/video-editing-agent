# ADR-001 — FFmpeg as Primary Deterministic Render Backend

**Status:** ACCEPTED  
**Date:** 2026-08-11

## Context

The product needs a reliable programmable executor for trim/concat/crop/scale/overlay/audio/subtitle/transcode/proxy/QC operations. EDL is already the sole exact timeline authority, so adopting a full NLE engine as the primary semantic layer would create a second rich timeline model.

## Decision

Use an `FFmpegRenderer` implementation family as the primary deterministic render backend behind `RendererPort`.

Use `ffprobe` as the primary local technical-media probe family.

FFmpeg does not become Domain authority and does not receive natural-language creative instructions.

## Consequences

Positive:

- broad mature media capability;
- headless/deterministic execution;
- excellent fit for generated filtergraphs from EDL;
- local CPU baseline plus hardware acceleration;
- common foundation for proxy, audio and QC.

Costs:

- complex filtergraph generation/escaping must be hidden behind typed builders;
- approved distribution build required;
- codec/patent review is separate from FFmpeg copyright license;
- interactive preview may still use another backend.

## Release gate

Production distribution records exact version/configuration/external libs/hashes/build recipe/notices and codec/legal review.

Do not redistribute arbitrary third-party FFmpeg binaries.
