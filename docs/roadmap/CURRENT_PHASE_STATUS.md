# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** RELEASED  
**Structural progress:** 100%  
**Current phase:** R0.13 — 1.0 release polish and compatibility  
**Engineering state:** R0.13_CLOSED_1_0_0_RELEASED  
**Updated:** 2026-09-19  
**Active work order:** NONE  
**Current review track:** SignPath Foundation pre-application / PR #35 security hardening

## Accepted release baseline

R0.13 is **CLOSED** and Stage A remains **100% complete**.

Accepted stable product:

- application version: `1.0.0`;
- exact stable source: `fc6391b846432586a41311a295251e8860cdf9fa`;
- stable release: `v1.0.0`;
- final Windows verification: **PASS**;
- installer SHA-256: `dd47f88953d134dac522990db80fc719367a7abe627203b142fe681cb786e5a8`.

Planning and Automatic Editing remain Human-accepted **PASS**.

Current repository engineering baseline:

`15cc7204a21818b3df60f80002e1627e59576185`

This includes the merged Apache-2.0/SignPath governance work, retained FFmpeg source fix, and real packaged VERSIONINFO evidence gate.

## Completed post-release governance gates

PR #36 — Apache-2.0 / SignPath governance: **MERGED / Human-approved**.

PR #38 — retained BtbN FFmpeg month-end packaging source and required-check trigger alignment: **MERGED / Human-approved**.

PR #39 — actual packaged PE VERSIONINFO readback/evidence, including the Windows PowerShell 5.1 encoding-safe ProductName expectation: **MERGED / Human-approved**.

These changes are accepted `main` truth.

## Windows packaging metadata proof

`Windows Packaging Candidate` run #10 / `35443472940` completed **SUCCESS** from:

`main@15cc7204a21818b3df60f80002e1627e59576185`

Real packaged executable results:

- `VideoEditingAgent.exe`: `ProductName=有岐`, `ProductVersion=1.0.0`, `FileVersion=1.0.0.0` — PASS;
- `VideoEditingAgent-cli.exe`: same values — PASS;
- `VideoEditingAgent-updater.exe`: same values — PASS.

Artifact:

`VideoEditingAgent-windows-x64-15cc7204a21818b3df60f80002e1627e59576185`

Artifact archive digest:

`sha256:8a88c158742c8a6f8e88378f61819903116da042d63ef8a04680b37a557148c6`

The workflow uploads both the built onedir tree and the complete packaging evidence directory containing `windows-version-info.json`.

**Windows VERSIONINFO evidence gate: PASS.**

## Governance controls active

- both named signing-team GitHub accounts have 2FA enabled;
- `main-production-protection` is active;
- no bypass actors;
- one approving PR review required;
- stale approvals dismissed on new pushes;
- unresolved review threads block merge;
- protected PRs must be up to date;
- required checks: `Quality Gate`, `inventory`, `repository-doctor`;
- protected-branch deletion and force/non-fast-forward updates blocked.

## Remaining post-release security track

### PR #35 — security hardening

`security: harden component update trust chain`

State: **Draft / not merge-ready**.

The branch includes signed-manifest verification, stricter update-origin and component-integrity checks, actual Authenticode signer-certificate binding, rollback/recovery hardening, updater protocol migration, release/promotion protections, and the production Ed25519 public-key rotation.

The final public Windows signing route is not yet integrated. The intended route is **SignPath Foundation**, subject to Foundation approval. The earlier PFX/cloud-HSM adapter remains engineering scaffolding rather than accepted production identity.

## Release boundary

Stable `v1.0.0` remains published and unchanged.

The existing stable release predates SignPath and must not be represented as SignPath-signed. The post-release governance and packaging-evidence work did not rebuild or replace the published 1.0.0 installer.

## Next controlled sequence

1. Update the existing `v1.0.0` release/download description for the SignPath application.
2. Submit the SignPath Foundation application.
3. Enable SignPath MFA for signing-team accounts when created.
4. After Foundation approval, integrate SignPath trusted-build signing into PR #35.
5. Run an end-to-end signed Windows RC and verify the v1.0.0 migration path.
6. Complete Liu Lei's final PR #35 security review before merge.

## Historical R0.13 closure

The original R0.13 scope covered installer ETA, DPI/typography, Day/Comfort/Night modes, component/file patching, bilingual installer terms, header consolidation/declaration, and 有岐 branding.

That scope is complete. The verified 1.0.0 RC assets were promoted byte-for-byte to the stable release.

Stable release: <https://github.com/orange-lee-tech/video-editing-agent/releases/tag/v1.0.0>  
Installer: <https://github.com/orange-lee-tech/video-editing-agent/releases/download/v1.0.0/VideoEditingAgent-Setup-1.0.0.exe>
