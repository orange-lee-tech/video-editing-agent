from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from video_editing_agent.application.ports.executor import DeterministicToolInvocation
from video_editing_agent.application.ports.rendered_media_qc import (
    RenderedMediaQcCode,
    RenderedMediaQcResult,
)
from video_editing_agent.application.ports.renderer import OutputSpec, RenderArtifact, RenderResult
from video_editing_agent.application.use_cases.review_runtime import (
    ReviewApplicationRuntime,
    ReviewRequest,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.review.model import ReviewCorrectionRoute, ReviewDisposition
from video_editing_agent.providers.review.ffmpeg_pcm import FFmpegPcmRenderedMediaQc


class RecordingRenderedMediaQc:
    def __init__(self, delegate: FFmpegPcmRenderedMediaQc) -> None:
        self._delegate = delegate
        self.last_result: RenderedMediaQcResult | None = None

    def inspect(self, path: Path) -> RenderedMediaQcResult:
        result = self._delegate.inspect(path)
        self.last_result = result
        return result


def _run(arguments: list[str]) -> None:
    completed = subprocess.run(
        arguments,
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "fixture command failed")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _make_fixture(ffmpeg: str, path: Path, *, silent: bool) -> None:
    audio = (
        "anullsrc=channel_layout=stereo:sample_rate=48000:d=2"
        if silent
        else "sine=frequency=1000:sample_rate=48000:duration=2"
    )
    _run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=320x180:rate=30:duration=2",
            "-f",
            "lavfi",
            "-i",
            audio,
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(path),
        ]
    )


def _artifact(path: Path, edl_ref: EntityRevisionRef, ffmpeg: str, ffprobe: str) -> RenderArtifact:
    return RenderArtifact(
        path,
        edl_ref,
        OutputSpec(path, 320, 180, 30),
        DeterministicToolInvocation(
            f"fixture-render:{path.stem}",
            ffmpeg,
            (),
            expected_output_refs=(str(path),),
        ),
        DeterministicToolInvocation(
            f"fixture-verify:{path.stem}",
            ffprobe,
            (),
            input_refs=(str(path),),
        ),
    )


def _review_fixture(
    path: Path,
    edl_ref: EntityRevisionRef,
    ffmpeg: str,
    ffprobe: str,
) -> tuple[object, RenderedMediaQcResult, str, str]:
    before = _sha256(path)
    qc = RecordingRenderedMediaQc(FFmpegPcmRenderedMediaQc(ffmpeg, ffprobe))
    runtime = ReviewApplicationRuntime(qc)
    verdict = runtime.review(
        ReviewRequest(
            edl_ref,
            RenderResult(_artifact(path, edl_ref, ffmpeg, ffprobe), ()),
            requires_audible_output=True,
        )
    )
    after = _sha256(path)
    assert qc.last_result is not None
    assert not hasattr(runtime, "render")
    assert not hasattr(runtime, "edit")
    assert not hasattr(runtime, "build_edl")
    return verdict, qc.last_result, before, after


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if ffmpeg is None or ffprobe is None:
        raise RuntimeError("ffmpeg and ffprobe must be available on PATH")

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    clean_path = output / "clean-review-fixture.mp4"
    silent_path = output / "silent-review-fixture.mp4"
    _make_fixture(ffmpeg, clean_path, silent=False)
    _make_fixture(ffmpeg, silent_path, silent=True)

    clean_ref = EntityRevisionRef("review-probe-clean-edl", 1)
    silent_ref = EntityRevisionRef("review-probe-silent-edl", 1)
    clean_verdict, clean_qc, clean_before, clean_after = _review_fixture(
        clean_path,
        clean_ref,
        ffmpeg,
        ffprobe,
    )
    silent_verdict, silent_qc, silent_before, silent_after = _review_fixture(
        silent_path,
        silent_ref,
        ffmpeg,
        ffprobe,
    )

    gates = {
        "CLEAN_REVIEW_PASS": clean_verdict.disposition is ReviewDisposition.PASS,
        "CLEAN_ROUTE_NONE": clean_verdict.correction_route is ReviewCorrectionRoute.NONE,
        "CLEAN_REAL_PCM_QC": clean_qc.audio_stream_present is True
        and clean_qc.is_inspectable
        and len(clean_qc.invocations) == 2
        and clean_qc.findings == (),
        "SILENT_REVIEW_CORRECTION_REQUIRED": (
            silent_verdict.disposition is ReviewDisposition.CORRECTION_REQUIRED
        ),
        "SILENT_ROUTE_AUDIO_EDITORIAL": (
            silent_verdict.correction_route is ReviewCorrectionRoute.RETURN_TO_AUDIO_EDITORIAL
        ),
        "SILENT_REAL_PCM_QC": silent_qc.audio_stream_present is True
        and silent_qc.is_inspectable
        and silent_qc.has_code(RenderedMediaQcCode.MOSTLY_SILENT)
        and silent_qc.silent_fraction is not None
        and silent_qc.silent_fraction > 0.95
        and len(silent_qc.invocations) == 2,
        "CLEAN_ARTIFACT_UNCHANGED": clean_before == clean_after,
        "SILENT_ARTIFACT_UNCHANGED": silent_before == silent_after,
        "EXACT_EDL_PROVENANCE": clean_verdict.report.target_ref == clean_ref
        and silent_verdict.report.target_ref == silent_ref,
    }
    report = {
        "classification": "REVIEW_ENGINEERING_PROBE_REAL_MEDIA_FIXTURES",
        "artifact_origin": "deterministic_real_media_fixture",
        "gates": {name: "PASS" if passed else "FAIL" for name, passed in gates.items()},
        "clean": {
            "disposition": clean_verdict.disposition.value,
            "route": clean_verdict.correction_route.value,
            "peak_dbfs": clean_qc.peak_dbfs,
            "rms_dbfs": clean_qc.rms_dbfs,
            "silent_fraction": clean_qc.silent_fraction,
            "clipped_samples": clean_qc.clipped_samples,
            "findings": [finding.code.value for finding in clean_qc.findings],
            "sha256": clean_after,
        },
        "silent": {
            "disposition": silent_verdict.disposition.value,
            "route": silent_verdict.correction_route.value,
            "peak_dbfs": silent_qc.peak_dbfs,
            "rms_dbfs": silent_qc.rms_dbfs,
            "silent_fraction": silent_qc.silent_fraction,
            "clipped_samples": silent_qc.clipped_samples,
            "findings": [finding.code.value for finding in silent_qc.findings],
            "sha256": silent_after,
        },
        "pass": all(gates.values()),
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
