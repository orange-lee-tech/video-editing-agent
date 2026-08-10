# Architecture

The repository is governed by the Architecture Contract v0.1.x series.

Authority order:

1. `ARCHITECTURE_CONTRACT_V0.1.md` — core domain model.
2. `ARCHITECTURE_CONTRACT_V0.1.1.md` — object relationships and schema matrix.
3. `ARCHITECTURE_CONTRACT_V0.1.2.md` — module ownership and interface matrix.

Implementation MUST conform to these contracts.

If implementation evidence requires an architectural change, record an ADR under
`docs/decisions/` before changing a contract.

Core pipeline:

`Brief -> ScriptPlan -> ShootingPlan -> Asset / Shot -> BeatMap -> EditPlan -> ResolutionDecision -> EDL -> Render -> ReviewReport`
