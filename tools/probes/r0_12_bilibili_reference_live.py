from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from video_editing_agent.adapters.cli.media_config import transnetv2_detector
from video_editing_agent.adapters.product.runtime import locate_media_executable
from video_editing_agent.application.ports.reference_acquisition import (
    ReferenceAcquisitionRequest,
)
from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions
from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.asset.policy import AssetUsageRole
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.ingest.ffprobe import FfprobeMediaProbe
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.media.shot_detection.transnet_runtime import (
    TRANSNETV2_WEIGHTS_FILENAME,
)
from video_editing_agent.providers.reference.bilibili import BilibiliHtmlReferenceResolver
from video_editing_agent.providers.reference.direct_https import (
    DirectHttpsAcquisitionPolicy,
    DirectHttpsReferenceAcquirer,
)
from video_editing_agent.storage.project.workspace import ProjectWorkspace

DEFAULT_URL = "https://www.bilibili.com/video/BV1Mq4y187xR?share_source=copy_web"


def _ffprobe(path: Path) -> dict[str, object]:
    executable = locate_media_executable("ffprobe")
    if executable is None:
        return {"available": False}
    completed = subprocess.run(
        [
            executable,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,width,height",
            "-of",
            "json",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    payload = json.loads(completed.stdout) if completed.returncode == 0 else {}
    streams = payload.get("streams", []) if isinstance(payload, dict) else []
    return {
        "available": True,
        "returncode": completed.returncode,
        "video_streams": streams,
    }


def _transnet_weights() -> Path | None:
    spec = importlib.util.find_spec("transnetv2_pytorch")
    if spec is None or spec.origin is None:
        return None
    candidate = Path(spec.origin).resolve().parent / TRANSNETV2_WEIGHTS_FILENAME
    return candidate if candidate.is_file() else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    args = parser.parse_args(argv)
    with tempfile.TemporaryDirectory(prefix="r0_12_bilibili_reference_") as temporary:
        result = DirectHttpsReferenceAcquirer(
            Path(temporary),
            policy=DirectHttpsAcquisitionPolicy(
                max_bytes=128 * 1024 * 1024,
                total_timeout_seconds=180,
            ),
            html_media_resolvers=(BilibiliHtmlReferenceResolver(),),
        ).acquire(ReferenceAcquisitionRequest(args.url))
        if result.acquired is None:
            print(
                json.dumps(
                    {
                        "status": "FAILED",
                        "diagnostics": [
                            {"code": item.code.value, "message": item.message}
                            for item in result.diagnostics
                        ],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 1
        acquired = result.acquired
        media_probe = _ffprobe(acquired.local_path)
        video_streams = media_probe.get("video_streams")
        ingest_report: dict[str, object]
        ffprobe_executable = locate_media_executable("ffprobe")
        if ffprobe_executable is None:
            ingest_report = {"status": "UNAVAILABLE"}
        else:
            workspace = ProjectWorkspace.open(Path(temporary) / "project")
            asset = AssetIngestService(
                FfprobeMediaProbe(ffprobe_executable), repository=workspace.assets
            ).ingest(
                LocalMediaSource(
                    acquired.local_path,
                    "reference_https",
                    AssetProvenance(
                        origin_type="reference_https",
                        source_page=acquired.original_url,
                        provider=acquired.provider,
                        provider_asset_id=acquired.provider_item_id,
                        retrieved_at=acquired.retrieved_at,
                    ),
                    AssetUsageRole.REFERENCE_ANALYSIS_ONLY,
                ),
                created_by="r0-12-bilibili-live-probe",
            )
            ingest_report = {
                "status": "PASS",
                "media_kind": asset.media_kind,
                "has_audio": asset.audio_channels is not None,
                "usage_role": asset.usage_role.value,
            }
            ffmpeg_executable = locate_media_executable("ffmpeg")
            weights = _transnet_weights()
            if ffmpeg_executable is None or weights is None:
                ingest_report["shot_detection"] = "UNAVAILABLE"
            else:
                asset_ref = EntityRevisionRef(asset.envelope.id, asset.envelope.revision)
                shots = workspace.detect(
                    asset_ref,
                    transnetv2_detector(
                        workspace.assets,
                        model_path=weights,
                        device="cpu",
                        ffmpeg_executable=ffmpeg_executable,
                    ),
                    ShotDetectionOptions(),
                )
                ingest_report["shot_detection"] = "PASS"
                ingest_report["shot_count"] = len(shots)
        report = {
            "status": (
                "PASS"
                if video_streams
                else "ACQUISITION_PASS_MEDIA_PROBE_UNAVAILABLE"
                if not media_probe.get("available")
                else "FAILED_MEDIA_PROBE"
            ),
            "provider": acquired.provider,
            "provider_item_id": acquired.provider_item_id,
            "bytes": acquired.byte_size,
            "content_type": acquired.content_type,
            "final_host": urlsplit(acquired.final_url).hostname,
            "content_addressed": acquired.content_hash.startswith("sha256:"),
            "ffprobe": media_probe,
            "ingest": ingest_report,
        }
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0 if video_streams and ingest_report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
