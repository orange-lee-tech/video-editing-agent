from __future__ import annotations

import ctypes
import os
from collections.abc import Callable, MutableMapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from video_editing_agent.application.ports.preview import (
    PreviewBackend,
    PreviewDecodeMode,
    PreviewDiagnostic,
    PreviewDiagnosticCode,
    PreviewPlaybackState,
    PreviewStatus,
)
from video_editing_agent.domain.common.media_time import MediaTime

_GST_CLOCK_TIME_NONE = (1 << 64) - 1
_GST_PLAY_MESSAGE_STATE_CHANGED = 3
_GST_PLAY_MESSAGE_ERROR = 6
_GST_PLAY_STATE_STOPPED = 0
_GST_PLAY_STATE_BUFFERING = 1
_GST_PLAY_STATE_PAUSED = 2
_GST_PLAY_STATE_PLAYING = 3
_GST_RANK_NONE = 0
_GST_ELEMENT_FACTORY_TYPE_DECODER = 1 << 0
_GST_ELEMENT_FACTORY_TYPE_HARDWARE = 1 << 12
_GST_ELEMENT_FACTORY_TYPE_MEDIA_VIDEO = 1 << 49
_GST_HARDWARE_VIDEO_DECODER_TYPE = (
    _GST_ELEMENT_FACTORY_TYPE_DECODER
    | _GST_ELEMENT_FACTORY_TYPE_HARDWARE
    | _GST_ELEMENT_FACTORY_TYPE_MEDIA_VIDEO
)


@dataclass(frozen=True, slots=True)
class GStreamerPreviewConfig:
    runtime_root: Path
    decode_mode: PreviewDecodeMode = PreviewDecodeMode.AUTO
    registry_path: Path | None = None
    provenance: str | None = None
    expected_major: int = 1
    expected_minor: int = 28

    def __post_init__(self) -> None:
        if self.expected_major < 0 or self.expected_minor < 0:
            raise ValueError("expected GStreamer version values must be non-negative")


@dataclass(frozen=True, slots=True)
class _NativeEvent:
    state: int | None = None
    error: str | None = None
    missing_plugin: bool = False


class _GStreamerApi(Protocol):
    def version(self) -> tuple[int, int, int, int]: ...

    def create_player(self) -> object: ...

    def get_message_bus(self, player: object) -> object: ...

    def set_uri(self, player: object, uri: str) -> None: ...

    def play(self, player: object) -> None: ...

    def pause(self, player: object) -> None: ...

    def seek(self, player: object, position_ns: int) -> None: ...

    def position_ns(self, player: object) -> int | None: ...

    def stop(self, player: object) -> None: ...

    def hardware_video_decoder_features(self) -> tuple[str, ...]: ...

    def set_feature_rank(self, name: str, rank: int) -> int | None: ...

    def drain_events(self, bus: object) -> tuple[_NativeEvent, ...]: ...

    def release(self, player: object, bus: object) -> None: ...


ApiFactory = Callable[[Path], _GStreamerApi]


class _GError(ctypes.Structure):
    _fields_ = [
        ("domain", ctypes.c_uint32),
        ("code", ctypes.c_int),
        ("message", ctypes.c_char_p),
    ]


class _GList(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.c_void_p),
        ("next", ctypes.c_void_p),
        ("prev", ctypes.c_void_p),
    ]


