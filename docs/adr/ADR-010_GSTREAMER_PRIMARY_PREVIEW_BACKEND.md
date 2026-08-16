# ADR-010 — GStreamer Primary Preview Backend

**Status:** ACCEPTED  
**Date:** 2026-08-16

## Context

R0.12 requires a practical interactive Windows Preview component, but Preview is not the editing timeline authority. The selection was intentionally delayed until real Windows evidence existed for candidate families:

1. GStreamer D3D11;
2. libVLC;
3. an auditable LGPL-configured libmpv candidate or a documented hard-gate exclusion.

The product decision priority is:

`deployability / compatibility / diagnosable degradation`
`>`
`stable external control / simple user operation`
`>`
`resource efficiency / acceleration`
`>`
`UI richness`

Canonical EDL remains the sole exact timeline authority. PreviewBackend only plays media/timeline positions requested by the application and cannot repair or reinterpret EDL.

## Decision

**GStreamer is the primary Stage-A Preview backend family.**

Initial accepted runtime/evidence baseline:

- GStreamer `1.28.6` Windows x86_64 MSVC private runtime;
- high-level control surface through GstPlay/playbin3 rather than hand-authored demux pipelines;
- D3D11 hardware path where available;
- explicit software video-decode fallback when hardware decode is unavailable/disabled;
- runtime/capability discovery and understandable diagnostics rather than assuming a preconfigured workstation.

Production integration must remain behind the existing replaceable `PreviewBackend` adapter seam. This ADR selects a backend family, not a new Domain authority.

## Evidence supporting GStreamer

Accepted R0.12 validation includes:

- official Windows runtime provenance/checksum evidence;
- private runtime independent of global executable PATH;
- actual windowed playback PASS on the Class-A restored-vendor-driver host;
- real high-level hardware path directly proven as:

`playbin3 → decodebin3 → d3d11h264dec → D3D11Memory/NV12 → d3d11videosink`;

- GstPlay deterministic control PASS for start, pause, eight randomized absolute seeks with target recovery, resume and clean release;
- three real user phone HEVC files: normal/auto path 3/3 PASS;
- the same three real HEVC files: explicit software-decode path 3/3 PASS with DOT topology evidence showing software decoding and no discovered D3D hardware decoder active;
- degraded-environment diagnostics remained visible while Oray virtual display was retained instead of being removed to make the benchmark cleaner.

On the deterministic fixture and one Class-A host, GStreamer also showed a lower observed peak working set and earlier first-window proxy than VLC. These measurements are supporting evidence only and are **not** the reason for selection.

## Hardware/software fallback policy

Stage-A production integration should implement the following bounded routing semantics:

1. discover relevant GStreamer runtime/device capability;
2. prefer the normal high-level playback path and allow supported D3D11 hardware decode/presentation to autoplug;
3. when hardware decode is unavailable, explicitly disabled or proven defective, demote/disable the relevant hardware decoder factories and permit software video decode;
4. retain presentation acceleration where it remains valid — software decoding does not require pretending the whole GPU is absent;
5. surface understandable diagnostic state when playback cannot initialize rather than silently rewriting media/timeline semantics.

A complete no-GPU/no-presentation-device simulation was not performed and is not implied by this ADR.

## libVLC disposition

libVLC `3.0.23` is **not rejected as technically unsuitable**. It remains a validated alternative backend family behind the same adapter seam.

Accepted libVLC evidence includes:

- official private runtime provenance;
- actual windowed playback PASS;
- D3D11VA hardware decode proof on Intel HD Graphics 520;
- deterministic API control PASS;
- real-phone HEVC normal playback/control 3/3 PASS;
- explicit software video decode PASS when per-media `:avcodec-hw=none` is used.

It is not selected as the Stage-A primary because:

- the tested global/instance `--avcodec-hw=none` option was unreliable in the embedding path and still selected D3D11VA;
- the correct per-media fallback control adds a configuration caveat that must be remembered by any future adapter;
- on the same Class-A deterministic fixture its observed peak working set was materially higher and its first-window proxy later, although it used less measured CPU in that run;
- there is no demonstrated product requirement that justifies shipping two complete playback runtimes in Stage A.

Therefore **libVLC is not bundled as an automatic cross-backend fallback by default**. If future Product Probes expose a GStreamer-specific compatibility failure that libVLC uniquely solves, the existing adapter boundary permits revisiting this decision without changing Domain/EDL semantics.

## libmpv disposition

libmpv is **hard-gate excluded for Stage A**, recorded in:

`docs/validation/R0.12_PREVIEW_LIBMPV_LGPL_HARD_GATE_EXCLUSION.md`

The exclusion is based on deployability/licensing/maintenance burden, not a claim that libmpv cannot play the media.

Upstream mpv supports LGPL mode with `-Dgpl=false` and shared libmpv, but the required Windows D3D11 candidate would make this project own a custom build and transitive dependency/license-notice closure. After bounded investigation, that burden is disproportionate while GStreamer and libVLC already satisfy the actual Preview product gates.

## Deployment and licensing consequences

The production Preview integration must:

- use an application/private GStreamer runtime rather than depend on an arbitrary user-global installation;
- record exact runtime version/provenance;
- package only the required runtime/plugin surface where practical and maintain the applicable LGPL/notices obligations;
- avoid silently loading unrelated GPL/proprietary plugin dependencies outside the approved runtime manifest;
- provide Environment Doctor/capability evidence for missing/broken runtime components;
- preserve CPU/software decode as a supported degraded strategy.

The benchmark's official GStreamer installer signing caveat remains a packaging concern to resolve during Windows product-owned deployment; it does not transfer authority into the backend.

## Compatibility scope and known gaps

Accepted evidence is strongest for the observed Class-A host:

- ThinkPad T470s;
- Intel HD Graphics 520;
- Lenovo OEM Intel driver `27.20.100.8854`;
- Oray virtual display present.

Still missing and **not implied**:

- ordinary Class-B current-Windows host evidence;
- Class-C newer Intel/AMD/NVIDIA evidence;
- an actual VFR file in the real-phone corpus;
- total no-GPU/no-presentation-device operation.

These become ordinary integration/Product-Probe risks rather than reasons to keep the backend-family benchmark open indefinitely.

## Authority invariants

This ADR does not change:

- EDL = sole exact executable timeline authority;
- Renderer = final quality/execution authority for canonical EDL;
- PreviewBackend = playback-only adapter;
- original user media is never overwritten;
- proxy/edit-friendly media remains derivative and cannot replace original Asset identity/final-render authority;
- Planning-only, Editing-only and Combined entry semantics.

## Consequences

Positive:

- one primary Windows Preview family is now frozen strongly enough for bounded production integration;
- hardware and software-decode behavior is observable and tested on real media;
- private-runtime/deployment direction is supported by upstream Windows packaging;
- pipeline diagnostics are unusually strong for later Environment Doctor work;
- the adapter remains replaceable.

Costs:

- GStreamer has a larger modular/plugin surface than a single-purpose thin player library;
- production packaging must deliberately control plugin/runtime contents and notices;
- GstPlay/D3D11 integration still requires a bounded production adapter implementation and user-facing diagnostics.

## STOP rule

The backend-family benchmark is closed by this ADR.

Do **not** continue adding player benchmarks merely because more codecs, machines or metrics could be tested. New backend-family investigation requires a concrete Product Probe failure or a new hard product requirement.

The project now returns to the Stage-A product input/output and ordinary-user productization corridor.
