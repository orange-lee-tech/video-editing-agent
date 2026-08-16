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

## Goal

Choose the Windows Preview backend family using reproducible evidence from the user's real Windows environment, with enough confidence to unblock later Preview integration, Proxy/cache design, packaging/runtime decisions and eventually the desktop/frontend ADR.

## Tool routing

### ChatGPT + GitHub — primary control plane

- inspect current architecture/roadmap/capability constraints;
- verify candidate official documentation, license/distribution posture and supported Windows integration surfaces before installation instructions are given;
- define the benchmark matrix and hard gates;
- interpret PowerShell evidence;
- write the final Preview ADR and closure evidence;
- keep repository governance synchronized.

### User PowerShell — primary execution plane

Use the real Windows machine for:

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
6. No arbitrary third-party binary may be adopted for commercial distribution without exact build/license/transitive/runtime evidence.
7. GUI/desktop framework remains intentionally undecided during this Work Order.

## Stage 0 — environment inventory

Before installing anything, capture:

- Windows version/build and architecture;
- CPU model / logical cores;
- RAM;
- GPU adapter(s), driver version(s), dedicated/shared memory where available;
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
- Python/native/IPC integration options relevant to this architecture;
- redistribution/package implications that affect later R0.14.

Do not install from random mirrors or unreviewed binary bundles.

## Stage 2 — benchmark corpus

Use both:

### Deterministic fixture

A reproducible local fixture generated/validated by FFmpeg, suitable for measuring startup, repeated seek and A/V playback behavior without content ambiguity.

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
- fail diagnosably rather than hanging or silently corrupting playback state.

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
- integration/control complexity;
- runtime/package footprint and redistribution burden.

Do not invent a universal weighted score unless the evidence later justifies one. Prefer hard gates + transparent trade-offs.

## Stage 4 — decision

Produce a Preview ADR that records:

- exact candidate versions/builds tested;
- Windows/hardware environment;
- test corpus;
- commands/methodology;
- raw or summarized measurements;
- known measurement limitations;
- winner and rejected alternatives;
- fallback policy if the preferred acceleration path is unavailable;
- packaging/license caveats deferred to R0.14;
- integration boundary: PreviewBackend remains an adapter and EDL remains authority.

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
- the preferred backend is selected by evidence, not preference;
- exact license/build/runtime caveats are recorded;
- a Preview ADR is accepted;
- the chosen boundary leaves EDL/Renderer authority intact;
- the result is sufficient to define the next bounded Preview integration or Proxy/cache Work Order without reopening the backend-family question.

## Immediate next action

User PowerShell performs Stage 0 inventory only. Do not install candidates yet. ChatGPT will use that inventory to prepare the exact candidate installation/benchmark commands from official current sources.