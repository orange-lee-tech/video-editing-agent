# Current Work Order

**ID:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Status:** ACTIVE — FINAL HUMAN GATE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** FINAL ORDINARY-USER WINDOWS ACCEPTANCE  
**Accepted release source:** `7753e5bbee93ca743152a7e2319c3f6739faff60`  
**Release candidate:** `VideoEditingAgent-Setup-0.1.0.exe`  
**Setup.exe SHA-256:** `9ba68f361f2d4c7881e1192b82e2fb3d750332d8844796829224a9dd1912033e`  
**Updated:** 2026-08-29

## Objective

Close Stage-A / 1.0 truthfully by performing the final ordinary-user Human Gate on the exact Windows Setup.exe that already passed automated release engineering.

No broad architecture work belongs in this work order.

## Engineering closure already achieved

The source and installer engineering gates are complete for the RC:

- Planning/Editing/UI source consolidated and accepted on GitHub;
- ordinary repository CI green;
- Windows onedir staging green;
- package static inspection green;
- packaged Doctor/runtime probe green;
- packaged launcher smoke green;
- verified Inno Setup 7.1.0 acquisition green;
- guided Setup.exe compilation green;
- Planning-only install green;
- Planning-only Editing-runtime isolation green;
- Planning-only → Full upgrade green;
- Full launcher green;
- same-version repair green;
- uninstall green;
- external Workspace preservation green;
- deferred speech payload exclusion green.

## Remaining Human Gate

The Product Owner should test the exact RC as an ordinary Windows user:

1. run `VideoEditingAgent-Setup-0.1.0.exe`;
2. inspect the wizard language/component/shortcut/finish-launch behavior;
3. install the normal Full option unless explicitly testing Planning-only;
4. launch from the installed application, not from the repository;
5. run one representative Planning case;
6. run one representative visual-first Editing case using local footage;
7. optionally rerun Setup to observe repair/upgrade behavior;
8. uninstall and verify user Workspace/original media remain.

The Human Gate should report only material PASS/FAIL observations. Cosmetic wishes that do not block ordinary use move to backlog rather than reopening Stage-A by default.

## 1.0 product boundary

1.0 ships:

- Core App / Planning;
- FFmpeg/ffprobe media runtime;
- TransNet/CPU Torch/reviewed weights;
- visual-first automatic Editing;
- current deterministic source-audio pass-through where implemented.

2.0 retains:

- advanced source-speech / ambience separation;
- sentence-preserving speech reconstruction;
- translated/bilingual subtitles;
- cross-language narration/TTS;
- Remote Reference URL.

## Exit condition

If the exact Setup.exe passes the Product Owner's ordinary-user Human Gate, immediately:

- record the Human evidence;
- set Stage-A completion gate to PASS;
- move structural progress directly from 95% to 100%;
- close this work order;
- archive the release-candidate identity and installer evidence.

Do not continue polishing non-blocking 2.0 or backlog items before closure.
