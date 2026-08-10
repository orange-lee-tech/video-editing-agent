# TransNetV2 Streaming Inference — R0.1-C3 Provenance Record

## Upstream reference

- Repository: `soCzech/TransNetV2`
- Revision: `85cef72af9a916bdfd7cc94a670c9cdfbf12d1ed`
- Reference paths:
  - `inference/transnetv2.py`
  - `inference-pytorch/README.md`
- Upstream license: MIT

## Local destinations

- `src/video_editing_agent/media/shot_detection/transnet_window.py`
- `src/video_editing_agent/media/shot_detection/transnet_predictions.py`

Reuse classification:

**Independently reimplemented from the published inference contract. No upstream source code is copied.**

## Published inference contract retained

The upstream inference implementation establishes the model-facing geometry and overlap semantics:

- input frames are RGB uint8 with shape `27 x 48 x 3`;
- one inference window contains 100 frames;
- the first and last 25 frames provide temporal context;
- only the center 50 predictions are retained from each window;
- consecutive windows advance by 50 real frames;
- the first frame is repeated to create left-edge context;
- the final frame is repeated to create right-edge context;
- final padded predictions beyond the real source length are discarded.

The PyTorch inference README independently confirms the 100-frame input shape and RGB uint8 contract.

## Intentional architectural change

The upstream convenience `predict_frames` implementation accepts an already materialized full-video frame array and constructs padded arrays/windows from it.

This project targets long personal footage and has already established a streaming FFmpeg frame source. R0.1-C3 therefore reformulates the same inference geometry as a bounded-memory iterator:

`RGB24 frame stream -> padded 100-frame window -> model probability window -> valid center 50 predictions -> advance 50 frames`

Only one raw model window plus small iterator state is resident regardless of total video duration. One scalar single-frame probability per source frame may be retained for later scene conversion; this is intentionally much smaller than retaining raw RGB frames.

## Local window API

`TransNetV2Window`

- exactly 100 frame payloads;
- `valid_output_frames` records how many of the center predictions correspond to real source frames;
- `center_frames` exposes the real-output portion for deterministic tests.

`iter_transnetv2_windows(frames)`

- consumes any iterable of fixed-size frame bytes;
- validates frame type and frame-size consistency;
- performs first/last frame padding;
- emits one window per 50 output frames;
- never depends on Torch, NumPy, model weights, FFmpeg, `Asset`, or `Shot` identity.

## Local predictor seam

`TransNetV2WindowPredictor`

- accepts exactly one normalized 100-frame window;
- returns one single-frame transition probability per model-window frame;
- is the only contract a future heavy Torch adapter must implement.

`collect_transnetv2_single_frame_predictions(frames, predictor)`

- drives the streaming window iterator;
- validates predictor output length;
- keeps only valid center predictions;
- rejects non-finite or out-of-range probabilities;
- reconstructs exactly one single-frame probability per real source frame.

This prevents the heavy model adapter from owning overlap policy, padding policy, Shot boundary policy, or application/domain semantics.

## Dependency impact

R0.1-C3 adds no Python package dependency.

A later model runner may depend on `transnetv2_pytorch`/Torch, but that dependency will sit behind the window-predictor/backend contracts rather than becoming an application/domain concern.
