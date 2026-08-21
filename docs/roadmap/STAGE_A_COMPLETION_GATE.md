# Stage A Completion Gate

**Status:** ACTIVE GATE  
**Stage:** A — Structural Construction  
**Last updated:** 2026-08-21  
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
- receive understandable failure/reshoot guidance rather than raw stack traces or silent fabrication.

The Planning-only path must remain legitimate and may end at ScriptPlan/ShootingPlan.

## Core 2 — Editing product gate

Required user outcome:

`user-selected local footage + editing intent/output destination`
`→ real media understanding/evidence`
`→ Director/EditPlan`
`→ Retrieval/Resolver`
`→ music/rhythm + spatial/audio + subtitle/graphics/minimal transitions`
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

The Stage-A editing-expression floor includes deterministic cuts, minimal transitions, structured subtitle emphasis, basic deterministic title/CTA/price-card graphics, spatial automation, and basic audio fade/duck execution. It does not require a monolithic effects engine or a feature-rich NLE timeline UI.

## Ordinary-user usability floor

The Stage-A user-facing surface may be visually plain. It must be practical, understandable, controllable and extensible.

At minimum the user must be able to:

- create/open project;
- select required inputs;
- select/identify outputs;
- start work;
- understand current progress/failure;
- locate produced plans/final media;
- perform the workflow without repository-file editing or manual Domain/EDL construction.

## Compatibility and deployment floor

Stage-A must not assume a preconfigured developer workstation.

The product direction must support:

- bounded/private runtime dependencies where practical;
- diagnosable degraded behavior when optional acceleration is unavailable;
- CPU-capable baseline behavior for supported workflows;
- clear environment diagnostics instead of unexplained failure;
- replaceable adapters so Preview/GUI/provider/runtime choices do not become Domain authority.

Final installer/package polish belongs to later release readiness, but Stage-A 100% cannot rely on undocumented manual developer setup as the normal user path.

## Evidence required for PASS

Before the control plane may set structural progress to `100`:

1. Core 1 Product Gate is explicitly `PASS` with durable Product Probe/Human Gate evidence.
2. Core 2 Product Gate is explicitly `PASS` with a real final MP4 from the actual automatic workflow.
3. Planning-only, Editing-only and Combined semantics are preserved.
4. The ordinary-user usability floor above is demonstrated on Windows.
5. The latest accepted `main` is green under the required repository quality/governance gates.
6. Closure evidence records exact commit, runtime/provider versions, machine/environment class and known limitations.

## Machine guard

`tools/maintenance/repo_doctor.py` must reject any control state that reports `structural_progress_percent: 100` unless:

- `stage_a_completion_gate: PASS`;
- `core_1_planning_product_gate: PASS`;
- `core_2_editing_product_gate: PASS`.

This file defines the product gate; the control state records its live result.
