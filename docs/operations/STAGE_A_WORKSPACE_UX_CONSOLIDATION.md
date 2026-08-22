# Stage A Workspace + UX Consolidation

**Updated:** 2026-08-22  
**Parent Work Order:** `R0.12-STAGE-A-FINAL-CLOSURE-002`  
**Status:** ACTIVE / RELEASED — BOUNDED LOCAL WAVE  
**Purpose:** make the existing Stage-A desktop product behave like one coherent user application before Windows packaging.

## Product intent

This wave is not visual polish for its own sake. It resolves product-structure leakage before packaging freezes paths, writable-data locations, resource ownership, and desktop interaction patterns.

The main principle is:

> one user-selected **Project Workspace** is the root for one video's durable project state and project-specific working data; the install directory remains read-only and disposable.

Remote reference URL observation is explicitly outside this wave and deferred to 2.0. The ordinary Planning UI must keep that unfinished field hidden.

## 1. Project Workspace becomes the shared desktop context

Keep the project-path control as the first ordinary field, but rename/present it as:

- Simplified Chinese: `项目工作区`
- English: `Project Workspace`

It is not a repeated Planning/Editing parameter. It is the shared context for the whole application session.

Requirements:

- one top-level workspace selector shared by Planning and Editing;
- once selected/opened, both workflows use the same workspace unless the user explicitly switches projects;
- current project/open state is clearly visible;
- existing `ProjectWorkspace` persistence remains authoritative; do not invent a second project database;
- existing projects remain readable;
- project switch/open actions must not silently discard unsaved form drafts;
- the workspace path must never be inside the packaged install directory by default.

### Project-specific writable data

Use the workspace deliberately for project-specific working state rather than scattering temporary state around the machine.

Logical ownership should cover:

- `project.sqlite3` / persisted Domain/Application state;
- content-addressed artifacts;
- reference/local analysis cache where applicable;
- provider-derived project media/cache;
- project-local autosave/form draft state;
- project-local undo/redo history for editable form state;
- task/session scratch files that are safe to resume or clear;
- run diagnostics/logs that belong to this project;
- default rendered outputs and previews.

Implementation may refine the physical layout, but it should converge on explicit roles comparable to:

```text
<Project Workspace>/
├─ project.sqlite3
├─ artifacts/
├─ cache/
├─ work/
├─ logs/
├─ provider_audio/
└─ outputs/
   ├─ preview/
   └─ final/
```

Do not duplicate canonical Domain data into ad-hoc JSON snapshots merely to satisfy this layout.

Global user configuration such as reusable API profiles may remain under the existing user-profile root. Project-specific state belongs in the Project Workspace; machine/user-level settings do not have to be copied into every project.

## 2. Output defaults follow the Project Workspace

The final output path should have a sensible project-local default, e.g. under `outputs/final/`, rather than forcing the user to fill both a project path and an unrelated output path every run.

Requirements:

- ordinary Editing can derive a default output destination from the current workspace;
- user may still choose `Save As` / another destination;
- no overwrite without explicit confirmation or deterministic collision-safe naming;
- output path remains visible/inspectable before execution.

## 3. Consolidate configuration actions on the main window

Current form-profile and API-profile actions are split across surfaces. Replace that interaction with one obvious main-window configuration entry.

Recommended top-level action:

`配置 / Configuration ▾`

Sub-actions:

- `导入 / Import`
- `导出 / Export`
- `保存 / Save`
- `删除 / Delete`

Import/export must allow independent selection of:

- Planning/form configuration;
- API/provider configuration;
- both together.

Security invariants:

- never export API keys as plaintext;
- retain Windows protected-secret storage semantics;
- exported API configuration may contain non-secret provider/model/profile metadata and protected references only when meaningful;
- do not pretend protected Windows credentials are automatically portable across machines;
- secrets must not enter project artifacts, logs, visible-output export, repository files, or package resources.

## 4. Add form-level Clear / Undo / Redo

Provide ordinary main-window commands with familiar names:

- `清空 / Clear`
- `撤销 / Undo`
- `重做 / Redo`

Requirements:

- operate on the active Planning or Editing form state, not merely the focused text widget;
- `Clear` affects the active editable form only; it must not delete project history, API credentials, rendered outputs, or persisted accepted Domain artifacts;
- `Undo` / `Redo` restore coherent form-state changes, including file selections where practical;
- support standard keyboard shortcuts (`Ctrl+Z`, `Ctrl+Y` and/or `Ctrl+Shift+Z`);
- disable or safely gate state mutation while a task is actively executing;
- store resumable draft/history state inside the Project Workspace when persistence is implemented;
- bound history size and provide a safe clear policy so undo history does not become an unbounded cache.

Do not reinterpret immutable/revisioned Domain history as UI undo history.

## 5. Make sub-sections vertically collapsible

Planning and Editing already behave as two major workflow surfaces. Their internal groups should not consume unnecessary horizontal width.

Convert these groups to vertical collapsible/accordion sections:

Planning:

- `内容目标 / Content Goal`
- `参考与拍摄条件 / References & Filming`

Editing:

- `成片目标 / Edit Goal`
- `素材与输出 / Media & Output`

Requirements:

- one-column/vertical reading order suitable for ordinary laptop windows;
- collapsed headers remain understandable and may show concise state summaries;
- keyboard/focus navigation remains valid;
- existing field semantics/validation remain unchanged;
- no critical controls disappear when resizing the ordinary window.

## 6. Brand icon: retire the generated pixel camera

The dependency-free Canvas pixel-camera mark is a temporary implementation asset and is not the desired product identity.

Direction:

- prefer the previously used/approved feather mark if a real repository/history asset can be recovered;
- do not invent a new approximate feather from memory;
- if the original cannot be recovered, keep icon replacement as an explicit Human Gate rather than silently shipping another improvised mark;
- one canonical brand asset should later feed splash/window/taskbar/executable/installer surfaces where platform format permits.

Packaging must not freeze the current pixel-camera mark as the permanent application identity.

## 7. Reference input boundary

For Stage A / 1.0:

- local reference video remains visible and supported;
- remote reference URL input remains hidden;
- do not add Douyin/Bilibili/Xiaohongshu URL controls;
- do not revive remote-reference support through tooltips, hidden defaults, or automatic crawling.

Future 2.0 home:

`ReferenceObservationPort` / provider-neutral remote-video observation capability.

## Non-goals

Do not:

- redesign Planning/Editing Domain authority;
- change Resolver/EDL/Renderer/Review ownership;
- add a timeline/NLE editor;
- implement remote reference observation;
- add provider-specific crawler/downloader product UI;
- start production TTS/separation work;
- start installer/packaging implementation inside this UX wave unless a tiny path/resource seam is required to avoid future incompatibility.

## Verification

Minimum engineering gate:

- focused state/history/workspace/profile tests;
- localization-catalog completeness;
- launcher smoke;
- Windows manual smoke for workspace selection, workflow switching, collapse/expand, configuration import/export choices, Clear/Undo/Redo, default output destination, and project switching;
- confirm no plaintext secret leakage;
- Ruff format/check;
- mypy `src`;
- full pytest;
- import-linter;
- build;
- repo doctor;
- `git diff --check`.

## Human acceptance

An ordinary user should be able to answer these without knowing repository architecture:

1. Where is this video's project/work saved?
2. How do I save/load my form/API configuration?
3. How do I undo a mistaken edit or clear the current form?
4. How do I collapse information I am not editing right now?
5. Where will the final video be written by default?

If those answers are obvious from the main window, the wave is ready to hand off to Packaging.
