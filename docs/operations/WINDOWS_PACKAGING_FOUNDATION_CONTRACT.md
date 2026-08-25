# Windows Packaging Foundation Contract

**Status:** PREPARATION FOUNDATION — IMPLEMENTATION NOT RELEASED  
**Parent:** R0.12-STAGE-A-FINAL-CLOSURE-002 / Wave D  
**Updated:** 2026-08-25

## Purpose

Define the engineering seams required before producing a Windows distributable.
Packaging is an application delivery layer, not a replacement architecture.

The goal is not merely to produce an `.exe`. The goal is a reproducible ordinary-user Windows product whose required runtime capabilities are explicit, diagnosable, replaceable and traceable instead of depending on whatever happens to be installed on the development machine.

Nothing in this preparation document releases Wave D. Packaging implementation begins only after Workspace/UX Human Gate acceptance and an explicit live-control release.

## Core boundaries

The package must separate:

- install resources (read-only application files);
- bundled runtime components;
- optional/installable runtime components;
- remote/network capabilities;
- user configuration and protected credentials;
- Project Workspace data;
- development-only tools/caches.

The install directory must never become the user's project storage root.

Packaging/bootstrap code must not gain Planning, Resolver, EDL, Renderer or other Domain/editorial authority.

## 1. Runtime manifest — one machine-readable component truth

Create one machine-readable ownership source for bundled and optional components.

Each component record should support, where applicable:

- stable component id/name;
- version/build/revision;
- classification: `bundled-required`, `bundled-optional`, `managed-optional`, `remote`, or `development-only`;
- required capability/use;
- runtime location policy rather than developer-machine absolute path;
- source/provenance;
- SHA256/content identity where distributable bytes are owned;
- license/NOTICE state;
- platform/architecture constraints;
- Doctor probe semantics;
- whether absence is fatal or degraded;
- packaging inclusion policy.

Release tooling, Capability Doctor, package validation and build evidence should consume the same manifest where practical. Do not create several manually synchronized lists that can drift.

### Initial runtime inventory that must be reconciled

The first Wave-D implementation audit must classify at least these currently known environments/components:

#### Required/bundle-candidate for ordinary Stage-A execution

- private Python 3.12 runtime;
- Tcl/Tk required by the desktop shell;
- approved FFmpeg + ffprobe exact build;
- TransNetV2 CPU runtime and reviewed weights required by the retained ordinary media-understanding path;
- application Python modules and required native DLLs;
- canonical product resources actually used by the launcher/package.

#### Retained 1.0 capability requiring an explicit release strategy

- `faster-whisper==1.2.1` speech runtime;
- approved/pinned speech model/component required for the final single-speaker original-voice + trusted-subtitle Human Gate.

Wave D must choose and document one truthful release strategy: bundled, or a controlled managed-optional component with clear Doctor/UX installation state. “It happens to be installed on the developer machine” is forbidden.

#### Remote/network capability — code may bundle, remote service/data does not

- DeepSeek reasoning/direction adapter;
- Gemini/OpenAI image-frame understanding adapters;
- public music discovery/acquisition providers such as Openverse/Wikimedia;
- network/proxy/timeout diagnostics and rights/provenance logic.

API keys/secrets must never bundle.

#### Optional/deferred unless current ordinary-path dependency audit proves otherwise

- MediaPipe recovery / EfficientDet Lite0 while release-license state remains unresolved;
- historical VAD/embedding/recovery components not required by the ordinary Stage-A path;
- GStreamer/VLC/libmpv or other preview candidates unless one is explicitly accepted as a release dependency.

#### Development-only — never copied as product layout

- `uv`;
- repository checkout / `.git`;
- `.venv`;
- `.uv-cache*`;
- `.private`;
- developer caches/build directories;
- repository-local `.tools` as a directory contract;
- machine-specific absolute paths.

An approved binary may be sourced from a reviewed development location during the build process, but its release ownership/location must come from the runtime manifest and package layout, not by copying the developer directory wholesale.

## 2. Resource/runtime locator

Create a dedicated resolution boundary for:

- frozen application resources;
- development resources;
- bundled runtime components;
- Project Workspace writable paths;
- user profile paths;
- optional externally/managed installed components.

The locator must make frozen/development mode explicit and testable.

Do not spread repository-relative or developer-machine absolute paths through business code.

Existing runtime resolution such as repository-local `.tools/ffmpeg-8.1/...` is a development fallback and must not become the package contract.

## 3. Capability Doctor

Startup/diagnostic surfaces should detect capability availability and explain recovery paths.

At minimum Wave D must reconcile diagnostics for:

- FFmpeg/ffprobe missing or wrong component;
- TransNet runtime/weights unavailable;
- speech component/model unavailable;
- install/resource permission failure;
- Project Workspace permission failure;
- protected-credential/profile failure;
- API provider not configured;
- network capability unavailable where relevant.

