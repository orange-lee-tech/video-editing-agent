# GitHub Automation

This directory contains CI and reproducible engineering/probe workflows.

## Current role

- `workflows/ci.yml` is the primary repository quality-gate workflow.
- Other named workflows preserve targeted provider/media/persistence/phase probe entry points and historical reproducibility.
- `scripts/` contains GitHub-runner helpers such as Windows FFmpeg installation.

Workflow filenames are **not** current roadmap authority. Old phase-specific workflows may remain after a phase closes because they preserve a reproducible diagnostic path.

Current project state must be read from:

- `docs/roadmap/CURRENT_PHASE_STATUS.md`
- `docs/operations/CURRENT_WORK_ORDER.md`

## Retention policy

Keep a workflow when it still provides one of:

- required CI coverage;
- reproducible provider/runtime validation;
- durable regression evidence that would be costly to reconstruct.

Remove or consolidate a workflow only after verifying that no active CI, validation record or maintenance path depends on it. Do not delete historical workflows merely to make the directory shorter.

Secrets, private media and local absolute paths must never be committed into workflow files.
