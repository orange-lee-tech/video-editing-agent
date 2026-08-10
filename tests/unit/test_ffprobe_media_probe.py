import json

import pytest

from video_editing_agent.media.ingest.ffprobe import parse_ffprobe_metadata


def test_parse_video_and_audio_metadata() -> None:
    payload = json.dumps(
        {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                    "avg_frame_rate": "30000/1001",
                    "r_frame_rate": "30/1",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "channels": 2,
                    "sample_rate": "48000",
                },
            ],
            "format": {"duration": "2.502"},
        }
    )

    metadata = parse_ffprobe_metadata(payload)

    assert metadata.media_kind == "video"
    assert metadata.duration_ms == 2_502
    assert metadata.width == 1920
    assert metadata.height == 1080
    assert metadata.fps == pytest.approx(30000 / 1001)
    assert metadata.codec == "h264"
    assert metadata.audio_channels == 2
    assert metadata.sample_rate_hz == 48_000


def test_parse_audio_only_metadata() -> None:
    payload = json.dumps(
        {
            "streams": [
                {
                    "codec_type": "audio",
                    "codec_name": "flac",
                    "channels": 1,
                    "sample_rate": "44100",
                }
            ],
            "format": {"duration": "1.25"},
        }
    )

    metadata = parse_ffprobe_metadata(payload)

    assert metadata.media_kind == "audio"
    assert metadata.duration_ms == 1_250
    assert metadata.codec == "flac"
    assert metadata.width is None
    assert metadata.fps is None
    assert metadata.audio_channels == 1
    assert metadata.sample_rate_hz == 44_100


def test_invalid_average_frame_rate_falls_back_to_real_rate() -> None:
    payload = json.dumps(
        {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "mpeg4",
                    "width": 320,
                    "height": 180,
                    "avg_frame_rate": "0/0",
                    "r_frame_rate": "25/1",
                }
            ],
            "format": {"duration": "4.0"},
        }
    )

    assert parse_ffprobe_metadata(payload).fps == 25.0


def test_payload_without_supported_stream_is_rejected() -> None:
    payload = json.dumps({"streams": [{"codec_type": "subtitle"}], "format": {}})

    with pytest.raises(ValueError, match="no supported video or audio stream"):
        parse_ffprobe_metadata(payload)


def test_invalid_json_is_rejected() -> None:
    with pytest.raises(ValueError, match="invalid JSON"):
        parse_ffprobe_metadata("not-json")
