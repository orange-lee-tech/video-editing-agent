from __future__ import annotations

import json
import os
import pathlib
import tempfile
from typing import Any

from video_editing_agent.application.ports.artifact_lifecycle import (
    ArtifactLifecycleDescriptor,
    ArtifactRetentionClass,
)


class LocalArtifactLifecycleRepository:
    """Atomic JSON metadata registry kept beside, but separate from, artifact binary identity."""

    def __init__(self, root: pathlib.Path) -> None:
        self._root = root.expanduser().resolve() / "lifecycle"
        self._root.mkdir(parents=True, exist_ok=True)

    def _path_for_artifact(self, artifact_id: str) -> pathlib.Path:
        if not artifact_id.startswith("art_sha256_"):
            raise ValueError("artifact_id must use the art_sha256_* content-addressed form")
        return self._root / f"{artifact_id}.json"

    @staticmethod
    def _payload(descriptor: ArtifactLifecycleDescriptor) -> dict[str, object]:
        return {
            "artifact_id": descriptor.artifact_id,
            "retention_class": descriptor.retention_class.value,
            "purpose": descriptor.purpose,
            "source_refs": list(descriptor.source_refs),
        }

    @staticmethod
    def _from_payload(value: dict[str, Any]) -> ArtifactLifecycleDescriptor:
        source_refs = value.get("source_refs", [])
        if not isinstance(source_refs, list):
            raise RuntimeError("artifact lifecycle source_refs must be a list")
        return ArtifactLifecycleDescriptor(
            artifact_id=str(value["artifact_id"]),
            retention_class=ArtifactRetentionClass(str(value["retention_class"])),
            purpose=str(value["purpose"]),
            source_refs=tuple(str(item) for item in source_refs),
        )

    def list_for_artifact(self, artifact_id: str) -> tuple[ArtifactLifecycleDescriptor, ...]:
        path = self._path_for_artifact(artifact_id)
        if not path.exists():
            return ()
        try:
            root = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"invalid artifact lifecycle metadata: {path}") from exc
        if not isinstance(root, list):
            raise RuntimeError("artifact lifecycle metadata root must be a list")
        descriptors = tuple(self._from_payload(item) for item in root if isinstance(item, dict))
        if len(descriptors) != len(root):
            raise RuntimeError("artifact lifecycle metadata entries must be objects")
        if any(descriptor.artifact_id != artifact_id for descriptor in descriptors):
            raise RuntimeError("artifact lifecycle metadata identity mismatch")
        return descriptors

    def _write(
        self,
        artifact_id: str,
        descriptors: tuple[ArtifactLifecycleDescriptor, ...],
    ) -> None:
        path = self._path_for_artifact(artifact_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            [self._payload(item) for item in descriptors],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{artifact_id}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = pathlib.Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)

    def add(self, descriptor: ArtifactLifecycleDescriptor) -> None:
        existing = self.list_for_artifact(descriptor.artifact_id)
        if descriptor in existing:
            return
        self._write(descriptor.artifact_id, (*existing, descriptor))

    def remove_all_for_artifact(self, artifact_id: str) -> None:
        self._path_for_artifact(artifact_id).unlink(missing_ok=True)
