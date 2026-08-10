# ADR-0001 — SQLite for local structured persistence

Status: **ACCEPTED — 2026-08-10**

## Context

The R0.3 footage-understanding foundation is complete, but authoritative `Asset` / `Shot` records and
derived `ShotAnalysis` revisions are still represented by in-memory repository implementations during
integration probes. They therefore do not yet survive process restart.

Architecture Contract v0.1.2 requires storage to persist and retrieve revisioned records without
acquiring semantic ownership. `AssetIngestService`, `ShotCatalog`, and `UnderstandingService` must
remain the owners that create the corresponding semantic records or revisions.

The first product is single-user and local-first. It does not need a network database, distributed
coordination, a database service, or a persistence framework.

Binary frame payloads already have a separate SHA-256 content-addressed `ArtifactStore`; storing those
bytes inside the structured-record database would collapse an intentional architecture boundary.

## Decision

Use Python 3.12's standard-library `sqlite3` module as the first local structured persistence backend.

The R0.4 persistence contract is:

- one SQLite database file inside a local project/workspace persistence boundary;
- structured revision identity is stored in explicit relational key columns;
- complete record bodies are encoded by deterministic versioned codecs;
- `Asset` primary identity is `(entity_id, revision)`;
- `Shot` primary identity is `(entity_id, revision)` and references the exact Asset revision;
- `ShotAnalysis` primary identity is `(shot_entity_id, shot_revision, analysis_revision)` and references
  the exact Shot revision;
- exact revision history is append-only from the repository API's perspective;
- saving the same exact revision with identical content is idempotent;
- saving the same exact revision with different content fails loudly instead of mutating history;
- `PRAGMA foreign_keys = ON` is enabled for every connection;
- `PRAGMA user_version` records the application schema version, beginning at `1`;
- transactions are explicit and committed or rolled back as one unit;
- SQLite stores structured records only; binary artifacts remain in `ArtifactStore`;
- SQLite repositories implement application-owned ports and never create semantic revisions.

R0.4 does **not** introduce WAL as a requirement. The initial single-user workload does not justify
making journal-mode policy part of the architecture contract. It can be evaluated later from measured
concurrency/runtime evidence.

R0.4 also does **not** introduce SQLAlchemy or a migration framework. Schema bootstrap/version checking
is small enough to remain explicit while the storage contract is still young.

## Alternatives considered

### JSON files as the primary record store

Rejected as the main structured persistence layer. JSON remains useful as a serialization format, but
using independent files as the repository would weaken atomic multi-record transactions, exact-revision
constraints, foreign-key integrity, and indexed lookup. It would also drift toward the file/message-bus
style explicitly rejected by the Architecture Contracts.

### SQLAlchemy

Deferred. It would add a substantial abstraction and dependency before the project has demonstrated a
need for multiple SQL backends or ORM behavior. The current repository ports already isolate storage
implementation details.

### PostgreSQL or another database service

Rejected for the local-first v0.x baseline. A server process, credentials, network lifecycle, and
multi-user concerns would add deployment complexity without solving a current product requirement.

### Store binary artifacts in SQLite

Rejected. Extracted frames and future large binary artifacts remain content-addressed files behind
`ArtifactStore`; SQLite holds references to them only.

## Consequences

Positive:

- process-restart durability becomes available without adding a runtime dependency;
- exact revision identity and referential integrity become machine-enforced;
- repository writes can be transactional and deterministic;
- local project data remains portable as ordinary files;
- Domain/Application contracts remain independent of SQLite.

Costs and constraints:

- codecs and schema evolution must be explicit and tested;
- one SQLite database permits only one active writer at a time, which is acceptable for the current
  single-user architecture;
- future schema changes require deliberate `user_version` migrations rather than silent table edits;
- storage corruption/recovery behavior will need operational validation before production claims.

## Contract impact

No Architecture Contract amendment is required.

This ADR implements the existing v0.1.2 rule that repositories persist data without semantic authority.
The dependency direction remains inward-facing:

`Application Port <- SQLite Repository implementation`

The following ownership remains unchanged:

- `AssetIngestService` creates `Asset` identity;
- `ShotCatalog` creates `Shot` identity;
- `UnderstandingService` creates `ShotAnalysis` revisions;
- repositories only save/load those already-created records;
- `ArtifactStore` continues to own binary artifact persistence, not Domain semantics.