Missing optional capability should produce truthful degradation, not unexplained failure.

Doctor must distinguish:

- application cannot start;
- core Editing capability cannot run;
- Planning without local reference can still run;
- retained optional/degraded feature unavailable;
- remote provider merely not configured.

## 4. Packaging micro-automation contract

Wave D must add small deterministic automation rather than relying on a long manual packaging ritual.

Prefer one PowerShell entry surface that composes small tools. The exact filenames may follow repository conventions, but the capabilities below are required.

### 4.1 Runtime-manifest validation

Automated validation must reject at least:

- required component with missing version/provenance/location policy;
- distributable component with missing required hash/license state;
- development-only path classified as release content;
- duplicate/conflicting component ownership;
- machine-specific absolute release path.

### 4.2 Deterministic onedir build

A checked-in build configuration must:

- pin the selected bundler version once chosen;
- build Windows x64 `onedir` first;
- use the ordinary application composition/launcher path;
- include only manifest-approved runtime/resources;
- avoid secrets;
- emit a build/release manifest containing source git SHA and component identities.

Onefile/installer optimization remains later work.

### 4.3 Static package inspection

Automated inspection of the staged artifact must fail on forbidden content such as:

- `.private`;
- `.git`;
- `.venv`;
- `.uv-cache*`;
- arbitrary developer cache/build trees;
- plaintext API secrets/credential exports;
- unreviewed model/binary payloads not represented by the manifest.

It must also verify required launcher/resources/licenses/manifest presence.

### 4.4 Packaged launcher/capability smoke

Automation should launch the produced onedir artifact directly rather than through `python`, `uv` or repository entrypoints.

CI/runner smoke may prove structural package behavior, but must not be described as full clean-machine Human Gate merely because the runner happens not to call its installed Python.

Automatable assertions should include:

- process launches from the staged artifact;
- install tree remains read-only from ordinary project behavior;
- a temporary external Project Workspace can be created/opened;
- project writable data is outside install tree;
- Doctor resolves bundled required runtime components;
- product exits cleanly;
- no repository-relative dependency is required.

### 4.5 Artifact identity and retention

Packaging workflow should upload the onedir candidate and its machine-readable evidence together:

- app/source git SHA;
- runtime manifest snapshot;
- package/build manifest;
- hashes where required;
- static inspection result;
- packaged launcher smoke result.

A later Human Gate should test that same identifiable artifact rather than rebuilding an untracked variant manually.

## 5. First packaging target

Use Windows onedir Engineering Probe first.

Target ordinary environment must not require:

- repository checkout;
- Python installation;
- `uv`;
- Git;
- developer-only PATH or environment setup.

Validate:

- ordinary launch without Python/uv/repository;
- resource resolution;
- Project Workspace remains user-owned and external to install directory;
- bundled component discovery;
- diagnostics behavior;
- protected credential/profile behavior;
- retained local media path;
- explicit speech component state.

Do not start installer/onefile optimization before runtime/resource ownership is stable.

## 6. Clean-machine-ish vs Human proof

Automated Windows runner/package smoke is useful but not sufficient for final Product/Human evidence.

Final proof must include a Windows environment/artifact run that demonstrates the ordinary user does not need the development repository or its Python/uv environment.

Human evidence should include at least:

- double-click ordinary launcher;
- Chinese user/path behavior where practical;
- Project Workspace create/open;
- reusable profile + Windows protected-secret round trip;
- bundled FFmpeg/ffprobe detection;
- TransNet CPU runtime/weights load;
- truthful speech component/model state;
- local MP4 ingest/shot-detection path;
- real retained Planning/Editing smoke as required by the active completion gate;
- uninstall/delete of application artifact does not delete user Projects/Profiles.

## 7. Non-goals and hard prohibitions

Do not:

- move Domain authority into packaging code;
- hard-code providers/models as product truth;
- bundle unreviewed binaries/models/licenses;
- copy developer caches/private assets into release artifacts;
- treat `.tools` or `.venv` as the install layout;
- make CUDA a normal-user hard requirement when the accepted CPU baseline is sufficient;
- hide missing capability by silently changing product semantics;
- auto-publish an executable merely because the build command succeeded;
- call Stage-A 100% because an EXE exists.

## 8. Release sequence

After Workspace/UX is accepted and Wave D is explicitly released, preferred order is:

```text
ordinary quality/governance gate
→ runtime inventory/BOM reconciliation
→ runtime manifest validator
→ resource/runtime locator + Capability Doctor
→ deterministic Windows onedir build
→ static package inspection
→ packaged launcher/capability smoke
→ artifact upload + exact identity
→ clean-machine-ish / Human Gate on that artifact
→ retained Product/Human evidence
→ explicit release decision
```

Packaging implementation must stop/report at its released boundary; it does not self-authorize installer/onefile/update/signing work unless the live control plane explicitly expands scope.
