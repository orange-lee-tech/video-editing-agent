# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** RELEASED  
**Structural progress:** 100%  
**Current phase:** R0.13 — 1.0 release polish and compatibility  
**Engineering state:** R0.13_CLOSED_1_0_0_RELEASED  
**Updated:** 2026-08-31  
**Active work order:** NONE

## Stage-A baseline

Stage-A remains **100% complete**.

Accepted core-product baseline:

- application version: `0.1.5`;
- exact source: `e59cab8475a615d29003c03497ddcdaf862476a6`;
- Planning Human Gate: **PASS**;
- Automatic Editing Human Gate: **PASS**.

R0.13 does not reopen those core gates unless a material regression is demonstrated.

## R0.13 scope

The Product Owner approved seven release-polish items before final 1.0.0 packaging:

1. localized installer remaining-time estimate/countdown;
2. Windows DPI-aware crisp typography;
3. persisted Day / Comfort / Night appearance modes;
4. component/file patch updating so ordinary patch releases do not require redownloading the full runtime bundle;
5. bilingual installer Software License and User Agreement requiring explicit interactive acceptance;
6. header consolidation so update checking lives inside Settings plus a sibling Declaration control;
7. visible product branding as `有岐` with slogan `创作有岐，表达有路`, while compatibility-sensitive internal identifiers remain stable.

## Release boundary

Structural progress remains **100%** because core construction is complete.

R0.13 is **CLOSED**. Planning and Editing remain accepted PASS. The Product Owner accepted the bounded presentation hotfix, the application version remains `1.0.0`, and the verified hotfix RC assets have been promoted to the stable `v1.0.0` release.

The full Setup.exe remains the bootstrap/recovery path. Routine future patch updates should use verified changed-component delivery with rollback rather than byte-level binary diff machinery.

## Verification focus

R0.13 must preserve:

- Stage-A Planning/Editing behavior;
- public update discovery;
- Windows packaged GUI smoke;
- packaged H.264 encode verification;
- installer upgrade/repair/uninstall lifecycle;
- Workspace/original-media safety.

Before final 1.0.0 authorization, Windows presentation must also be reviewed at 100%, 125%, 150% and 200% display scaling.


## Current 0.1.6 engineering RC

Exact candidate: `111b50f13d1b19670dfe0e0a68bfa2da00212a5f`  
Windows RC: `33379570088` — **SUCCESS**  
Installer SHA-256: `f6a90b2a8b484806e893d0bbcc369adf5ced83425a14e887bc6f65954528796b`

This is the remediated Human-review candidate after three observed UI regressions in the earlier 0.1.6 RC: Settings must retain Import / Export / Save / Delete profile actions, developer-homepage activation must show the temporary-closure notice instead of exposing the page, and Day / Comfort / Night selection must visibly preview immediately. The remediated candidate passed repository and Windows staging / Setup.exe / install-upgrade-repair-uninstall engineering verification.

The Product Owner reports all required visual/interaction review items **PASS**, including the required Windows display-scaling review. R0.13 is closed and final `1.0.0` packaging is authorized. Remaining activity is release finalization only; no new creative capability scope is opened.


## Final stable 1.0.0 release

Stable release: `v1.0.0` — **PUBLISHED**  
Exact release source: `fc6391b846432586a41311a295251e8860cdf9fa`  
Final Windows verification run: `33401022544` — **SUCCESS**  
Installer lifecycle: **PASS**  
Installer: `VideoEditingAgent-Setup-1.0.0.exe`  
Installer SHA-256: `dd47f88953d134dac522990db80fc719367a7abe627203b142fe681cb786e5a8`

Stable release page: https://github.com/orange-lee-tech/video-editing-agent/releases/tag/v1.0.0  
Direct installer: https://github.com/orange-lee-tech/video-editing-agent/releases/download/v1.0.0/VideoEditingAgent-Setup-1.0.0.exe

The final stable installer and component patch assets are byte-for-byte copies of `v1.0.0-rc-fc6391b`, which passed the Windows install / upgrade / repair / uninstall lifecycle gate. Promotion run `33406476432` succeeded, `v1.0.0` now resolves to `fc6391b846432586a41311a295251e8860cdf9fa`, and no product-source rebuild occurred during promotion.


## 1.0.0 presentation hotfix candidate

The Product Owner confirms both core functions **PASS**. Final presentation review found three non-core regressions, now repaired without changing the release version:

- local-reference picker aligned to the actual local-reference field;
- English visible brand localized to `Youqi` with slogan `Create your way, express your path`;
- clipped header API-status pill removed, eliminating the stray `/` glyph.

Exact source: `fc6391b846432586a41311a295251e8860cdf9fa`  
Version: `1.0.0`  
Quality Gate: run `33400752251` — **SUCCESS**  
Windows RC: run `33401022544` — **SUCCESS**  
Installer lifecycle: **PASS**  
Prerelease: `v1.0.0-rc-fc6391b`

Human Gate: **PASS** for all three presentation items. Core Planning/Editing were not reopened. This candidate is now the final stable `1.0.0` source.
