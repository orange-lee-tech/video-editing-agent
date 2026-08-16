# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-16
current_phase: R0.12
phase_state: PREVIEW_REAL_PLAYBACK_BENCHMARK_ACTIVE
active_work_order: R0.12-PREVIEW-BACKEND-BENCHMARK-001
accepted_code_baseline: 500c8563e3686a5aaef055ffb5301553aa999fd9
control_plane_baseline: 4901067df74553a121e3ec5978b3e999a91cb9a2
structural_progress_percent: 90
stage_a_completion_gate: OPEN
core_1_planning_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
core_2_editing_product_gate: FOUNDATION_PASS_USER_FLOW_OPEN
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

Accepted production-code baseline remains `500c8563e3686a5aaef055ffb5301553aa999fd9`. The active Work Order is evidence/ADR work only; no new Preview production implementation is authorized yet.

## Stage-A completion truth

Structural progress remains **90%**.

Canonical hard gate:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Live state:

- `stage_a_completion_gate: OPEN`;
- Core 1 Planning: foundation accepted, ordinary-user product flow still open;
- Core 2 Editing: foundation accepted, ordinary-user automatic final-MP4 flow still open.

100% remains forbidden until both core Product Gates and the overall Stage-A gate are `PASS`.

## Current active boundary

`R0.12-PREVIEW-BACKEND-BENCHMARK-001` is ACTIVE.

Current state:

`prepared private candidate runtimes`
`→ real Windows playback/control benchmark`
`→ auditable libmpv gate`
`→ Preview backend ADR`

PreviewBackend remains playback-only. EDL remains sole exact timeline authority.

## Current Preview evidence state

### Stage 0 — environment/device capability — PASS

Durable evidence:

`docs/validation/R0.12_PREVIEW_STAGE0_WINDOWS_ENVIRONMENT_EVIDENCE.md`

Observed Class-A host:

- ThinkPad T470s type 20JT, i5-6300U, Intel HD Graphics 520;
- Windows 11 build family 26100;
- Oray virtual display present;
- earlier degraded state preserved with Microsoft Basic Display Adapter;
- Lenovo OEM Intel driver successfully restored to `27.20.100.8854` without removing Oray.

Project FFmpeg capability probe:

- deterministic 1080p H.264/AAC fixture generation: PASS;
- software decode fallback: PASS;
- D3D11VA device initialization: PASS;
- selected physical adapter: `8086:1916 Intel(R) HD Graphics 520`;
- H.264 D3D11VA decode: 360/360 frames, 0 errors, exit 0.

The software-vs-D3D11VA null-output throughput numbers are capability evidence only and are not used to rank Preview backends.

### Stage 1 — candidate provenance/private runtime — PASS FOR GSTREAMER + VLC

Durable evidence:

`docs/validation/R0.12_PREVIEW_STAGE1_CANDIDATE_PREPARATION_EVIDENCE.md`

GStreamer 1.28.6:

- official SHA-256 matched;
- private current-user runtime prepared;
- `d3d11videosink` registered;
- `d3d11h264dec` registered against Intel HD Graphics 520;
- D3D11-memory decode/presentation surface present;
- plugin reports LGPL.

VLC/libVLC 3.0.23:

- official static ZIP size and SHA-256 matched;
- private runtime contains `vlc.exe`, `libvlc.dll`, plugins;
- `--ignore-config --intf dummy` isolated startup exits `0` with no `vlcrc` load failure.

Wave-1 preflight confirmed:

- no GStreamer/VLC executable is available from global PATH;
- benchmark root is absent from User PATH and Machine PATH;
- both candidates are therefore exercised through explicit private paths rather than developer-machine global setup.

### Stage 3 — real playback/control benchmark — ACTIVE

Durable evidence:

`docs/validation/R0.12_PREVIEW_REAL_PLAYBACK_BENCHMARK_EVIDENCE.md`

Wave 1 on the deterministic 1080p H.264/AAC fixture:

