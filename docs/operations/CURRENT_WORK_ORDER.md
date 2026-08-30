# Current Work Order

**ID:** R0.13-RELEASE-POLISH-001  
**Status:** ACTIVE — RELEASE POLISH / COMPATIBILITY  
**Phase:** R0.13 — 1.0 release polish and update engineering  
**Mode:** BOUNDED POST-STAGE-A PRODUCTIZATION  
**Accepted Stage-A baseline:** 0.1.5 / e59cab8475a615d29003c03497ddcdaf862476a6  
**Opened:** 2026-08-31  
**Updated:** 2026-08-31

## Objective

Prepare the already Human-accepted Stage-A product for a credible 1.0.0 release without reopening core feature construction.

This work order is limited to four Product Owner-approved release-polish items:

1. installer progress must show a useful remaining-time estimate/countdown;
2. Windows desktop text rendering must be crisp and DPI-aware, with Chinese typography using an appropriate CJK UI font;
3. the desktop must provide persisted Day / Comfort / Night appearance modes;
4. routine future updates must use a verified component/file patch path by default, with the full Setup.exe retained only as bootstrap/recovery fallback.

## Non-goals

Do not add:

- advanced speech reconstruction;
- bilingual/translated subtitles;
- TTS/narration;
- Remote Reference URL;
- new editing effects or creative capabilities;
- byte-level binary delta algorithms such as bsdiff;
- silent background self-update without user consent.

Do not generate or publish a final `1.0.0` installer under this work order until the four scoped items are verified and the Product Owner authorizes release packaging.

## Acceptance criteria

### Installer ETA

- the guided Inno Setup UI displays localized estimated remaining time during file installation;
- the estimate is derived from actual observed progress and elapsed time rather than a fixed fake countdown;
- early/unstable progress is labeled as estimating;
- unattended/silent installer behavior remains unchanged.

### DPI and typography

- the GUI declares Windows DPI awareness before Tk is created;
- Tk scaling is derived from the actual display DPI;
- Chinese UI uses `Microsoft YaHei UI` when available; English uses `Segoe UI`;
- default body/meta sizes are readable at ordinary Windows scaling;
- static tests lock the DPI bootstrap and typography contract;
- Windows packaging smoke verifies the GUI still starts.

### Appearance modes

- modes: `day`, `comfort`, `night`;
- selection is exposed in Settings and persisted outside project workspaces;
- theme changes apply without changing product data or API secrets;
- all semantic tokens are switched together, including native Tk text/canvas surfaces;
- contrast-sensitive text/button states remain readable.

### Component patch updates

- update metadata can describe a full installer plus independently versioned component archives;
- the application can plan an update by comparing installed component versions/hashes with manifest state;
- a separate updater process can download, SHA-256 verify, stage, replace and rollback changed application files;
- the running GUI never overwrites its own executable in-process;
- failed verification/replacement restores the previous installation;
- unchanged heavyweight runtimes are not downloaded for an app-core-only patch;
- full Setup.exe remains available for first install, repair, incompatible layout changes and updater failure.

## Required verification

- repository Quality Gate;
- unit tests for theme persistence, DPI bootstrap, update-manifest compatibility and patch planning;
- updater rollback/integrity tests;
- Windows packaging staging smoke;
- real packaged H.264 encode gate remains PASS;
- guided installer lifecycle remains PASS;
- one Windows visual compatibility review at 100%, 125%, 150% and 200% scaling before final 1.0.0 authorization.

## Exit condition

When all four items pass engineering verification and the Product Owner accepts the Windows presentation/update behavior:

- close R0.13;
- freeze the 1.0 release candidate scope;
- only then authorize final `1.0.0` packaging.
