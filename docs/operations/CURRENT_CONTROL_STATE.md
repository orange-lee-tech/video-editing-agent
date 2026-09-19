# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-09-19
current_phase: R0.13
phase_state: CLOSED_1_0_0_RELEASED
active_work_order: NONE
active_construction_branch: NONE
accepted_code_baseline: fc6391b846432586a41311a295251e8860cdf9fa
accepted_engineering_baseline: 15cc7204a21818b3df60f80002e1627e59576185
current_main_baseline: 15cc7204a21818b3df60f80002e1627e59576185
latest_human_gate_candidate: fc6391b846432586a41311a295251e8860cdf9fa
structural_progress_percent: 100
stage_a_completion_gate: PASS
core_1_planning_product_gate: PASS
core_2_editing_product_gate: PASS
windows_release_delivery_gate: PASS
windows_versioninfo_evidence_gate: PASS
codex_release: CLOSED
foreman: v2-trigger-first
disclosure_policy: trigger-first
development_stage: RELEASED
stable_release_tag: v1.0.0
stable_release_source: fc6391b846432586a41311a295251e8860cdf9fa
stable_installer_sha256: dd47f88953d134dac522990db80fc719367a7abe627203b142fe681cb786e5a8
post_release_review_state: SIGNPATH_FOUNDATION_PREAPPLICATION_READY
security_review_pr: 35
governance_review_pr: 36
governance_review_state: MERGED_APPROVED
ffmpeg_retention_fix_pr: 38
ffmpeg_retention_fix_state: MERGED_APPROVED
versioninfo_evidence_pr: 39
versioninfo_evidence_state: MERGED_APPROVED
windows_packaging_candidate_run: 35443472940
windows_packaging_candidate_state: PASS
main_ruleset: main-production-protection
writer: chatgpt
---

## Current accepted truth

Stage A remains complete at **100%**. Planning and Automatic Editing remain Human-accepted **PASS** and are not reopened by the current post-release work.

The accepted stable product/release baseline remains:

- application version: `1.0.0`;
- exact stable product source: `fc6391b846432586a41311a295251e8860cdf9fa`;
- stable tag: `v1.0.0`;
- stable installer SHA-256: `dd47f88953d134dac522990db80fc719367a7abe627203b142fe681cb786e5a8`.

The current accepted repository-engineering baseline is:

`15cc7204a21818b3df60f80002e1627e59576185`

This includes the Human-approved Apache-2.0 / SignPath governance merge, the retained FFmpeg packaging-source fix, and fail-closed packaged VERSIONINFO verification.

R0.13 remains **CLOSED**. There is **no active product-construction work order** and no active construction branch.

## Completed SignPath pre-application governance/packaging gates

### PR #36 — Apache-2.0 and SignPath governance

PR #36 was Human-approved by Liu Lei and merged to `main` as part of the accepted baseline.

Accepted repository truth now includes:

- Apache License 2.0 for project-authored material;
- aligned NOTICE and packaged-license handling;
- user-term presentation compatible with Apache-2.0 rights;
- public code-signing policy;
- privacy disclosures for optional providers and update infrastructure;
- Windows ProductName/ProductVersion metadata contract;
- protected-main governance and MFA expectations.

### PR #38 — retained FFmpeg packaging source

PR #38 was Human-approved and merged.

The expired BtbN daily FFmpeg autobuild pin was replaced by the retained month-end build:

- tag: `autobuild-2026-08-31-13-27`;
- asset: `ffmpeg-n8.1.2-50-g1a748fe2cd-win64-lgpl-shared-8.1.zip`;
- archive SHA-256: `e9712ffbdb03ef71bbab660c75b835bfe698ef6fad0247c76d8d394a39a3db63`.

The existing runtime hard gates remain: reject GPL/nonfree builds, require `libopenh264`, require `libx264` disabled, and perform a real H.264 encode + ffprobe check.

The same PR also aligned the Ruleset-required `inventory` and `repository-doctor` contexts so they run on every pull request.

### PR #39 — real packaged VERSIONINFO evidence

