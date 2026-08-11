from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ArtifactPayload:
    media_type: str
    content: bytes

    def __post_init__(self) -> None:
        if not self.media_type.strip():
            raise ValueError("media_type must not be empty")
        if not self.content:
            raise ValueError("artifact content must not be empty")


@dataclass(frozen=True, slots=True)
class StoredArtifactRef:
    artifact_id: str
    content_hash: str
    media_type: str
    byte_size: int

    def __post_init__(self) -> None:
        if not self.artifact_id.startswith("art_sha256_"):
            raise ValueError("artifact_id must use the art_sha256_* content-addressed form")
        if not self.content_hash.startswith("sha256:"):
            raise ValueError("content_hash must use the sha256:* form")
        if not self.media_type.strip():
            raise ValueError("media_type must not be empty")
        if isinstance(self.byte_size, bool) or not isinstance(self.byte_size, int):
            raise TypeError("byte_size must be an int")
        if self.byte_size <= 0:
            raise ValueError("byte_size must be > 0")


class ArtifactStore(Protocol):
    """Persist non-domain binary artifacts behind opaque content-addressed references."""

    def put(self, payload: ArtifactPayload) -> StoredArtifactRef: ...

    def get(self, ref: StoredArtifactRef) -> bytes: ...

    def delete(self, ref: StoredArtifactRef) -> bool: ...
