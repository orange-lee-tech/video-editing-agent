from pathlib import Path

from video_editing_agent.system import process


def test_external_process_policy_uses_create_no_window_only_on_windows(monkeypatch) -> None:
    monkeypatch.setattr(process.os, "name", "posix")
    assert process.external_process_creationflags() == 0

    monkeypatch.setattr(process.os, "name", "nt")
    monkeypatch.setattr(process.subprocess, "CREATE_NO_WINDOW", 0x08000000, raising=False)
    assert process.external_process_creationflags() == 0x08000000


def test_media_child_process_call_sites_apply_shared_no_console_policy() -> None:
    paths = (
        "src/video_editing_agent/media/ingest/ffprobe.py",
        "src/video_editing_agent/media/shot_detection/ffmpeg_frames.py",
        "src/video_editing_agent/media/understanding/frame_extraction.py",
        "src/video_editing_agent/render/edl_ffmpeg.py",
        "src/video_editing_agent/providers/review/ffmpeg_pcm.py",
    )
    for name in paths:
        content = Path(name).read_text(encoding="utf-8")
        assert "external_process_creationflags" in content, name
        assert "creationflags=external_process_creationflags()" in content, name
