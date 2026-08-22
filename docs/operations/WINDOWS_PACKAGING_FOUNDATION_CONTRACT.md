# Windows Packaging Foundation Contract

**Status:** PREPARATION FOUNDATION
**Parent:** R0.12-STAGE-A-FINAL-CLOSURE-002 / Wave D

## Purpose

Define the engineering seams required before producing a Windows distributable.
Packaging is an application delivery layer, not a replacement architecture.

## Core boundaries

The package must separate:

- install resources (read-only application files);
- runtime components;
- user configuration;
- Project Workspace data;
- optional capabilities.

The install directory must never become the user's project storage root.

## Required foundations

### Runtime manifest

Create one machine-readable ownership source for bundled and optional components.

It should describe:

- component name;
- version/build;
- required or optional status;
- provenance/license metadata;
- runtime location.

Release tooling, Doctor, and packaging validation should consume the same source where practical.

### Resource/runtime locator

Create a dedicated resolution boundary for:

- frozen application resources;
- development resources;
- project workspace paths;
- user profile paths;
- optional installed capabilities.

Do not spread repository-relative or developer-machine absolute paths through business code.

### Capability Doctor

Startup diagnostics should detect capability availability and explain recovery paths.

Examples:

- FFmpeg missing;
- speech component unavailable;
- model unavailable;
- permission failure;
- API provider not configured.

Missing optional capability should produce truthful degradation, not unexplained failure.

## First packaging target

Use Windows onedir engineering probe first.

Validate:

- ordinary launch without Python/uv/repository;
- resource resolution;
- Project Workspace remains user-owned;
- bundled component discovery;
- diagnostics behavior.

Do not start installer/onefile optimization before runtime/resource ownership is stable.

## Non-goals

Do not:

- move Domain authority into packaging code;
- hard-code providers/models as product truth;
- bundle unreviewed binaries/models/licenses;
- copy developer caches/private assets into release artifacts.
