# CAP-08 — EDL, Renderer, Subtitle, Preview, Proxy and Cache

**Status:** CANDIDATE CAPABILITY SPEC  
**Architecture:** `ARCHITECTURE_CONTRACT_V0.2.md`  
**Scope:** Validated decisions → executable timeline → local preview/render/output

---

## 1. Purpose

Convert approved structured editing decisions into deterministic media execution while preserving EDL as the sole exact timeline authority.

This capability should be boring in the best sense: once EDL is valid, rendering should not require creative AI decisions.

---

## 2. Ownership

```text
EDLBuilder / TimelineAllocator → EDL
EDLValidator                   → deterministic validation result
Renderer                       → RenderArtifact
Subtitle/Graphics builders     → structured track artifacts/proposals
PreviewBackend                 → interactive playback only
DerivativeMediaService         → proxies/edit-friendly media
ArtifactStore                  → files/cache
```

Renderer never mutates EDL to “make it work”.

---

## 3. EDL inputs

Possible inputs:

- EditPlan revision;
- ResolutionDecision(s);
- BeatMap/music alignment context;
- ReframeDecision(s);
- MusicSelectionDecision;
- AudioMixDecision;
- voiceover/subtitle/graphics artifacts;
- OutputSpec.

EDLBuilder rejects incomplete/incompatible decisions.

---

## 4. EDL tracks

Conceptual track families:

```text
video
source_audio
BGM
voiceover
SFX
subtitle
title/overlay/graphics
```

Track representation must support deterministic ordering/composition.

---

## 5. EDLSegment source mapping

Every media segment contains authoritative source mapping and exact timeline placement.

Conceptual required data:

```text
asset_ref
optional shot_ref
source_range: MediaTimeRange
timeline_range: MediaTimeRange
playback rate / time mapping
track
```

Source range must be legal under Asset/Shot constraints.

---

## 6. Timeline authority

Only EDL defines authoritative:

```text
timeline_in
timeline_out
track placement
```

Resolver supplies grounded source choices and timing feasibility but not final timeline coordinates.

BeatMap does not place clips.

Renderer does not move them.

---

## 7. Time-varying spatial transforms

EDL must support Auto Reframe and other deterministic animation via a transform curve/keyframes.

Concepts:

```text
crop center x(t)
crop center y(t)
scale/zoom(t)
position(t)
opacity(t)
optional rotation(t)
interpolation semantics
```

Static transforms are a special case.

---

## 8. Time-varying audio automation

EDL audio semantics should support:

- gain envelope;
- fades;
- crossfades;
- mute/preserve-source ranges;
- loop/source mapping;
- pan/channel routing where needed;
- deterministic ducking/sidechain instruction where supported.

One static `audio_gain` is insufficient.

---

## 9. Subtitle semantic layer

Subtitle content/timing should exist as structured cues before backend rendering.

Conceptual cue:

```text
text
timeline range
speaker/ref optional
emphasis tokens/style intent
layout region
language
```

ASR transcript is not automatically final subtitle wording.

SubtitlePlanner may:

- split/merge readable cues;
- apply user edits;
- emphasize keywords;
- enforce safe-zone/layout policy.

---

## 10. Subtitle render layers

Preferred layered strategy:

### Standard captions

```text
structured cues
→ ASS
→ libass/FFmpeg
```

Good for:

- normal subtitles;
- emphasis/color/font/outline/shadow;
- multilingual text;
- deterministic burn-in.

### Complex motion graphics

Use a dedicated deterministic graphics renderer/provider for:

- CTA cards;
- price cards;
- charts;
- animated titles;
- sophisticated typography/layout.

No one component needs to own both simple captions and every future motion-graphics feature.

---

## 11. FFmpeg baseline

FFmpeg/ffprobe is the preferred primary deterministic media backend family for:

- probe/decode;
- trim/concat;
- scale/crop/overlay;
- audio mix/filter;
- subtitle burn-in;
- transcode;
- proxy generation;
- technical QC;
- final encode.

Production distribution requires an approved build profile and separate license/patent review.

---

## 12. Renderer Port

Conceptual interface:

```text
render(edl_ref, output_spec)
→ RenderArtifact
```

Backend may be swapped/extended.

First long-term default candidate: FFmpegRenderer.

Rich NLE backends remain optional adapters, not Domain authority.

