from __future__ import annotations

from pathlib import Path

from video_editing_agent.application.ports.preview import (
    PreviewDecodeMode,
    PreviewDiagnosticCode,
    PreviewPlaybackState,
)
from video_editing_agent.application.use_cases.preview_runtime import PreviewApplicationRuntime
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.providers.preview.gstreamer import (
    GStreamerPreviewBackend,
    GStreamerPreviewConfig,
    _NativeEvent,
)


class FakeGStreamerApi:
    def __init__(
        self,
        *,
        version: tuple[int, int, int, int] = (1, 28, 6, 0),
        feature_ranks: dict[str, int] | None = None,
    ) -> None:
        self.version_value = version
        self.feature_ranks = {} if feature_ranks is None else dict(feature_ranks)
        self.events: list[_NativeEvent] = []
        self.operations: list[tuple[str, object]] = []
        self.position = 0
        self.player = object()
        self.bus = object()
        self.released = False

    def version(self) -> tuple[int, int, int, int]:
        return self.version_value

    def create_player(self) -> object:
        self.operations.append(("create_player", self.player))
        return self.player

    def get_message_bus(self, player: object) -> object:
        assert player is self.player
        self.operations.append(("get_message_bus", player))
        return self.bus

    def set_uri(self, player: object, uri: str) -> None:
        assert player is self.player
        self.operations.append(("set_uri", uri))

    def play(self, player: object) -> None:
        assert player is self.player
        self.operations.append(("play", player))

    def pause(self, player: object) -> None:
        assert player is self.player
        self.operations.append(("pause", player))

    def seek(self, player: object, position_ns: int) -> None:
        assert player is self.player
        self.position = position_ns
        self.operations.append(("seek", position_ns))

    def position_ns(self, player: object) -> int | None:
        assert player is self.player
        return self.position

    def stop(self, player: object) -> None:
        assert player is self.player
        self.operations.append(("stop", player))

    def set_feature_rank(self, name: str, rank: int) -> int | None:
        previous = self.feature_ranks.get(name)
        if previous is None:
            return None
        self.feature_ranks[name] = rank
        self.operations.append(("set_feature_rank", (name, rank)))
        return previous

    def drain_events(self, bus: object) -> tuple[_NativeEvent, ...]:
        assert bus is self.bus
        events = tuple(self.events)
        self.events.clear()
        return events

    def release(self, player: object, bus: object) -> None:
        assert player is self.player
        assert bus is self.bus
        self.released = True
        self.operations.append(("release", player))


def _runtime_tree(root: Path) -> None:
    bin_dir = root / "bin"
    plugin_dir = root / "lib" / "gstreamer-1.0"
    bin_dir.mkdir(parents=True)
    plugin_dir.mkdir(parents=True)
    for name in (
        "gstreamer-1.0-0.dll",
        "gstplay-1.0-0.dll",
        "gobject-2.0-0.dll",
        "glib-2.0-0.dll",
    ):
        (bin_dir / name).write_bytes(b"fixture")


def test_preview_application_runtime_exposes_playback_only_operations(tmp_path: Path) -> None:
    root = tmp_path / "gst"
    _runtime_tree(root)
    api = FakeGStreamerApi()
    backend = GStreamerPreviewBackend(
        GStreamerPreviewConfig(root),
        api_factory=lambda _: api,
        environment={},
        platform_name="nt",
    )

    runtime = PreviewApplicationRuntime.from_backend(backend)

    assert tuple(runtime.preview.__dataclass_fields__) == (
        "initialize",
        "load",
        "play",
        "pause",
        "seek",
        "status",
        "stop",
        "release",
    )
    assert not hasattr(runtime.preview, "render")
    assert not hasattr(runtime.preview, "edit")


def test_gstreamer_preview_lifecycle_and_exact_seek(tmp_path: Path) -> None:
    root = tmp_path / "gst"
    _runtime_tree(root)
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"media")
    api = FakeGStreamerApi()
    environment = {"PATH": "original-path"}
    backend = GStreamerPreviewBackend(
        GStreamerPreviewConfig(root, provenance="official-msvc-private-runtime"),
        api_factory=lambda _: api,
        environment=environment,
        platform_name="nt",
    )

    initialized = backend.initialize()
    assert initialized.state is PreviewPlaybackState.READY
    assert initialized.runtime_version == "1.28.6.0"
    assert initialized.runtime_provenance == "official-msvc-private-runtime"
    assert environment["GST_PLUGIN_SYSTEM_PATH_1_0"] == str(
        root.resolve() / "lib" / "gstreamer-1.0"
    )
    assert environment["GST_PLUGIN_PATH_1_0"] == ""

    assert backend.load(media).state is PreviewPlaybackState.LOADED
    assert backend.play().state is PreviewPlaybackState.PLAYING
    assert backend.pause().state is PreviewPlaybackState.PAUSED

    sought = backend.seek(MediaTime(3, 2))
    assert sought.diagnostics == ()
    assert ("seek", 1_500_000_000) in api.operations
    assert sought.position == MediaTime(3, 2)

    assert backend.stop().state is PreviewPlaybackState.STOPPED
    first_release = backend.release()
    second_release = backend.release()
    assert first_release.state is PreviewPlaybackState.RELEASED
    assert second_release.state is PreviewPlaybackState.RELEASED
    assert api.released is True
    assert environment == {"PATH": "original-path"}


