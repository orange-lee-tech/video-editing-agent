# Product UX Backlog

**Updated:** 2026-08-19  
**Purpose:** preserve ordinary-user product feedback without reopening already-passed gates or confusing polish with Stage-A completion.

Priority:

- **P0** — robustness/correctness on a valid ordinary-user path;
- **P1** — high-value usability/persistence;
- **P2** — expansion/polish that should not fake unsupported capability.

The implementation specification for the preserved local stabilization candidate is:

`docs/operations/STAGE_A_UX_STABILIZATION_WAVE.md`

The broader desktop-shell design baseline is:

`docs/product/DESKTOP_UI_DESIGN_SYSTEM_V0.1.md`

The current gate-critical Editing integration correction is owned by:

`docs/operations/CURRENT_WORK_ORDER.md`

Do not mix commercial UI polish into that integration repair.

## P0 — Planning no-facts safe creative repair

If authoritative facts, reference URL and local reference video are all empty, Planning must still create from the other brief fields.

Observed failure: a real proposal invented unsupported claims such as natural-origin/purity implications and the factual reviewer correctly rejected them, but the entire flow terminated.

Required behavior:

- empty facts/reference is valid;
- title/objective/audience/platform/core message remain creative intent, not factual authority;
- first unsupported proposal is reviewed/rejected normally;
- feed the rejection reasons to one bounded full-proposal repair attempt;
- never weaken the factual reviewer or silently coerce a claim into a fact;
- second invalid proposal fails closed with a localized explanation.

**Current status:** implemented/tested in the preserved local UX candidate; not yet accepted into remote production baseline.

## P1 — Responsive long-running launcher

Planning/Editing work must not freeze the Tkinter UI.

- long-running work executes off the Tk main thread;
- Tk mutations return through `root.after(...)` or an equivalent safe queue;
- duplicate Start actions are disabled while active;
- the window remains repaintable/movable during API, FFmpeg and render work;
- controls recover after completion/failure.

**Current status:** local candidate/manual smoke PASS; pending final post-Splash gate + commit/CI.

## P1 — Output viewing and export

- visible vertical scrollbar for Planning and Editing output;
- `导出 / Export` action;
- export exact visible output as UTF-8 `.txt`;
- default directory Desktop, user may choose another location;
- never export secrets or hidden internal diagnostics.

**Current status:** local candidate/manual smoke PASS; pending commit/CI.

## P1 — Honest runtime ETA/progress

During Planning/Editing:

- show predicted completion clock time to the minute, e.g. `预计 20:58 完成（约 7 分钟）`;
- recalculate at least every 30 seconds;
- recalculate on meaningful stage/workload changes;
- show `正在估算… / Estimating…` until enough evidence exists;
- derive ETA from observed stage timing and known media/workload characteristics;
- allow ETA to move earlier/later;
- never use a fake percentage or arbitrary cosmetic countdown;
- provider-directed waits should visibly look like intentional waiting rather than a frozen app when safely observable.

**Current status:** local candidate; real provider-wait behavior still needs later product observation.

## P1 — UI-aligned localization

Selected UI language controls stable ordinary-user presentation:

- stage labels and progress messages;
- ScriptPlan/ShootingPlan presentation labels;
- Editing result presentation;
- stable validation/runtime/provider error summaries;
- dialogs/profile/export messages.

Simplified Chinese UI should not primarily display raw English class names such as `VisualProviderTransientError` or `ScriptProposalRejectedError`.

Provider raw detail may appear as bounded secondary diagnostics when useful. Do not machine-translate persisted canonical artifacts in ways that change meaning.

**Current status:** local candidate/manual smoke PASS; pending commit/CI.

## P1 — Local profiles and protected API credentials

Default profile root under Documents, suggested:

`%USERPROFILE%\Documents\Video Editing Agent\Profiles`

Main Planning/form surface and Settings surface provide `文件 / File` with:

- 保存 / Save
- 另存为 / Save As
- 读取 / Load
- 删除 / Delete

Suggested defaults:

- `编导-YYYY-M-D.txt`
- `API-YYYY-M-D.txt`

Users may rename profiles.

Ordinary form/profile metadata may be UTF-8 human-readable text. API secrets must **not** be plaintext in Documents, project files, logs or repo content. On Windows use a user-scoped protected mechanism such as DPAPI/Credential Manager and store only an opaque credential reference in the profile. Non-Windows fallback remains session-only rather than plaintext persistence.

