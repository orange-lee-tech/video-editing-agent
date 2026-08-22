# Product UX Backlog

**Updated:** 2026-08-22  
**Purpose:** preserve ordinary-user UX work without overriding the live Work Order.  
**Current authority:** `docs/operations/CURRENT_WORK_ORDER.md` and `docs/operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`.

Priority:

- **P0** — required for the current Stage-A / 1.0 closure;
- **P1** — high-value usability after the current closure wave is stable;
- **P2 / 2.0** — future capability expansion that must not be faked in 1.0.

## Current truth

- structural progress is **95%**; Stage-A completion remains OPEN;
- Planning Product/Human Gate is PASS on the supported 1.0 surface;
- ordinary no-speech Editing Human Gate is PASS with real footage, source audio, rights-safe BGM and no fabricated subtitles;
- ordinary remote reference URL is hidden in 1.0; local reference video remains supported;
- bounded Bilibili acquisition is only an engineering fallback seam;
- provider-neutral remote/video observation is deferred to 2.0;
- next sequence is Project Workspace + UX consolidation → Windows packaging → final retained Human Gate.

Do not use this backlog to reopen an accepted gate or override the live control trio.

---

# P0 — Project Workspace + UX consolidation

Specification:

`docs/operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`

Required ordinary-user outcomes:

1. One shared top-level `项目工作区 / Project Workspace` context for Planning and Editing.
2. Project-specific writable state belongs under that workspace: existing `project.sqlite3`, artifacts, project cache/work/session scratch, bounded form draft/undo-redo state, project logs and default outputs. Do not duplicate canonical Domain state into ad-hoc snapshots.
3. Editing derives a visible project-local default output, while retaining explicit Save As and safe overwrite/collision handling.
4. Main-window configuration actions are consolidated into Import / Export / Save / Delete. Form configuration and API/provider configuration can be selected independently or together. Never export plaintext API keys; retain Windows protected-secret semantics.
5. Main-window Clear / Undo / Redo acts on coherent active-form state, not only the focused text widget. UI history is separate from immutable/revisioned Domain history and must be bounded.
6. Planning and Editing internal groups become vertical collapsible sections suitable for ordinary laptop windows.
7. The generated Canvas pixel-camera mark must not be frozen as the permanent brand. Prefer the real previously approved feather asset if it can be recovered; otherwise leave icon replacement as a Human Gate rather than inventing an approximation.
8. Project switching/opening must not silently discard unsaved drafts and must not default writable project state into the packaged install directory.
9. Remote reference URL stays hidden throughout this wave.

---

# P1 — retained usability backlog

## Media selection summary

After selecting multiple source files, show a compact local summary such as selected count and optional total size, with inspect/reselect actions. Exact selected paths remain authoritative; do not scan unrelated files or call the cloud just to build the summary.

## Result actions

Once a result exists:

- Planning: Copy result / Export TXT;
- Editing: Open output directory / Copy output path / View technical details.

Do not show output actions before a result exists.

## Recent projects

A bounded recent-project list may store only workspace path, non-sensitive display metadata and last-opened time. Do not duplicate canonical project entities or secrets.

## Capability-oriented Settings / Doctor

Present product roles before vendor names: Reasoning & Direction and Visual Understanding. Provider/model/endpoint/credential configure those roles; no silent provider fallback.

Environment Doctor should remain a static/local readiness surface by default and must not silently spend API quota.

## Provider quota / wait UX

Provider-directed retry/wait states should look intentional rather than frozen. Primary messages are localized, technical detail is bounded, and secrets stay redacted.

## High-DPI / keyboard / laptop Human Smoke

Retain 100/125/150% scaling, 1366×768-class screen, Chinese/English, Tab order, keyboard activation and non-color-only status checks.

## Safe Cancel / Resume

Do not expose a decorative Cancel button until worker/provider/FFmpeg cancellation and accepted-artifact state have a tested owner-safe contract.

---

# P2 / 2.0 — explicit expansion backlog

## Provider-neutral remote reference observation

Future ordinary remote-reference support should live behind a provider-neutral capability such as `ReferenceObservationPort`.

Preferred capability order:

1. provider can directly observe a supported remote/video URL → native observation;
2. provider accepts uploaded media → bounded acquisition/upload;
3. provider is image-only → controlled frame-observation fallback;
4. no truthful supported capability → fail closed.

Planning consumes structured reference observations/style evidence; it must not learn Bilibili/Douyin/Xiaohongshu mechanics.

Only after this capability exists should ordinary product work consider Bilibili, Douyin, Xiaohongshu or other site adapters. Do not build a generic crawler/downloader, login/cookie/DRM bypass, or pretend a URL text box is a finished feature.

## Public-material / similar-plan research

When backed by a real replaceable research/material adapter, Planning may recommend public material or learn from similar examples. Research remains analysis-only until the user explicitly imports/selects eligible material and satisfies source/rights contracts. No silent stock/generated replacement visuals.

## Production synthetic voice / advanced audio

Production TTS, advanced speech/ambience separation, advanced stem mixing and richer speaker-aware subtitle systems remain beyond 1.0. Preserve existing seams; do not expose unfinished controls.

## Rich editing / NLE UX

Timeline/NLE editing, advanced effects/transitions and rich subtitle animation remain future work. They must not displace the ordinary one-click path.

---

# Accepted baseline — do not reopen casually

Already implemented/accepted unless a regression is observed:

- responsive long-running Tkinter execution;
- output scrollbar and UTF-8 visible-output export;
- Chinese/English stable presentation;
- evidence-based ETA surface;
- local form/API profiles with Windows protected credentials and no plaintext-key persistence;
- true placeholder guidance;
- ordinary Editing multi-file selection with redundant folder UI removed;
- localized quota/provider failure presentation;
- modernized Stage-A desktop shell/workflow switcher;
- startup splash tied to real startup milestones;
- explicit output profiles;
- remote reference URL hidden from ordinary 1.0 Planning after the 2026-08-22 decision.

Historical superseded UX wave details belong in `docs/archive/**` and are not current authority.

## Current execution order

1. Project Workspace + UX consolidation;
2. compatible Windows onedir packaging foundation;
3. clean-machine-ish distributable proof;
4. retained Planning / Editing / clear single-speaker subtitle Human Gate;
5. exact-head quality, governance and CI closure;
6. only then Stage-A 100% if the completion contract is genuinely satisfied.

UX polish or an EXE by itself does not close Stage A.
