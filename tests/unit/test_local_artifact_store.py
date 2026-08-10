import hashlib
from pathlib import Path

import pytest

from video_editing_agent.application.ports.artifact_store import ArtifactPayload
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore


def test_local_store_is_content_addressed_and_deduplicates(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts")
    payload = ArtifactPayload(media_type="image/png", content=b"png-payload")

    first = store.put(payload)
    second = store.put(payload)

    digest = hashlib.sha256(payload.content).hexdigest()
    assert first == second
    assert first.artifact_id == f"art_sha256_{digest}"
    assert first.content_hash == f"sha256:{digest}"
    assert store.get(first) == payload.content


def test_local_store_detects_tampered_content(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    store = LocalArtifactStore(root)
    ref = store.put(ArtifactPayload(media_type="image/png", content=b"original"))
    digest = ref.content_hash.removeprefix("sha256:")
    stored_path = root / "sha256" / digest[:2] / digest
    stored_path.write_bytes(b"tampered")

    with pytest.raises(RuntimeError, match="integrity"):
        store.get(ref)