**Current status:** local candidate/manual dummy-secret round-trip PASS; plaintext scan PASS; pending commit/CI.

## P1 — Placeholder guidance instead of fake values

On first launch/no loaded profile:

- true placeholder guidance, visually distinct from real content;
- placeholder disappears on focus/input and may return when empty on blur;
- placeholder is never submitted;
- concise domain examples.

The local stabilization candidate currently includes explicit `此行必填 / 此行可空置` inside placeholders because that was the first-run safety requirement.

**Follow-up polish:** move required/optional status to labels/help text where practical and shorten the placeholder itself. The current screenshots show that repeating the full phrase on every row adds visual noise. This follow-up must preserve the same validation semantics.

## P1 — Editing source selection simplification

User decision on 2026-08-18: `素材文件` and `素材文件夹` overlap.

Ordinary Editing UI should expose **one** mechanism:

- keep `素材文件 / Media Files`;
- chooser supports multi-select;
- remove `素材文件夹 / Media Folder` from the ordinary UI;
- preserve exact user-selected paths and provenance;
- do not silently scan unrelated files from a directory;
- present selected-file count/readability when many files are selected.

Lower-level folder-expansion compatibility code may remain temporarily if deleting it causes unrelated churn, but it should not stay user-facing.

**Current status:** local candidate/manual smoke PASS.

## P1 — Reference share-text compatibility, bounded not scraper-first

The Reference URL field may contain surrounding share prose plus an HTTPS URL, e.g. a Douyin-style copied share message.

Desired behavior:

1. deterministically extract the first HTTPS URL;
2. use existing bounded redirect/direct-HTTPS acquisition;
3. direct supported public media remains reference-analysis-only and may be analyzed;
4. if the final target is HTML/platform page, explain in the selected UI language that the user should download/select the reference locally;
5. do not make Stage A depend on platform reverse engineering/scrapers.

**Current status:** parser/regression implemented in local candidate; no platform scraper added.

## P1 — Provider quota/wait UX

Real Gemini Editing probes exposed free-tier HTTP 429 conditions.

Desired ordinary-user behavior:

- primary message localized, e.g. visual service currently reached a request/quota limit and the task stopped;
- when safely available, secondary diagnostics may show provider/model/retry delay/quota identifier;
- provider-directed wait must not look like an app freeze;
- never expose keys;
- never silently switch provider/model to bypass quota.

## P1 — Commercial information hierarchy

Current screenshots are functional but too flat for a commercial desktop product.

Required follow-up:

- clear Header / workflow / input / status / result hierarchy;
- use semantic sections instead of ten visually equal full-width rows;
- one obvious Primary CTA per workflow;
- Secondary actions visually quieter;
- result surface separated from run/technical log;
- empty result surface shows a helpful empty-state rather than a large unexplained blank area;
- stable design tokens for typography, spacing, borders and status semantics.

Do this with stock `tkinter.ttk` first; framework migration is not required to solve the present problem.

## P1 — Media selection summary component

After selecting multiple source files, do not force the user to read a long semicolon/path string.

Show a compact local-only summary such as:

```text
已选择 7 个视频
总大小 1.8 GB
[查看文件] [重新选择]
```

Requirements:

- exact selected paths remain authoritative inside controller state;
- no unrelated directory scan;
- no cloud/API call merely to show the summary;
- file list remains inspectable.

## P1 — Output overwrite confirmation

Renderer correctly protects canonical source media from output collision, but the FFmpeg backend currently executes with overwrite enabled for an existing non-source output path.

Ordinary product behavior before rendering an already-existing target:

- `另存为` / suggest new name;
- explicit `覆盖`;
- `取消`.

Do not move this policy into Renderer editorial authority; it belongs in the product/controller boundary before execution.

## P1 — Capability-oriented API settings

The current remote product shell still treats `DeepSeek` as the only reasoning/Director provider and Vision as Gemini/OpenAI.

The future Settings surface must present product roles first:

- `思考与编导 / Reasoning & Direction`;
- `视觉理解 / Vision Understanding`.

Provider/profile/protocol/model/endpoint/credential are configuration of those roles.

Implementation plan:

`docs/architecture/PROVIDER_NEUTRAL_PRODUCT_BINDING_PLAN.md`

