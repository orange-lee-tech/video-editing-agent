# Stage A Completion Gate

**Status:** ACTIVE GATE  
**Stage:** A — Structural Construction  
**Last updated:** 2026-08-26  
**Purpose:** Prevent false 100% completion claims and bind structural closure to real product usability.

## Rule

Stage-A structural progress may be reported as `100%` only when **both core product functions are genuinely usable by an ordinary Windows user through the real product path**.

Backend modules, green unit tests, synthetic probes, hand-authored internal artifacts, CLI-only engineering paths, or a polished GUI do not satisfy this gate by themselves.

## Core 1 — Planning product gate

Required user outcome:

`reference/high-performing/commercial intent`
`→ Brief`
`→ persisted inspectable ScriptPlan`
`→ executable ShootingPlan`

PASS requires that an ordinary Windows user can:

- create/open a project;
- provide the planning goal, reference/high-performing target and commercial constraints through a product-facing input path;
- run the real planning workflow without editing repository files;
- inspect the resulting ScriptPlan;
- inspect/use the resulting ShootingPlan;
- revise/lock where the current product contract requires it;
- receive understandable failure/reshoot guidance rather than raw stack traces or silent fabrication;
- obtain a ScriptPlan/ShootingPlan whose quality is practically useful for an ordinary user rather than merely structurally valid or fact-safe.

The Planning-only path must remain legitimate and may end at ScriptPlan/ShootingPlan.

Planning factual safety and Planning usefulness are both required: a plan that invents unsupported commercial claims fails, and a plan that becomes repetitive/empty/static merely to avoid claims also fails the ordinary-user quality bar.

## Core 2 — Editing product gate

Required 1.0 user outcome:

`user-selected local footage + editing intent/output destination`
`→ real media understanding/evidence`
`→ Director/EditPlan`
`→ Retrieval/Resolver`
`→ music/rhythm + spatial/basic audio + minimal graphics/transitions`
`→ canonical EDL`
`→ Renderer`
`→ Review/repair where required`
`→ final MP4`

PASS requires that an ordinary Windows user can:

- create/open a project;
- select local footage files/folder;
- provide editing intent;
- choose/confirm an output destination;
- start the actual production workflow without hand-authoring EditPlan, ResolutionDecision or EDL;
- observe meaningful progress and understandable failure state;
- obtain and locate a real final MP4;
- keep original user media untouched;
- use Editing-only without fabricated ScriptPlan/ShootingPlan;
- use Combined mode when Planning artifacts exist, with Planning as optional enrichment rather than activation license.

The Stage-A / 1.0 editing-expression floor is **visual-first**. It includes grounded deterministic cuts, minimal transitions, basic deterministic title/CTA/price-card graphics, spatial automation, music/rhythm handling and basic audio fade/duck/pass-through execution. It does not require a monolithic effects engine or a feature-rich NLE timeline UI.

## 1.0 speech boundary

Per Product Owner decision on 2026-08-26, advanced source-speech continuity belongs to a later dual-track audio/video design and is not a Stage-A / 1.0 completion blocker.

The following are deferred to 2.0:

- advanced source-speech / ambience separation;
- sentence-preserving dialogue reconstruction after visual cuts;
- multilingual transcript translation;
- translated or bilingual subtitle production;
- cross-language narration / TTS;
- speaker-aware subtitle/narration systems.

Existing provider-neutral seams and prior speech-runtime engineering evidence may be preserved, but unfinished controls must not be exposed in the ordinary 1.0 UI and deferred capabilities must not inflate the default 1.0 payload merely because they were previously packaged for engineering proof.

Original source audio may remain a deterministic pass-through behavior where already implemented. 1.0 must not claim speech-continuity reconstruction or speech-aware cut authority.

## Ordinary-user usability floor

The Stage-A user-facing surface may be visually plain. It must be practical, understandable, controllable and extensible.

At minimum the user must be able to:

- create/open project;
- select required inputs;
- select/identify outputs;
- start work;
- understand current progress/failure;
- locate produced plans/final media;
- perform the workflow without repository-file editing or manual Domain/EDL construction;
- avoid being presented with unfinished/deferred controls as if they were supported 1.0 capabilities.

## Compatibility and deployment floor

Stage-A must not assume a preconfigured developer workstation.

The product direction must support:

- bounded/private runtime dependencies where practical;
- diagnosable degraded behavior when optional acceleration is unavailable;
- CPU-capable baseline behavior for supported workflows;
- clear environment diagnostics instead of unexplained failure;
- replaceable adapters so Preview/GUI/provider/runtime choices do not become Domain authority.

Final 1.0 closure additionally requires the Product Owner-approved guided Windows `Setup.exe` delivery path. A raw PyInstaller onedir/ZIP is engineering staging, not the ordinary-user release experience.

## Evidence required for PASS

Before the control plane may set structural progress to `100`:

1. Core 1 Product Gate is explicitly `PASS` with durable Product Probe/Human Gate evidence including quality, not only schema validity.
2. Core 2 Product Gate is explicitly `PASS` with a real final MP4 from the actual visual-first automatic workflow.
3. Planning-only, Editing-only and Combined semantics are preserved.
4. The ordinary-user usability floor above is demonstrated on Windows.
5. The latest accepted `main` is green under the required repository quality/governance gates.
6. The guided `Setup.exe` install/update-or-repair/uninstall path is Human-tested and preserves Workspaces/Profiles/originals.
7. Closure evidence records exact commit, runtime/provider versions, installer/component identities, machine/environment class and known limitations/deferred 2.0 capabilities.

## Machine guard

`tools/maintenance/repo_doctor.py` must reject any control state that reports `structural_progress_percent: 100` unless:

- `stage_a_completion_gate: PASS`;
- `core_1_planning_product_gate: PASS`;
- `core_2_editing_product_gate: PASS`.

This file defines the product gate; the control state records its live result.
