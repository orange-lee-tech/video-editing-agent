from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.media_corpus_manifest import build_manifest  # noqa: E402


def test_manifest_is_anonymous_stable_and_preserves_confirmed_coverage(
    tmp_path, monkeypatch
) -> None:
    media = tmp_path / "private-name.mp4"
    media.write_bytes(b"media")
    monkeypatch.setattr(
        "tools.media_corpus_manifest._probe",
        lambda path, ffprobe: {"duration_seconds": 1.0, "size_bytes": 5, "streams": []},
    )
    first = build_manifest(tmp_path, tmp_path / "ffprobe")
    digest = first["clips"][0]["sha256"]
    first["clips"][0]["coverage"] = ["low_motion", "camera_pan"]
    second = build_manifest(tmp_path, tmp_path / "ffprobe", first)
    assert second["clips"][0]["coverage"] == ["camera_pan", "low_motion"]
    assert second["clips"][0]["clip_id"] == f"clip_{digest[:12]}"
    assert "private-name" not in str(second)
