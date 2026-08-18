# Product UX Backlog

**Updated:** 2026-08-18  
**Purpose:** Preserve ordinary-user product feedback without reopening already-passed gates or diluting the active Stage-A Editing Product Gate.

## Priority interpretation

- **P0 — robustness / correctness:** should be repaired before release if it materially breaks an otherwise valid ordinary-user path.
- **P1 — usability / persistence:** high-value ordinary-user improvement, but not a reason to delay the active Editing Product Probe unless it blocks that probe.
- **P2 — polish / expansion:** useful product refinement after the two Stage-A core gates are closed.

## P0 — Planning no-facts safe creative fallback

User requirement:

If `authoritative_facts`, reference URL and local reference video are all empty, Planning must still create a script faithfully from the other supplied brief fields.

Observed real failure:

A new ordinary-user input with empty authoritative facts/reference fields reached ScriptPlan generation but was rejected because the proposal introduced unsupported concrete claims such as natural-origin/purity implications. The semantic reviewer was correct to reject unsupported facts; the product robustness defect is that the entire Planning flow terminated rather than repairing/regenerating a safe proposal.

Desired behavior:

- empty facts/reference remains a valid Planning input;
- brief title/objective/audience/platform/core message remain usable as creative intent;
- creative intent does not automatically become factual authority;
- when a proposal adds unsupported concrete claims, feed the rejection reasons back into a bounded repair/regeneration attempt;
- if repair still fails, present a localized ordinary-user explanation rather than raw exception/class names;
- never silently weaken the factual-claim reviewer.

## P1 — Output viewing and export

- add a visible vertical scrollbar to the long output/progress area;
- add an `导出 / Export` action;
- save the current output as UTF-8 `.txt` to a user-selected path;
- default export directory: Desktop;
- export must contain the exact user-visible output, not secrets or hidden internal diagnostics.

## P1 — Runtime ETA in the output surface

During Planning and Editing work, the ordinary-user output area should report an estimated completion time.

Required behavior:

- display the predicted completion clock time to the minute, for example `预计 20:58 完成（约 7 分钟）`;
- recalculate the estimate at least every 30 seconds while work remains active;
- also recalculate immediately on meaningful stage transitions or workload changes;
- before enough evidence exists, show an honest estimating state rather than an invented ETA;
- derive the prediction from real observed stage timing, remaining workload and relevant media/runtime characteristics where available;
- allow the estimate to move earlier or later as evidence improves;
- never present a fixed timer, fake percentage or cosmetic countdown as measured progress;
- ETA display is advisory only and must not become execution authority or block the workflow.

## P1 — UI-aligned localization

When the UI language is Simplified Chinese, ordinary-user output should also be Simplified Chinese; when English is selected, ordinary-user output should be English.

Scope:

- generated ScriptPlan/ShootingPlan presentation language follows the selected UI language;
- progress labels and stable product diagnostics are localized;
- user-facing errors are mapped from stable error codes/reasons to localized explanations;
- do not machine-translate persisted canonical artifacts merely for display if doing so would change their semantic content;
- raw exception class names/provider implementation details belong in bounded diagnostics, not the primary ordinary-user message.

## P1 — Local profiles and safe credential persistence

User-facing concept:

- default profile storage location under the user's Documents directory;
- Planning/form profile naming suggestion: `编导-YYYY-M-D`;
- API profile naming suggestion: `API-YYYY-M-D`;
- users may rename profiles;
- both the main Planning surface and Settings surface provide a `文件 / File` menu with `保存 / Save`, `另存为 / Save As`, `读取 / Load`, `删除 / Delete`.

Security boundary:

- ordinary form/profile data may be persisted in a human-readable local profile file;
- API provider/model/config metadata may be represented in the profile file;
- API secret values must **not** be stored as plaintext in Documents `.txt` files;
- secrets should use Windows Credential Manager / DPAPI or an equivalent OS-protected credential store, with the profile storing only a credential reference/identifier;
- no secret may be committed to the repository, project artifacts or logs.

The exact on-disk schema may evolve even if the first user-visible profile extension is `.txt`.

## P1 — Placeholder guidance instead of fake values

For first launch or when no profile is loaded:

- required and optional fields show placeholder guidance;
- examples must visually look like placeholders, not real values;
- placeholders disappear on focus/input and are never submitted as field values;
- examples should explicitly say `此行必填` or `此行可空置`;
- keep examples short and domain-relevant.

Example style:

- `此行必填，示例：介绍一款适合通勤的小瓶水`
- `此行可空置，示例：仅使用手机、室内自然光`

## P1 — Reference URL/share-text compatibility, bounded not scraper-first

Desired ordinary-user input may contain a whole platform share message, for example prose plus a `https://v.douyin.com/.../` short URL.

Bounded design:

1. extract the first supported HTTPS URL from pasted share text;
2. follow safe bounded redirects;
3. if the resolved resource is directly retrievable supported media (`video/*`) or another provider-supported public file URL, keep it reference-analysis-only and analyze it;
4. if the resolved target is only an HTML platform page, do not silently treat it as video media;
5. do not make Stage A depend on brittle platform-specific scraping/downloader reverse engineering;
6. provide a clear localized fallback: choose/download the reference video locally and use `本地参考视频`.

Future platform-specific official integrations may be added only when their permission/auth/rights model is explicit.

## P2 — Opt-in `公共素材` guidance

Add a Planning checkbox `公共素材`, default unchecked.

When checked, it means the user permits the Planning system to recommend what public/stock material could substitute for specific planned shots.

Frozen source/rights boundary remains:

- recommendations/research may occur during Planning;
- public material does not automatically enter the commercial final video;
- before Resolver/final-output eligibility, the user must actually select/import the asset as local media and satisfy the product's rights/source attestation contract;
- no silent stock/generated replacement visual substitution.

## P2 — Opt-in `类似方案` research

Add a Planning checkbox `类似方案`, default unchecked.

When checked, the user permits reference/research enrichment from publicly accessible similar examples, including public video resources, webpages and text information.

Constraints:

- research/reference evidence remains analysis-only;
- it cannot become Resolver-eligible final visual media by itself;
- sources/provenance should be inspectable where practical;
- web/search capability must be provided through an explicit replaceable adapter rather than hidden provider-specific behavior;
- Planning should use the user's actual shooting device, shooting notes and other brief constraints when translating similar examples into a new plan.

## P2 — Startup splash and progress

On launcher activation, immediately show a small centered non-resizable splash window using the existing pixel-style product icon.

Desired behavior:

- similar in role/scale to a Photoshop-style startup splash, not a full secondary application window;
- one horizontal segmented/experience-bar-like progress indicator inspired by Minecraft's visual rhythm without copying game assets;
- show real startup stages such as configuration load, profile/credential reference load, runtime discovery and UI readiness;
- do not fake progress with an arbitrary timer;
- prevent ordinary interaction with the main window until startup is ready, while keeping the process responsive.

## Current execution rule

These items are preserved as product backlog. They do not reopen the Stage-A Planning Product Gate that passed on 2026-08-18.

The active closure priority is now the real Stage-A Editing Product Gate. Only a backlog item that blocks the Editing Product Probe should preempt that gate.