---

## 13. OpenTimelineIO position

OTIO may support:

- rational-time utilities;
- interchange;
- export adapters.

Preferred direction:

```text
our Domain EDL
├─ FFmpeg render adapter
└─ OTIO interchange adapter
```

OTIO does not replace EDL authority.

Professional interchange formats are later product capability, not first output requirement.

---

## 14. Output

Initial user-facing formal export:

```text
MP4
```

OutputSpec controls:

- canvas/resolution;
- fps/timebase;
- codec/container profile;
- audio profile;
- quality target;
- platform preset where selected.

Codec choices are release/ADR decisions.

---

## 15. Edit-friendly media

For VFR/difficult source formats:

```text
Original Asset
→ Edit-Friendly Artifact
```

with authoritative source-time mapping.

This may simplify seeking/analysis but never replaces Asset identity.

---

## 16. Proxy

Proxy addresses heavy source decode/seek.

```text
Original/Edit-Friendly
→ low-cost Proxy
→ interactive preview
```

Proxy profile may be selected adaptively from Environment Doctor benchmarks.

Final render does not use low-resolution proxy as source quality authority.

---

## 17. Timeline preview cache

Different problem from proxy:

> timeline effects/compositing are too expensive to calculate interactively.

Use chunk/range preview rendering:

```text
EDL range
→ PreviewChunk Artifact
```

When one EDL range changes:

```text
compute affected range
→ invalidate only overlapping chunks
→ background rebuild
```

---

## 18. Preview backend

Candidate families include:

- GStreamer D3D11;
- LGPL-configured libmpv;
- libVLC;
- optional richer GES/MLT backends if justified.

Selection requires Windows product benchmark, not README preference.

Preview backend has no timeline authority.

---

## 19. Cache classes

Rebuildable:

- proxies;
- thumbnails;
- waveforms;
- preview chunks;
- temporary extracted frames;
- temporary render graph artifacts.

Durable derived evidence is not cleared by generic cache cleanup.

UI should show storage location/size and class-specific cleanup.

---

## 20. Hardware routing

Backend chooses hardware path according to capability/task.

Possible acceleration:

- Media Foundation;
- Intel QSV/oneVPL;
- AMD AMF;
- NVIDIA NVENC/NVDEC;
- D3D11 video paths.

Do not make GPU mandatory.

Hardware decode is not automatically best for CPU analysis if GPU→RAM transfer dominates.

---

## 21. Codec/distribution gate

Before commercial Windows release preserve:

```text
FFmpeg version
configure flags
enabled external libs
binary hashes
source/build recipe
notices
codec/patent review status
```

OSS license compliance and codec patent/licensing are separate questions.

Do not redistribute arbitrary third-party binaries.

---

## 22. EDL validation

Deterministic checks include:

- source range within Asset/Shot;
- legal rational time mapping;
- no invalid overlap;
- track validity;
- assets available;
- supported transforms/effects;
- transition ranges feasible;
- audio automation valid;
- output duration constraints;
- locks respected;
- no unconstitutional visual source.

Failure returns structured diagnostics.

---

## 23. Render technical QC

After render use local probes/filters for:

- decode success;
- duration/resolution/fps;
- audio presence;
- black frames;
- freeze;
- silence;
- loudness/peak;
- PTS/time continuity;
- subtitle/overlay bounds where measurable;
- codec/container profile.

Do this before paying a VLM to review the output.

---

## 24. Benchmarks

### Renderer

- known EDL → deterministic expected media;
- cross-platform/time rounding;
- visual/audio sync;
- transform accuracy;
- subtitle accuracy;
- render speed/quality.

### Preview

- startup latency;
- scrub/seek;
- 4K phone footage;
- VFR/HDR cases;
- CPU/GPU/RAM;
- integration complexity.

### Proxy/cache

- generation time;
- seek speed;
- size;
- final-original mapping;
- range invalidation correctness.

### Codec

- quality/bitrate;
- encode speed;
- compatibility;
- CPU/GPU availability.

---

## 25. Not frozen here

- exact EDL JSON/schema syntax;
- OTIO adoption scope;
- preview backend winner;
- proxy resolution/codec;
- approved FFmpeg build flags;
- H.264 encoder backend;
- graphics renderer implementation;
- final subtitle font/style presets;
- professional interchange formats.
