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
4. Original user media must never be overwritten.
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

## Stage 1 — candidate provenance / preparation — PASS FOR GSTREAMER + VLC

Durable evidence:

`docs/validation/R0.12_PREVIEW_STAGE1_CANDIDATE_PREPARATION_EVIDENCE.md`

### GStreamer 1.28.6

Preparation accepted:

- official Windows x86_64 MSVC installer SHA-256 matched official sidecar;
- current-user private runtime installation succeeded;
- `gst-launch-1.0` / `gst-inspect-1.0` present;
- `d3d11videosink` present;
- `d3d11h264dec` present and identifies Intel HD Graphics 520;
- D3D11-memory NV12 output path exposed;
- plugin reports LGPL.

Packaging caveat retained: the downloaded official installer reports Authenticode `NotSigned`; product packaging later requires explicit provenance/notices policy rather than assuming installer signing.

### VLC/libVLC 3.0.23

Preparation accepted:

- official static VideoLAN win64 ZIP size and SHA-256 matched exactly;
- ZIP magic validation and extraction PASS;
- private runtime contains `vlc.exe`, `libvlc.dll`, and plugins;
- isolated startup with `--ignore-config --intf dummy` exits `0` without a `vlcrc` load error.

### Runtime isolation

Wave-1 preflight confirms:

- `gst-play-1.0`, `gst-launch-1.0`, `gst-inspect-1.0`, and `vlc` are not available through global PATH;
- benchmark root is absent from User PATH and Machine PATH;
- both candidates are exercised through absolute private-runtime paths.

### libmpv

Still separately gated:

- upstream mpv is GPLv2-or-later by default;
- LGPLv2.1-or-later mode requires `-Dgpl=false` plus dependency/build review;
- arbitrary prebuilt Windows binaries are not accepted as product evidence.

## Stage 2 — benchmark corpus

Use both:

1. deterministic project-generated H.264/AAC fixture;
2. representative real user phone/camera footage, preferably including difficult/VFR material when available.

HDR/4K is tested only when suitable source/hardware exists; absence is recorded.

## Stage 3 — hard gates and comparative evidence — ACTIVE

Durable evidence:

`docs/validation/R0.12_PREVIEW_REAL_PLAYBACK_BENCHMARK_EVIDENCE.md`

### Wave 1 — actual windowed playback — COMPLETE

Same deterministic 1080p H.264/AAC fixture and same Class-A restored-vendor-driver host.

Observed:

- both GStreamer 1.28.6 and VLC 3.0.23 completed actual windowed playback;
- GStreamer first-observed-window proxy approximately `518 ms`, max working set approximately `139.7 MiB`, average machine CPU estimate approximately `10.2%`;
- VLC first-observed-window proxy approximately `838 ms`, max working set approximately `291 MiB`, average machine CPU estimate approximately `6.0%`;
- VLC logs directly prove D3D11VA hardware decode on Intel HD Graphics 520;
- one enumerated GStreamer D3D11 device reported unsupported video-device interface, but playback completed; retain this as degraded-environment diagnostic evidence rather than hiding it by removing Oray;
- no backend winner is declared from Wave 1.

Measurement caveat: `FirstWindowMs` is not exact first-frame latency.

### Wave 2A — GStreamer actual hardware path — PASS

Actual high-level playback proof used canonical file URI, `playbin3`, `uridecodebin3/decodebin3`, `GST_PLUGIN_FEATURE_RANK=d3d11h264dec:MAX`, `d3d11videosink`, private runtime, and DOT graph capture.

Observed:

- process exit code `0`;
- five pipeline state-transition DOT graphs captured;
- actual graph contains `GstD3D11H264Dec:d3d11h264dec0`;
- actual graph contains `GstD3D11VideoSink:d3d11videosink0`;
- decoder context reports `Intel(R) HD Graphics 520`, vendor `8086`, device `1916`, `hardware=true`;
- 1920x1080@30 H.264 constrained-baseline input enters `d3d11h264dec0`;
- output remains NV12 `video/x-raw(memory:D3D11Memory)` through the playback graph into the D3D11 sink.

GStreamer hardware decode/presentation proof is closed. Do not reopen manual demux experiments.

### Wave 2B — deterministic API control / seek / scrub — PASS

The accepted file-based harness validated Windows PowerShell 5.1, Python 3.13.14, the private GStreamer MSVC GstPlay runtime, the private VLC/libVLC runtime, the deterministic fixture and a clean repository working tree before candidate execution.

Observed:

- GStreamer GstPlay control process exit code `0`;
- VLC/libVLC 3 control process exit code `0`;
- `GStreamer API control PASS = True`;
- `VLC API control PASS = True`;
- final `WAVE 2B API CONTROL PASS` marker;
- repository remained clean.

The candidate PASS markers are emitted only after start, pause with bounded drift, eight repeated absolute randomized seeks with target recovery, resume with timeline advancement, and clean stop/release checks complete.

The terminal summary did not expose the individual numeric seek-proxy payloads, so no mean/max seek latency ranking is accepted from this run. Behavioral control reliability is accepted; precise numeric comparison remains optional evidence if it becomes decision-critical.

### Wave 3 — real/VFR + software fallback — NEXT

Next evidence:

- representative real phone/camera footage, preferably including VFR;
- explicit software/fallback behavior and diagnostics for the leading candidates;
- preserve Oray unless a repeatable adapter-selection issue requires isolation;
- keep Class-B/Class-C evidence gaps explicit;
- compare runtime/deployment burden only with observed artifacts and official license/build facts.

## Stage 4 — decision / ADR

Before ADR acceptance, resolve the third candidate family:

- prepare an auditable LGPL-configured libmpv candidate, or
- document a hard-gate exclusion if a reproducible, acceptable Windows distribution/build path cannot be established without disproportionate product risk.

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

A small benchmark-only harness is allowed when justified; prefer private file-based PowerShell/Python tooling over giant interactive blocks.

## Exit gate

PASS only when:

- all three candidate families have reproducible Windows evidence or a documented hard-gate reason for exclusion;
- environment capability is separated from backend capability;
- selection is based on deployment/compatibility/degradation plus playback performance;
- fallback/diagnostic behavior is recorded;
- exact license/build/runtime caveats are recorded;
- a Preview ADR is accepted;
- EDL/Renderer authority remains intact;
- the result is sufficient to define the next bounded Preview integration Work Order without reopening the backend-family question.

## Immediate next action

1. run representative real/VFR footage through GStreamer and VLC/libVLC using the now-proven playback/control surfaces;
2. exercise explicit software/fallback behavior and record diagnostic quality;
3. inspect persisted Wave-2B stdout only if precise seek-proxy numbers become decision-critical;
4. resolve the libmpv LGPL provenance/build gate through official build/license evidence;
5. compare deployment/runtime footprint and embedding/control burden;
6. write and accept the Preview backend ADR;
7. keep Codex unreleased until a bounded production integration Work Order exists.
