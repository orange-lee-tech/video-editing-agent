from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class CapabilityStatus(StrEnum):
    READY = "ready"
    AVAILABLE_AFTER_INSTALL = "available_after_install"
    AVAILABLE_BUT_SLOW = "available_but_slow"
    HARDWARE_BLOCKED = "hardware_blocked"
    CLOUD_FALLBACK = "cloud_fallback"
    UNAVAILABLE = "unavailable"


class ProductCapability(StrEnum):
    HOST_RUNTIME = "host_runtime"
    MEDIA_PROBE_RENDER = "media_probe_render"
    PREVIEW_PLAYBACK = "preview_playback"
    PLANNING_CLOUD = "planning_cloud"
    EDITING_CLOUD_DIRECTOR = "editing_cloud_director"
    VISUAL_UNDERSTANDING = "visual_understanding"
    OPTIONAL_LOCAL_ACCELERATION = "optional_local_acceleration"
    SHOT_DETECTION = "shot_detection"
    SPEECH_RECOGNITION = "speech_recognition"
    INSTALL_RESOURCES = "install_resources"
    WORKSPACE_STORAGE = "workspace_storage"


@dataclass(frozen=True, slots=True)
class EnvironmentCapabilityCheck:
    capability: ProductCapability
    component: str
    status: CapabilityStatus
    summary: str
    evidence: tuple[str, ...] = ()
    repair_guidance: str | None = None

    def __post_init__(self) -> None:
        if not self.component.strip():
            raise ValueError("component must not be empty")
        if not self.summary.strip():
            raise ValueError("summary must not be empty")
        if self.repair_guidance is not None and not self.repair_guidance.strip():
            raise ValueError("repair_guidance must not be empty when present")


@dataclass(frozen=True, slots=True)
class EnvironmentReport:
    checks: tuple[EnvironmentCapabilityCheck, ...]

    def for_capability(
        self, capability: ProductCapability
    ) -> tuple[EnvironmentCapabilityCheck, ...]:
        return tuple(item for item in self.checks if item.capability is capability)


class EnvironmentProbe(Protocol):
    """Inspect machine/runtime facts only; no creative-state mutation authority."""

    def probe(self) -> tuple[EnvironmentCapabilityCheck, ...]: ...
