from __future__ import annotations

import hashlib
from pathlib import Path

from video_editing_agent.adapters.bootstrap.resource_locator import (
    ResourceRuntimeLocator,
    RuntimeLayout,
)
from video_editing_agent.adapters.bootstrap.runtime_manifest import InclusionPolicy
from video_editing_agent.application.ports.environment_doctor import (
    CapabilityStatus,
    EnvironmentCapabilityCheck,
    ProductCapability,
)


class RuntimeManifestProbe:
    """Read-only packaging foundation probe; it neither installs nor selects providers."""

    def __init__(self, locator: ResourceRuntimeLocator) -> None:
        self._locator = locator

    def probe(self) -> tuple[EnvironmentCapabilityCheck, ...]:
        return tuple(self._check(item.component_id) for item in self._locator.manifest.components)

    def _check(self, component_id: str) -> EnvironmentCapabilityCheck:
        component = self._locator.manifest.component(component_id)
        assert component is not None
        path = self._locator.existing_component_path(component_id)
        evidence = [
            f"kind={component.kind.value}",
            f"classification={component.classification.value}",
            f"inclusion={component.inclusion.value}",
            f"declared_version={component.version}",
        ]
        capability = _capability(component.capability)
        if component.inclusion is InclusionPolicy.EXCLUDE:
            return EnvironmentCapabilityCheck(
                capability,
                f"runtime_manifest:{component_id}",
                CapabilityStatus.READY,
                "Component is explicitly excluded from the packaged payload",
                tuple(evidence),
            )
        if (
            self._locator.layout is RuntimeLayout.DEVELOPMENT
            and component.inclusion is InclusionPolicy.INCLUDE
        ):
            return EnvironmentCapabilityCheck(
                capability,
                f"runtime_manifest:{component_id}",
                CapabilityStatus.READY,
                "Component is supplied by the explicit development runtime",
                tuple(evidence + ["resolution=development-runtime"]),
            )
        if path is None:
            status = (
                CapabilityStatus.UNAVAILABLE
                if component.absence_fatal
                else CapabilityStatus.AVAILABLE_AFTER_INSTALL
            )
            return EnvironmentCapabilityCheck(
                capability,
                f"runtime_manifest:{component_id}",
                status,
                "Required runtime component is missing"
                if component.absence_fatal
                else "Optional runtime component is not installed",
                tuple(evidence),
                "Restore this component from the product-approved runtime distribution.",
            )
        evidence.append(f"path={path}")
        if component.sha256 is not None:
            actual = _sha256(path)
            evidence.append(f"sha256_match={str(actual == component.sha256).lower()}")
            if actual != component.sha256:
                return EnvironmentCapabilityCheck(
                    capability,
                    f"runtime_manifest:{component_id}",
                    CapabilityStatus.UNAVAILABLE,
                    "Runtime component integrity check failed",
                    tuple(evidence),
                    "Restore this component from the product-approved runtime distribution.",
                )
        return EnvironmentCapabilityCheck(
            capability,
            f"runtime_manifest:{component_id}",
            CapabilityStatus.READY,
            "Runtime component is present and satisfies its manifest declaration",
            tuple(evidence),
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _capability(value: str) -> ProductCapability:
    mapping = {
        "media-probe-render": ProductCapability.MEDIA_PROBE_RENDER,
        "shot-detection": ProductCapability.SHOT_DETECTION,
        "speech-recognition": ProductCapability.SPEECH_RECOGNITION,
        "install-resources": ProductCapability.INSTALL_RESOURCES,
    }
    return mapping.get(value, ProductCapability.HOST_RUNTIME)
