# Ordinary Windows Desktop Product Policy

**Status:** USER-APPROVED PRODUCT POLICY  
**Approved:** 2026-08-25  
**Updated:** 2026-08-25  
**Scope:** Windows desktop ordinary-user experience, runtime management, API configuration, Workspace ownership, installation and maintenance  
**Authority note:** Records explicit Product Owner direction. A later Product Constitution revision should absorb these rules verbatim in substance rather than weakening them.

## 1. Ordinary-user principle

The supported Windows product path must be operable by a normal user who does not know what a terminal, PowerShell, Command Prompt, Python, uv or Git is.

The product MUST NOT require terminal knowledge for normal:

- installation/startup;
- environment preparation;
- API/provider configuration;
- Project Workspace selection;
- Planning;
- Editing;
- output discovery;
- ordinary diagnostics/recovery;
- application update/repair/uninstall.

Developer shells may remain engineering tools, but they are not a product UI.

## 2. API / provider configuration

API configuration must be exposed through a clear GUI intended for non-technical users.

The GUI should:

- use provider names and plain-language capability explanations;
- clearly distinguish reasoning/direction from visual-understanding providers;
- explain where a key is used and that the application does not ship user credentials;
- mask secret values;
- never require users to set environment variables manually;
- provide understandable validation/error feedback rather than raw stack traces;
- support secure user-level persistence when the user chooses to save a profile;
- never write plaintext API keys into ordinary project/profile files or logs.

Exact provider onboarding/help links and visual design may evolve, but ease of use for non-technical users is a product requirement.

## 3. Project Workspace separation

Program installation/runtime ownership and user Project Workspace ownership must remain separate.

The product should make this separation visible and understandable so that:

- uninstalling/replacing the application does not delete projects;
- deleting a project does not damage the application;
- user originals, project database/state, caches and outputs do not live inside the install directory by default;
- multiple projects remain independently manageable;
- accidental deletion or overwrite risk is reduced.

Application update, repair and uninstall must preserve user Projects/Profiles/original media unless the user separately and explicitly requests their deletion.

## 4. Runtime/environment management

The preferred architecture is application-owned/private runtime components rather than modifying arbitrary system-wide developer environments.

The product MAY automate installation or update of required basic components and MAY offer guided installation of optional/advanced components when this improves ordinary-user usability.

Automation must remain bounded and diagnosable.

### 4.1 Non-destructive automatic actions

For application-owned components, installation/update may be automated when the operation is non-destructive and the UI clearly communicates what is happening.

Examples include:

- downloading a missing application-owned runtime component;
- installing a required private component into an application-controlled location;
- updating an application-owned component to the supported compatible version;
- verifying hashes/versions and repairing a missing file without touching unrelated user software.

### 4.2 Destructive or reconfiguration actions require consent

Explicit user consent is required before the product performs an operation that deletes, replaces, downgrades, substantially reconfigures, or otherwise destructively changes an existing environment/component.

This includes, where applicable:

- deleting an existing runtime/component tree;
- replacing a user-selected component with another implementation;
- downgrading a component;
- changing system-wide PATH/environment configuration;
- removing an existing installation;
- resetting or rebuilding an existing configured environment when user state may be affected.

The UI must explain the proposed action and consequence in ordinary language before proceeding.

The normal design should prefer an application-private compatible runtime rather than trying to reuse, repair or delete an arbitrary system Python, FFmpeg, CUDA or developer environment.

## 5. Failure and recovery UX

When a required capability is missing or broken, the normal GUI should prefer:

`detect → explain → offer safe repair/install/update → obtain consent when destructive → verify → continue`

rather than:

`show raw exception → tell user to open terminal → ask user to install developer tooling manually`.

A user may decline an optional repair/install action. The product should then explain what capability will be unavailable or degraded.

## 6. UI design evidence

Public software, open-source projects, platform conventions and real user feedback may be researched as UI/UX references.

References are inputs, not authority. Final UI decisions must preserve this product's own workflow, safety, Workspace ownership, credential protection and flexible Planning/Editing production-line semantics.

Established installation/update systems should be evaluated before custom bootstrap/update machinery is invented. Current reference candidates include Inno Setup, NSIS, Velopack and, where prerequisite chaining actually justifies it, WiX/Burn.

## 7. Windows distribution requirement

The raw PyInstaller `onedir` ZIP is an engineering staging/evidence format, not the normal 1.0 user-delivery format.

The normal Windows release MUST provide a guided `Setup.exe` experience before Stage-A / 1.0 release closure. The installer/maintenance path must support at least:

- a normal Windows installation wizard;
- a license/agreement page where applicable;
- an understandable install location;
- user-selectable desktop shortcut creation;
- a completion option to launch the application;
- install-state detection and a safe upgrade/repair path;
- normal uninstall through Windows conventions;
- clear explanation/choice when an existing application-owned component conflicts with the supported version;
- explicit consent before destructive replacement or substantial reconfiguration;
- preservation of Project Workspaces, profiles and original media across application update/repair/uninstall.

A giant single embedded payload is not a product requirement. Release engineering should prefer component ownership and verified acquisition where this reduces unnecessary downloads and maintenance risk.

## 8. Capability-oriented component delivery

The application is a flexible production line. Distribution should reflect that rather than forcing every user to acquire every heavy runtime on first install.

The release architecture should be able to distinguish at least:

- core desktop / Planning capability;
- media runtime (for example FFmpeg/ffprobe);
- scene-detection runtime (TransNet/CPU Torch/weights);
- speech runtime (faster-whisper/CTranslate2/PyAV/model).

Exact component boundaries may evolve after measurement, but they must be application-owned, versioned, verifiable and diagnosable. Planning-only users should not be required to download the complete heavy Editing/speech stack merely because those capabilities exist.

## 9. Engineering iteration vs product operation

Terminal/PowerShell use is permitted and encouraged for focused engineering diagnostics, patch application and local verification during development/Human Gate repair. This does not weaken Section 1: terminal knowledge remains forbidden as a requirement for the normal released product.

During repair iterations, prefer small patches and focused Workspace/log evidence over repeatedly rebuilding and transferring the full release payload. A complete installer/package build is reserved for explicit release-candidate validation.
