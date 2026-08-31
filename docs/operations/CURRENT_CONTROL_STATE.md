# Current Control State

---
schema: video-editing-agent-control-state/v1
updated: 2026-08-31
current_phase: R0.13
phase_state: CLOSED_1_0_0_RELEASED
active_work_order: NONE
active_construction_branch: main
accepted_code_baseline: 35d99730d250d09c23a955c8df682c037335f58c
accepted_engineering_baseline: 111b50f13d1b19670dfe0e0a68bfa2da00212a5f
current_main_baseline: 35d99730d250d09c23a955c8df682c037335f58c
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
writer: chatgpt
---

## Current accepted truth

Stage-A remains complete at **100%** with accepted core baseline:

`e59cab8475a615d29003c03497ddcdaf862476a6` / version `0.1.5`.

R0.13 is a bounded post-Stage-A release-engineering phase. It does not reopen Planning or Editing unless a material regression appears.

## Closed R0.13 work

Work order:

`R0.13-RELEASE-POLISH-001`

Approved scope:

1. installer remaining-time estimate/countdown;
2. Windows DPI-aware typography and clearer Chinese text;
3. persisted Day / Comfort / Night appearance modes;
4. verified component/file patch updates with rollback, while retaining the full Setup.exe as bootstrap/recovery fallback;
5. bilingual installer Software License and User Agreement with explicit interactive acceptance;
6. header consolidation so update checking lives inside Settings plus a sibling Declaration control;
7. visible product branding as `有岐` with slogan `创作有岐，表达有路`, while compatibility-sensitive internal identifiers remain stable.

## Release boundary

Final `1.0.0` is **PUBLISHED and FINAL** after the Product Owner accepted the bounded presentation hotfix on 2026-08-31. The stable `v1.0.0` tag now resolves to exact source `fc6391b846432586a41311a295251e8860cdf9fa`; that source passed the repository Quality Gate and full Windows installer lifecycle before byte-for-byte promotion of the verified RC assets.

No advanced creative capability work belongs in this phase.

Execution discipline: direct bounded repository edits are preferred for deterministic work; Codex is reserved for genuinely complex/local Windows iteration. The accepted Planning and Editing paths are protected invariants and any regression blocks R0.13 closure.

## Required invariants

R0.13 changes must preserve:

- accepted Planning/Editing behavior;
- external Workspace/original-media safety;
- public update discovery;
- packaged H.264 encode verification;
- guided installer lifecycle;
- fail-open network/update checks;
- explicit user consent for applying an update.

Byte-level binary delta algorithms are out of scope; component/file replacement with cryptographic verification and rollback is the chosen 1.0 update strategy.


## Current R0.13 engineering candidate

Version `0.1.6`, exact source `111b50f13d1b19670dfe0e0a68bfa2da00212a5f`, completed Windows RC run `33379570088` with **SUCCESS**.

Installer SHA-256:

`f6a90b2a8b484806e893d0bbcc369adf5ced83425a14e887bc6f65954528796b`

This candidate supersedes the earlier `6a6bb6f` Human-review candidate after Product Owner feedback found three UI regressions: inaccessible profile Import / Export / Save / Delete actions in the fixed-height Settings dialog, premature developer-homepage exposure, and appearance selection that did not visibly apply on selection. The remediation preserves both form/API profile actions in a resizable scrollable Settings surface, replaces developer-homepage navigation with the temporary-closure notice, and applies Day / Comfort / Night preview immediately with cancel restore and persisted apply behavior.

Engineering verification is complete. The Product Owner reports all R0.13 visual/interaction review items **PASS**, including the final three presentation-hotfix checks. R0.13 is closed and stable `v1.0.0` is final. Final hotfix Windows verification run `33401022544` passed install / upgrade / repair / uninstall lifecycle validation. The final stable installer SHA-256 is `dd47f88953d134dac522990db80fc719367a7abe627203b142fe681cb786e5a8`.


## Stable release

Release: https://github.com/orange-lee-tech/video-editing-agent/releases/tag/v1.0.0  
Installer: https://github.com/orange-lee-tech/video-editing-agent/releases/download/v1.0.0/VideoEditingAgent-Setup-1.0.0.exe

The final stable assets were promoted byte-for-byte from `v1.0.0-rc-fc6391b` after Human Gate acceptance; no product binary rebuild occurred during promotion. Stable promotion run `33406476432` passed, and `v1.0.0` now resolves to exact source `fc6391b846432586a41311a295251e8860cdf9fa`.


## 1.0.0 presentation hotfix review

The Product Owner reports both core product functions **PASS** and those core gates remain closed/accepted. During final 1.0.0 presentation acceptance, three bounded desktop defects were observed: the local-reference picker was attached to the wrong grid row, English mode left the visible product brand/slogan in Chinese, and the header API-status pill could collapse to a stray `/` glyph.

Exact hotfix source: `fc6391b846432586a41311a295251e8860cdf9fa`  
Application version: `1.0.0` (unchanged)  
Repository Quality Gate: **PASS**, run `33400752251`  
Windows RC / installer lifecycle: **PASS**, run `33401022544`  
Human-review prerelease: `v1.0.0-rc-fc6391b`

The Product Owner visually rechecked all three presentation fixes and reports **PASS**. The verified RC assets were promoted to the stable `v1.0.0` release without rebuilding. No Planning/Editing capability was reopened.
