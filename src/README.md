# Source Layout

**Last updated:** 2026-08-22

Production code lives in `video_editing_agent/` and follows the accepted v0.2 ownership/dependency direction.

High-level packages:

- `domain/` — durable product/domain values and invariants; no outer-layer dependency.
- `application/` — provider-neutral ports, use-case orchestration and canonical application contracts.
- `planning/` — Brief/Script/Shooting planning ownership and reference-guidance projection.
- `media/` — ingest, shot detection, understanding, speech and temporal-evidence machinery for exact user-footage evidence.
- `editing/` — Director/Resolver editing decisions and grounded source-selection machinery.
- `music/` — BeatMap, music selection, audio editorial and decision→diagnostic execution support.
- `providers/` — replaceable LLM/vision/speech/embedding/reference adapters behind owned seams. Site/provider mechanics stay here and must not become Planning/Editing Domain truth.
- `storage/` — persistence/workspace implementations; storage never gains semantic ownership.
- `adapters/` — external composition/entry surfaces, including CLI and ordinary desktop product shell.
- `render/` — canonical EDL execution/render implementation; Renderer executes owned decisions and does not invent editorial authority.

## Current attention hints

For ordinary current work, start from the active Work Order and only then inspect the package that owns the task.

Examples:

- desktop UX / Project Workspace → `adapters/product/`, `storage/project/`, then focused tests;
- packaging/runtime/resource location → adapter/bootstrap/runtime-locator surfaces, never Domain;
- exact user-footage understanding → `media/` + owned repositories;
- remote reference-site mechanics → `providers/reference/`; ordinary Stage-A URL input is currently hidden and remote/video-native observation is deferred to 2.0;
- canonical timing/output → `domain/edl`, application EDL builder, `render/`.

Do not recursively read every package to start a bounded task.

## Folder hygiene

Do not keep empty Python packages merely to advertise future roadmap ideas. Architecture/capability documents define future seams; create implementation packages when construction actually begins.

A folder existing in `src/` should therefore mean there is real code or an immediately required package boundary, not just a placeholder.

Avoid creating duplicate helper modules when an existing owner can carry the behavior. Prefer one stable port/owner plus replaceable adapters over provider/site/model branches scattered across ProductFlow.

Dependency direction is enforced by `pyproject.toml` import-linter contracts.
