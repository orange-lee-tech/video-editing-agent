# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 95%  
**Current phase:** R0.12 — Stage-A final ordinary-user Windows acceptance  
**Engineering state:** STAGE_A_REPLACEMENT_INSTALLER_RC_REQUIRED  
**Updated:** 2026-08-29  
**Active work order:** `R0.12-STAGE-A-FINAL-CLOSURE-002`

## Progress truth

Stage-A source construction is effectively complete, but the previous final installer candidate is no longer the acceptance target.

The earlier Windows RC was built from:

`7753e5bbee93ca743152a7e2319c3f6739faff60`

and passed automated Windows lifecycle checks. During the subsequent ordinary-user desktop Human Gate, material usability/packaging defects were identified and repaired.

Current accepted source candidate:

`80ab920b19c1ed1aebef4fa9b7eab05d6a509f38`

Ordinary repository CI is green for this source.

## Current gates

- Planning source path after Human Gate repair: **ACCEPTED SOURCE / REPLACEMENT INSTALLER PENDING**.
- Editing visual-first source path after Human Gate repair: **ACCEPTED SOURCE / REPLACEMENT INSTALLER PENDING**.
- Windowed ordinary-user GUI vs diagnostics CLI split: **IMPLEMENTED / CI GREEN**.
- Installer pre-initialization defect: **REPAIRED / CI GREEN**.
- Packaged GUI smoke wait semantics: **REPAIRED / CI GREEN**.
- Review-blocked rendered candidate visibility and correction presentation: **IMPLEMENTED / CI GREEN**.
- Task-local AI usage telemetry and desktop presentation: **IMPLEMENTED / CI GREEN**.
- Previous Windows Setup.exe RC from `7753e5b...`: **SUPERSEDED FOR FINAL ACCEPTANCE**.
- Replacement Windows Setup.exe from `80ab920...`: **REQUIRED**.
- Stage-A completion gate: **OPEN FOR REPLACEMENT RC + FINAL ORDINARY-USER HUMAN GATE**.

Therefore structural progress remains **95%**. The project policy explicitly forbids artificial percentage increments.

## Final path to 100%

```text
80ab920... exact source
→ manual Windows Release Candidate workflow
→ automated staging/install/upgrade/repair/uninstall PASS
→ new SHA-addressed Setup.exe
→ ordinary Windows install
→ installed Planning Human check
→ installed visual-first Editing Human check
→ uninstall / Workspace preservation observation
→ durable Human evidence
→ Stage-A 100%
```

If the replacement installer passes and the Product Owner accepts that exact artifact, move directly to 100% and close R0.12 Stage-A.

## Non-blocking follow-up

Do not reopen these before Stage-A closure:

- dual-track audio/video speech reconstruction;
- translated/bilingual subtitles;
- cross-language narration/TTS;
- Remote Reference URL;
- Web Setup / delta updates;
- cosmetic UI backlog that does not prevent ordinary use.

The Inno Setup commercial-use licensing policy remains a release-management item before commercial distribution, not a blocker to the present engineering/Human RC.
