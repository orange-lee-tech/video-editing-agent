# Current Work Order

**ID:** R0.13-RELEASE-POLISH-001  
**Status:** ACTIVE — ENGINEERING PASS / HUMAN REVIEW PENDING  
**Phase:** R0.13 — 1.0 release polish and update engineering  
**Mode:** BOUNDED POST-STAGE-A PRODUCTIZATION  
**Accepted Stage-A baseline:** 0.1.5 / e59cab8475a615d29003c03497ddcdaf862476a6  
**Opened:** 2026-08-31  
**Updated:** 2026-08-31

## Objective

Prepare the already Human-accepted Stage-A product for a credible 1.0.0 release without reopening core feature construction.

This work order is limited to seven Product Owner-approved release-polish items:

1. installer progress must show a useful remaining-time estimate/countdown;
2. Windows desktop text rendering must be crisp and DPI-aware, with Chinese typography using an appropriate CJK UI font;
3. the desktop must provide persisted Day / Comfort / Night appearance modes;
4. routine future updates must use a verified component/file patch path by default, with the full Setup.exe retained only as bootstrap/recovery fallback;
5. guided installation must present a bilingual Software License and User Agreement that the user must explicitly accept before installation can continue;
6. the desktop header must consolidate update checking into Settings and add a sibling Declaration button with the Product Owner-approved temporary developer statement;
7. the visible product brand must become `有岐`, with the slogan `创作有岐，表达有路`, while preserving internal executable/AppId/update identifiers needed for compatibility.

## Non-goals

Do not add:

- advanced speech reconstruction;
- bilingual/translated subtitles;
- TTS/narration;
- Remote Reference URL;
- new editing effects or creative capabilities;
- byte-level binary delta algorithms such as bsdiff;
- silent background self-update without user consent.

Do not generate or publish a final `1.0.0` installer under this work order until the seven scoped items are verified and the Product Owner authorizes release packaging.

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

### Installer agreement

- Simplified Chinese and English agreement files are maintained in the repository;
- the guided installer displays the agreement for the selected language before installation;
- the user must explicitly accept the agreement before proceeding;
- the agreement covers software licensing, AI-output limitations, third-party API/network transmission, API charges/credentials, media/music rights, updates, third-party components, warranty disclaimer, liability limits, privacy/local data, prohibited use and termination;
- silent/unattended engineering smoke may accept the license through installer automation, but ordinary interactive installation must not bypass consent.

### Header consolidation and declaration

- the top-level header exposes only language, Settings and Declaration controls at the same visual level;
- update checking is available inside Settings and may still run silently/fail-open at startup;
- Declaration opens a modal containing the Product Owner-approved temporary developer statement and exactly one in-content acknowledgement button (`知道了` / localized equivalent);
- closing the declaration does not change product data or network state.

### Product branding

- the visible product name is `有岐`;
- the visible slogan is exactly `创作有岐，表达有路` followed by the runtime version;
- installer display name, shortcuts and user-facing updater titles use `有岐`;
- internal executable names, AppId, package/module identifiers and update component IDs remain stable unless an explicit migration is separately approved.

### Component patch updates

- update metadata can describe a full installer plus independently versioned component archives;
- the application can plan an update by comparing installed component versions/hashes with manifest state;
- a separate updater process can download, SHA-256 verify, stage, replace and rollback changed application files;
- the running GUI never overwrites its own executable in-process;
- failed verification/replacement restores the previous installation;
- unchanged heavyweight runtimes are not downloaded for an app-core-only patch;
- full Setup.exe remains available for first install, repair, incompatible layout changes and updater failure.

## Execution constraints

- ChatGPT remains the control plane and should use direct bounded repository edits for deterministic work;
- Codex may be used only when local Windows/runtime iteration or genuinely complex multi-file debugging materially reduces risk; do not spend token budget on clerical work;
- the accepted Stage-A Planning and Editing core paths are protected invariants. Any regression in either core path blocks R0.13 release-polish closure.

## Required verification

- repository Quality Gate;
- unit tests for theme persistence, DPI bootstrap, update-manifest compatibility and patch planning;
- updater rollback/integrity tests;
- Windows packaging staging smoke;
- real packaged H.264 encode gate remains PASS;
- guided installer lifecycle remains PASS;
- one Windows visual compatibility review at 100%, 125%, 150% and 200% scaling before final 1.0.0 authorization.

## Exit condition

When all seven items pass engineering verification and the Product Owner accepts the Windows presentation/update behavior:

- close R0.13;
- freeze the 1.0 release candidate scope;
- only then authorize final `1.0.0` packaging.


## Current engineering candidate

R0.13 engineering implementation is complete for candidate:

- version: `0.1.6`;
- source: `6a6bb6fb84345a3c974168f0b4fa0d013af2fc92`;
- Windows RC: `33325249400` — **SUCCESS**;
- installer SHA-256: `fb44abd8818ded1e899757e8ba33132ebffe88cc409578d29a1fba9081da4787`;
- installer + component patch assets: published on prerelease `v0.1.6-rc-6a6bb6f`.

Do not close this work order until the Product Owner reviews the installer/UI/theme/branding/update experience and accepts the Windows presentation at the required scaling levels.
