# Current Work Order

**ID:** `R0.12-PREVIEW-BACKEND-BENCHMARK-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Preview backend benchmark / ADR evidence  
**Mode:** EVIDENCE + ADR; no production Preview implementation yet  
**Accepted code baseline entering work:** `500c8563e3686a5aaef055ffb5301553aa999fd9`  
**Activated:** 2026-08-16  
**Codex release:** NO

## Why this work exists

R0.12 requires a practical interactive Windows Preview path, while Roadmap V2 and CAP-08 intentionally leave the backend family unfrozen. Selection must come from reproducible Windows evidence rather than familiarity or UI preference.

Candidate families:

1. GStreamer with D3D11 paths;
2. an auditable LGPL-configured libmpv build;
3. libVLC.

Preview is an adapter concern only. It must not gain EDL/timeline authority, rewrite source mappings, or determine final-render semantics.

## Product decision principle

Priority:

`deployability / compatibility / diagnosable degradation`
`>`
`stable external control / simple user operation`
`>`
`resource efficiency / acceleration`
`>`
`UI richness`

A backend does not win because it is fastest on one machine.

## Tool routing

### ChatGPT + GitHub

Primary control plane for current-state/CI observation, official runtime/license/provenance verification, benchmark design/evidence interpretation, deterministic governance/validation writes, ADR and Work Order closure.

### User PowerShell

Primary local evidence plane for Windows hardware/runtime behavior, private media, real playback/control probes and local diagnostics.

### Codex

**NOT RELEASED.** Preserve quota for a later bounded production integration or difficult multi-file runtime problem.

## Constitutional / architecture constraints

1. EDL remains sole exact timeline authority.
2. PreviewBackend is playback-only.
3. Final render remains canonical EDL → Renderer.
4. Original user media must never be overwritten.
5. CPU/software fallback remains part of the product strategy; GPU acceleration is optional capability routing.
6. Missing/broken acceleration must be diagnosable where fallback is practical.
7. No arbitrary third-party binary may become a product-distribution dependency without exact provenance/license/build evidence.
8. GUI/desktop framework remains undecided during this Work Order.
9. Proxy/cache, Graphics/transitions, Renderer operational controls and packaging remain outside this Work Order.

## Environment classes

- **Class A — degraded / low-end / fallback:** old CPU/iGPU, missing/basic driver, virtual-display interference or software decode/render.
- **Class B — ordinary supported Windows:** current normal Windows hardware with functioning vendor GPU driver.
- **Class C — newer / accelerated:** newer Intel/AMD/NVIDIA hardware.

Current accepted host is Class-A restored-vendor-driver evidence. Missing Class-B/Class-C evidence must not be inferred from it.

## Stage 0 — environment/device capability — PASS

Durable evidence:

`docs/validation/R0.12_PREVIEW_STAGE0_WINDOWS_ENVIRONMENT_EVIDENCE.md`

Accepted host/evidence includes Intel HD Graphics 520, restored Lenovo OEM driver `27.20.100.8854`, Oray retained, project FFmpeg software H.264 decode PASS, D3D11VA initialization PASS and 360/360 H.264 D3D11VA frames with zero errors.

## Stage 1 — candidate provenance/private runtime — PASS FOR GSTREAMER + VLC

Durable evidence:

`docs/validation/R0.12_PREVIEW_STAGE1_CANDIDATE_PREPARATION_EVIDENCE.md`

Accepted:

- GStreamer 1.28.6 official Windows x86_64 MSVC runtime, checksum/provenance checked, D3D11 decoder/sink present, private runtime;
- VLC/libVLC 3.0.23 official static win64 ZIP, size/SHA-256 checked, private runtime;
- benchmark execution does not depend on global executable PATH entries.

libmpv remains separately gated.

## Stage 2 — benchmark corpus

Accepted corpus now includes:

1. deterministic project-generated H.264/AAC fixture;
2. three real user phone HEVC files.

The three real-phone files did not contain observable VFR behavior in sampled frame timestamps. This is recorded as an evidence gap, not fabricated away.

## Stage 3 — hard gates and comparative evidence — COMPLETE FOR GSTREAMER + VLC ON CURRENT CLASS-A SCOPE

Durable evidence:

- `docs/validation/R0.12_PREVIEW_REAL_PLAYBACK_BENCHMARK_EVIDENCE.md`
- `docs/validation/R0.12_PREVIEW_WAVE3_REAL_MEDIA_SOFTWARE_FALLBACK_EVIDENCE.md`

### Wave 1 — actual playback — PASS

Both GStreamer 1.28.6 and VLC 3.0.23 completed actual windowed playback on the deterministic fixture. No winner was declared from process/resource proxies.

### Wave 2A — GStreamer actual hardware path — PASS

Actual high-level path proven:

`playbin3 → decodebin3 → d3d11h264dec → D3D11Memory/NV12 → d3d11videosink`

Manual `filesrc/qtdemux` proof experiments are retired and must not be reopened.

### Wave 2B — deterministic API control — PASS

GStreamer GstPlay and libVLC 3 both passed start, pause, eight randomized absolute seeks with target recovery, resume and clean release.

### Wave 3 — real phone HEVC + explicit software fallback — ACCEPTED WITH VFR GAP

Observed:

- GStreamer normal/auto: **3/3 PASS**;
- GStreamer explicit software-decode mode: **3/3 PASS**, with DOT evidence showing software decoder path and no discovered D3D hardware decoder factory active;
- libVLC normal/auto: **3/3 PASS**;
- libVLC explicit software-decode fallback: **PASS** after targeted configuration diagnosis.

Important libVLC configuration evidence:

- instance/global `--avcodec-hw=none` alone remained unreliable on this embedding path and still selected D3D11VA;
- per-media `:avcodec-hw=none` completed control successfully and logs showed `matching "none"` followed by `no hw decoder modules matched`;
- global + per-media also proved software decode;
- therefore future libVLC adapter work must use the tested per-media control rather than assume the global option is sufficient.

D3D11 presentation/output is not treated as hardware decoding.

Known Stage-3 evidence gaps retained:

- no actual VFR sample in the real-phone corpus;
- no Class-B/Class-C host evidence;
- no total no-GPU/no-presentation-device simulation.

These gaps do not justify reopening already accepted deterministic or real-HEVC playback/control evidence.

## Stage 4 — libmpv LGPL provenance/build gate — ACTIVE / NEXT

Before Preview ADR acceptance, resolve the third candidate family by one of two evidence-backed outcomes:

1. prepare an auditable Windows libmpv candidate configured for the approved LGPL path, including dependency/subproject license/build review; or
2. document a hard-gate exclusion if a reproducible acceptable Windows LGPL build/distribution path cannot be established without disproportionate product/license/deployment risk.

Hard rules:

- upstream/default GPL builds are not silently accepted for the product;
- arbitrary common third-party Windows mpv binaries are not product evidence;
- build flags alone are insufficient without dependency/subproject review;
- do not spend Codex quota on this provenance/build investigation.

## Final comparison / ADR after libmpv resolution

Compare with hard gates + transparent trade-offs, not a universal weighted score:

- deployability/private-runtime burden;
- compatibility/degraded behavior;
- software/hardware fallback and diagnostics;
- external control/embedding burden;
- observed resource behavior where comparable;
- licensing/distribution obligations;
- future proxy/cache compatibility.

The Preview ADR must select the primary backend, rejected alternatives/fallback policy, packaging/license caveats, tested environment/version scope and preserve the invariant that PreviewBackend is playback-only while EDL remains authority.

## Explicit STOP scope

This Work Order does **not** authorize production implementation of GUI/frontend, Proxy/cache, Renderer operational controls, Graphics/transitions, EDL redesign, installer/packaging or Domain authority changes.

After the Preview ADR, do **not** continue expanding player benchmarking without a specific unresolved product gate. Close the benchmark and return to Stage-A Product I/O/productization work.

## Exit gate

PASS only when:

- all three candidate families have reproducible Windows evidence or a documented hard-gate exclusion;
- environment capability is separated from backend capability;
- fallback/diagnostic behavior and license/runtime caveats are recorded;
- a Preview ADR is accepted;
- EDL/Renderer authority remains intact;
- the result is sufficient to define the next bounded Preview integration Work Order without reopening the backend-family question.

## Immediate next action

1. resolve the libmpv LGPL provenance/build gate;
2. perform the final GStreamer/VLC/libmpv comparison;
3. write and accept the Preview backend ADR;
4. close this benchmark;
5. keep Codex unreleased until a bounded production integration Work Order exists.