- both GStreamer 1.28.6 and VLC 3.0.23 completed actual windowed playback;
- GStreamer first-observed window proxy approximately `518 ms`, max working set approximately `139.7 MiB`, average machine CPU estimate approximately `10.2%`;
- VLC first-observed window proxy approximately `838 ms`, max working set approximately `291 MiB`, average machine CPU estimate approximately `6.0%`;
- VLC logs explicitly prove D3D11VA hardware decode on Intel HD Graphics 520;
- GStreamer logs prove active D3D11 presentation/device activity, while auto-selected H.264 decoder still needs direct Wave-2 proof before claiming hardware-decode selection from this playback run;
- one GStreamer-enumerated D3D11 device reported unsupported video-device interface on this host; playback nevertheless completed and the diagnostic remains retained rather than hidden by removing Oray;
- no backend winner is declared from Wave 1.

Measurement caveats:

- `FirstWindowMs` is a window-handle appearance proxy, not exact first-frame latency;
- the first PowerShell process wrapper did not reliably preserve the displayed child `ExitCode` on this host and must be corrected for Wave 2;
- local benchmark residue `vlc-help.txt` appeared as an untracked repository file and must be removed, not committed.

### libmpv

Still separately gated:

- GPL by default;
- LGPL path requires `-Dgpl=false` plus dependency/build review;
- arbitrary common Windows binaries remain unapproved.

### Missing hardware classes

Class-B ordinary-current-Windows and Class-C accelerated evidence remain missing and must not be implied from the T470s host.

## Current benchmark action

Wave 2 is next.

On the same deterministic fixture:

- remove local `vlc-help.txt` benchmark residue;
- obtain direct GStreamer `d3d11h264dec → d3d11videosink` playback evidence;
- preserve reliable child exit status;
- run deterministic repeated absolute seek and scrub-like random-seek control for both candidates;
- observe post-seek playback/A-V recovery, stability, CPU/RAM and diagnostics;
- do not disable Oray unless a repeatable adapter-selection defect requires an isolation experiment.

Official control surfaces are sufficient for this decision: GstPlay supports absolute time seek and seek-done messages; libVLC 3 exposes time/position control. GUI clicking is not accepted as sole control evidence.

Representative user/VFR footage follows only after deterministic control is stable.

## Tool routing

### ChatGPT + GitHub

- current-state/CI observation;
- official dependency/license/runtime verification;
- benchmark design and evidence interpretation;
- small deterministic governance/validation writes;
- Preview ADR and Work Order closure.

### User PowerShell

- private runtime execution;
- real Windows playback/seek/scrub/resource probes;
- private media evidence;
- hardware/runtime diagnostics.

### Codex

**NO ACTIVE RELEASE.** Preserve remaining quota for later bounded production integration or difficult multi-file runtime debugging.

## Final-10-percent execution corridor

Do not open these concurrently without an explicit dependency:

1. finish R0.12 productization floor;
2. minimum Review/repair loop;
3. ordinary-user Windows runtime / Environment Doctor;
4. plain product-facing integration for both real cores;
5. real Stage-A Product Probes / Human Gate, then and only then structural 100%.

The Stage-A product I/O impact audit remains recorded separately and does not interrupt the current Preview Work Order.

## Constitutional constraints

- EDL remains sole exact timeline authority.
- PreviewBackend is playback-only.
- final rendering remains canonical EDL → Renderer.
- original user media is never overwritten.
- CPU/software fallback remains a supported strategy; GPU is optional routing.
- no unreviewed third-party binary is adopted for product distribution.
- GUI/desktop framework remains undecided during this benchmark.
- no temporary shortcut may fabricate Planning artifacts, source timestamps, Domain decisions or a Product Gate PASS.

## Documentation synchronization rule

Dynamic state is canonical only in:

- `docs/operations/CURRENT_CONTROL_STATE.md`;
- `docs/operations/CURRENT_WORK_ORDER.md`;
- `docs/roadmap/CURRENT_PHASE_STATUS.md`.

`tools/maintenance/repo_doctor.py` + `repository-governance` check machine-detectable consistency. Stable entry files point here instead of duplicating phase snapshots.

## STOP boundary

Do not concurrently implement Graphics/transitions, Proxy/cache, Renderer operational controls, GUI/desktop frontend, packaging or EDL redesign while the Preview benchmark is active unless the Work Order is explicitly revised.
