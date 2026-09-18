# Current Work Order

**ID:** NONE  
**Status:** CLOSED — NO ACTIVE CONSTRUCTION WORK ORDER  
**Phase:** R0.13 — 1.0 release polish and update engineering  
**Mode:** POST-RELEASE REVIEW ONLY  
**Accepted stable baseline:** 1.0.0 / fc6391b846432586a41311a295251e8860cdf9fa  
**Most recently closed work order:** R0.13-RELEASE-POLISH-001  
**Updated:** 2026-09-18

## Current authorization

There is currently **no active product-construction work order**.

R0.13 is closed, stable `v1.0.0` is published, and the Planning / Automatic Editing product gates remain accepted **PASS**.

The work now in progress is a bounded **post-release security and signing-governance review**. It does not authorize new product scope and must not be interpreted as reopening R0.13.

## Protected invariants

Until a new explicit construction work order is opened:

- do not add new creative/editing capabilities;
- do not reopen accepted Planning or Automatic Editing behavior without a demonstrated regression;
- do not replace or mutate existing stable `v1.0.0` release assets;
- do not weaken update-origin, signature, hash, signer-identity, rollback, or release-evidence checks;
- do not represent unsigned or self-signed artifacts as publicly trusted production releases;
- do not activate a production code-signing path before the selected public-signing route is approved and verified.

## Current review track A — PR #35 security hardening

PR: `#35 security: harden component update trust chain`  
State: **Draft / not merge-ready**  
Branch: `fix/unsigned-patch-update-trust`

The security branch currently contains the update trust-chain hardening work, including:

- Ed25519-signed update-manifest verification and strict signature checks;
- reviewed update URL/origin/redirect boundaries;
- component SHA-256 and size verification;
- actual Authenticode signer-certificate extraction and certificate-fingerprint binding;
- updater rollback/integrity protections;
- protocol migration from released v1.0.0;
- sealed RC/stable promotion evidence;
- production Ed25519 public-key rotation.

The owner-generated Ed25519 private seed is not repository content.

The production Windows Authenticode/signing adapter is **not yet final**. Earlier PFX/cloud-HSM implementation text is engineering scaffolding, not the accepted production route. The currently selected direction is the SignPath Foundation open-source signing program, subject to Foundation approval and trusted-build integration.

### PR #35 exit conditions

PR #35 must remain unmerged until all of the following are true:

1. the actual approved public-signing route is integrated;
2. all security/quality workflows pass at the resulting head;
3. a signed Windows RC is produced through the trusted build;
4. signer identity, installer/component signatures, signed update manifest, and release evidence are verified;
5. the v1.0.0-to-secure-release recovery/migration path is exercised;
6. Liu Lei completes the final human security review.

## Current review track B — PR #36 Apache-2.0 / SignPath governance

PR: `#36 governance: adopt Apache-2.0 for 有岐`  
State: **Ready for review / not merged**  
Branch: `governance/adopt-apache-2.0`

This branch proposes the repository-governance prerequisites for the free SignPath Foundation route:

- Apache License 2.0 for project-authored material;
- NOTICE and shipped-license packaging;
- user-term presentation that does not narrow Apache-2.0 rights;
- public code-signing policy;
- privacy disclosures for optional AI providers and update infrastructure;
- Windows product/version metadata for project-owned executables and installer;
- tests that lock the release metadata contract.

These changes are still review material. They become accepted repository truth only after Human approval and protected-branch merge.

### Repository controls already completed

The following are already active and do not depend on PR #36 merging:

- GitHub 2FA is enabled for both named signing-team accounts;
- `main-production-protection` is active on the default branch;
- bypass actors: none;
- one approving PR review required;
- new pushes dismiss stale approvals;
- unresolved review threads block merge;
- the PR branch must be up to date;
- `Quality Gate`, `inventory`, and `repository-doctor` are required checks;
- deletion and force/non-fast-forward updates are blocked on the protected default branch.

### PR #36 exit conditions

1. Liu Lei completes Human review and explicitly approves the governance/licensing change.
2. Protected-branch required checks pass.
3. PR #36 merges to `main`.
4. A Windows Packaging Candidate built from merged source proves the intended VERSIONINFO values on real executables.
5. The stable `v1.0.0` release/download page is expanded with a concise functionality description and code-signing-policy link.
6. The SignPath Foundation application is submitted.
7. SignPath MFA is enabled for signing-team accounts when those accounts are created.

## Historical closed work order

The most recently closed construction order was:

`R0.13-RELEASE-POLISH-001`

It covered the accepted 1.0 release-polish scope:

1. installer remaining-time estimate;
2. Windows DPI-aware typography;
3. Day / Comfort / Night appearance modes;
4. verified component/file patch updates with rollback;
5. bilingual installer terms;
6. Settings/update consolidation plus Declaration;
7. 有岐 branding and slogan while preserving compatibility-sensitive internal identifiers.

That work order is **closed**. Its stable release evidence is:

- tag: `v1.0.0`;
- exact release source: `fc6391b846432586a41311a295251e8860cdf9fa`;
- final Windows verification: **PASS**;
- installer: `VideoEditingAgent-Setup-1.0.0.exe`;
- installer SHA-256: `dd47f88953d134dac522990db80fc719367a7abe627203b142fe681cb786e5a8`.

The original 1.0.0 installer used explicit interactive agreement acceptance. PR #36 proposes a future governance-compatible presentation change for Apache-2.0 licensing; because PR #36 is not yet merged, that proposal must not be retroactively described as part of the published v1.0.0 behavior.

## Next authorized sequence

The next authorized actions are review/release-governance actions only:

1. finish PR #36 Human review;
2. merge PR #36 only after all protected-branch gates pass;
3. verify real Windows package metadata;
4. prepare and submit the SignPath Foundation application;
5. after SignPath approval, integrate the trusted signing route into PR #35;
6. execute signed-RC and migration verification;
7. finish PR #35 Human review before merge.

A new product-development work order must be explicitly opened before any unrelated product construction begins.
