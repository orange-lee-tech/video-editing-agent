# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 95%  
**Current phase:** R0.12 — Stage-A final ordinary-user Windows acceptance  
**Engineering state:** STAGE_A_FINAL_HUMAN_GATE_FAILED_PATCH_ACTIVE  
**Updated:** 2026-08-29  
**Active work order:** R0.12-STAGE-A-FINAL-CLOSURE-002

## Progress truth

The 0.1.0 installer built from source 80ab920b19c1ed1aebef4fa9b7eab05d6a509f38 passed automated Windows lifecycle engineering but failed the real installed-product Human Gate.

Planning recovered and completed after the machine restart/network recovery. The first Planning rejection was a factual-safety rejection of an unsupported portability implication and is not itself a release defect.

Editing remains a release blocker because the installed application:

- repeatedly flashes child terminal windows during media/runtime work;
- ends the representative real-footage flow in rerender_same_edl rather than final PASS;
- hides the actionable renderer diagnostic behind a generic correction presentation.

The installed UI also lacks visible version identity and an update-discovery path for already distributed copies.

## Current technical findings

- Internal FFmpeg/ffprobe child processes are launched without a shared Windows no-console policy.
- Review permits one same-EDL repair attempt, but ProductFlow currently does not execute that retry.
- Current source-audio construction assumes source audio for each selected video segment even though ingest metadata can identify assets without audio; this is a priority reproduction target for the render failure.
- Application version 0.1.0 is duplicated between project/package inputs and installer inputs instead of being one authoritative source.

## Current gates

- Planning installed path: **HUMAN RUN RECOVERED; FINAL PATCH REGRESSION REQUIRED**.
- Editing visual-first installed path: **HUMAN FAIL — PATCH REQUIRED**.
- Child-process desktop behavior: **FAIL — TERMINAL FLASHING**.
- Renderer/review correction behavior: **FAIL — NO DELIVERABLE PASS / DIAGNOSTIC TOO WEAK**.
- Version visibility: **MISSING**.
- Update discovery for distributed installs: **MISSING**.
- Previous 0.1.0 automated installer lifecycle: **ENGINEERING PASS, HUMAN SUPERSEDED**.
- Stage-A completion gate: **OPEN FOR PATCH + REPLACEMENT RC + FINAL HUMAN GATE**.

Therefore structural progress remains **95%**.

## Final path to 100%

```text
bounded release-blocker patch
→ replacement version > 0.1.0
→ CI
→ Windows Release Candidate workflow
→ install/upgrade/repair/uninstall PASS
→ ordinary-user Planning regression
→ ordinary-user visual-first Editing PASS
→ confirm no child terminal flashes
→ confirm visible version/update discovery
→ durable Human evidence
→ Stage-A 100%
```

## Update-distribution direction

Because the source repository is private, update discovery must not depend on authenticated access to this repository.

Use a public, source-free stable-channel manifest for version metadata and release notice. The desktop app may check it asynchronously at startup and on explicit user request. Offline/update-check failure must never block core work.

A silent self-updater or delta updater remains deferred; the current guided Setup.exe can continue to perform explicit upgrades using the stable AppId.

## Non-blocking follow-up

Do not broaden this patch into:

- advanced speech reconstruction;
- translated/bilingual subtitles;
- cross-language narration/TTS;
- Remote Reference URL;
- delta/Web Setup auto-updater;
- unrelated cosmetic redesign.

The Inno Setup commercial-use licensing policy remains a release-management item before commercial distribution.