class _CtypesGStreamerApi:
    def __init__(self, bin_dir: Path) -> None:
        self._gst = ctypes.CDLL(str(bin_dir / "gstreamer-1.0-0.dll"))
        self._play = ctypes.CDLL(str(bin_dir / "gstplay-1.0-0.dll"))
        self._gobject = ctypes.CDLL(str(bin_dir / "gobject-2.0-0.dll"))
        self._glib = ctypes.CDLL(str(bin_dir / "glib-2.0-0.dll"))
        self._bind()
        self._gst.gst_init(None, None)

    def _bind(self) -> None:
        self._gst.gst_init.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self._gst.gst_init.restype = None
        self._gst.gst_version.argtypes = [
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.c_uint),
        ]
        self._gst.gst_version.restype = None
        self._gst.gst_bus_set_flushing.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._gst.gst_bus_set_flushing.restype = None
        self._gst.gst_bus_pop.argtypes = [ctypes.c_void_p]
        self._gst.gst_bus_pop.restype = ctypes.c_void_p
        self._gst.gst_mini_object_unref.argtypes = [ctypes.c_void_p]
        self._gst.gst_mini_object_unref.restype = None
        self._gst.gst_element_factory_find.argtypes = [ctypes.c_char_p]
        self._gst.gst_element_factory_find.restype = ctypes.c_void_p
        self._gst.gst_element_factory_list_get_elements.argtypes = [ctypes.c_uint64, ctypes.c_uint]
        self._gst.gst_element_factory_list_get_elements.restype = ctypes.c_void_p
        self._gst.gst_plugin_feature_list_free.argtypes = [ctypes.c_void_p]
        self._gst.gst_plugin_feature_list_free.restype = None
        self._gst.gst_object_get_name.argtypes = [ctypes.c_void_p]
        self._gst.gst_object_get_name.restype = ctypes.c_void_p
        self._gst.gst_plugin_feature_get_rank.argtypes = [ctypes.c_void_p]
        self._gst.gst_plugin_feature_get_rank.restype = ctypes.c_uint
        self._gst.gst_plugin_feature_set_rank.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        self._gst.gst_plugin_feature_set_rank.restype = None

        self._play.gst_play_new.argtypes = [ctypes.c_void_p]
        self._play.gst_play_new.restype = ctypes.c_void_p
        self._play.gst_play_get_message_bus.argtypes = [ctypes.c_void_p]
        self._play.gst_play_get_message_bus.restype = ctypes.c_void_p
        self._play.gst_play_set_uri.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self._play.gst_play_set_uri.restype = None
        self._play.gst_play_play.argtypes = [ctypes.c_void_p]
        self._play.gst_play_play.restype = None
        self._play.gst_play_pause.argtypes = [ctypes.c_void_p]
        self._play.gst_play_pause.restype = None
        self._play.gst_play_seek.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
        self._play.gst_play_seek.restype = None
        self._play.gst_play_get_position.argtypes = [ctypes.c_void_p]
        self._play.gst_play_get_position.restype = ctypes.c_uint64
        self._play.gst_play_stop.argtypes = [ctypes.c_void_p]
        self._play.gst_play_stop.restype = None
        self._play.gst_play_message_parse_type.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
        ]
        self._play.gst_play_message_parse_type.restype = None
        self._play.gst_play_message_parse_state_changed.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
        ]
        self._play.gst_play_message_parse_state_changed.restype = None
        self._play.gst_play_message_parse_error_missing_plugin.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self._play.gst_play_message_parse_error_missing_plugin.restype = ctypes.c_int
        self._play.gst_play_message_parse_error.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_void_p,
        ]
        self._play.gst_play_message_parse_error.restype = None

        self._gobject.g_object_unref.argtypes = [ctypes.c_void_p]
        self._gobject.g_object_unref.restype = None
        self._glib.g_error_free.argtypes = [ctypes.c_void_p]
        self._glib.g_error_free.restype = None
        self._glib.g_free.argtypes = [ctypes.c_void_p]
        self._glib.g_free.restype = None

    def version(self) -> tuple[int, int, int, int]:
        major = ctypes.c_uint()
        minor = ctypes.c_uint()
        micro = ctypes.c_uint()
        nano = ctypes.c_uint()
        self._gst.gst_version(
            ctypes.byref(major),
            ctypes.byref(minor),
            ctypes.byref(micro),
            ctypes.byref(nano),
        )
        return major.value, minor.value, micro.value, nano.value

    def create_player(self) -> object:
        player = self._play.gst_play_new(None)
        if not player:
            raise RuntimeError("gst_play_new returned NULL")
        return player

    def get_message_bus(self, player: object) -> object:
        bus = self._play.gst_play_get_message_bus(player)
        if not bus:
            raise RuntimeError("gst_play_get_message_bus returned NULL")
        return bus

    def set_uri(self, player: object, uri: str) -> None:
        self._play.gst_play_set_uri(player, uri.encode("utf-8"))

    def play(self, player: object) -> None:
        self._play.gst_play_play(player)

    def pause(self, player: object) -> None:
        self._play.gst_play_pause(player)

    def seek(self, player: object, position_ns: int) -> None:
        self._play.gst_play_seek(player, position_ns)

    def position_ns(self, player: object) -> int | None:
        position = int(self._play.gst_play_get_position(player))
        return None if position == _GST_CLOCK_TIME_NONE else position

    def stop(self, player: object) -> None:
        self._play.gst_play_stop(player)

    def hardware_video_decoder_features(self) -> tuple[str, ...]:
        list_pointer = self._gst.gst_element_factory_list_get_elements(
            _GST_HARDWARE_VIDEO_DECODER_TYPE,
            _GST_RANK_NONE,
        )
        if not list_pointer:
            return ()
        names: list[str] = []
        node_pointer = list_pointer
        try:
            while node_pointer:
                node = ctypes.cast(node_pointer, ctypes.POINTER(_GList)).contents
                if node.data:
                    name_pointer = self._gst.gst_object_get_name(node.data)
                    if name_pointer:
                        try:
                            names.append(
                                ctypes.string_at(name_pointer).decode("utf-8", errors="replace")
                            )
                        finally:
                            self._glib.g_free(name_pointer)
                node_pointer = node.next
        finally:
            self._gst.gst_plugin_feature_list_free(list_pointer)
        return tuple(sorted(set(names)))

    def set_feature_rank(self, name: str, rank: int) -> int | None:
        feature = self._gst.gst_element_factory_find(name.encode("ascii"))
        if not feature:
            return None
        try:
            previous = int(self._gst.gst_plugin_feature_get_rank(feature))
            self._gst.gst_plugin_feature_set_rank(feature, rank)
            return previous
        finally:
            self._gobject.g_object_unref(feature)

    def drain_events(self, bus: object) -> tuple[_NativeEvent, ...]:
        events: list[_NativeEvent] = []
        while True:
            message = self._gst.gst_bus_pop(bus)
            if not message:
                return tuple(events)
            try:
                message_type = ctypes.c_int()
                self._play.gst_play_message_parse_type(message, ctypes.byref(message_type))
                if message_type.value == _GST_PLAY_MESSAGE_STATE_CHANGED:
                    state = ctypes.c_int()
                    self._play.gst_play_message_parse_state_changed(message, ctypes.byref(state))
                    events.append(_NativeEvent(state=state.value))
                elif message_type.value == _GST_PLAY_MESSAGE_ERROR:
                    missing = bool(
                        self._play.gst_play_message_parse_error_missing_plugin(message, None, None)
                    )
                    error_pointer = ctypes.c_void_p()
                    self._play.gst_play_message_parse_error(
                        message, ctypes.byref(error_pointer), None
                    )
                    text = "GStreamer playback reported an error"
                    if error_pointer.value:
                        try:
                            error = ctypes.cast(error_pointer, ctypes.POINTER(_GError)).contents
                            if error.message:
                                text = error.message.decode("utf-8", errors="replace")
                        finally:
                            self._glib.g_error_free(error_pointer)
                    events.append(_NativeEvent(error=text, missing_plugin=missing))
            finally:
                self._gst.gst_mini_object_unref(message)

    def release(self, player: object, bus: object) -> None:
        self._gst.gst_bus_set_flushing(bus, 1)
        self._gobject.g_object_unref(bus)
        self._gobject.g_object_unref(player)


