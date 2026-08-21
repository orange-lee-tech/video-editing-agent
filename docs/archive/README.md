# Documentation Archive

**Last updated:** 2026-08-21  
**Attention class:** `EXCLUDED_DEFAULT`

This directory contains **retired repository documents** preserved for provenance but no longer active entry points or authority.

## Default attention rule

Humans and repository-aware agents must **not** recursively browse `docs/archive/**` during ordinary current work.

Open archived material only when a concrete task requires:

- explicit historical/provenance investigation;
- backward-compatibility analysis against a retired contract;
- legal/license provenance;
- a current authority document that explicitly points to a retired predecessor.

Always inspect current authority first. Archived material can explain history but can never override current product, architecture or live-state truth.

## Archive rule

A document belongs here when all are true:

- a newer active document or system has superseded it;
- current work should not consult it by default;
- deleting it would erase useful design/provenance history.

Archive placement is a semantic decision. Automation may report archive candidates but must not move files here automatically.

Current authority/navigation starts at `../README.md` and `../DOCUMENT_REGISTRY.json`.

## Contents

- `architecture/` — retired Architecture Contract v0.1 series.
- `decisions/` — retired pre-A0 ADR location/material.
- `upstream/` — retired Upstream V1 bootstrap policy/component snapshots.
- `roadmap/` — retired construction audits superseded as active navigation.

Additional category mirrors may be created when a future superseded active document genuinely satisfies the archive rule.

## Do not archive

Do not move a file here merely because it describes a completed phase. Accepted closure evidence, incidents/probes, research and current acceptance records remain in their canonical `validation/`, `logs/` or `research/` locations while they still prove or explain current engineering truth.

Do not resurrect an archived document by copying old rules back into active code. If an old idea becomes useful again, re-evaluate it against the current Constitution, Architecture Contract, capability specs and ADRs first.

Do not rewrite historical originals simply to add modern metadata/update dates. Git history and the generated document manifest provide their update provenance without mutating the record.
