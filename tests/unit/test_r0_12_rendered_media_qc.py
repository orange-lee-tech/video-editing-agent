from __future__ import annotations

import subprocess
import wave
from pathlib import Path

from video_editing_agent.application.ports.rendered_media_qc import RenderedMediaQcCode
from video_editing_agent.providers.review import ffmpeg_pcm
from video_editing_agent.providers.review.ffmpeg_pcm import FFmpegPcmRenderedMediaQc


def _completed(
    return_code: int = 0, *, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], return_code, stdout=stdout, stderr=stderr)


def _write_pcm16(path: Path, samples: tuple[int, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = b"".join(item.to_bytes(2, "little", signed=True) for item in samples)
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(16_000)
        stream.writeframes(raw)


def test_missing_output_is_typed_without_shelling_out(tmp_path: Path, monkeypatch) -> None:
    calls: list[object] = []

    def fail_if_called(invocation):
        calls.append(invocation)
        raise AssertionError("runner must not be called for missing output")

    monkeypatch.setattr(ffmpeg_pcm, "_run", fail_if_called)

    result = FFmpegPcmRenderedMediaQc().inspect(tmp_path / "missing.mp4")

    assert result.has_code(RenderedMediaQcCode.OUTPUT_MISSING)
    assert result.is_inspectable is False
    assert calls == []


def test_no_audio_stream_is_measured_without_pcm_extraction(tmp_path: Path, monkeypatch) -> None:
    media = tmp_path / "silent-video.mp4"
    media.write_bytes(b"fixture")
    calls = []

    def runner(invocation):
        calls.append(invocation)
        assert invocation.tool_id == "ffprobe"
        return _completed(stdout='{"streams": []}')

    monkeypatch.setattr(ffmpeg_pcm, "_run", runner)

    result = FFmpegPcmRenderedMediaQc().inspect(media)

    assert result.audio_stream_present is False
    assert result.has_code(RenderedMediaQcCode.NO_AUDIO_STREAM)
    assert result.is_inspectable is True
    assert len(calls) == 1


def test_clean_pcm_extraction_returns_metrics(tmp_path: Path, monkeypatch) -> None:
    media = tmp_path / "clean.mp4"
    media.write_bytes(b"fixture")

    def runner(invocation):
        if invocation.tool_id == "ffprobe":
            return _completed(stdout='{"streams": [{"codec_type": "audio"}]}')
        _write_pcm16(Path(invocation.arguments[-1]), (1000, -1000, 2000, -2000) * 400)
        return _completed()

    monkeypatch.setattr(ffmpeg_pcm, "_run", runner)

    result = FFmpegPcmRenderedMediaQc().inspect(media)

    assert result.audio_stream_present is True
    assert result.peak_dbfs is not None
    assert result.rms_dbfs is not None
    assert result.clipped_samples == 0
    assert result.findings == ()
    assert len(result.invocations) == 2


def test_clipped_pcm_is_typed(tmp_path: Path, monkeypatch) -> None:
    media = tmp_path / "clipped.mp4"
    media.write_bytes(b"fixture")

    def runner(invocation):
        if invocation.tool_id == "ffprobe":
            return _completed(stdout='{"streams": [{"codec_type": "audio"}]}')
        _write_pcm16(Path(invocation.arguments[-1]), (32767, -32768, 1000, -1000) * 400)
        return _completed()

    monkeypatch.setattr(ffmpeg_pcm, "_run", runner)

    result = FFmpegPcmRenderedMediaQc().inspect(media)

    assert result.has_code(RenderedMediaQcCode.CLIPPING)
    assert result.clipped_samples is not None
    assert result.clipped_samples > 0


def test_mostly_silent_pcm_is_typed(tmp_path: Path, monkeypatch) -> None:
    media = tmp_path / "mostly-silent.mp4"
    media.write_bytes(b"fixture")

    def runner(invocation):
        if invocation.tool_id == "ffprobe":
            return _completed(stdout='{"streams": [{"codec_type": "audio"}]}')
        _write_pcm16(Path(invocation.arguments[-1]), (0,) * 2000 + (1000,) * 10)
        return _completed()

    monkeypatch.setattr(ffmpeg_pcm, "_run", runner)

    result = FFmpegPcmRenderedMediaQc().inspect(media)

    assert result.has_code(RenderedMediaQcCode.MOSTLY_SILENT)
    assert result.silent_fraction is not None
    assert result.silent_fraction > 0.95


def test_ffprobe_failure_is_typed(tmp_path: Path, monkeypatch) -> None:
    media = tmp_path / "probe-fail.mp4"
    media.write_bytes(b"fixture")
    monkeypatch.setattr(
        ffmpeg_pcm,
        "_run",
        lambda invocation: _completed(1, stderr="probe failed"),
    )

    result = FFmpegPcmRenderedMediaQc().inspect(media)

    assert result.has_code(RenderedMediaQcCode.INSPECTION_FAILED)
    assert result.is_inspectable is False


def test_pcm_extraction_failure_is_typed(tmp_path: Path, monkeypatch) -> None:
    media = tmp_path / "extract-fail.mp4"
    media.write_bytes(b"fixture")
    calls = 0

    def runner(invocation):
        nonlocal calls
        calls += 1
        if calls == 1:
            return _completed(stdout='{"streams": [{"codec_type": "audio"}]}')
        return _completed(1, stderr="extract failed")

    monkeypatch.setattr(ffmpeg_pcm, "_run", runner)

    result = FFmpegPcmRenderedMediaQc().inspect(media)

    assert result.has_code(RenderedMediaQcCode.INSPECTION_FAILED)
    assert result.is_inspectable is False
    assert len(result.invocations) == 2
