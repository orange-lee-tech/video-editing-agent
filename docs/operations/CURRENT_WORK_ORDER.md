# Current Work Order

**ID:** `R0.12-WINDOWS-ENVIRONMENT-DOCTOR-001`  
**Status:** ACTIVE  
**Phase:** R0.12 — Windows Environment Doctor / ordinary-user runtime readiness  
**Mode:** PRODUCT INTEGRATION / CAPABILITY DISCOVERY  
**Accepted production-code baseline:** `2cfeb664552769ade09f58bc2905ab531733a66a`  
**Activated:** 2026-08-17  
**Codex release:** NO

## Previous Work Order result

`R0.12-MINIMUM-REVIEW-REPAIR-LOOP-001` — **PASS / CLOSED**.

Accepted production baseline:

`2cfeb664552769ade09f58bc2905ab531733a66a`

Closure evidence:

`docs/validation/R0.12_MINIMUM_REVIEW_REPAIR_CLOSURE.md`

Bounded Windows real-media Review run:

`32033179672` — PASS.

The production Review path accepted clean media, returned typed `CORRECTION_REQUIRED / RETURN_TO_AUDIO_EDITORIAL` for a real AAC silent-track defect, preserved exact EDL provenance and did not mutate delivered media.

## Why this work exists

Stage-A 100% explicitly forbids assuming a preconfigured developer workstation.

The repository already has strong individual runtime proofs, but ordinary Windows usability is still fragmented across:

- Python 3.12 package execution;
- FFmpeg / ffprobe requirements used by ingest, extraction, render and Review;
- a private GStreamer Preview runtime;
- provider-specific API-key requirements;
- optional local model/runtime components;
- developer-oriented PowerShell Probe/install scripts.

Today an ordinary user can still encounter a low-level missing executable, missing runtime, missing key or unsupported capability before the product explains what is actually available on the machine.

This Work Order creates the smallest reliable **Environment Doctor** machine-fact boundary. It does not choose the final installer technology.

## Source contracts

Canonical capability direction:

