# Stage A UX Stabilization Wave

**Date:** 2026-08-18  
**Parent Work Order:** `R0.12-STAGE-A-PRODUCT-GATE-CLOSURE-001`  
**Execution owner:** Codex under ChatGPT foreman review  
**Purpose:** consolidate already-recorded ordinary-user UX/robustness issues while the real Editing Product Probe is temporarily blocked by Gemini free-tier quota.

## Non-goals

This wave is **not** a new roadmap phase and does not change Stage-A structural progress.

Do not redesign:

- Planning/Editing product-core architecture;
- Director/Resolver ownership;
- canonical EDL authority;
- Renderer/Review policy;
- source provenance/rights boundaries;
- provider/model selection policy.

Do not add a platform scraper or an NLE/timeline editor.

## A. Responsive launcher execution

Current Planning/Editing flows run synchronously on the Tkinter UI thread. Refactor the launcher so long-running work executes off the Tk main thread while all widget mutations remain marshalled back through `root.after(...)` or an equivalent Tk-safe queue.

Acceptance:

- window remains movable/repaintable during API/FFmpeg/render work;
- duplicate Start clicks are disabled while a run is active;
- controls return to a valid state after completion/failure;
- no Tk widget is mutated directly from a worker thread;
- launcher smoke test remains deterministic.

This is prerequisite infrastructure for ETA/progress updates.

## B. Output surface: scrollbar, export and ordinary-user diagnostics

For both Planning and Editing output areas:

- place the `Text` widget in a frame with a visible vertical scrollbar;
- add `导出 / Export` near the output surface;
- export the **exact visible output text** as UTF-8 `.txt`;
- default save directory is the user's Desktop;
- user chooses/changes the destination with a normal save dialog;
- never export API secrets or hidden diagnostic state.

Primary output should contain ordinary-user status. Raw exception class names should not be the primary message.

## C. UI-aligned localization

When UI language is Simplified Chinese, all stable user-facing launcher content must be Simplified Chinese; English UI must use English.

Required scope:

- ProductFlow stage labels;
- stable progress messages;
- Planning and Editing result presentation labels;
- common validation/runtime/provider error summaries;
- dialog titles/buttons;
- export/profile messages.

Provider raw detail may remain as bounded technical detail after a localized explanation when useful, but do not present `VisualProviderTransientError`, `ScriptProposalRejectedError`, etc. as the primary user message.

Do not machine-translate persisted canonical artifacts solely for display. Instead make Planning providers produce user-facing language matching the selected UI language where the planning request supports that without changing factual authority.

## D. Honest ETA/progress experience

During active Planning/Editing work display an estimated completion clock time to the minute, e.g.:

`预计 20:58 完成（约 7 分钟）`

Requirements:

- recompute at least every 30 seconds;
- recompute immediately on ProductFlow stage transitions and material workload changes;
- before enough evidence exists display `正在估算… / Estimating…`;
- use real observed stage timing and known workload such as number of selected media files/shots where available;
- persist only non-sensitive timing statistics locally if cross-run history is used;
- never show fake percentage/progress based on arbitrary timers;
- ETA may move earlier/later as evidence changes;
- ETA is advisory only.

Provider-directed waiting should not look like a frozen app. If the code can safely surface a retry wait, show a localized waiting state. Do not broaden provider authority merely to display countdowns.

## E. Editing source selection: one ordinary-user mechanism

User decision: `素材文件 / Media Files` and `素材文件夹 / Media Folder` overlap.

Ordinary UI shall:

- keep **Media Files** only;
- chooser supports selecting multiple local media files in one action;
- remove the separate Media Folder field/button;
- show the selected-file count in a useful way if the path string becomes unwieldy;
- preserve exact user-selected paths;
- do not silently scan unrelated directory contents.

Lower-level folder-expansion helper/code may remain temporarily if removal would cause unrelated churn, but it must not remain exposed in the ordinary launcher.

## F. First-run placeholder guidance

On first launch or when no saved profile is loaded, use true placeholder guidance instead of fake submitted values.

Requirements:

- placeholder disappears on focus/input;
- placeholder text is never returned as actual field value;
- placeholder returns when an optional/required field becomes empty and loses focus;
- visually distinguish placeholder text from real text;
- explicitly mark required/optional in the placeholder.

Suggested Simplified Chinese examples:

Planning/common:

- Project: `此行必填，示例：选择一个项目目录`
- Title: `此行必填，示例：通勤小水瓶`
- Objective: `此行必填，示例：告诉上班族它方便携带`
- Audience: `此行必填，示例：上班族`
- Platform: `此行必填，示例：抖音`
- Core message: `此行必填，示例：小巧、方便`
- Authoritative facts: `此行可空置，示例：容量 350mL（仅填写已确认事实）`
- Reference URL/share text: `此行可空置，示例：粘贴公开视频直链或含 HTTPS 链接的分享文本`
- Local reference: `此行可空置，可选择本地参考视频`
- Camera: `此行可空置，示例：手机`
- Notes: `此行可空置，示例：室内自然光、无需稳定器`

