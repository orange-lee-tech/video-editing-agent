# FireRed FFmpeg Frame Source — R0.1-C2 Provenance Record

## Upstream reference

- Repository: `FireRedTeam/FireRed-OpenStoryline`
- Revision: `c9e945215586f45c12a61c1951ee9a8e9c43a027`
- Reviewed path: `src/open_storyline/utils/ffmpeg_utils.py`
- Relevant upstream function: `read_video_frames_as_rgb24`
- License at reviewed revision: Apache-2.0

## Local destination

`src/video_editing_agent/media/shot_detection/ffmpeg_frames.py`

Reuse classification:

**Independently reimplemented from reviewed behavior and interface requirements. No upstream source code is copied.**

## Behavior retained

The local frame source retains the useful media contract observed upstream:

- FFmpeg is invoked as an external executable;
- video is sampled at a fixed FPS;
- frames are resized to a fixed width and height using `fast_bilinear`;
- audio is ignored;
- pixel format is RGB24;
- raw frame bytes are read from FFmpeg stdout.

These behaviors are required by a future TransNetV2-compatible backend but remain independent of the model itself.

## Intentional divergence: streaming instead of whole-video buffering

The reviewed FireRed helper calls `communicate()` and materializes all decoded raw RGB frames before constructing a NumPy array.

That design is simple but makes resident raw-frame memory grow with video duration. This project targets long personal footage, so R0.1-C2 deliberately does not inherit that memory behavior.

The local implementation:

- reads exactly one fixed-size RGB24 frame at a time;
- yields frames through an iterator;
- keeps model batching/windowing outside the FFmpeg source;
- rejects incomplete final frames instead of silently truncating trailing bytes;
- stores FFmpeg stderr in a temporary file so unread stderr cannot fill a pipe while stdout is streamed;
- terminates an unfinished FFmpeg process when the consumer closes the iterator early;
- reports a missing executable as a clear runtime error.

## Architecture boundary

`ffmpeg_frames.py` is media infrastructure for shot detection.

It does not know about:

- `Brief`
- `ScriptPlan`
- `ShootingPlan`
- `Shot`
- `EditPlan`
- `EDL`
- TransNetV2 model APIs
- FireRed Node state
- output clip creation

Its sole responsibility is:

`video source -> stream of complete fixed-rate RGB24 frames`

The future TransNetV2 backend will consume this stream and own model-specific rolling-window inference.

## Dependency impact

R0.1-C2 adds no Python package dependency.

A real integration run requires an FFmpeg executable available through configuration or the execution environment, but FFmpeg is not imported into Domain or Application code.
