# Repository Governance Lessons

Non-authoritative durable repository-maintenance lessons.

## 1. Active files and retired files should not share the same shelf

When a document is genuinely superseded and no longer an active entry point, move it to `docs/archive/` instead of leaving duplicate-looking versions beside current authority. Preserve provenance; remove ambiguity.

Archive is not a trash can. Closure evidence, A0 acceptance, incident/probe ledgers and research still used to explain current decisions remain in their canonical homes.

## 2. Every major directory needs a truthful README

A directory README should answer: what belongs here, what is current, what is historical, and where the real authority lives. Stale navigation can mislead a new AI more easily than missing documentation.

## 3. Do not scaffold empty future implementation packages

Empty Python packages make the source tree look more complete than it is and create fake ownership signals. Keep future capability boundaries in architecture/CAP/Roadmap documents; create implementation directories when actual code arrives.

## 4. Root README is a doorway, not an archive

The root README should describe product identity, current construction state, authority/navigation and basic verification. Detailed history belongs in validation/logs/archive rather than accumulating forever at the repository root.

## 5. One canonical home per document type

Examples:

- ADRs → `docs/adr/`;
- current phase → `CURRENT_PHASE_STATUS.md`;
- current execution boundary → `CURRENT_WORK_ORDER.md`;
- incidents/probes → `docs/logs/`;
- retired docs → `docs/archive/`.

Parallel homes such as the old `docs/decisions/` ADR location create routing ambiguity.

## 6. Do not rewrite the roadmap just because time passed

Roadmap V2 remains valid while capability decomposition, ordering and exit criteria remain sound. Progress belongs in the current-status pointer and validation evidence. Create a new roadmap only for a material strategic change.

## 7. Governance automation must stay non-authoritative

Micro-tools may detect stale links, misplaced retired files, tracked caches/private paths and inconsistent status/work-order pointers. They may not decide product policy, architecture semantics or whether a subjective Product Probe is acceptable.

## 8. Housekeeping changes should be coherent and reviewable

Prefer a dedicated governance commit/batch rather than mixing archive moves, README rewrites and feature code. After structural cleanup, run repository checks/CI so tidiness never comes at the cost of a broken build.
