# Current Roadmap Phase Status

**Roadmap V2:** ACTIVE  
**Development stage:** RELEASED  
**Structural progress:** 100%  
**Current phase:** R0.13 — 1.0 release polish and compatibility  
**Engineering state:** R0.13_CLOSED_1_0_0_RELEASED  
**Updated:** 2026-09-18  
**Active work order:** NONE  
**Current review track:** Post-release security and signing governance

## Accepted release baseline

R0.13 is **CLOSED** and Stage-A remains **100% complete**.

Accepted stable product:

- application version: `1.0.0`;
- exact stable source: `fc6391b846432586a41311a295251e8860cdf9fa`;
- stable release: `v1.0.0`;
- final Windows verification: **PASS**;
- installer SHA-256: `dd47f88953d134dac522990db80fc719367a7abe627203b142fe681cb786e5a8`.

Planning and Automatic Editing remain Human-accepted **PASS**. No current activity reopens those product gates.

The repository default branch currently points to `b201c685fa74b83e3559e16b50f63aea58eddd83`, a documentation finalization commit after the accepted 1.0.0 product source.

## Current post-release review

Current engineering activity is a bounded **post-release security / signing-governance review**, not a new product-construction phase.

### PR #35 — security hardening

`security: harden component update trust chain`

State: **Draft / not merge-ready**.

The branch includes signed-manifest verification, stricter update-origin and component-integrity checks, actual Authenticode signer-certificate binding, rollback/evidence hardening, updater-protocol migration, and release/promotion protections.

The production Ed25519 public key has been rotated on the branch; the private seed is not repository content.

The final public Windows signing route is not yet integrated. The previous PFX/cloud-HSM adapter is an engineering placeholder, not an accepted production identity. The intended route is now the **SignPath Foundation** open-source signing program, subject to Foundation approval.

### PR #36 — Apache-2.0 / SignPath governance

`governance: adopt Apache-2.0 for 有岐`

State: **Ready for review / not merged**.

The branch proposes:

- Apache License 2.0 for project-authored material;
- aligned NOTICE/license packaging;
- user-term presentation compatible with Apache-2.0 rights;
- public code-signing policy;
- privacy disclosures for optional providers and update infrastructure;
- Windows VERSIONINFO/ProductName/ProductVersion metadata contracts.

These are pending Human review and are not yet accepted `main` truth.

## Governance controls already active

Repository-level controls now in force:

- both named signing-team GitHub accounts have 2FA enabled;
- `main-production-protection` is active on the default branch;
- no bypass actors are configured;
- one approving PR review is required;
- stale reviews are dismissed after new commits;
- unresolved review threads block merge;
- protected merges must be up to date;
- required checks are `Quality Gate`, `inventory`, and `repository-doctor`;
- protected-branch deletion and force/non-fast-forward updates are blocked.

These controls are current repository state and do not depend on PR #35/#36 merging.

## Release boundary

Stable `v1.0.0` remains published and unchanged.

The existing stable release predates SignPath integration and must not be represented as SignPath-signed. Current governance/security work does not authorize changing the published 1.0.0 binaries.

The following remain outside the current review boundary:

- new creative/editing capabilities;
- reopening Planning or Automatic Editing;
- replacing existing stable-release bytes;
- weakening update trust to make unsigned/self-signed artifacts appear production-trusted.

## Next controlled sequence

1. Liu Lei completes the human review of PR #36.
2. PR #36 may merge only after the protected-branch review/check requirements pass.
3. Run the Windows Packaging Candidate from merged source and inspect actual EXE VERSIONINFO.
4. Refresh the `v1.0.0` release/download description for the SignPath application.
5. Submit the SignPath Foundation application and enable SignPath MFA for signing-team accounts.
6. After Foundation approval, integrate SignPath trusted-build signing into PR #35.
7. Run an end-to-end signed Windows RC and verify the v1.0.0 migration path.
8. Complete human security review of PR #35 before merge.

## Historical R0.13 closure

The original R0.13 scope covered installer ETA, DPI/typography, Day/Comfort/Night modes, component/file patching, bilingual installer terms, header consolidation/declaration, and 有岐 branding.

That scope has been completed and accepted. The verified 1.0.0 RC assets were promoted byte-for-byte to the stable release; no product-source rebuild occurred during stable promotion.

Stable release: <https://github.com/orange-lee-tech/video-editing-agent/releases/tag/v1.0.0>  
Installer: <https://github.com/orange-lee-tech/video-editing-agent/releases/download/v1.0.0/VideoEditingAgent-Setup-1.0.0.exe>
