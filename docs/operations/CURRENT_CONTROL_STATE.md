# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-09-18
current_phase: R0.13
phase_state: CLOSED_1_0_0_RELEASED
active_work_order: NONE
active_construction_branch: NONE
accepted_code_baseline: fc6391b846432586a41311a295251e8860cdf9fa
accepted_engineering_baseline: b201c685fa74b83e3559e16b50f63aea58eddd83
current_main_baseline: b201c685fa74b83e3559e16b50f63aea58eddd83
latest_human_gate_candidate: fc6391b846432586a41311a295251e8860cdf9fa
structural_progress_percent: 100
stage_a_completion_gate: PASS
core_1_planning_product_gate: PASS
core_2_editing_product_gate: PASS
windows_release_delivery_gate: PASS
codex_release: CLOSED
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: RELEASED
stable_release_tag: v1.0.0
stable_release_source: fc6391b846432586a41311a295251e8860cdf9fa
stable_installer_sha256: dd47f88953d134dac522990db80fc719367a7abe627203b142fe681cb786e5a8
post_release_review_state: SECURITY_AND_SIGNING_GOVERNANCE_IN_REVIEW
security_review_pr: 35
governance_review_pr: 36
main_ruleset: main-production-protection
writer: chatgpt
---

## Current accepted truth

Stage-A remains complete at **100%**. Planning and Automatic Editing remain Human-accepted **PASS** and are not reopened by the current post-release work.

The accepted product/release baseline is:

- application version: `1.0.0`;
- exact stable product source: `fc6391b846432586a41311a295251e8860cdf9fa`;
- stable tag: `v1.0.0`;
- stable installer SHA-256: `dd47f88953d134dac522990db80fc719367a7abe627203b142fe681cb786e5a8`.

The current `main` baseline is `b201c685fa74b83e3559e16b50f63aea58eddd83` (`docs: finalize human-accepted 1.0.0`). It is the accepted repository-control baseline; the stable product bytes remain anchored to `fc6391b...`.

R0.13 is **CLOSED**. There is **no active product construction work order** and no active construction branch.

## Post-release security and signing governance review

Two bounded review tracks are open. Neither is part of the accepted `main` baseline until its own Human/automation gates pass and the PR is merged.

### PR #35 — update trust-chain hardening

`security: harden component update trust chain` remains **Draft / not merge-ready**.

Current security branch: `fix/unsigned-patch-update-trust`. The branch head includes the owner-generated production Ed25519 public-key rotation at `79460885647138cbabbfb76e7b40c35eb64099c8`; the private seed is not repository content.

This track hardens signed update manifests, URL/origin policy, component hashes/sizes, Authenticode signer binding, rollback, release evidence, and stable promotion. It must remain unmerged until the final public Windows signing route is integrated and a signed RC plus the v1.0.0 migration path are exercised.

The earlier PFX/cloud-HSM placeholder is **not** the accepted production-signing baseline. The current intended public-signing route is the SignPath Foundation open-source program, subject to Foundation approval and later workflow integration.

### PR #36 — Apache-2.0 and SignPath governance

`governance: adopt Apache-2.0 for 有岐` is **Ready for review / not merged**.

The branch contains the proposed Apache-2.0 project license, NOTICE/license packaging, compatible user-term presentation, public code-signing policy, privacy disclosures, and Windows product/version metadata contract required for the SignPath route.

These changes are still review material. They must not be described as accepted repository truth until the requested human review and protected-branch merge complete.

## Repository governance controls now active

The following controls are already active repository state, independent of whether PR #35/#36 merge:

- both named signing-team GitHub accounts have confirmed 2FA enabled;
- repository ruleset `main-production-protection` is active on the default branch;
- bypass actors: none;
- pull requests require at least one approving review;
- stale approvals are dismissed after new pushes;
- unresolved review threads block merge;
- protected merges require the branch to be up to date;
- required checks: `Quality Gate`, `inventory`, and `repository-doctor`;
- deletion and non-fast-forward/force-push of the protected default branch are blocked.

## Stable-release boundary

Existing `v1.0.0` release assets remain final and unchanged. They predate the planned SignPath Foundation integration and must not be represented as SignPath-signed.

No current governance/security review authorizes:

- replacement of stable `v1.0.0` assets;
- reopening Planning or Automatic Editing;
- new creative/product scope;
- silent weakening of update trust or release evidence;
- production signing before the selected public-signing route is approved and verified.

## Next controlled sequence

1. Finish Liu Lei's human review of PR #36.
2. Merge PR #36 only after the required approval and protected-branch checks pass.
3. Run a Windows Packaging Candidate from the merged source and verify real VERSIONINFO values on the built project executables.
4. Refresh the existing `v1.0.0` release/download description for the SignPath application.
5. Submit the SignPath Foundation application and enable SignPath MFA for signing-team accounts when created.
6. After Foundation approval, integrate the real SignPath trusted-build/signing path into PR #35, replacing the temporary production-signing placeholder.
7. Exercise the signed Windows RC, update-manifest/component evidence, and v1.0.0-to-secure-release migration.
8. Complete Liu Lei's security review of PR #35 before any merge.

## Stable release

Release: <https://github.com/orange-lee-tech/video-editing-agent/releases/tag/v1.0.0>  
Installer: <https://github.com/orange-lee-tech/video-editing-agent/releases/download/v1.0.0/VideoEditingAgent-Setup-1.0.0.exe>

The final stable assets were promoted byte-for-byte from the Human-accepted RC. No post-release security/governance work has modified those published bytes.
