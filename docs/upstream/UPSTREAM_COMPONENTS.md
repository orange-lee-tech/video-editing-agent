# Upstream Component Ledger

| Upstream | Role | Code reuse status | Destination | Provenance |
|---|---|---|---|---|
| FireRed-OpenStoryline | Pipeline/media/render reference | Not migrated | TBD | Pending |
| MoneyPrinterTurbo | Material provider reference | Not migrated | TBD | Pending |
| CutClaw | Editing architecture reference | Forbidden | N/A | Reference only |
| BeatSync Engine | BeatMap algorithm reference | Not migrated | TBD | Reference only |

Before any source migration:

1. identify exact upstream file;
2. record upstream commit SHA;
3. verify license at that revision;
4. identify local destination;
5. classify copied/adapted/independently reimplemented;
6. preserve notices when required;
7. run all architecture and test gates.
