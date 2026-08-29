# Current Work Order

**ID:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Status:** ACTIVE — REPLACEMENT RC + FINAL HUMAN GATE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** REPLACEMENT WINDOWS RELEASE CANDIDATE THEN ORDINARY-USER ACCEPTANCE  
**Accepted source candidate:** `80ab920b19c1ed1aebef4fa9b7eab05d6a509f38`  
**Previous superseded RC source:** `7753e5bbee93ca743152a7e2319c3f6739faff60`  
**Updated:** 2026-08-29

## Objective

Close Stage-A / 1.0 truthfully by packaging the post-Human-Gate repaired source into a fresh Windows Setup.exe, passing the automated Windows lifecycle, then performing the final ordinary-user Human Gate on that exact installer.

No broad architecture work belongs in this work order.

## What changed after the previous RC

The previous Setup.exe passed automated release engineering but ordinary-user testing exposed material desktop/release defects. The accepted repair source now includes:

- true windowed GUI executable separated from the console diagnostics CLI;
- removal of installer pre-initialization app-path logic that could break the wizard;
- packaged GUI smoke that waits for process completion and uses a clean external smoke Workspace;
- editable user forms during background execution while the active task uses an immutable request snapshot;
- localized task-local AI usage telemetry;
- review-blocked rendered output retained as a clearly labelled candidate;
- clearer correction/failure presentation;
- public-music candidate names during rights checks;
- active-page mouse-wheel scrolling.

Ordinary repository CI is green at the accepted source candidate.

## Immediate engineering gate

Run the manual GitHub Actions workflow:

`Windows Release Candidate`

with exact input:

`source_ref = 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38`

Acceptance requires:

- exact source checkout;
- pinned packaging environment;
- Windows onedir build;
- static package inspection;
- packaged Doctor/runtime probe;
- windowed GUI packaged smoke;
- verified Inno Setup acquisition;
- guided Setup.exe compilation;
- Planning-only install;
- Planning-only → Full upgrade;
- Full installed launcher;
- same-version repair;
- uninstall;
- external Workspace preservation;
- deferred 2.0 payload exclusion;
- SHA-addressed uploaded Setup.exe artifact.

If any step fails, freeze new feature work and repair only the smallest release blocker.

## Final Human Gate

After the replacement workflow passes, the Product Owner should test the exact new Setup.exe as an ordinary Windows user:

1. run the installer through the normal wizard;
2. install the normal Full option;
3. launch from the installed application, not from the repository;
4. run one representative Planning case;
5. run one representative visual-first Editing case using local footage;
6. confirm the corrected desktop behavior is materially acceptable;
7. uninstall and verify user Workspace/original media remain.

The Human Gate should report only material PASS/FAIL observations. Cosmetic wishes that do not block ordinary use move to backlog rather than reopening Stage-A by default.

## Exit condition

If the replacement Setup.exe passes automated release engineering and the Product Owner's ordinary-user Human Gate:

- record the new exact source SHA, workflow run, installer SHA-256 and artifact identity;
- record durable Human evidence;
- set Stage-A completion gate to PASS;
- move structural progress directly from 95% to 100%;
- close this work order;
- archive the superseded RC identity as historical evidence.

Do not continue polishing non-blocking 2.0 or backlog items before closure.
