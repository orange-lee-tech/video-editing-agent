# Current Work Order

**ID:** `R0.12-EDITPLAN-COMPAT-001`  
**Status:** CLOSED  
**Phase:** R0.12 — parallel workflow compatibility correction  
**Owner/writer:** ChatGPT architecture/control + User PowerShell execution  
**Codex release:** NOT USED

## Result

PASS at accepted code baseline `1abc185a793d6a73ea55824bd2a036a1a134151a`.

The Planning/Editing coupling in `EditPlan` was removed without redesigning downstream Editing authority:

- Editing-only can carry exact Brief provenance with no ScriptPlan/ShootingPlan;
- Combined mode retains exact ScriptPlan/ShootingPlan provenance and can also carry Brief provenance;
- the pre-existing ScriptPlan+ShootingPlan positional construction remains intentionally compatible;
- ShootingPlan-without-ScriptPlan, intent-free, and Script-only-without-Brief shapes fail closed;
- existing slot uniqueness/order guards remain active;
- Resolver and EDLBuilder outputs are invariant to Planning provenance when slots/candidates/decisions are otherwise identical;
- no EditPlan persistence/database layer was invented.

Production scope remained bounded to `src/video_editing_agent/domain/edit/model.py`; all other changes were focused tests. Resolver, CandidateWindow generation, Retrieval, EDLBuilder, Canonical EDL, Renderer, Media Understanding, subtitle, spatial, music and audio production logic were not modified.

## Verification accepted

Local Windows:

- focused tests: 20 PASS;
- `uv run ruff format --check .`: PASS, 440 files formatted;
- `uv run ruff check .`: PASS;
- mypy: 184 source files PASS;
- full pytest: 551 PASS;
- import-linter: 3 contracts kept;
- `uv build`: PASS;
- `git diff --check`: PASS;
- living Resolver → EDLBuilder → Renderer smoke: 10/10 PASS with verified FFmpeg MP4 output.

Remote GitHub:

- semantic commit `25943f0157b7a63ea97a9f36f3c74955fd21840d` contains the bounded Domain/test migration;
- format-only follow-up `1abc185a793d6a73ea55824bd2a036a1a134151a` changes only two test files by adding formatter-required blank lines;
- remote `ci/quality-gate-diagnostic` at `1abc185a793d6a73ea55824bd2a036a1a134151a`: SUCCESS;
- durable closure evidence: `docs/validation/R0.12_EDITPLAN_PARALLEL_ENTRY_CLOSURE.md`.

## Durable verification rule

Future full local quality gates must mirror CI and include both Ruff formatting and linting:

```text
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
uv run lint-imports
uv build
git diff --check
```

Capability-specific probes are additional, not substitutes.

## Stop state

This work order is finished. Foreman must not treat it as active implementation work.

There is intentionally no downstream implementation work order active yet. ChatGPT/Product Owner must pre-process the next bounded Application step: a real Editing entry/orchestration boundary that starts from Brief/editorial intent + user footage and reuses the same Editing Core. Do not fake that step with an empty wrapper, a hand-authored EditPlan, or duplicated Resolver/EDLBuilder/Renderer logic.