No silent provider fallback.

## P1 — Diagnostics / Doctor surface

Expose Environment Doctor through an ordinary-user action after the underlying capability-aware provider refactor is ready.

Default Doctor should be a **static/local readiness check** and should not silently spend API quota.

Useful summary:

- local media tools ready/not ready;
- shot-detection runtime ready/not ready;
- reasoning capability configured/not configured;
- vision capability configured/not configured;
- output/project path readiness.

Technical details may be expandable.

## P1 — Project/path safety preflight

Before creating/writing a project or starting a long run, ordinary UX should eventually detect/translate common desktop conditions:

- unwritable location;
- low disk space;
- unavailable drive/network path;
- suspicious output collision;
- same project already open elsewhere when proven by a concurrency probe.

Do not add warnings unsupported by real checks.

## P2 — Open result/output location and copy result

Low-risk efficiency actions once the corresponding result exists:

- Planning: `复制结果`, `导出 TXT`;
- Editing: `打开输出目录`, `复制成片路径`, `查看技术详情`.

Do not show output actions before a result exists.

## P2 — Recent projects

A bounded recent-project list can reduce repetitive folder selection.

Persist only:

- project path;
- non-sensitive display metadata;
- last-opened time.

Do not persist API secrets or duplicate canonical project entities into a global recent-list database.

## P2 — Safe Cancel / Resume

A Cancel button is useful only after the application/provider/FFmpeg lifecycle has an owner-safe cancellation contract.

Before exposing it, define and test:

- worker cancellation token;
- provider request timeout/cancel semantics;
- FFmpeg child-process termination;
- canonical artifact state after cancellation;
- retry/resume from accepted revisions.

No decorative Cancel button.

## P2 — High DPI / keyboard / window-size Human Smoke

The next shell-polish Human Gate should include at least:

- Windows 100% / 125% / 150% scaling;
- 1366×768-class screen;
- normal/maximized window;
- Chinese/English;
- Tab order and keyboard activation;
- important status not conveyed by color alone.

## P2 — Opt-in `公共素材` guidance

Default unchecked. When implemented with real backing capability, it means the user permits Planning to recommend public/stock material that could substitute for planned shots.

Rights boundary remains:

- recommendation/research may occur during Planning;
- public material does not automatically enter commercial final output;
- user must actually select/import an asset as local media and satisfy the product's source/rights contract before Resolver eligibility;
- no silent stock/generated replacement visuals.

Do **not** ship a decorative checkbox with no real adapter behind it.

## P2 — Opt-in `类似方案` research

Default unchecked once a real replaceable research/search adapter exists.

When implemented, user permits reference/research enrichment from publicly accessible similar examples, including public video resources, webpages and text.

- research evidence remains analysis-only;
- cannot become Resolver-eligible final visual media by itself;
- provenance should be inspectable where practical;
- actual shooting device/notes/brief constraints must shape the resulting plan;
- do not fake this capability by adding prompt text without a real research adapter.

## P2 — Startup splash and real startup progress

Immediately on launch show a small centered non-resizable splash with a restrained product/pixel mark.

- progress corresponds to real startup milestones such as language/theme init, profile storage discovery, safe credential references, lightweight runtime readiness, main-window construction and ready;
- no arbitrary timer/fake percentage;
- main UI remains non-interactive until ready while the process stays responsive;
- no need to deliberately delay a fast startup merely to make the splash visible longer.

**Current status:** after manual repaint/pixel-mark repair the user confirmed the startup icon is visible; final full local gate still pending.

## Current execution rule

Planning Product/Human Gate remains PASS.

Editing Product/Human Gate remains OPEN and structural progress remains 90%.

The 2026-08-19 integration audit found that the current ordinary Editing ProductFlow omits part of the already-required Stage-A editing-expression floor. Therefore the next gate-closing Editing Product Probe is blocked not only by provider/runtime availability but also by the integration repair now specified in `CURRENT_WORK_ORDER.md`.

Execution order:

1. finalize/push/accept the preserved local UX candidate;
2. repair the Stage-A ordinary Editing integration gap;
3. resume the real Editing Product/Human Gate;
4. only after that, proceed with broader Provider-neutral/commercial-shell/packaging work as separate bounded waves.

Completing UX polish alone does **not** close Editing Gate or raise Stage A to 100%.