def _default_api_factory(bin_dir: Path) -> _GStreamerApi:
    return _CtypesGStreamerApi(bin_dir)


class GStreamerPreviewBackend(PreviewBackend):
    """Thin GstPlay adapter with no EDL/editorial mutation authority."""

    def __init__(
        self,
        config: GStreamerPreviewConfig,
        *,
        api_factory: ApiFactory = _default_api_factory,
        environment: MutableMapping[str, str] | None = None,
        platform_name: str = os.name,
    ) -> None:
        self._config = config
        self._api_factory = api_factory
        self._environment = os.environ if environment is None else environment
        self._platform_name = platform_name
        self._api: _GStreamerApi | None = None
        self._player: object | None = None
        self._bus: object | None = None
        self._state = PreviewPlaybackState.NEW
        self._runtime_version: str | None = None
        self._media_path: Path | None = None
        self._diagnostics: tuple[PreviewDiagnostic, ...] = ()
        self._disabled_features: tuple[str, ...] = ()
        self._saved_feature_ranks: dict[str, int] = {}
        self._saved_environment: dict[str, str | None] = {}

    def initialize(self) -> PreviewStatus:
        if self._state is PreviewPlaybackState.RELEASED:
            return self._failure(
                PreviewDiagnosticCode.RELEASED,
                "Preview backend has already been released",
            )
        if self._api is not None and self._player is not None and self._bus is not None:
            return self.status()
        if self._platform_name != "nt":
            return self._failure(
                PreviewDiagnosticCode.RUNTIME_INVALID,
                "Stage-A GStreamer Preview adapter currently requires Windows",
            )

        root = self._config.runtime_root.expanduser().resolve()
        bin_dir = root / "bin"
        plugin_dir = root / "lib" / "gstreamer-1.0"
        required = (
            bin_dir / "gstreamer-1.0-0.dll",
            bin_dir / "gstplay-1.0-0.dll",
            bin_dir / "gobject-2.0-0.dll",
            bin_dir / "glib-2.0-0.dll",
        )
        if not root.is_dir():
            return self._failure(
                PreviewDiagnosticCode.RUNTIME_NOT_FOUND,
                f"GStreamer private runtime does not exist: {root}",
            )
        missing = tuple(path.name for path in required if not path.is_file())
        if missing or not plugin_dir.is_dir():
            detail = ", ".join(missing) if missing else "lib/gstreamer-1.0"
            return self._failure(
                PreviewDiagnosticCode.RUNTIME_INVALID,
                f"GStreamer private runtime is missing required components: {detail}",
            )

        registry_path = self._config.registry_path
        if registry_path is None:
            registry_path = root.parent / "registry" / "gstreamer-1.0.bin"
        registry_path = registry_path.expanduser().resolve()
        registry_path.parent.mkdir(parents=True, exist_ok=True)

        self._configure_environment(bin_dir, plugin_dir, registry_path)
        try:
            api = self._api_factory(bin_dir)
            version = api.version()
            if version[:2] != (self._config.expected_major, self._config.expected_minor):
                self._restore_environment()
                return self._failure(
                    PreviewDiagnosticCode.RUNTIME_INVALID,
                    "GStreamer runtime version "
                    f"{version[0]}.{version[1]}.{version[2]}.{version[3]} "
                    "does not match expected "
                    f"{self._config.expected_major}.{self._config.expected_minor}.x",
                )

            self._api = api
            self._runtime_version = ".".join(str(value) for value in version)
            if self._config.decode_mode is PreviewDecodeMode.SOFTWARE_VIDEO:
                disabled: list[str] = []
                for feature in api.hardware_video_decoder_features():
                    previous = api.set_feature_rank(feature, _GST_RANK_NONE)
                    if previous is not None:
                        self._saved_feature_ranks[feature] = previous
                        disabled.append(feature)
                self._disabled_features = tuple(disabled)

            player = api.create_player()
            self._player = player
            bus = api.get_message_bus(player)
            self._bus = bus
            self._state = PreviewPlaybackState.READY
            self._diagnostics = ()
            return self.status()
        except (AttributeError, OSError, RuntimeError) as error:
            self._release_native()
            self._restore_environment()
            return self._failure(
                PreviewDiagnosticCode.LIBRARY_LOAD_FAILED,
                f"GStreamer private runtime initialization failed: {error}",
            )

    def load(self, path: Path) -> PreviewStatus:
        if not self._require_active():
            return self.status()
        resolved = path.expanduser().resolve()
        if not resolved.exists():
            return self._operation_failure(
                PreviewDiagnosticCode.MEDIA_NOT_FOUND,
                f"Preview media does not exist: {resolved}",
            )
        if not resolved.is_file():
            return self._operation_failure(
                PreviewDiagnosticCode.MEDIA_NOT_LOCAL_FILE,
                f"Preview media must be a local file: {resolved}",
            )
        assert self._api is not None
        assert self._player is not None
        try:
            self._api.set_uri(self._player, resolved.as_uri())
        except (OSError, RuntimeError) as error:
            return self._operation_failure(
                PreviewDiagnosticCode.BACKEND_FAILURE,
                f"GStreamer failed to load local media: {error}",
            )
        self._media_path = resolved
        self._state = PreviewPlaybackState.LOADED
        self._diagnostics = ()
        return self.status()

    def play(self) -> PreviewStatus:
        if not self._require_media():
            return self.status()
        assert self._api is not None
        assert self._player is not None
        try:
            self._api.play(self._player)
        except (OSError, RuntimeError) as error:
            return self._operation_failure(
                PreviewDiagnosticCode.PLAYBACK_FAILED,
                f"GStreamer play request failed: {error}",
            )
        self._state = PreviewPlaybackState.PLAYING
        self._diagnostics = ()
        return self.status()

    def pause(self) -> PreviewStatus:
        if not self._require_media():
            return self.status()
        assert self._api is not None
        assert self._player is not None
        try:
            self._api.pause(self._player)
        except (OSError, RuntimeError) as error:
            return self._operation_failure(
                PreviewDiagnosticCode.PLAYBACK_FAILED,
                f"GStreamer pause request failed: {error}",
            )
        self._state = PreviewPlaybackState.PAUSED
        self._diagnostics = ()
        return self.status()

    def seek(self, position: MediaTime) -> PreviewStatus:
        if not self._require_media():
            return self.status()
        if position.value < 0:
            return self._operation_failure(
                PreviewDiagnosticCode.INVALID_SEEK,
                "Preview seek position must be non-negative",
            )
        nanoseconds = position.as_fraction() * 1_000_000_000
        if nanoseconds.denominator != 1:
            return self._operation_failure(
                PreviewDiagnosticCode.INVALID_SEEK,
                "Preview seek position must be exactly representable in nanoseconds",
            )
        assert self._api is not None
        assert self._player is not None
        try:
            self._api.seek(self._player, nanoseconds.numerator)
        except (OSError, RuntimeError) as error:
            return self._operation_failure(
                PreviewDiagnosticCode.PLAYBACK_FAILED,
                f"GStreamer absolute seek failed: {error}",
            )
        self._diagnostics = ()
        return self.status()

    def stop(self) -> PreviewStatus:
        if not self._require_active():
            return self.status()
        assert self._api is not None
        assert self._player is not None
        try:
            self._api.stop(self._player)
        except (OSError, RuntimeError) as error:
            return self._operation_failure(
                PreviewDiagnosticCode.PLAYBACK_FAILED,
                f"GStreamer stop request failed: {error}",
            )
        self._state = PreviewPlaybackState.STOPPED
        self._diagnostics = ()
        return self.status()

    def status(self) -> PreviewStatus:
        self._drain_events()
        position = self._position()
        return PreviewStatus(
            backend="gstreamer",
            state=self._state,
            decode_mode=self._config.decode_mode,
            runtime_root=self._config.runtime_root.expanduser().resolve(),
            runtime_version=self._runtime_version,
            runtime_provenance=self._config.provenance,
            media_path=self._media_path,
            position=position,
            disabled_hardware_features=self._disabled_features,
            diagnostics=self._diagnostics,
        )

    def release(self) -> PreviewStatus:
        if self._state is PreviewPlaybackState.RELEASED:
            return self.status()
        self._release_native()
        self._restore_environment()
        self._state = PreviewPlaybackState.RELEASED
        self._media_path = None
        self._diagnostics = ()
        return self.status()

    def _require_active(self) -> bool:
        if self._state is PreviewPlaybackState.RELEASED:
            self._diagnostics = (
                PreviewDiagnostic(
                    PreviewDiagnosticCode.RELEASED,
                    "Preview backend has already been released",
                ),
            )
            return False
        if self._api is None or self._player is None or self._bus is None:
            self._diagnostics = (
                PreviewDiagnostic(
                    PreviewDiagnosticCode.NOT_INITIALIZED,
                    "Preview backend must be initialized before use",
                ),
            )
            return False
        return True

    def _require_media(self) -> bool:
        if not self._require_active():
            return False
        if self._media_path is None:
            self._diagnostics = (
                PreviewDiagnostic(
                    PreviewDiagnosticCode.NO_MEDIA_LOADED,
                    "Preview media must be loaded before playback control",
                ),
            )
            return False
        return True

    def _drain_events(self) -> None:
        if self._api is None or self._bus is None:
            return
        try:
            events = self._api.drain_events(self._bus)
        except (OSError, RuntimeError) as error:
            self._state = PreviewPlaybackState.FAILED
            self._diagnostics = (
                PreviewDiagnostic(
                    PreviewDiagnosticCode.BACKEND_FAILURE,
                    f"GStreamer diagnostic bus failed: {error}",
                    True,
                ),
            )
            return
        for event in events:
            if event.error is not None:
                code = (
                    PreviewDiagnosticCode.MISSING_PLUGIN
                    if event.missing_plugin
                    else PreviewDiagnosticCode.PLAYBACK_FAILED
                )
                self._state = PreviewPlaybackState.FAILED
                self._diagnostics = (PreviewDiagnostic(code, event.error),)
                continue
            if event.state is not None:
                mapped = {
                    _GST_PLAY_STATE_STOPPED: PreviewPlaybackState.STOPPED,
                    _GST_PLAY_STATE_BUFFERING: PreviewPlaybackState.BUFFERING,
                    _GST_PLAY_STATE_PAUSED: PreviewPlaybackState.PAUSED,
                    _GST_PLAY_STATE_PLAYING: PreviewPlaybackState.PLAYING,
                }.get(event.state)
                if mapped is not None:
                    self._state = mapped

    def _position(self) -> MediaTime | None:
        if self._api is None or self._player is None:
            return None
        if self._state in {
            PreviewPlaybackState.NEW,
            PreviewPlaybackState.READY,
            PreviewPlaybackState.RELEASED,
        }:
            return None
        try:
            position = self._api.position_ns(self._player)
        except (OSError, RuntimeError):
            return None
        return None if position is None else MediaTime(position, 1_000_000_000)

    def _release_native(self) -> None:
        api = self._api
        if api is None:
            return
        for name, rank in self._saved_feature_ranks.items():
            try:
                api.set_feature_rank(name, rank)
            except (OSError, RuntimeError):
                pass
        self._saved_feature_ranks.clear()
        player, bus = self._player, self._bus
        self._player = None
        self._bus = None
        if player is not None and bus is not None:
            try:
                api.stop(player)
            except (OSError, RuntimeError):
                pass
            try:
                api.release(player, bus)
            except (OSError, RuntimeError):
                pass
        self._api = None

    def _configure_environment(self, bin_dir: Path, plugin_dir: Path, registry_path: Path) -> None:
        changes = {
            "PATH": str(bin_dir) + os.pathsep + self._environment.get("PATH", ""),
            "GST_PLUGIN_SYSTEM_PATH_1_0": str(plugin_dir),
            "GST_PLUGIN_PATH_1_0": "",
            "GST_REGISTRY_1_0": str(registry_path),
        }
        for key, value in changes.items():
            if key not in self._saved_environment:
                self._saved_environment[key] = self._environment.get(key)
            self._environment[key] = value

    def _restore_environment(self) -> None:
        for key, previous in self._saved_environment.items():
            if previous is None:
                self._environment.pop(key, None)
            else:
                self._environment[key] = previous
        self._saved_environment.clear()

    def _failure(self, code: PreviewDiagnosticCode, message: str) -> PreviewStatus:
        self._state = PreviewPlaybackState.FAILED
        self._diagnostics = (PreviewDiagnostic(code, message),)
        return self.status()

    def _operation_failure(self, code: PreviewDiagnosticCode, message: str) -> PreviewStatus:
        self._diagnostics = (PreviewDiagnostic(code, message),)
        return self.status()
