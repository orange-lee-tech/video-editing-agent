from __future__ import annotations

import importlib.metadata
from datetime import UTC, datetime

import pytest

from video_editing_agent.application.ports.text_embedding import (
    EmbeddingIntent,
    TextEmbeddingRequest,
    TextEmbeddingResult,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.speech import SpeechSegment, SpeechTranscript
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis, VisualSemantics
from video_editing_agent.media.indexing.dense import (
    DenseRepresentationSource,
    DenseShotIndex,
    speech_text_source,
    visual_semantic_source,
)
from video_editing_agent.providers.embedding.sentence_transformers import (
    SentenceTransformersConfig,
    SentenceTransformersTextEmbeddingPort,
    SentenceTransformersUnavailableError,
)
from video_editing_agent.storage.artifact.lifecycle_repository import (
    LocalArtifactLifecycleRepository,
)
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore


class Embeddings:
    def __init__(self, revision: str = "r1") -> None:
        self.revision = revision
        self.intents: list[EmbeddingIntent] = []

    def embed(self, request: TextEmbeddingRequest) -> TextEmbeddingResult:
        self.intents.append(request.intent)
        vectors = tuple((1.0, 0.0) if "match" in text else (0.0, 1.0) for text in request.texts)
        return TextEmbeddingResult("fake", self.revision, 2, vectors)


def _index(tmp_path, port):
    root = tmp_path / "artifacts"
    return DenseShotIndex(
        embedding_port=port,
        artifact_store=LocalArtifactStore(root),
        artifact_lifecycle_repository=LocalArtifactLifecycleRepository(root),
    )


def test_projection_uses_current_visual_and_persisted_speech_revisions() -> None:
    ref = EntityRevisionRef("sht_1", 3)
    analysis = ShotAnalysis(
        ref,
        4,
        AnalysisProfile.SEMANTIC,
        datetime.now(UTC),
        visual=VisualSemantics(summary="summary", tags=("tag",), actions=("action",)),
    )
    segment = SpeechSegment("spoken", MediaTimeRange(MediaTime(1, 1), MediaTime(1, 1)))
    transcript = SpeechTranscript(
        ref, 7, datetime.now(UTC), "provider", "r1", "spoken", segments=(segment,)
    )
    assert visual_semantic_source(analysis) == DenseRepresentationSource(
        ref, "visual_semantic_text", 4, "summary\ntag\naction"
    )
    assert speech_text_source(transcript) == DenseRepresentationSource(
        ref, "speech_text", 7, "spoken"
    )


def test_dense_index_persists_restores_and_orders_ties(tmp_path) -> None:
    port = Embeddings()
    index = _index(tmp_path, port)
    records = index.rebuild(
        tuple(
            DenseRepresentationSource(
                EntityRevisionRef(shot, 1), "visual_semantic_text", 2, "match"
            )
            for shot in ("sht_b", "sht_a")
        )
    )
    assert [
        x.shot_ref.entity_id for x in index.search("match", representation="visual_semantic_text")
    ] == ["sht_a", "sht_b"]
    assert port.intents == [EmbeddingIntent.DOCUMENT, EmbeddingIntent.QUERY]
    reopened = _index(tmp_path, port)
    assert reopened.restore(tuple(x.artifact_id for x in records)) == records
    assert reopened.search("match", representation="visual_semantic_text") == index.search(
        "match", representation="visual_semantic_text"
    )


def test_model_revision_mismatch_fails_closed(tmp_path) -> None:
    port = Embeddings()
    index = _index(tmp_path, port)
    index.rebuild(
        (DenseRepresentationSource(EntityRevisionRef("sht", 1), "speech_text", 2, "match"),)
    )
    port.revision = "r2"
    with pytest.raises(ValueError, match="provenance mismatch"):
        index.search("match", representation="speech_text")


def test_optional_embedding_runtime_absence_is_clean(monkeypatch) -> None:
    def missing(package):
        raise importlib.metadata.PackageNotFoundError(package)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    port = SentenceTransformersTextEmbeddingPort(SentenceTransformersConfig("unused", "revision"))
    with pytest.raises(SentenceTransformersUnavailableError, match="unavailable"):
        port.embed(TextEmbeddingRequest(("text",), EmbeddingIntent.DOCUMENT))
