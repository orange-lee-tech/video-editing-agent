# Upstream Component Ledger

| Upstream | Role | Code reuse status | Destination | Provenance |
|---|---|---|---|---|
| FireRed-OpenStoryline | Pipeline/media/render reference | R0.1-A/B/C1/C2 independently reimplemented; no source copied | `application/ports/shot_detector.py`, `media/shot_detection/` | `FIRERED_SPLIT_SHOTS_R0.1.md`, `FIRERED_FFMPEG_FRAMES_R0.1.md` |
| soCzech/TransNetV2 | Shot-detection inference-contract reference | R0.1-C3/D1 independently reimplemented; no source copied | `media/shot_detection/transnet_window.py`, `transnet_predictions.py`, `transnet_scenes.py` | `TRANSNETV2_WINDOW_R0.1.md`, `TRANSNETV2_RUNTIME_R0.1.md` |
| allenday/transnetv2_pytorch / PyPI `transnetv2-pytorch` | Optional Torch inference runtime reference | R0.1-D1 adapter implemented independently; package not yet persisted in project dependencies | `media/shot_detection/transnet_runtime.py`, `transnet_backend.py` | `TRANSNETV2_RUNTIME_R0.1.md` |
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
