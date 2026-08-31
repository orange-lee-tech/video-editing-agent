# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** RELEASE_ENGINEERING  
**Structural progress:** 100%  
**Current phase:** R0.13 — 1.0 release polish and compatibility  
**Engineering state:** RELEASE_POLISH_ENGINEERING_PASS_HUMAN_REVIEW_PENDING  
**Updated:** 2026-08-31  
**Active work order:** R0.13-RELEASE-POLISH-001

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

Final `1.0.0` packaging remains **NOT AUTHORIZED** until R0.13 closes.

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

Exact candidate: `6a6bb6fb84345a3c974168f0b4fa0d013af2fc92`  
Windows RC: `33325249400` — **SUCCESS**  
Installer SHA-256: `fb44abd8818ded1e899757e8ba33132ebffe88cc409578d29a1fba9081da4787`

The seven-item R0.13 implementation has passed repository and Windows engineering verification. Remaining work is Product Owner visual/interaction review only; R0.13 and final 1.0.0 packaging remain open/not authorized until that review is accepted.