PR #39 was Human-reviewed, fixed after a Windows PowerShell 5.1 encoding finding, re-approved by Liu Lei, and merged.

The packaging path now reads the actual PE `FileVersionInfo` from all three project-owned executables and fails closed unless the expected values match. The ProductName expectation is constructed from Unicode code points rather than a Chinese literal in the BOM-less PowerShell script.

## Windows Packaging Candidate evidence

Final SignPath pre-application packaging proof:

- workflow: `Windows Packaging Candidate`;
- run: `35443472940` / run #10;
- source: `main@15cc7204a21818b3df60f80002e1627e59576185`;
- result: **SUCCESS**;
- uploaded artifact: `VideoEditingAgent-windows-x64-15cc7204a21818b3df60f80002e1627e59576185`;
- artifact archive digest: `sha256:8a88c158742c8a6f8e88378f61819903116da042d63ef8a04680b37a557148c6`;
- artifact upload includes `build/packaging/dist/VideoEditingAgent` and `build/packaging/evidence`.

The real Windows binaries reported:

- `VideoEditingAgent.exe` — ProductName `有岐`, ProductVersion `1.0.0`, FileVersion `1.0.0.0` — **PASS**;
- `VideoEditingAgent-cli.exe` — ProductName `有岐`, ProductVersion `1.0.0`, FileVersion `1.0.0.0` — **PASS**;
- `VideoEditingAgent-updater.exe` — ProductName `有岐`, ProductVersion `1.0.0`, FileVersion `1.0.0.0` — **PASS**.

The same successful packaging path writes `build/packaging/evidence/windows-version-info.json`, and the workflow uploads the complete evidence directory.

Therefore the **Windows VERSIONINFO evidence gate is PASS**.

## Repository governance controls active

- both named signing-team GitHub accounts have confirmed 2FA enabled;
- `main-production-protection` is active on the default branch;
- bypass actors: none;
- pull requests require at least one approving review;
- stale approvals are dismissed after new pushes;
- unresolved review threads block merge;
- protected merges require the branch to be up to date;
- required checks: `Quality Gate`, `inventory`, and `repository-doctor`;
- deletion and non-fast-forward/force-push of the protected default branch are blocked.

## Remaining security/signing track — PR #35

`security: harden component update trust chain` remains **Draft / not merge-ready**.

Current branch: `fix/unsigned-patch-update-trust`.

It contains update-manifest signature verification, origin/hash/size checks, actual Authenticode signer-certificate binding, rollback/recovery protections, release evidence, updater protocol migration, and the owner-generated production Ed25519 public-key rotation.

The earlier PFX/cloud-HSM production-signing adapter is not accepted production truth. The selected public-signing route is SignPath Foundation, subject to Foundation approval and trusted-build integration.

PR #35 must remain unmerged until SignPath is approved, the real SignPath path is integrated, a signed Windows RC and v1.0.0 migration path are exercised, and Liu Lei completes the final security review.

## Stable-release boundary

Existing `v1.0.0` release assets remain final and unchanged. They predate SignPath integration and must not be represented as SignPath-signed.

No current governance/security work authorizes replacement of those stable bytes.

## Next controlled sequence

1. Expand the existing `v1.0.0` release/download description with a concise functionality description and a public code-signing-policy link.
2. Submit the SignPath Foundation application.
3. Enable SignPath MFA for signing-team accounts when those accounts are created.
4. After Foundation approval, integrate the real SignPath trusted-build/signing path into PR #35.
5. Exercise the signed Windows RC, signed update-manifest/component evidence, and v1.0.0-to-secure-release migration.
6. Complete Liu Lei's final PR #35 security review before merge.

## Stable release

Release: <https://github.com/orange-lee-tech/video-editing-agent/releases/tag/v1.0.0>  
Installer: <https://github.com/orange-lee-tech/video-editing-agent/releases/download/v1.0.0/VideoEditingAgent-Setup-1.0.0.exe>

The final stable assets were promoted byte-for-byte from the Human-accepted RC. No post-release governance, packaging-evidence, or security work has modified those published bytes.
