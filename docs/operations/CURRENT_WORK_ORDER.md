# Current Work Order

**ID:** NONE  
**Status:** CLOSED — NO ACTIVE CONSTRUCTION WORK ORDER  
**Phase:** R0.13 — 1.0 release polish and update engineering  
**Mode:** POST-RELEASE REVIEW / SIGNPATH PRE-APPLICATION ONLY  
**Accepted stable baseline:** 1.0.0 / fc6391b846432586a41311a295251e8860cdf9fa  
**Accepted engineering baseline:** 15cc7204a21818b3df60f80002e1627e59576185  
**Most recently closed work order:** R0.13-RELEASE-POLISH-001  
**Updated:** 2026-09-19

## Current authorization

There is currently **no active product-construction work order**.

R0.13 is closed, stable `v1.0.0` is published, and the Planning / Automatic Editing product gates remain accepted **PASS**.

Current work is limited to SignPath Foundation pre-application and the already-open post-release security track. It does not authorize new product scope or reopening R0.13.

## Protected invariants

Until a new explicit construction work order is opened:

- do not add new creative/editing capabilities;
- do not reopen accepted Planning or Automatic Editing behavior without a demonstrated regression;
- do not replace or mutate existing stable `v1.0.0` release assets;
- do not weaken update-origin, signature, hash, signer-identity, rollback, or release-evidence checks;
- do not represent unsigned or self-signed artifacts as publicly trusted production releases;
- do not activate a production code-signing path before the selected public-signing route is approved and verified.

## Closed governance / packaging-evidence tracks

### PR #36 — Apache-2.0 / SignPath governance

State: **MERGED / Human-approved**.

Apache-2.0 licensing, NOTICE/license packaging, compatible user-term presentation, public code-signing policy, privacy disclosures, Windows product/version metadata contract, and SignPath governance prerequisites are accepted `main` truth.

### PR #38 — retained FFmpeg packaging source

State: **MERGED / Human-approved**.

The unavailable BtbN daily FFmpeg autobuild was replaced with the retained month-end LGPL shared build:

- `autobuild-2026-08-31-13-27`;
- `ffmpeg-n8.1.2-50-g1a748fe2cd-win64-lgpl-shared-8.1.zip`;
- SHA-256 `e9712ffbdb03ef71bbab660c75b835bfe698ef6fad0247c76d8d394a39a3db63`.

The runtime GPL/nonfree rejection, OpenH264 requirement, libx264 exclusion and real encode probe remain enforced.

### PR #39 — packaged VERSIONINFO evidence

State: **MERGED / Human-approved after review fix**.

The Windows package now reads back the actual PE VERSIONINFO from all three project-owned executables and fails closed on mismatches.

Liu Lei identified and the branch fixed a Windows PowerShell 5.1 encoding hazard by constructing the expected Chinese ProductName from Unicode code points instead of using a Chinese literal in the BOM-less script.

## SignPath packaging evidence gate

Final proof run:

- workflow: `Windows Packaging Candidate`;
- run: `35443472940` / #10;
- source: `15cc7204a21818b3df60f80002e1627e59576185`;
- result: **SUCCESS**.

Actual binary results:

- `VideoEditingAgent.exe`: ProductName `有岐`, ProductVersion `1.0.0`, FileVersion `1.0.0.0` — PASS;
- `VideoEditingAgent-cli.exe`: ProductName `有岐`, ProductVersion `1.0.0`, FileVersion `1.0.0.0` — PASS;
- `VideoEditingAgent-updater.exe`: ProductName `有岐`, ProductVersion `1.0.0`, FileVersion `1.0.0.0` — PASS.

Uploaded artifact:

`VideoEditingAgent-windows-x64-15cc7204a21818b3df60f80002e1627e59576185`

Artifact archive SHA-256:

`8a88c158742c8a6f8e88378f61819903116da042d63ef8a04680b37a557148c6`

The workflow uploads `build/packaging/evidence`, including the generated `windows-version-info.json`.

**SignPath Windows metadata pre-application gate: PASS.**

## Current review track — PR #35 security hardening

PR: `#35 security: harden component update trust chain`  
State: **Draft / not merge-ready**  
Branch: `fix/unsigned-patch-update-trust`

The security branch contains:

- Ed25519-signed update-manifest verification and strict signature checks;
- reviewed update URL/origin/redirect boundaries;
- component SHA-256 and size verification;
- actual Authenticode signer-certificate extraction and certificate-fingerprint binding;
- updater rollback/integrity protections;
- protocol migration from released v1.0.0;
- sealed RC/stable promotion evidence;
- production Ed25519 public-key rotation.

The owner-generated Ed25519 private seed is not repository content.

The production Windows signing path is still not final. The selected route is SignPath Foundation, subject to approval and trusted-build integration. Earlier PFX/cloud-HSM code is scaffolding, not the accepted production signing identity.

### PR #35 exit conditions

PR #35 must remain unmerged until all of the following are true:

1. SignPath Foundation approves the project;
2. SignPath MFA is enabled for the required signing-team accounts;
3. the actual SignPath trusted-build path is integrated;
4. all security/quality workflows pass at the resulting head;
5. a signed Windows RC is produced through the trusted build;
6. signer identity, installer/component signatures, signed update manifest and release evidence are verified;
7. the v1.0.0-to-secure-release recovery/migration path is exercised;
8. Liu Lei completes the final human security review.

## Repository governance controls completed

- GitHub 2FA enabled for both named signing-team accounts;
- `main-production-protection` active;
- bypass actors: none;
- one approving PR review required;
- new pushes dismiss stale approvals;
- unresolved review threads block merge;
- protected PRs must be up to date;
- `Quality Gate`, `inventory`, and `repository-doctor` are required on every PR;
- deletion and force/non-fast-forward updates blocked on the protected default branch.

## Stable-release boundary

The published `v1.0.0` assets remain unchanged and unsigned by SignPath.

The original 1.0.0 installer used the behavior and legal presentation present in the accepted 1.0.0 source. Later Apache-2.0/governance changes on `main` must not be retroactively described as changes to the already-published binary.

## Next authorized sequence

The next authorized actions are release-governance actions only:

1. refresh the existing `v1.0.0` release/download description with a concise functionality summary and public code-signing-policy link;
2. submit the SignPath Foundation application;
3. enable SignPath MFA when signing-team accounts are created;
4. after SignPath approval, integrate the trusted signing route into PR #35;
5. execute signed-RC and migration verification;
6. finish PR #35 Human security review before merge.

A new product-development work order must be explicitly opened before unrelated product construction begins.