- `docs/capabilities/CAP-10_DEPLOYMENT_SECURITY_AUTONOMY.md`
- `docs/research/LOCAL_TOOLBOX_AND_DEPLOYMENT.md`
- `docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Frozen principles:

```text
hardware capability != software capability
feature listed       != feature proven ready
GPU absent            != basic product unusable
missing optional path != silent fallback
machine/provider data != Domain creative authority
```

## Objective

Create one product-owned diagnostic surface that can answer, in typed and sanitized form:

1. whether the host is a supported Stage-A Windows environment;
2. whether the running Python satisfies the product minimum;
3. whether FFmpeg and ffprobe are resolvable and can execute a tiny deterministic probe;
4. whether the approved Preview private runtime can initialize through the production Preview seam when configured;
5. whether required cloud provider credentials are configured **without exposing their values**;
6. what optional capabilities are absent versus merely degraded;
7. which capabilities block Planning, Editing, Preview or local media execution;
8. what the ordinary user should repair next;
9. how the product can rerun the same probes after repair.

## Frozen status vocabulary

Use the CAP-10 semantics, subject only to implementation-level naming compatibility:

- `READY`
- `AVAILABLE_AFTER_INSTALL`
- `AVAILABLE_BUT_SLOW`
- `HARDWARE_BLOCKED`
- `CLOUD_FALLBACK`
- `UNAVAILABLE`

A capability may also carry typed product-impact metadata, but do not create an unrelated second status taxonomy.

## Minimum Stage-A capability set

### Host runtime

Inspect at least:

- operating system / Windows support status;
- Python runtime version;
- architecture;
- practical free disk information for the selected working location when available.

Do not make CPU model or GPU presence a hard basic-product gate by itself.

### FFmpeg / ffprobe

Do not mark ready from `PATH` presence alone.

Minimum proof:

```text
resolve executable
→ execute bounded version/probe command
→ validate successful process result
→ record normalized version/capability evidence
```

The check must remain argument-array/direct-process based; no shell command construction from media/provider text.

### Preview

If a GStreamer private-runtime location is configured, readiness must be based on the production Preview runtime initialization contract, not merely directory existence.

If no packaged/configured private Preview runtime exists, report a typed install/configuration state. Do not silently switch backend families.

### Cloud intelligence configuration

At minimum inspect configuration presence for the providers currently used by accepted product paths:

- `DEEPSEEK_API_KEY` — Planning + Director;
- `GEMINI_API_KEY` — supported visual-understanding provider;
- `OPENAI_API_KEY` — supported visual-understanding provider.

Rules:

- never include secret values in Environment Doctor result, logs or repair report;
- presence is configuration evidence, **not** a live provider-connectivity PASS;
- Gemini/OpenAI are alternative supported visual paths; both are not required;
- network/provider outages remain separate runtime failures.

### Optional local capabilities

The Doctor may report currently detectable optional local model/runtime paths, but this first batch must not become an installer for Torch, CUDA, ASR, embedding or tracking packages.

Unknown optional capability must not falsely block deterministic local editing/rendering that does not require it.

## Product-impact model

Each finding should be attributable to a product capability such as:

- `planning_cloud`
- `editing_cloud_director`
- `visual_understanding`
- `media_probe_render`
- `preview_playback`
- `optional_local_acceleration`

The aggregate result must preserve per-capability states. Do not collapse everything into one misleading boolean `environment_ok`.

## Repair report

Generate a copyable, sanitized report suitable for the user or an external assistant.

It may include normalized OS/runtime facts, component/status/product impact, concise repair guidance and a request to rerun Environment Doctor after repair.

It must not include API-key values, OAuth tokens/cookies, full environment dumps, unrelated personal paths, media-derived untrusted text or arbitrary model-generated shell commands.

When installation guidance is needed, prefer official-source wording and never advise disabling security controls.

## Application ownership

Expected layering:

```text
EnvironmentDoctor application owner
→ replaceable capability-probe ports
→ Windows/tool/provider/private-runtime adapters
→ typed EnvironmentReport
```

Environment Doctor may inspect capability and generate sanitized guidance. It may not mutate Domain creative state, EDL, assets, rights state or project decisions, and it may not automatically install arbitrary dependencies in this Work Order.

## CLI / product-facing seam

A minimal CLI exposure is allowed and desirable as an Engineering/Product integration seam, but CLI-only success does **not** complete the ordinary-user Product Gate.

Prefer a project-independent command shape if it fits current parser ownership, conceptually:

```text
video-editing-agent doctor
```

Do not force Environment Doctor to create or edit a project merely to inspect the machine.

## Required deterministic tests

Cover at least:

1. supported Windows + compatible Python → host runtime ready;
2. non-Windows Stage-A host is reported honestly, not crashed;
3. FFmpeg missing → typed install-required state;
4. FFmpeg present but execution fails → not READY;
5. FFmpeg + ffprobe bounded probe success → READY;
6. Preview runtime missing/unconfigured → typed non-ready without backend switch;
7. Preview runtime probe success → READY;
8. DeepSeek key missing blocks relevant cloud configuration without exposing secret text;
9. present provider key is reported only as configured, never echoed;
10. Gemini/OpenAI visual alternatives do not require both keys;
11. optional GPU/local acceleration missing does not make deterministic core falsely unavailable;
12. generated repair report contains no supplied secret value;
13. untrusted filenames/media text cannot become repair command authority;
14. aggregate report preserves per-capability statuses.

Existing Renderer, Preview, Review, Planning and Editing tests must remain green.

## Real Windows evidence

After deterministic gates pass, require one bounded Windows Environment Doctor Engineering Probe using the production surface.

It must prove at least:

- actual Windows host facts are reported;
- pinned FFmpeg/ffprobe are probed as READY;
- one deliberately unavailable/misconfigured component remains typed non-ready rather than crashing;
- secret redaction is demonstrated with a synthetic sentinel secret;
- no project/Domain mutation is required;
- result is structured for later UI consumption.

Do not download the large GStreamer runtime solely to decorate this probe. Preserve already accepted Preview Windows evidence unless a new Preview defect is exposed.

## Installer boundary

Not in this Work Order:

- final installer technology;
- signed installer/update channel;
- automatic arbitrary package installation;
- bundled/private Python decision;
- CUDA/Torch model manager;
- registry/system-wide mutation;
- administrative privilege workflow.

Environment Doctor must remain useful regardless of those later packaging decisions.

## Resource constraint

Approximately **9% Codex quota remains**.

### ChatGPT + GitHub

Primary owner for contract reduction, typed capability/application seams, deterministic tool/provider probes, focused tests, bounded CLI integration, CI/Windows Engineering Probe and governance.

### Codex

**NO ACTIVE RELEASE.**

Release only if a genuine Windows-only multi-file runtime issue appears that connector-first work and hosted Windows evidence cannot close efficiently.

### User PowerShell

Use only if GitHub-hosted Windows evidence cannot represent the required capability or a real local-user/Human Gate becomes necessary.

## Exit gate

PASS requires:

- one production Environment Doctor application boundary;
- per-capability typed status and product impact;
- FFmpeg/ffprobe readiness proven by execution;
- Preview readiness represented through the accepted production seam/configuration contract;
- provider-secret presence inspected without disclosure;
- sanitized repair report;
- deterministic tests and repository quality gates green;
- one bounded Windows production Environment Doctor probe PASS;
- no Domain/editorial mutation;
- no installer technology falsely frozen;
- structural progress remains 90% unless ordinary-user Product Gate structure genuinely changes.

## STOP boundary

Do not build the final installer.

Do not make GPU presence a basic-product requirement.

Do not trust declared executable/runtime presence without a tiny probe where readiness matters.

Do not leak secrets into reports/logs/tests.

Do not auto-execute repair commands generated from model/media/provider text.

Do not reopen Preview/backend benchmarking.

Do not expand into GUI/frontend or the full ordinary-user workflow orchestrator in this Work Order.