Editing:

- Media files: `此行必填，请选择一个或多个本地视频`
- Output MP4: `此行必填，请选择最终 MP4 输出位置`

Provide equivalent concise English placeholders.

## G. Local profile files and safe credential persistence

Default profile root:

`%USERPROFILE%\Documents\Video Editing Agent\Profiles`

Main launcher and API Settings dialog each expose a `文件 / File` menu with:

- 保存 / Save
- 另存为 / Save As
- 读取 / Load
- 删除 / Delete

Suggested default names:

- Planning/form profile: `编导-YYYY-M-D.txt`
- API profile: `API-YYYY-M-D.txt`

Users may rename files.

### Form profile

May store ordinary non-secret fields as UTF-8 human-readable `.txt` content with a versioned deterministic schema.

Do not persist placeholders as values.

### API profile

May store non-secret provider/model/profile metadata in the `.txt` file.

**API key plaintext is forbidden.**

On Windows, protect secrets with a Windows-native user-scoped mechanism such as DPAPI/Credential Manager. The profile file stores only an opaque credential identifier/reference. Loading an API profile resolves the protected secret into the current process/session.

Requirements:

- secrets never enter repo/project artifacts/logs/exported output;
- deleting an API profile removes or invalidates its associated protected credential where safe;
- non-Windows fallback must remain session-only and explicitly say protected persistence is unavailable rather than storing plaintext.

Keep dependencies minimal; do not add a large credential framework solely for this wave if stdlib/ctypes Windows DPAPI can satisfy the contract safely.

## H. Planning no-facts safe repair

Existing factual review remains strict.

If authoritative facts, reference URL and local reference are all absent, Planning must still be able to create from title/objective/audience/platform/core message.

When the first ScriptPlan proposal invents unsupported concrete claims:

- reviewer rejects it as today;
- feed the structured/local rejection reasons back to the planner;
- allow **one** bounded full-proposal repair attempt;
- never silently convert creative intent into authoritative fact;
- second invalid proposal fails closed with a localized user explanation.

Add regression coverage for:

1. no-facts first proposal rejected then safe repair accepted;
2. two rejected proposals stop after two planner calls;
3. factual reviewer is not weakened.

## I. Reference share-text parsing — bounded only

For the Planning Reference URL field:

- accept a pasted string containing surrounding prose plus an HTTPS URL;
- extract the first HTTPS URL deterministically;
- pass that URL through the existing bounded direct-HTTPS reference acquisition path;
- if redirects resolve to supported direct media, analyze it as reference-only;
- if the final resource is HTML/platform page, return a localized explanation telling the user to download/select the reference locally;
- do **not** implement Douyin/platform-specific scraping or reverse-engineered downloading.

Add parser tests for plain direct URL, Douyin-style share text containing one URL, no URL, and multiple URLs (first URL wins).

## J. `公共素材` / `类似方案` controls

Do not ship decorative controls that do nothing.

For this wave:

- it is acceptable to leave these two P2 controls out of the executable UI until an explicit public-material/research adapter exists;
- preserve their requirements in `PRODUCT_UX_BACKLOG.md`;
- do not encode fake behavior into prompt text as a substitute for an actual research capability.

## K. Startup splash

Add a small centered non-resizable splash displayed immediately when launcher activation begins.

Use the existing product/pixel icon when available.

The splash contains one horizontal segmented/experience-bar-like progress indicator, visually inspired by Minecraft's bar rhythm without copying game assets.

Progress must correspond to real startup milestones such as:

1. initialize UI language/theme;
2. locate profile storage;
3. load profile index / safe credential references;
4. resolve lightweight runtime readiness information;
5. construct main window;
6. ready.

Do not fake progress with a timer. Main UI must not become interactive before ready.

## L. Quota/provider error UX

For a persistent provider 429 after bounded retries, present a localized primary message such as:

`视觉理解服务当前达到请求/配额限制，本次任务已停止。请稍后重试或检查 API 用量。`

If safe structured metadata is available, include provider/model/retry-delay/quota identifier in a secondary diagnostic section. Never expose keys.

Do not silently switch provider/model.

## Tests and quality gate

Add focused tests for newly extracted non-UI helpers wherever possible instead of relying only on Tk screenshots.

Minimum expected verification:

- formatter;
- Ruff/lint;
- mypy;
- full pytest suite;
- architecture/import contracts;
- build;
- launcher smoke mode;
- Windows-local manual smoke for placeholder/profile/export/multi-file selection/splash/responsiveness.

## Completion report required from Codex

Report:

1. exact commit SHA;
2. changed files and why;
3. tests/commands with results;
4. any intentionally deferred item from this wave and evidence why;
5. Windows manual-smoke observations;
6. confirmation that no plaintext API key appears in profile files/logs/tests;
7. confirmation that product-core authority/invariants were not changed.

Do not declare Stage A PASS or 100%. ChatGPT will reobserve GitHub and the user will later rerun the real Editing Product/Human Gate.
