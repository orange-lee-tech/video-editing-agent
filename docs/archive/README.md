# Documentation Archive

This directory contains **retired repository documents** that are preserved for provenance but are no longer active entry points or authority.

## Archive rule

A document belongs here when all of the following are true:

- a newer active document or system has superseded it;
- current work should not consult it by default;
- deleting it would erase useful design/provenance history.

Archive material is read-only historical context. It must never override current authority or live state.

Current authority/navigation starts at `../README.md`.

## Contents

- `architecture/` — retired Architecture Contract v0.1 series. Active architecture is `../architecture/ARCHITECTURE_CONTRACT_V0.2.md`.
- `decisions/` — retired pre-A0 ADR location/material. New ADRs belong in `../adr/`.
- `upstream/` — retired Upstream V1 bootstrap policy/component snapshots. Active governance is in `../upstream/*_V2.md`.
- `roadmap/` — completed construction audits that are useful for provenance but no longer belong beside the live roadmap pointer.

## Do not archive

Do not move a file here merely because it describes a completed phase. Accepted closure evidence, incident/probe ledgers and the A0 acceptance record remain in their canonical directories because they still prove or govern current engineering state.

Do not resurrect an archived document by copying its old rules back into active code. If an old idea becomes useful again, re-evaluate it against the current Constitution, Architecture Contract, capability specs and ADRs first.
