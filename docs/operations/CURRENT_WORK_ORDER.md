# Current Work Order

**ID:** `R0.12-PREVIEW-BACKEND-BENCHMARK-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Preview backend benchmark / ADR evidence  
**Mode:** EVIDENCE + ADR; no production Preview implementation yet  
**Accepted code baseline entering work:** `500c8563e3686a5aaef055ffb5301553aa999fd9`  
**Activated:** 2026-08-16  
**Codex release:** NO

## Why this work exists

R0.12 requires a practical interactive Windows Preview path, but Roadmap V2 and CAP-08 intentionally leave the backend family unfrozen. Selection must come from real Windows evidence rather than familiarity or UI preference.

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

Stage A does not require a flashy interface. It requires a practical, understandable and replaceable playback component that works across realistic Windows capability classes and admits a bounded packaging story later.

A backend does not win because it is fastest on one machine.

## Tool routing

### ChatGPT + GitHub

Primary control plane:

- current GitHub/CI observation;
- official runtime/license/provenance verification;
- benchmark design and evidence interpretation;
- small deterministic benchmark/governance writes;
- ADR and closure evidence;
- synchronization of live control documents.

### User PowerShell

Primary local evidence plane:

- Windows hardware/driver/runtime observation;
- controlled candidate preparation;
- playback/seek/scrub probes;
- CPU/RAM/GPU/process evidence;
- real private footage;
- local logs/screenshots when useful.

### Codex

**NOT RELEASED.**

Do not spend Codex quota on package discovery, installation, benchmarking, documentation or ADR reasoning. Reconsider only after a backend winner exists and bounded production integration materially benefits from repeated multi-file edit/test/repair loops.

## Constitutional / architecture constraints

1. EDL remains sole exact timeline authority.
2. PreviewBackend is playback-only.
3. Final render remains canonical EDL → Renderer; preview/proxy media is not quality authority.
4. Original user media is never overwritten.
5. CPU/software fallback remains part of the product strategy; GPU acceleration is optional capability routing.
6. Missing/broken acceleration must be diagnosable rather than an unexplained hard failure where fallback is practical.
7. No arbitrary third-party binary may become a product-distribution dependency without exact provenance/license/build evidence.
8. GUI/desktop framework remains undecided during this Work Order.
9. Proxy/cache, Graphics/transitions, Renderer operational controls and packaging are outside this Work Order.

## Environment classes

### Class A — degraded / low-end / fallback

Old CPU/iGPU, missing/basic driver, virtual-display interference or software-only decode/render. Tests degraded behavior and diagnosability.

### Class B — ordinary supported Windows

Current normal Windows hardware with functioning vendor GPU driver. This is the intended default-user performance class.

### Class C — newer / accelerated

Newer Intel/AMD/NVIDIA hardware with modern decode/render acceleration.

Missing Class-B/Class-C evidence must be recorded honestly rather than inferred from Class A.

## Stage 0 — environment and device capability — PASS

Durable evidence:

`docs/validation/R0.12_PREVIEW_STAGE0_WINDOWS_ENVIRONMENT_EVIDENCE.md`

Observed host:

- Lenovo ThinkPad T470s type 20JT / i5-6300U / Intel HD Graphics 520;
- Windows 11 build family 26100;
- approximately 19.88 GiB RAM;
- Oray virtual display present.

The same host has been preserved in two useful states:

1. degraded: Microsoft Basic Display Adapter;
2. restored vendor driver: Intel HD Graphics 520 `27.20.100.8854` from the Lenovo OEM path.

Project FFmpeg 8.1 confirms:

- deterministic fixture generation: PASS;
- software H.264 decode fallback: PASS;
- D3D11VA adapter initialization: PASS;
- adapter selected as `8086:1916 Intel(R) HD Graphics 520`;
- H.264 D3D11VA decode: 360/360 frames, 0 errors, exit 0.

The software-vs-hardware throughput values from the null-output capability probe are **not** Preview performance rankings; real playback/presentation/seek must be benchmarked through each candidate's actual path.

This host remains Class-A restored-vendor-driver evidence, not universal Class-B proof.

## Stage 1 — candidate provenance / preparation — ACTIVE

Current official-source gate:

### GStreamer

- current stable family observed: 1.28.6;
- official Windows x86_64 MSVC distribution exists;
- Windows 11 supported;
- 1.28 installers support current-user/private-directory installation and runtime-only mode;
- benchmark should use official MSVC x86_64 runtime, not a random third-party bundle;
- D3D11 capability and fallback/diagnostics will be tested directly.

### libVLC

- current stable Windows release observed: VLC 3.0.23;
- official VideoLAN 64-bit ZIP is available and suitable for isolated side-by-side benchmark preparation;
- libVLC/VLC codebase is published under LGPL 2.1 terms, but later product packaging still requires notices/runtime provenance review;
- benchmark should use official VideoLAN distribution only.

### libmpv

- upstream mpv is GPLv2-or-later by default;
- LGPLv2.1-or-later mode requires `-Dgpl=false`;
- official upstream Windows compilation documentation supports building shared libmpv and explicitly notes `-Dgpl=false` plus dependency review;
- common Windows mpv binaries are not automatically accepted as an LGPL product baseline;
- libmpv therefore remains a separate provenance/build gate and must not be represented by an arbitrary prebuilt binary.

## Stage 2 — benchmark corpus

Use both:

1. deterministic project-generated H.264/AAC fixture;
2. representative real user phone/camera footage, preferably including difficult/VFR material when available.

HDR/4K is tested only when suitable source/hardware exists; absence is recorded.

## Stage 3 — hard gates and comparative evidence

Each candidate must, or be excluded by a documented hard-gate reason:

- open/play media reliably;
- provide deterministic external seek/control suitable for a thin adapter;
- remain subordinate to canonical EDL authority;
- have an acceptable license/distribution path;
- support a practical deployment story without assuming a developer workstation;
- fail diagnosably;
- expose practical software/hardware fallback where feasible.

Compare:

- cold startup / first frame;
- repeated seek and scrub-like random seeks;
- stability after repeated control operations;
- CPU, RAM and GPU behavior;
- A/V behavior;
- difficult/VFR footage;
- hardware acceleration and fallback;
- external-control/API/IPC burden;
- runtime/package footprint;
- private deployment burden;
- diagnostic quality.

Do not invent a universal weighted score. Prefer hard gates plus transparent trade-offs.

## Stage 4 — decision / ADR

The Preview ADR must record exact tested versions/builds, environment class, corpus, commands/methodology, measurements, limitations, primary winner, rejected alternatives, fallback policy, packaging/license caveats and the invariant that PreviewBackend remains an adapter while EDL remains authority.

The ADR may select one primary backend plus a defined fallback strategy.

## Explicit STOP scope

This Work Order does **not** authorize production implementation of:

- GUI/desktop frontend;
- Proxy/cache;
- Renderer progress/cancellation/encoding routing;
- Graphics/transitions;
- EDL schema redesign;
- Domain authority changes;
- installer/packaging.

A small benchmark-only harness is allowed when justified; prefer private PowerShell tooling first.

## Exit gate

PASS only when:

- all three candidate families have reproducible Windows evidence or a documented hard-gate exclusion;
- environment capability is separated from backend capability;
- selection is based on deployment/compatibility/degradation plus playback performance;
- fallback/diagnostic behavior is recorded;
- exact license/build/runtime caveats are recorded;
- a Preview ADR is accepted;
- EDL/Renderer authority remains intact;
- the result is sufficient to define the next bounded Preview integration Work Order without reopening the backend-family question.

## Immediate next action

Prepare **GStreamer 1.28.6 MSVC x86_64 runtime** and **VLC/libVLC 3.0.23 win64** in isolated benchmark directories using official distributions and checksum verification. Do not alter global PATH.

After runtime verification, run the same deterministic fixture through both actual playback paths and collect startup/seek/scrub/resource/fallback evidence. Keep libmpv on its separate LGPL provenance/build gate until an auditable candidate is prepared.
