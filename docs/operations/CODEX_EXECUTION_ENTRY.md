# Codex Execution Entry

Purpose: expose whether Codex currently has an authorized construction release.

## Release state

**Work Order:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Release:** OPEN — BOUNDED UX STABILIZATION WAVE ONLY  
**Writer:** Codex  
**Foreman:** ChatGPT

Execution specification:

`docs/operations/STAGE_A_UX_STABILIZATION_WAVE.md`

Current Work Order mode:

`PRODUCT PROBE → TEMPORARY UX STABILIZATION → HUMAN GATE`

## Why this release is justified

The real Stage-A Editing Product Probe is temporarily blocked by the user's current Gemini free-tier quota after legitimate real-product requests. The user explicitly chose to use the quota-reset interval to consolidate already-recorded ordinary-user UX/robustness work.

This wave is multi-file and Windows-specific. It includes Tkinter background execution/responsiveness, safe Windows credential persistence, profile/file dialogs, localization/presentation, ETA/progress behavior, splash startup behavior and targeted Planning robustness. That boundary is appropriate for one local Codex implementation/test iteration and is not efficiently or safely handled as a series of tiny GitHub text edits.

## Authorized scope

Codex is authorized to implement only the requirements in:

`docs/operations/STAGE_A_UX_STABILIZATION_WAVE.md`

including:

- responsive Tkinter worker/UI-thread separation;
- output scrollbar and UTF-8 TXT export;
- UI-aligned localization of stable progress/result/error presentation;
- honest ETA recalculated at least every 30 seconds;
- one ordinary Editing source mechanism: multi-select `Media Files`; remove `Media Folder` from the UI;
- first-run required/optional placeholders that are never submitted;
- local form/API profile file workflow;
- Windows-protected API-key persistence with no plaintext secret files;
- one bounded Planning no-facts repair path without weakening factual review;
- bounded share-text HTTPS extraction without platform scraping;
- real-milestone startup splash;
- localized persistent provider/quota error UX;
- focused tests and small adapter/UI refactors required for testability.

## Forbidden scope

Do not:

- redesign Planning/Editing core architecture;
- make Planning mandatory for Editing;
- weaken factual review, Resolver grounding, canonical EDL or Review policy;
- let reference-only media become final visual media;
- add stock/generated replacement visuals;
- add a timeline/NLE editor;
- add a Douyin/platform scraper/downloader;
- store API keys in plaintext `.txt`, project files, logs or repository data;
- silently switch provider/model after quota/failure;
- fake progress percentages/ETA values;
- ship decorative `公共素材` / `类似方案` controls that have no real adapter behind them;
- create new R0.12 microphases;
- claim Product/Human Gate PASS or Stage-A 100%.

## Execution protocol

1. reobserve current `origin/main` before editing;
2. preserve unknown local changes; do not overwrite user work;
3. read `CURRENT_WORK_ORDER.md`, this file, and `STAGE_A_UX_STABILIZATION_WAVE.md` before implementation;
4. make one coherent bounded implementation;
5. run formatter, lint/Ruff, mypy, full tests, architecture/import contracts, build and launcher smoke;
6. perform Windows-local manual smoke for UI/profile/export/splash/responsiveness where deterministic automation cannot prove behavior;
7. commit/push only after local verification is green;
8. report exact commit SHA, changed files, tests, deferred items, manual-smoke findings, secret-storage confirmation and invariant confirmation;
9. stop. Do not continue into the Editing Product Gate or unrelated backlog without a new release.

## Acceptance rule

Codex report is evidence only, not acceptance.

After the report, ChatGPT must reobserve current `main`, exact diff and CI before closing this release. The user will later rerun the real Editing Product/Human Gate when provider quota is available.
