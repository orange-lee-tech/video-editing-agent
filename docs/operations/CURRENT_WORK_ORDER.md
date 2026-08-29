# Current Work Order

**ID:** R0.12-STAGE-A-FINAL-CLOSURE-002  
**Status:** ACTIVE — FINAL HUMAN GATE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** FINAL ORDINARY-USER WINDOWS ACCEPTANCE  
**Superseded Human candidate:** 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38 / 0.1.0  
**Accepted replacement source:** 71d7b7b46fa819f87aba785cefcc2bcf97ab7a46 / 0.1.1  
**Updated:** 2026-08-30

## Objective

Perform the final ordinary-user Human Gate on the exact 0.1.1 Windows installer that already passed engineering verification.

Do not reopen broad architecture, unrelated polish or 2.0 capabilities unless the Human Gate finds a material release blocker.

## Release candidate authority

- Version: **0.1.1**
- Source: `71d7b7b46fa819f87aba785cefcc2bcf97ab7a46`
- Windows RC run: `33262066851`
- Installer: `VideoEditingAgent-Setup-0.1.1.exe`
- SHA-256: `fc93f83b0543a1163a44796c7f430dcc68ff5f7a5c9112134b84f5dd15cae6ea`
- Private prerelease tag: `v0.1.1-rc-71d7b7b`
- Release asset ID: `535433505`
- Release page: `https://github.com/orange-lee-tech/video-editing-agent/releases/tag/v0.1.1-rc-71d7b7b`
- Direct asset: `https://github.com/orange-lee-tech/video-editing-agent/releases/download/v0.1.1-rc-71d7b7b/VideoEditingAgent-Setup-0.1.1.exe`

## Engineering verification already complete

The replacement candidate passed:

1. repository Quality Gate and regression suite;
2. Windows packaged windowed-GUI smoke;
3. exact CPython 3.12.13 packaging environment;
4. verified Inno Setup 7.1.0 acquisition;
5. guided 0.1.1 Setup.exe compilation;
6. Planning-only installation;
7. installed Planning launcher;
8. Planning-only → Full upgrade;
9. Full launcher;
10. same-version Full repair;
11. uninstall;
12. external Workspace preservation;
13. durable private prerelease publication.

The full installer lifecycle reported:

`Installer lifecycle smoke PASSED.`

## Accepted 0.1.1 repair scope

### Windows child-process UX

A shared Windows no-console creation policy now applies to FFmpeg/ffprobe/media subprocesses used by the GUI while retaining stdout/stderr and exit-code diagnostics.

### Same-EDL repair

When Review requests `RERENDER_SAME_EDL`, ProductFlow performs exactly one automatic rerender of the identical canonical EDL and reviews it with `repair_attempt=1`.

### Source-audio robustness

Selected source clips without audio streams no longer fabricate SOURCE_AUDIO mappings. Original audio remains preserved when real source audio exists.

### Diagnostics

The product presentation now distinguishes missing verified output from a post-render rejected candidate and surfaces typed renderer/QC problem details.

### Version identity

The installed desktop visibly identifies **v0.1.1**, and packaging/version tests guard against drift.

### Update discovery

The application has asynchronous fail-open startup update discovery plus an explicit Check for Updates action.

Stable manifest:

`https://orange-lee-tech.github.io/homepages/video-editing-agent/stable/latest.json`

Update-check failure never blocks Planning or Editing.

## Final Human Gate

Use the exact installer above as an ordinary Windows user and verify:

1. installer opens and Full installation completes normally;
2. installed application visibly shows **v0.1.1**;
3. representative Planning succeeds while factual safety remains intact;
4. representative real-footage Editing produces an approved final MP4;
5. no terminal/console windows flash during ordinary media processing/rendering;
6. update-check UI is understandable and non-blocking;
7. if Editing fails deliberately or naturally, the result exposes an actionable diagnostic rather than a misleading generic message;
8. uninstall/upgrade behavior does not damage the external Workspace or original media.

Cosmetic wishes and 2.0 capabilities are backlog items, not Stage-A blockers.

## Exit condition

If the Product Owner accepts this exact 0.1.1 installer without a material blocker:

- record durable Human evidence;
- set Planning and Editing product gates to PASS;
- set Windows release delivery gate to PASS;
- set Stage-A completion gate to PASS;
- move structural progress directly **95% → 100%**;
- close this work order and R0.12.

If a material blocker appears, freeze unrelated work and repair only the smallest responsible surface.
