# Current Work Order

**ID:** `R0.12-PREVIEW-BACKEND-BENCHMARK-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Preview backend benchmark / ADR evidence  
**Mode:** EVIDENCE + ADR; no production Preview implementation yet  
**Accepted code baseline entering work:** `500c8563e3686a5aaef055ffb5301553aa999fd9`  
**Activated:** 2026-08-16  
**Codex release:** NO

## Why this work exists

R0.12 still requires an interactive Windows execution experience. Roadmap V2 and CAP-08 explicitly leave the Preview backend unfrozen and require a real Windows benchmark rather than selecting a player by README familiarity or framework preference.

The candidate families are:

1. GStreamer with D3D11 paths;
2. an approved LGPL-configured libmpv build;
3. libVLC.

Preview is an adapter concern only. It must not gain EDL/timeline authority, rewrite source mappings, or determine final render semantics.

The result of this Work Order is a benchmark-backed ADR and a bounded integration recommendation. It is not yet a GUI implementation and is not permission to redesign Renderer, EDL, Proxy/cache or Domain models.

## Product principle for this decision

The Preview choice is a product-deployment decision, not a single-machine speed contest.

Priority is:

`deployability / compatibility / diagnosable degradation`
`>`
`stable external control / simple user operation`
`>`
`resource efficiency / peak acceleration`
`>`
`UI richness`

The product does not require a flashy interface at Stage A. It does require a practical, understandable and controllable path that can be extended later without forcing ordinary users to manually prepare a developer workstation.

A backend does not win because it is fastest on one machine. It must remain predictable across hardware classes, support software fallback where feasible, expose enough diagnostics to explain unavailable acceleration, and admit a bounded packaging story for later R0.14.

## Goal

Choose the Windows Preview backend family using reproducible evidence from real Windows environments, with enough confidence to unblock later Preview integration, Proxy/cache design, packaging/runtime decisions and eventually the desktop/frontend ADR.

The benchmark must distinguish backend quality from host-environment quality. Driver defects, unsupported acceleration or virtual-display interference are recorded as environment capability states rather than silently attributed to the backend.

## Tool routing

### ChatGPT + GitHub — primary control plane

- inspect current architecture/roadmap/capability constraints;
- verify candidate official documentation, license/distribution posture and supported Windows integration surfaces before installation instructions are given;
- define the benchmark matrix and hard gates;
- interpret PowerShell evidence;
- distinguish backend defects from driver/OS/hardware capability defects;
- write the final Preview ADR and closure evidence;
- keep repository governance synchronized.

### User PowerShell — primary execution plane

Use real Windows machines/environments for:

- environment inventory;
- candidate runtime/version discovery;
- controlled installation only after exact sources are approved;
- standardized playback/seek/scrub stress runs;
- CPU/RAM/GPU/process evidence collection;
- real phone-footage and deterministic fixture checks;
- logs and screenshots where useful.

Temporary benchmark outputs should stay outside durable Domain state and should not be confused with product artifacts.

### Codex — NOT RELEASED

Do not spend Codex quota on discovery, package installation, benchmark observation or ADR reasoning.

Codex may be reconsidered only after a backend winner exists and a later bounded implementation requires coherent multi-file integration or repeated modify→run→observe loops that are inefficient through PowerShell/manual patches.

## Constitutional/architecture constraints

1. EDL remains sole exact timeline authority.
2. PreviewBackend is playback-only; it does not move clips, select source timestamps, repair EDL or mutate authoritative decisions.
3. Final render quality remains owned by the canonical EDL + Renderer path; low-resolution proxy/preview media is not final source authority.
4. Original user media must never be overwritten.
5. CPU-only operation remains a supported baseline; GPU acceleration is optional capability routing, not a mandatory product assumption.
6. Missing/broken GPU acceleration must produce a diagnosable degraded state rather than an unexplained hard failure where software fallback is practical.
7. No arbitrary third-party binary may be adopted for commercial distribution without exact build/license/transitive/runtime evidence.
8. GUI/desktop framework remains intentionally undecided during this Work Order.
9. Preview integration must remain thin enough that replacing the backend later does not rewrite Domain, EDL or product workflow semantics.

## Environment classes

Do not treat one development laptop as the product hardware definition.

Evidence should be classified into at least these capability classes as practical:

### Class A — degraded / low-end / fallback environment

Examples:

- old CPU/iGPU;
- missing or basic display driver;
- hardware decode unavailable;
- virtual display/remote-display interference;
- software-decode/render fallback.

This class tests whether the product fails clearly or remains usefully operable at reduced performance.

### Class B — ordinary supported Windows environment

A normal current Windows machine with a functioning vendor GPU driver and common integrated/discrete GPU capability.

This is the main default-user performance class.

### Class C — newer/accelerated environment

A newer Intel/AMD/NVIDIA system where modern hardware decode/render paths are available.

This class tests whether the architecture can benefit from acceleration without making it mandatory.

Not all three classes must be physically available before the first ADR, but missing evidence must be recorded explicitly and must not be disguised as universal proof.

## Stage 0 — environment inventory

Before installing anything, capture:

- Windows version/build and architecture;
- CPU model / logical cores;
- RAM;
- GPU adapter(s), driver version(s), dedicated/shared memory where available;
- whether vendor GPU drivers or only generic/basic display drivers are active;
- virtual/remote display devices that may affect D3D adapter selection;
- current FFmpeg/ffprobe path + version/build configuration;
- Python/uv project baseline;
- presence/version/path of GStreamer, mpv/libmpv and VLC/libVLC if already installed;
- package-manager availability relevant to controlled candidate installation.

No candidate receives credit merely for already being installed.

## Stage 1 — candidate provenance / install gate

For each candidate, ChatGPT must verify against current official sources:

- supported Windows build/distribution channel;
- relevant license/build configuration;
- whether the runtime can be embedded/controlled without forcing timeline ownership upstream;
- hardware decode / D3D11 support expectations;
- software fallback behavior where documented;
- Python/native/IPC integration options relevant to this architecture;
- private/side-by-side deployment feasibility versus machine-wide prerequisites;
- redistribution/package implications that affect later R0.14.

Do not install from random mirrors or unreviewed binary bundles.

Prefer product-owned/private runtime deployment over requiring users to manually configure global PATH or preinstall developer SDKs, unless evidence shows a shared prerequisite is materially safer/simpler.

## Stage 2 — benchmark corpus

Use both:

### Deterministic fixture

A reproducible local fixture generated/validated by the project-controlled FFmpeg runtime, suitable for measuring startup, repeated seek and A/V playback behavior without content ambiguity.

### Real user footage

At least one representative phone/camera source from the user's actual target workflow. Prefer difficult material when available, such as high-resolution phone footage or VFR source.

HDR/4K cases are tested when the local hardware/source corpus makes them practical; absence of such a source is recorded rather than fabricated.

## Stage 3 — benchmark dimensions

### Hard gates

A candidate must:

- open and play the benchmark media reliably on Windows;
- support deterministic external seek/control suitable for a future application adapter;
- not require ownership of canonical timeline semantics;
- have an acceptable license/distribution path for the intended product direction;
- support a practical deployment story that does not assume a preconfigured developer machine;
- fail diagnosably rather than hanging or silently corrupting playback state;
- expose or permit a clear fallback path when preferred hardware acceleration is unavailable, where technically practical.

### Comparative evidence

Record where measurable:

- cold/startup latency;
- first-frame latency;
- repeated seek latency and seek stability;
- scrub-like repeated random-seek behavior;
- CPU utilization;
- process memory;
- GPU decode/3D utilization where observable;
- playback smoothness / dropped-frame or equivalent diagnostic evidence;
- audio/video behavior after repeated seeks;
- VFR/difficult-codec behavior;
- hardware acceleration behavior/fallback;
- behavior with generic/basic display driver versus functioning vendor driver when such evidence is available;
- integration/control complexity;
- runtime/package footprint and redistribution burden;
- amount of host-machine setup required;
- quality of diagnostics for missing codecs/drivers/runtime components.

Do not invent a universal weighted score unless the evidence later justifies one. Prefer hard gates + transparent trade-offs.

## Stage 4 — decision

Produce a Preview ADR that records:

- exact candidate versions/builds tested;
- Windows/hardware/driver environment class;
- test corpus;
- commands/methodology;
- raw or summarized measurements;
- known measurement limitations;
- winner and rejected alternatives;
- fallback policy if the preferred acceleration path is unavailable;
- minimum/recommended environment implications without prematurely freezing final system requirements;
- packaging/license caveats deferred to R0.14;
- integration boundary: PreviewBackend remains an adapter and EDL remains authority.

The ADR may select one primary backend plus a defined fallback strategy. It must not pretend all hardware behaves identically.

## Explicit STOP scope

This Work Order does **not** authorize substantive production implementation of:

- GUI/desktop frontend;
- Proxy/cache;
- Renderer progress/cancellation/encoding routing;
- Graphics/transitions;
- EDL schema redesign;
- Domain authority changes;
- packaging/installer.

If useful benchmarking requires a small temporary harness, prefer PowerShell/private tooling first. Any durable repository code must be separately justified and remain benchmark-only.

## Exit gate

PASS only when:

- all three candidate families have either reproducible real-Windows benchmark evidence or a documented hard-gate reason for exclusion;
- environment capability state is separated from backend capability state;
- the preferred backend is selected by compatibility/deployment evidence plus performance, not preference or single-machine peak speed;
- software/hardware fallback behavior and diagnostic expectations are recorded;
- exact license/build/runtime caveats are recorded;
- a Preview ADR is accepted;
- the chosen boundary leaves EDL/Renderer authority intact;
- the result is sufficient to define the next bounded Preview integration or Proxy/cache Work Order without reopening the backend-family question.

## Current Stage 0 evidence

The first observed machine is a Lenovo-class low-end/legacy Windows environment with Intel hardware ID `VEN_8086&DEV_1916`, but Windows currently loads `Microsoft Basic Display Adapter` instead of a vendor Intel display driver. An `OrayIddDriver` virtual display device is also present. This environment is therefore classified as **Class A degraded/fallback evidence**, not a valid sole basis for comparing D3D11 hardware-acceleration performance.

The repository also contains its own FFmpeg runtime under `.tools`; absence of global `ffmpeg`/`ffprobe` on PATH is therefore not by itself a project-environment defect. Product deployment should not assume users configure a global FFmpeg PATH.

## Immediate next action

Do not install Preview candidates yet.

First confirm the display/driver capability state and preserve this machine as a useful degraded/fallback sample. Then decide whether to restore a normal vendor Intel driver for an additional Class B-like run or obtain ordinary-supported hardware evidence elsewhere. Candidate installation and benchmark commands will be prepared only from reviewed official sources.