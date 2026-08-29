# Current Work Order

**ID:** R0.12-STAGE-A-FINAL-CLOSURE-002  
**Status:** ACTIVE — FINAL HUMAN GATE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** FINAL ORDINARY-USER WINDOWS ACCEPTANCE  
**Superseded candidate:** 0.1.1 / 71d7b7b46fa819f87aba785cefcc2bcf97ab7a46  
**Accepted replacement source:** eadbaa74c686f9fe526cb1d3eab64dde21c94d84 / 0.1.2  
**Updated:** 2026-08-30

## Objective

Perform the final ordinary-user Human Gate on the exact 0.1.2 Windows installer that passed engineering verification after the 0.1.1 Human Gate exposed insufficient tolerance for a retryable Gemini HTTP 503 high-demand spike.

Do not reopen broad architecture or unrelated 2.0 capabilities.

## Human evidence retained from 0.1.1

Planning:

- installed Planning completed successfully;
- the earlier factual-safety review behavior remains accepted.

Editing:

- local input validation passed;
- media ingest/understanding began normally;
- multiple Gemini visual-understanding requests completed successfully;
- a later request returned retryable HTTP 503 because the model was experiencing high demand;
- the installed product surfaced a typed `VisualProviderTransientError`.

This evidence does not indicate a Renderer or local media-runtime regression.

## 0.1.2 release candidate authority

- Version: **0.1.2**
- Source: `eadbaa74c686f9fe526cb1d3eab64dde21c94d84`
- Windows RC run: `33265346143`
- Installer: `VideoEditingAgent-Setup-0.1.2.exe`
- SHA-256: `32838e2748ae60f0059d461cccadbc5dc971ae3a9d2fc49922f3d9d8821f8c43`
- Private prerelease tag: `v0.1.2-rc-eadbaa7`
- Release asset ID: `535517911`
- Release page: `https://github.com/orange-lee-tech/video-editing-agent/releases/tag/v0.1.2-rc-eadbaa7`
- Direct asset: `https://github.com/orange-lee-tech/video-editing-agent/releases/download/v0.1.2-rc-eadbaa7/VideoEditingAgent-Setup-0.1.2.exe`

## Engineering verification complete

0.1.2 passed:

1. repository Quality Gate;
2. visual transient retry regression tests;
3. version identity/update tests;
4. Windows packaged GUI smoke;
5. exact CPython 3.12.13 packaging environment;
6. verified Inno Setup 7.1.0 acquisition;
7. guided Setup.exe compilation;
8. Planning-only installation;
9. installed Planning launcher;
10. Planning-only → Full upgrade;
11. Full launcher;
12. same-version Full repair;
13. uninstall and external Workspace preservation;
14. durable private prerelease publication.

The installer lifecycle reported:

`Installer lifecycle smoke PASSED.`

## 0.1.2 transient-provider policy

Only explicit `VisualProviderTransientError` failures are retried.

Default budget:

- attempt 1 fails → wait 2 seconds;
- attempt 2 fails → wait 4 seconds;
- attempt 3 fails → wait 8 seconds;
- attempt 4 fails → wait 16 seconds;
- attempt 5 failing ends the bounded retry budget.

Provider-supplied RetryInfo overrides a shorter local delay.

Non-retryable visual response/schema errors are not retried.

When all attempts fail, the error remains typed as transient and explicitly says the automatic retry budget was exhausted.

## Final Human Gate

Install the exact 0.1.2 candidate and verify:

1. application visibly shows v0.1.2;
2. brief representative Planning regression remains acceptable;
3. representative real-footage Editing progresses through visual understanding and produces an approved final MP4;
4. no terminal windows flash during normal processing/rendering;
5. a short provider-demand spike is tolerated without immediate task failure when it clears inside the retry window;
6. persistent provider unavailability still terminates cleanly with an actionable diagnostic rather than hanging indefinitely;
7. update-check UI remains non-blocking;
8. Workspace/original media remain safe.

Do not require the Product Owner to deliberately reproduce a provider outage if the real provider is healthy during the run. The successful real-footage Editing outcome plus the automated retry regression evidence is sufficient unless another transient failure occurs naturally.

## Exit condition

If the exact 0.1.2 installer passes ordinary-user acceptance without a material blocker:

- record durable Human evidence;
- set Planning and Editing product gates to PASS;
- set Windows release delivery gate to PASS;
- set Stage-A completion gate to PASS;
- move structural progress directly **95% → 100%**;
- close this work order and R0.12.

If a material blocker appears, freeze unrelated work and repair only the smallest responsible surface.

Broad resumable-task/checkpoint deduplication remains backlog unless Human Gate demonstrates it is required for release closure.
