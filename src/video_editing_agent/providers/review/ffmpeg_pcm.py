from __future__ import annotations

import json
import subprocess
import wave
from pathlib import Path
from tempfile import TemporaryDirectory

from video_editing_agent.application.ports.executor import DeterministicToolInvocation
from video_editing_agent.application.ports.rendered_media_qc import (
    RenderedMediaQcCode,
    RenderedMediaQcFinding,
    RenderedMediaQcResult,
)
from video_editing_agent.music.audio_editorial import inspect_pcm16_wav
from video_editing_agent.system.process import external_process_creationflags


def _run(invocation: DeterministicToolInvocation) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [invocation.tool_id, *invocation.arguments],
        creationflags=external_process_creationflags(),
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )


def _audio_probe_invocation(path: Path, executable: str) -> DeterministicToolInvocation:
    return DeterministicToolInvocation(
        f"review-audio-probe:{path.name}",
        executable,
        (
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "json",
            str(path),
        ),
        (str(path),),
    )


def _pcm_extract_invocation(
    path: Path, pcm_path: Path, executable: str
) -> DeterministicToolInvocation:
    return DeterministicToolInvocation(
        f"review-pcm-extract:{path.name}",
        executable,
        (
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-y",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-vn",
            "-c:a",
            "pcm_s16le",
            str(pcm_path),
        ),
        (str(path),),
        (str(pcm_path),),
    )


def _audio_stream_present(content: str) -> bool | None:
    try:
        root: object = json.loads(content)
    except json.JSONDecodeError:
        return None
    if not isinstance(root, dict):
        return None
    streams = root.get("streams")
    if not isinstance(streams, list):
        return None
    return any(isinstance(item, dict) and item.get("codec_type") == "audio" for item in streams)


def _failure(
    path: Path,
    code: RenderedMediaQcCode,
    message: str,
    invocations: tuple[DeterministicToolInvocation, ...] = (),
) -> RenderedMediaQcResult:
    return RenderedMediaQcResult(
        path,
        None,
        None,
        None,
        None,
        None,
        (RenderedMediaQcFinding(code, message),),
        invocations,
    )


class FFmpegPcmRenderedMediaQc:
    """Extract temporary PCM16 evidence from delivered media; never changes the render."""

    def __init__(self, ffmpeg_executable: str = "ffmpeg", ffprobe_executable: str = "ffprobe"):
        self._ffmpeg = ffmpeg_executable
        self._ffprobe = ffprobe_executable

    def inspect(self, path: Path) -> RenderedMediaQcResult:
        if not path.is_file():
            return _failure(
                path,
                RenderedMediaQcCode.OUTPUT_MISSING,
                "rendered output does not exist or is not a regular file",
            )

        probe = _audio_probe_invocation(path, self._ffprobe)
        try:
            probed = _run(probe)
        except OSError as exc:
            return _failure(
                path,
                RenderedMediaQcCode.INSPECTION_FAILED,
                str(exc),
                (probe,),
            )
        if probed.returncode != 0:
            return _failure(
                path,
                RenderedMediaQcCode.INSPECTION_FAILED,
                probed.stderr.strip() or "ffprobe audio inspection failed",
                (probe,),
            )
        audio_present = _audio_stream_present(probed.stdout)
        if audio_present is None:
            return _failure(
                path,
                RenderedMediaQcCode.INSPECTION_FAILED,
                "ffprobe audio inspection returned invalid JSON evidence",
                (probe,),
            )
        if not audio_present:
            return RenderedMediaQcResult(
                path,
                False,
                None,
                None,
                None,
                None,
                (
                    RenderedMediaQcFinding(
                        RenderedMediaQcCode.NO_AUDIO_STREAM,
                        "delivered media contains no audio stream",
                    ),
                ),
                (probe,),
            )

        with TemporaryDirectory(prefix="video-editing-agent-review-") as directory:
            pcm_path = Path(directory) / "audio.wav"
            extract = _pcm_extract_invocation(path, pcm_path, self._ffmpeg)
            try:
                extracted = _run(extract)
            except OSError as exc:
                return _failure(
                    path,
                    RenderedMediaQcCode.INSPECTION_FAILED,
                    str(exc),
                    (probe, extract),
                )
            if extracted.returncode != 0 or not pcm_path.is_file():
                return _failure(
                    path,
                    RenderedMediaQcCode.INSPECTION_FAILED,
                    extracted.stderr.strip() or "FFmpeg PCM extraction failed",
                    (probe, extract),
                )
            try:
                pcm = inspect_pcm16_wav(str(pcm_path))
            except (EOFError, OSError, wave.Error) as exc:
                return _failure(
                    path,
                    RenderedMediaQcCode.INSPECTION_FAILED,
                    str(exc),
                    (probe, extract),
                )

        unexpected_warnings = tuple(
            warning
            for warning in pcm.warnings
            if warning
            not in {
                "clipped PCM samples detected",
                "mostly silent audio",
                "empty audio",
            }
        )
        if unexpected_warnings:
            return _failure(
                path,
                RenderedMediaQcCode.INSPECTION_FAILED,
                "; ".join(unexpected_warnings),
                (probe, extract),
            )

        findings: list[RenderedMediaQcFinding] = []
        if pcm.clipped_samples > 0:
            findings.append(
                RenderedMediaQcFinding(
                    RenderedMediaQcCode.CLIPPING,
                    "clipped PCM samples detected in delivered output",
                )
            )
        if pcm.silent_fraction > 0.95:
            findings.append(
                RenderedMediaQcFinding(
                    RenderedMediaQcCode.MOSTLY_SILENT,
                    "delivered output PCM is mostly silent",
                )
            )
        return RenderedMediaQcResult(
            path,
            True,
            pcm.peak_dbfs,
            pcm.rms_dbfs,
            pcm.silent_fraction,
            pcm.clipped_samples,
            tuple(findings),
            (probe, extract),
        )
