# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** STRUCTURAL_CONSTRUCTION  
**Structural progress:** 95%  
**Current phase:** R0.12 — Stage-A final source consolidation + Windows release delivery  
**Engineering state:** STAGE_A_FINAL_SOURCE_CONSOLIDATION_AND_INSTALLER  
**Updated:** 2026-08-26

## Progress truth

Structural percentage measures real ordinary-user end-to-end usability, not module/test/UI count.

Hard 100% contract:

`docs/roadmap/STAGE_A_COMPLETION_GATE.md`

Current remote `main` is:

`153a7686aef3700c2a992542884a33dc135225cc`

The latest Product Owner Human Gate was executed on a focused local patch based on that main. That local patch is not yet an accepted GitHub implementation SHA, so its successful observations are evidence for the next acceptance step rather than proof that current remote main is already release-ready.

Current gates:

- Planning Product/Human Gate: **OPEN — QUALITY HARDENING REQUIRED.** The focused local repair stopped unsupported fit/operability claims from escaping review and Planning completed, but the recovered ScriptPlan/ShootingPlan was too sparse, repetitive and commercially weak for the Product Owner's quality bar.
- Editing visual-first Product/Human Gate: **LOCAL PASS PENDING ACCEPTED SHA / INSTALLER.** Real Chinese-speaking and English-speaking local footage both reached completed automatic visual-first edits after the cross-language retrieval repair. This proves the visual understanding → Director → Resolver → EDL → Renderer core path on the local repair candidate.
- Speech-continuity / multilingual voice production: **DEFERRED TO 2.0 BY PRODUCT OWNER.** Source-speech separation/reconstruction, sentence-preserving dialogue editing, translated/bilingual subtitles and cross-language synthesized narration must not block 1.0 and unfinished controls must remain hidden.
- Editing no-speech historical Human baseline: remains PASS unless a later regression disproves it.
- local reference video: supported.
- remote reference URL: deliberately deferred to 2.0; not a 1.0 blocker.
- Project Workspace / desktop UX foundation: ACCEPTED / PR #17.
- Windows packaging/runtime foundation: ACCEPTED / PR #19 + PR #20.
- Windows ordinary release delivery: **OPEN** — final user delivery must be guided `Setup.exe`, not raw large ZIP extraction.
- Stage-A completion gate: OPEN.

Therefore progress remains **95%**, not 100%.

## Current implementation truth

Accepted runtime/packaging engineering foundation:

`c2c959239cf8842388ac661777c19f20f64a6a90` (PR #20)

Current remote main:

`153a7686aef3700c2a992542884a33dc135225cc`

A focused local repair based on this main has now demonstrated two important behaviors:

1. conservative factual recovery can prevent repeated unsupported commercial claims from being committed; and
2. keeping internal lexical retrieval queries aligned with footage-evidence language can resolve real Chinese/English footage correctly through the visual-first Editing path.

These repairs still require normal source acceptance, full quality verification and CI before they become main truth.

The current onedir artifact size (~769 MB compressed / ~1.88 GB extracted) is engineering staging/evidence only. Speech runtime/model content is no longer a default 1.0 release requirement after the 2026-08-26 Product Owner decision, so the final installer should not carry that payload merely because the earlier engineering probe did.

## Active closure method

The final source and release loop is:

```text
accepted real Human evidence
→ preserve focused local repair
→ Planning quality hardening + small UI cleanup
→ targeted tests
→ full repository quality gate
→ commit/push/CI
→ explicit release-candidate staging build
→ guided Setup.exe build
→ ordinary-user installer Human Gate
→ closure evidence
```

Do not use a full Windows artifact as the transport for every source repair.

## What remains before effective 100%

### A. Planning quality closure

Planning factual safety must remain fail-closed, but the normal successful result must also be useful. The ScriptPlan/ShootingPlan should avoid repetitive fallback copy, preserve section roles, provide a meaningful hook/structure/closing without inventing facts, and give ordinary users concrete executable filming instructions, alternate/backup coverage and realistic equipment-aware guidance.

This is a quality gate, not permission to weaken commercial-fact review.

### B. Final Editing source acceptance

Accept the focused cross-language retrieval repair through normal repository tests/quality gate/CI. Visual-first Editing remains the 1.0 authority. Do not reopen speech-continuity reconstruction as a 1.0 blocker.

### C. 1.0 UI isolation

Hide unfinished speech/subtitle translation/TTS controls. Configuration import should use direct independent Form/Director and API actions rather than a select-scope-then-import interaction. Remote reference URL remains hidden.

### D. Provider/runtime robustness

Retain bounded, understandable provider quota/wait behavior and truthful runtime diagnostics. Engineering development-runtime conveniences must not become ordinary-user setup requirements.

### E. Windows release delivery

Produce and Human-test a guided `Setup.exe` install/upgrade-or-repair/uninstall path using established installer tooling. The 1.0 default payload should contain only capabilities actually shipped in 1.0; deferred speech/TTS assets must not inflate the default package.

### F. Closure evidence

Record exact final release SHA/artifact identities, installer/runtime component identities and concise Human PASS/FAIL observations.

If all gates pass, Stage-A may move directly from 95% to 100%. Do not create artificial percentage increments for each repair.

## Active Work Order

`R0.12-STAGE-A-FINAL-CLOSURE-002`
