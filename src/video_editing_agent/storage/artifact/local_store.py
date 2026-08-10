from __future__ import annotations

import hashlib
import os
import pathlib
import tempfile

from video_editing_agent.application.ports.artifact_store import (
    ArtifactPayload,
    StoredArtifactRef,
)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class LocalArtifactStore:
    """Local content-addressed artifact storage; filesystem paths are not artifact identity."""

    def __init__(self, root: pathlib.Path) -> None:
        self._root = root.expanduser().resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def _path_for_digest(self, digest: str) -> pathlib.Path:
        return self._root / "sha256" / digest[:2] / digest

    def put(self, payload: ArtifactPayload) -> StoredArtifactRef:
        digest = _sha256(payload.content)
        ref = StoredArtifactRef(
            artifact_id=f"art_sha256_{digest}",
            content_hash=f"sha256:{digest}",
            media_type=payload.media_type,
            byte_size=len(payload.content),
        )
        destination = self._path_for_digest(digest)
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            existing = destination.read_bytes()
            if existing != payload.content:
                raise RuntimeError(
                    "artifact content-address collision or store corruption detected"
                )
            return ref

        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            prefix=f".{digest}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = pathlib.Path(stream.name)
            stream.write(payload.content)
            stream.flush()
            os.fsync(stream.fileno())

        try:
            os.replace(temporary_path, destination)
        finally:
            temporary_path.unlink(missing_ok=True)
        return ref

    def get(self, ref: StoredArtifactRef) -> bytes:
        digest = ref.content_hash.removeprefix("sha256:")
        expected_artifact_id = f"art_sha256_{digest}"
        if ref.artifact_id != expected_artifact_id:
            raise ValueError("artifact_id does not match content_hash")

        path = self._path_for_digest(digest)
        content = path.read_bytes()
        actual_digest = _sha256(content)
        if actual_digest != digest or len(content) != ref.byte_size:
            raise RuntimeError("stored artifact failed integrity verification")
        return content