def test_software_video_mode_demotes_and_restores_known_hardware_decoders(
    tmp_path: Path,
) -> None:
    root = tmp_path / "gst"
    _runtime_tree(root)
    api = FakeGStreamerApi(
        feature_ranks={
            "d3d11h264dec": 257,
            "d3d11h265dec": 257,
            "d3d12h264dec": 258,
        }
    )
    backend = GStreamerPreviewBackend(
        GStreamerPreviewConfig(root, decode_mode=PreviewDecodeMode.SOFTWARE_VIDEO),
        api_factory=lambda _: api,
        environment={},
        platform_name="nt",
    )

    status = backend.initialize()

    assert status.state is PreviewPlaybackState.READY
    assert status.decode_mode is PreviewDecodeMode.SOFTWARE_VIDEO
    assert status.disabled_hardware_features == (
        "d3d11h264dec",
        "d3d11h265dec",
        "d3d12h264dec",
    )
    assert api.feature_ranks["d3d11h264dec"] == 0
    assert api.feature_ranks["d3d11h265dec"] == 0
    assert api.feature_ranks["d3d12h264dec"] == 0

    backend.release()

    assert api.feature_ranks["d3d11h264dec"] == 257
    assert api.feature_ranks["d3d11h265dec"] == 257
    assert api.feature_ranks["d3d12h264dec"] == 258


def test_missing_runtime_and_version_mismatch_are_typed(tmp_path: Path) -> None:
    missing = GStreamerPreviewBackend(
        GStreamerPreviewConfig(tmp_path / "missing"),
        api_factory=lambda _: FakeGStreamerApi(),
        environment={},
        platform_name="nt",
    )
    missing_status = missing.initialize()
    assert missing_status.state is PreviewPlaybackState.FAILED
    assert missing_status.diagnostics[0].code is PreviewDiagnosticCode.RUNTIME_NOT_FOUND

    root = tmp_path / "gst"
    _runtime_tree(root)
    wrong = GStreamerPreviewBackend(
        GStreamerPreviewConfig(root),
        api_factory=lambda _: FakeGStreamerApi(version=(1, 30, 0, 0)),
        environment={},
        platform_name="nt",
    )
    wrong_status = wrong.initialize()
    assert wrong_status.state is PreviewPlaybackState.FAILED
    assert wrong_status.diagnostics[0].code is PreviewDiagnosticCode.RUNTIME_INVALID


def test_preview_rejects_missing_media_and_unrepresentable_seek(tmp_path: Path) -> None:
    root = tmp_path / "gst"
    _runtime_tree(root)
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"media")
    api = FakeGStreamerApi()
    backend = GStreamerPreviewBackend(
        GStreamerPreviewConfig(root),
        api_factory=lambda _: api,
        environment={},
        platform_name="nt",
    )
    assert backend.initialize().diagnostics == ()

    missing = backend.load(tmp_path / "missing.mp4")
    assert missing.diagnostics[0].code is PreviewDiagnosticCode.MEDIA_NOT_FOUND

    assert backend.load(media).diagnostics == ()
    invalid = backend.seek(MediaTime(1, 3))
    assert invalid.diagnostics[0].code is PreviewDiagnosticCode.INVALID_SEEK
    assert not any(operation[0] == "seek" for operation in api.operations)


def test_gstreamer_bus_missing_plugin_failure_is_typed(tmp_path: Path) -> None:
    root = tmp_path / "gst"
    _runtime_tree(root)
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"media")
    api = FakeGStreamerApi()
    backend = GStreamerPreviewBackend(
        GStreamerPreviewConfig(root),
        api_factory=lambda _: api,
        environment={},
        platform_name="nt",
    )
    backend.initialize()
    backend.load(media)
    api.events.append(
        _NativeEvent(
            error="Your GStreamer installation is missing a decoder",
            missing_plugin=True,
        )
    )

    status = backend.status()

    assert status.state is PreviewPlaybackState.FAILED
    assert status.diagnostics[0].code is PreviewDiagnosticCode.MISSING_PLUGIN
    assert "missing a decoder" in status.diagnostics[0].message


def test_state_events_are_diagnostic_truth_not_timeline_authority(tmp_path: Path) -> None:
    root = tmp_path / "gst"
    _runtime_tree(root)
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"media")
    api = FakeGStreamerApi()
    backend = GStreamerPreviewBackend(
        GStreamerPreviewConfig(root),
        api_factory=lambda _: api,
        environment={},
        platform_name="nt",
    )
    backend.initialize()
    backend.load(media)
    api.events.append(_NativeEvent(state=1))

    status = backend.status()

    assert status.state is PreviewPlaybackState.BUFFERING
    assert status.media_path == media.resolve()
    assert status.position == MediaTime(0, 1)
