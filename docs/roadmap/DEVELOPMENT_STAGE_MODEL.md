# Development Stage Model

**Status:** ACTIVE GOVERNANCE PRINCIPLE  
**Updated:** 2026-08-15

## Purpose

Separate structural product construction from later commercial-grade refinement so progress numbers and acceptance criteria remain honest.

The project is currently building the whole house before polishing every room.

## Stage A — Structural Construction

This is the current 0–100% progress scale.

Goal:

> complete the full product loop with correct authority boundaries, extensible contracts, deterministic execution, compatibility, observability and safe failure behavior.

A Stage-A capability may still have rough defaults, limited corpus tuning, basic UX or known non-blocking quality defects.

Stage A does **not** permit postponing structural defects. The following remain blockers when material:

- wrong ownership or hidden authority;
- ambiguous/non-deterministic executable semantics;
- broken compatibility or migration behavior;
- unsafe destructive behavior;
- untraceable provenance;
- hard-coded provider/dependency lock-in that violates architecture;
- missing fail-closed behavior at a required trust/license boundary;
- architecture that prevents later quality improvement without demolition.

Stage-A 100% means:

> the planned construction roadmap is structurally closed end to end **and the two core product workflows are genuinely operable through a normal user path**, ready for systematic refinement.

The two mandatory operability gates are:

1. **Planning core:** a user supplies the intended high-performing/reference/commercial goal and receives a persisted, inspectable `ScriptPlan` plus executable `ShootingPlan` from the real planning pipeline.
2. **Editing core:** a user selects local footage as the visual source and an output destination, runs the real owned understanding → music → Director/Resolver → spatial/audio → EDL → Renderer path, and receives a real final MP4 with the Stage-A minimum music/text/subtitle/editing-expression floor. Human-entered or hand-authored internal selections must not masquerade as automatic pipeline output.

Stage-A 100% also requires a **minimum ordinary Windows user entry point**. It need not be visually polished, but an ordinary user must be able to:

- create/open a project;
- select input footage files and/or a footage folder;
- select or clearly identify the output folder;
- provide the planning/editing inputs required by the two core workflows;
- start the workflow and observe meaningful progress or failure state;
- locate the generated Script/ShootingPlan and final MP4 without editing repository files or manually constructing internal Domain/EDL artifacts.

The engineering CLI may remain available, but CLI-only access does **not** satisfy the Stage-A 100% product-operability gate.

Acceptance must include real Product Probe execution of both core workflows through the user-facing path. Green unit tests, isolated module probes, or a synthetic integration smoke are necessary evidence but cannot substitute for this gate.

Stage-A 100% does **not** mean commercial perfection or final product maturity.

## Stage B — Product Refinement

Begins only after Stage A reaches 100% and the construction loop is accepted.

Primary work shifts toward:

- real-corpus output quality and editorial taste;
- UX and interaction polish;
- defaults, presets and controllability;
- performance, latency, memory and storage efficiency;
- visual/audio/subtitle consistency;
- robustness across difficult media and hardware;
- error recovery and diagnostics;
- benchmark-driven tuning;
- packaging/release experience;
- commercial-grade fit and finish.

Stage B may replace or tune Stage-A implementations behind preserved contracts. It should improve rooms without moving load-bearing walls unless evidence proves an architectural correction is actually required.

## Debt rule

Record known limitations instead of endlessly polishing them during construction.

Classify them as:

- **structural debt** — threatens architecture, correctness, extensibility, compatibility or safety; fix before advancing when material;
- **finish debt** — quality/UX/performance/polish limitation that does not threaten the structure; carry into Stage B with evidence.

## Progress reporting

Until Stage A closes, report:

- **Structural construction progress:** 0–100%;
- **Current roadmap phase progress:** 0–100%.

After Stage A reaches 100%, keep it fixed at 100% and begin a separate Stage-B refinement percentage.

Never reinterpret Stage-A 100% as "commercial quality is 100%".
