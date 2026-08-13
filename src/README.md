# Source Layout

Production code lives in `video_editing_agent/` and follows the accepted v0.2 ownership/dependency direction.

High-level packages:

- `domain/` — durable product/domain values and invariants; no outer-layer dependency.
- `application/` — ports and use-case orchestration.
- `planning/` — Brief/Script/Shooting planning implementations.
- `media/` — ingest, understanding, speech and temporal-evidence machinery.
- `editing/` — Director/Resolver editing decision implementations that currently exist.
- `music/` — BeatMap, music selection, audio editorial and decision→diagnostic execution support.
- `providers/` — replaceable LLM/vision/speech/embedding adapters behind owned seams.
- `storage/` — persistence implementations; storage never gains semantic ownership.
- `adapters/` — current external entry adapters such as CLI.
- `render/` — render-layer namespace; full EDL/renderer productization remains future Roadmap work.

## Folder hygiene

Do not keep empty Python packages merely to advertise future roadmap ideas. Architecture/capability documents define future seams; create implementation packages when construction actually begins.

A folder existing in `src/` should therefore mean there is real code or an immediately required package boundary, not just a placeholder.

Dependency direction is enforced by `pyproject.toml` import-linter contracts.
