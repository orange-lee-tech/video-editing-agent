# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-16
current_phase: R0.12
phase_state: PREVIEW_BACKEND_BENCHMARK_ACTIVE
active_work_order: R0.12-PREVIEW-BACKEND-BENCHMARK-001
accepted_code_baseline: 500c8563e3686a5aaef055ffb5301553aa999fd9
control_plane_baseline: 529467389de11d49f9204558fc6190d3bfd51d42
previous_work_order: R0.12-EDITING-DIRECTOR-ENTRY-001
previous_work_order_result: PASS
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: STRUCTURAL_CONSTRUCTION
writer: chatgpt
---

## Routing truth

The accepted two-core architecture remains unchanged:

- Planning-only: `Brief → ScriptPlan → ShootingPlan`;
- Editing-only: `Brief/editorial intent + user local footage → Editing Core`;
- Combined: Planning artifacts optionally enrich the same Editing Core.

Accepted code baseline remains `500c8563e3686a5aaef055ffb5301553aa999fd9`. No new production code is authorized by the current benchmark Work Order.

## Current active boundary

`R0.12-PREVIEW-BACKEND-BENCHMARK-001` is ACTIVE.

Goal:

`real Windows environment classes + standardized media corpus`
`→ GStreamer D3D11 / approved LGPL libmpv / libVLC evidence`
`→ compatibility/deployment-backed Preview backend ADR`

The benchmark exists to unblock later interactive Preview integration and downstream desktop/frontend decisions without giving any playback library EDL/timeline authority.

## Product decision principle

The Preview decision is not a single-development-machine performance contest.

Priority:

`deployability / compatibility / diagnosable degradation`
`>`
`stable external control / simple operation`
`>`
`resource efficiency / peak acceleration`
`>`
`UI richness`

Stage A does not require a visually elaborate desktop. It requires a practical and understandable user path, predictable behavior across hardware classes, clean fallback when acceleration is unavailable where practical, and a future-extensible adapter boundary.

The product should prefer private/product-owned runtime components over assumptions that ordinary users manually configure global PATHs, developer SDKs or machine-wide multimedia stacks, unless later packaging evidence proves otherwise.

## Environment evidence classes

### Class A — degraded / fallback

Old/low-end hardware, generic/basic display driver, unavailable hardware decode, remote/virtual display interference or software decode/render fallback.

Purpose: verify graceful degradation and useful diagnostics.

### Class B — ordinary supported Windows

A normal current Windows system with a functioning vendor GPU driver and common integrated/discrete graphics capability.

Purpose: default-user performance and reliability evidence.

### Class C — newer accelerated Windows

A newer Intel/AMD/NVIDIA system with modern acceleration available.

Purpose: verify optional acceleration benefits without making them mandatory.

Do not infer universal product support from one class alone.

## Current observed environment

The current benchmark laptop reports Intel hardware ID `VEN_8086&DEV_1916`, but Windows is loading `Microsoft Basic Display Adapter` rather than a vendor Intel graphics driver. `OrayIddDriver` is also present as a virtual display device.

Therefore this machine is currently classified as **Class A degraded/fallback evidence**. Its present D3D11/hardware-decode measurements must not be used as the sole comparison of GStreamer/libmpv/libVLC acceleration quality.

The repository contains a project-controlled FFmpeg runtime under `.tools`; global `ffmpeg`/`ffprobe` absence from PATH is not by itself an environment failure and reinforces the product direction that user machines should not need manual global multimedia PATH setup.

## Tool routing

### ChatGPT + GitHub

Primary control/analysis channel:

- current official candidate/license/runtime verification;
- compatibility-first benchmark design;
- distinguish backend issues from OS/driver/hardware capability issues;
- evidence interpretation;
- ADR/governance writes;
- final acceptance.

### User PowerShell

Primary execution channel:

- Windows environment inventory;
- driver/capability verification;
- controlled candidate install after source approval;
- local media generation/use;
- playback/seek/resource measurements;
- logs and runtime evidence.

### Codex

**NO ACTIVE RELEASE.**

Remaining Plus/Codex quota is intentionally preserved. Do not spend Codex on environment discovery, package installation, benchmarking or ADR reasoning.

Reconsider Codex only after a backend winner exists and a later bounded integration task actually benefits from coherent multi-file execution or repeated modify→run→observe loops.

## Constitutional constraints

- EDL remains sole exact timeline authority.
- PreviewBackend is playback-only.
- final rendering remains canonical EDL → Renderer; preview/proxy media is not quality authority.
- original user media is never overwritten.
- CPU-only remains a supported baseline; GPU acceleration is optional routing.
- missing acceleration should be diagnosable and degrade safely where practical.
- no unreviewed third-party binary is adopted for product distribution.
- GUI/desktop framework remains undecided during this benchmark.
- backend replacement must remain localized behind the Preview adapter rather than rewriting Domain/EDL semantics.

## Current next action

Do not install Preview candidates yet.

Preserve the current machine as degraded/fallback evidence. Decide whether to restore a functioning Intel vendor driver for a second run on the same hardware or obtain separate ordinary-supported Windows evidence before treating hardware-accelerated benchmark results as representative.

## STOP boundary

Do not concurrently implement Graphics/transitions, Proxy/cache, Renderer operational controls, GUI/desktop frontend, packaging or EDL redesign while the benchmark is active.

## Remaining R0.12 terrain after Preview decision

- bounded Stage-A Graphics + minimal transitions;
- Preview integration based on the selected backend;
- Proxy/edit-friendly media + range-aware cache;
- Renderer progress/cancellation/diagnostics and controlled execution routing.

The order after the Preview ADR will be re-evaluated from actual evidence rather than assumed now.