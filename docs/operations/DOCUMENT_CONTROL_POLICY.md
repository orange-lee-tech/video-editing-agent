# Document Control Policy

**Status:** ACTIVE  
**Last updated:** 2026-08-21  
**Scope:** repository documentation/control surfaces

## Purpose

Keep the repository easy to navigate for humans and AI as history grows. The goal is not maximum documentation; it is minimum attention cost with durable provenance.

## Canonical navigation

Use:

- `AGENTS.md` for agent attention/safety rules;
- `docs/DOCUMENT_REGISTRY.json` for the compact map;
- `docs/README.md` for documentation authority/navigation;
- the live trio for current execution truth:
  - `docs/operations/CURRENT_CONTROL_STATE.md`
  - `docs/roadmap/CURRENT_PHASE_STATUS.md`
  - `docs/operations/CURRENT_WORK_ORDER.md`

Do not create a second authority stack when an existing canonical file can be refreshed.

## Update-date rule

Every managed document must have a discoverable update date.

1. Active authority/control documents edited in a change must declare their current date in-file using an existing date field or `Last updated: YYYY-MM-DD`.
2. Other managed tracked documents are guaranteed a machine-visible `git_last_changed` date by the generated registry manifest.
3. `docs/archive/**` is exempt from forced metadata rewrites. Historical originals must not be modified merely to add a date; their Git history is the authoritative update date.
4. New active Markdown governance documents should declare `Last updated` from creation.

A date is metadata, not evidence that the document is still semantically current. Authority/lifecycle always wins over recency.

## Attention classes

- `CORE` — normal current-work entry points. Read first when relevant.
- `ON_DEMAND` — active material read only when the current task touches its area.
- `EVIDENCE_ONLY` — validation/log/research history used when proof or rationale is needed.
- `EXCLUDED_DEFAULT` — known to the registry but not opened during ordinary work.

`docs/archive/**` is always `EXCLUDED_DEFAULT`.

## Lifecycle classes

- `ACTIVE` — current authority, contract, plan, or operating reference.
- `LIVE` — frequently refreshed current-state pointer.
- `EVIDENCE` — durable proof/history; not current authority by itself.
- `RETIRED` — superseded provenance under archive.

## Placement rules

- `docs/product/` — constitutional product policy and subordinate product guidance.
- `docs/architecture/` — active architecture contracts/plans.
- `docs/capabilities/` — active capability specifications.
- `docs/adr/` — current architecture decisions.
- `docs/roadmap/` — durable roadmap and live phase/completion gates.
- `docs/operations/` — dynamic execution/control/release-readiness material.
- `docs/validation/` — accepted Product/Engineering/Human Gate evidence.
- `docs/logs/` — incidents, probes, chronicles and lessons.
- `docs/research/` — non-normative survey/research evidence.
- `docs/upstream/` — active upstream/reuse/license ledger.
- `docs/archive/<category>/` — retired superseded documents preserved for provenance.

A completed phase document is not automatically archival. If it still proves current engineering truth, keep it in validation/logs/research as appropriate.

## Archive decision rule

Archive only when all are true:

1. a newer active document/system supersedes it;
2. ordinary current work should no longer consult it;
3. deletion would erase useful provenance.

Archiving is a semantic decision. Automation may flag candidates but must never automatically move files into archive.

## Registry model

`docs/DOCUMENT_REGISTRY.json` is intentionally compact. It contains:

- canonical relative paths;
- directory ownership/map;
- attention/lifecycle rules;
- default excluded surfaces;
- generator/workflow pointers.

The exhaustive path manifest is generated from Git-tracked files by `tools/maintenance/document_registry.py` and GitHub Actions. Keeping the exhaustive list generated rather than hand-maintained prevents stale navigation and avoids loading hundreds of paths into every AI context.

## Governance automation

`tools/maintenance/document_registry.py` must:

- enumerate tracked managed documents without walking ignored local/runtime directories;
- derive category/lifecycle/attention class from deterministic path rules;
- expose a Git-derived last-change date for every managed file;
- parse declared dates from active documents where available;
- validate canonical registry paths and excluded-default rules;
- produce a deterministic JSON manifest for audit/artifact use.

`.github/workflows/document-registry.yml` runs this inventory on governance-relevant changes and publishes the complete manifest as an artifact. `repository-governance.yml` continues to enforce live-state and repository invariants.

## Engineering-file navigation

Do not create a database row for every source file merely for discoverability. Engineering structure is governed by:

- directory `README.md` maps;
- Architecture Contract / CAP / ADR ownership;
- import-linter/package boundary tests;
- focused source/test discovery inside the active work boundary.

The document registry should reduce source-code scanning, not duplicate the source tree.

## Maintenance closeout

When a wave closes:

1. record durable validation evidence if the result is product/engineering significant;
2. refresh the live trio immediately;
3. update affected active authority/operation documents and their dates;
4. retire superseded documents only if the archive rule is satisfied;
5. run repository governance and registry inventory;
6. leave the next work order small, current and unambiguous.
