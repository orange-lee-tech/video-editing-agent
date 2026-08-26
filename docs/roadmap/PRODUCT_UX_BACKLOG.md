# Product UX Backlog

**Updated:** 2026-08-26  
**Purpose:** preserve ordinary-user UX work without overriding the live Work Order.  
**Current authority:** `docs/operations/CURRENT_WORK_ORDER.md`.

Priority:

- **P0** — required for the current Stage-A / 1.0 closure;
- **P1** — high-value usability after the current closure wave is stable;
- **P2 / 2.0** — future capability expansion that must not be faked in 1.0.

## Current truth

- structural progress is **95%**; Stage-A completion remains OPEN;
- Planning factual recovery now works in a focused local repair, but Planning quality still requires hardening;
- Chinese-speaking and English-speaking real local footage both completed the visual-first automatic Editing path on the focused local repair candidate;
- source-speech continuity reconstruction, translated/bilingual subtitles and cross-language narration/TTS are deferred to 2.0 by Product Owner decision on 2026-08-26;
- ordinary remote reference URL remains hidden in 1.0; local reference video remains supported;
- Windows runtime/onedir engineering proof exists; normal 1.0 delivery still requires guided `Setup.exe`.

Do not use this backlog to override the live control trio.

---

# P0 — final 1.0 source/UI freeze

## Project Workspace ownership

Keep one shared top-level `项目工作区 / Project Workspace` context for Planning and Editing. Project-specific writable state belongs under that workspace; global reusable profiles stay outside the project and API secrets remain protected rather than serialized as plaintext.

## Configuration actions — direct ownership, no scope-checkbox ceremony

The current "select Form/API scope, then choose Import/Export/Save/Delete" interaction is too indirect.

For 1.0, configuration actions should be owned explicitly by configuration type:

- **Form / Director configuration** — direct Import / Export / Save / Delete actions;
- **API / Provider configuration** — direct Import / Export / Save / Delete actions;
- do not require the user to tick one or two scope checkboxes before an obvious action;
- never export plaintext API keys; retain Windows protected-secret semantics;
- labels should remain understandable to ordinary users in Chinese and English.

The important design rule is direct action ownership, not the exact button arrangement.

## Deferred-capability isolation

The ordinary 1.0 UI must hide rather than cosmetically expose unfinished/deferred capabilities, including:

- source-speech separation/reconstruction;
- translated or bilingual subtitle output;
- cross-language narration/TTS;
- advanced speaker-aware voice/subtitle controls;
- remote reference URL.

If an internal seam remains for future compatibility, that does not authorize a user-facing 1.0 control.

## Planning result quality

Planning output must be understandable and useful as an actual shooting construction manual. Avoid generic hook copy, duplicated authoritative facts and repeated static-product instructions. Use section-role-aware truthful creative framing, equipment-aware instructions, alternate/backup coverage and practical ordinary-user wording.

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

Provider-directed retry/wait states should look intentional rather than frozen. Primary messages are localized, technical detail is bounded, secrets stay redacted, and retry remains bounded rather than becoming an unending loop.

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

## Dual-track speech / multilingual voice production

The long-term solution for speech-heavy footage is **not** to make sentence boundaries the primary video-cut authority. It is to keep visual editing and speech/narration production as separate coordinated tracks.

2.0 scope includes:

- source-speech / ambience separation where technically/licensing-appropriate;
- sentence-preserving dialogue reconstruction after visual-first cuts;
- original-language transcript with reliable timing;
- target-language translation;
- original / translated / bilingual subtitle modes;
- cross-language narration/TTS;
- original-audio mute/duck/retain controls coordinated with narration;
- speaker-aware subtitle/narration systems;
- explicit source-language, subtitle-language and narration-language choices rather than one overloaded "video language" setting.

Provider interfaces should remain replaceable; visual evidence must not be overwritten by translated text and translated/narrated content must not become source-footage authority.

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
- Project Workspace separation;
- remote reference URL hidden from ordinary 1.0 Planning.

Historical superseded UX wave details belong in `docs/archive/**` and are not current authority.

## Current execution order

1. preserve/accept focused local Human Gate repair;
2. Planning quality hardening + direct configuration UI + deferred-capability hiding + bounded provider wait;
3. exact-head quality/governance/CI closure;
4. release-candidate staging build with 1.0-only default runtime payload;
5. guided `Setup.exe` build and install/repair/uninstall Human Gate;
6. Stage-A 100% only if the completion contract is genuinely satisfied.

UX polish or an EXE by itself does not close Stage A.
