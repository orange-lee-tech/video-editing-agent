# Current Work Order

**ID:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Status:** ACTIVE — FINAL HUMAN GATE  
**Phase:** R0.12 — Stage-A final closure  
**Mode:** FINAL ORDINARY-USER WINDOWS ACCEPTANCE  
**Accepted release source:** `80ab920b19c1ed1aebef4fa9b7eab05d6a509f38`  
**Release candidate:** `VideoEditingAgent-Setup-0.1.0.exe`  
**Setup.exe SHA-256:** `15978b647dec198996b747ea41fdb77fce61c8fe59261cd983c26ae0c74e34da`  
**Artifact:** `VideoEditingAgent-Setup-80ab920b19c1ed1aebef4fa9b7eab05d6a509f38`  
**Artifact ID:** `9712373668`  
**Windows RC run:** `33243959576`  
**Updated:** 2026-08-29

## Objective

Close Stage-A / 1.0 truthfully by performing the final ordinary-user Human Gate on the exact replacement Windows Setup.exe that already passed automated release engineering.

No broad architecture or packaging construction work belongs in this work order.

## Engineering closure already achieved

The accepted post-Human-Gate repaired source and replacement installer gates are complete:

- ordinary repository CI green for `80ab920...`;
- exact release-source checkout green;
- pinned Windows packaging environment green;
- Windows onedir staging green;
- package static inspection green;
- packaged Doctor/runtime probe green;
- windowed GUI packaged smoke green;
- verified Inno Setup 7.1.0 acquisition green;
- guided Setup.exe compilation green;
- Planning-only install green;
- Planning-only → Full upgrade green;
- Full installed launcher green;
- same-version repair green;
- uninstall green;
- external Workspace preservation green;
- deferred 2.0 payload exclusion green.

The previous `7753e5b...` installer is superseded for final acceptance.

## Remaining Human Gate

The Product Owner should test the exact replacement RC as an ordinary Windows user:

1. obtain artifact `VideoEditingAgent-Setup-80ab920b19c1ed1aebef4fa9b7eab05d6a509f38` from run `33243959576`;
2. verify the contained Setup.exe SHA-256 is `15978b647dec198996b747ea41fdb77fce61c8fe59261cd983c26ae0c74e34da`;
3. run `VideoEditingAgent-Setup-0.1.0.exe` through the normal wizard;
4. install the normal Full option;
5. launch from the installed application, not from the repository;
6. run one representative Planning case;
7. run one representative visual-first Editing case using local footage;
8. confirm the repaired desktop behaviors are materially acceptable;
9. uninstall and verify user Workspace/original media remain.

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

If the exact replacement Setup.exe passes the Product Owner's ordinary-user Human Gate:

- record durable Human evidence;
- set Stage-A completion gate to PASS;
- move structural progress directly from 95% to 100%;
- close this work order;
- archive the final release-candidate identity and installer evidence.

Do not continue polishing non-blocking 2.0 or backlog items before closure.
