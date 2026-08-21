# Codex Execution Entry

**Last updated:** 2026-08-21  
**Purpose:** expose whether Codex currently has an authorized local construction release.

## Release state

**Work Order:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Release:** OPEN — BOUNDED PLANNING REFERENCE COMPATIBILITY WAVE ONLY  
**Foreman:** ChatGPT  
**Authority:** `docs/operations/CURRENT_WORK_ORDER.md`

This release exists only to prove one compatible provider-specific reference acquisition path for an ordinary public Bilibili video page. It is not authorization for a generic crawler/downloader project.

## Mandatory attention order

1. root `AGENTS.md`;
2. `docs/DOCUMENT_REGISTRY.json`;
3. `docs/operations/CURRENT_CONTROL_STATE.md`;
4. `docs/roadmap/CURRENT_PHASE_STATUS.md`;
5. `docs/operations/CURRENT_WORK_ORDER.md`;
6. only task-relevant source/tests;
7. Product/Architecture/CAP/ADR only if a concrete implementation question requires them.

`docs/archive/**`, `.private/**`, `.tools/**`, `.uv-cache*/**`, `.venv/**`, `build/**` and `dist/**` remain default-excluded from discovery.

## Released target

Observed real input:

`https://www.bilibili.com/video/BV1Mq4y187xR?share_source=copy_web`

Current generic `DirectHttpsReferenceAcquirer` correctly preserves bounded HTTPS/SSRF/IP/redirect/MIME/size/timeout rules, but the page does not expose a supported static HTML video declaration.

Existing seam:

`PlanningReferenceCapabilities.acquisition: ReferenceAcquisitionPort`

The implementation must keep Planning Domain unaware of Bilibili/site mechanics.

## Required result

Provide the smallest compatible acquisition design that lets a supported ordinary public Bilibili video page produce the same `AcquiredReferenceMedia` contract consumed by existing Planning.

Prefer provider-specific composition behind the existing `ReferenceAcquisitionPort` rather than adding Bilibili branches to Planning flow.

Preserve:

- reference media remains analysis-only and never Resolver-eligible final footage;
- original URL/provenance and content hash remain recorded;
- public HTTPS, SSRF/DNS/IP/redirect/size/timeout protections remain bounded;
- no ambient credentials, login circumvention or paid/protected-content bypass;
- unsupported/private/login/DRM/provider-change cases fail closed with useful diagnostics;
- generic webpage acquisition remains bounded; no arbitrary `<a>` traversal, whole-site crawling or browser automation.

A provider-specific page may use only the minimum public metadata/playback information needed to obtain an analyzable public reference stream. Any extra request target must be independently revalidated as public HTTPS.

## Bounded self-repair

Within this release, self-check and repair defects that directly prevent the supported Bilibili page → trusted reference media → existing Planning path or break required quality gates.

Do not repair unrelated backlog or redesign the acquisition framework. If the first provider proof reveals one small reusable routing/composition seam, add only that seam rather than a speculative plugin framework.

## Verification required

At minimum:

- focused acquisition/provider tests;
- existing direct-HTTPS security regression tests;
- a bounded real/public Bilibili engineering probe when network access permits;
- Planning integration test proving acquired reference reaches the existing reference-analysis path;
- Ruff format/check;
- mypy `src`;
- full pytest;
- import-linter;
- build;
- repo doctor;
- `git diff --check`.

Do not run paid model/provider requests merely to prove acquisition. Human Product Gate will be performed separately after engineering acceptance.

## Forbidden

Do not:

- read `docs/archive/**` for this task;
- introduce yt-dlp or another broad downloader dependency unless a new explicit review authorizes it;
- add login cookies/session scraping;
- bypass region/membership/DRM/protected-content restrictions;
- turn Planning into a Bilibili-aware module;
- implement Douyin/Xiaohongshu support in this wave;
- start Windows packaging work;
- claim Stage-A 100%;
- commit/push unless explicitly requested after local verification.

## Stop condition

Report changed files, acquisition/routing design, exact security invariants retained, focused/live/full verification, unsupported Bilibili cases, and the one ordinary Human Gate action needed next. Then stop.
