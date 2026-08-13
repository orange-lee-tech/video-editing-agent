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
    def __init__(self, model_id: str = "fake", revision: str = "r1") -> None:
        self.model_id = model_id
        self.revision = revision

    def embed(self, request: TextEmbeddingRequest) -> TextEmbeddingResult:
        vectors = tuple((1.0, 0.0) if "match" in text else (0.0, 1.0) for text in request.texts)
        return TextEmbeddingResult(self.model_id, self.revision, 2, vectors)


def _index(tmp_path, port):
    root = tmp_path / "artifacts"
    return DenseShotIndex(
        embedding_port=port,
        artifact_store=LocalArtifactStore(root),
        artifact_lifecycle_repository=LocalArtifactLifecycleRepository(root),
    )


def _source(shot: str, analysis: int, kind: str, source: int, text: str = "match"):
    source_kind = "shot_analysis" if kind == "visual_semantic_text" else "speech_transcript"
    return DenseRepresentationSource(
        EntityRevisionRef(shot, 1), analysis, kind, source_kind, source, text
    )


def test_projection_separates_analysis_and_transcript_revisions() -> None:
    ref = EntityRevisionRef("sht_1", 3)
    analysis = ShotAnalysis(
        ref,
        4,
        AnalysisProfile.SEMANTIC,
        datetime.now(UTC),
        visual=VisualSemantics(summary="summary"),
    )
    segment = SpeechSegment("spoken", MediaTimeRange(MediaTime(1, 1), MediaTime(1, 1)))
    transcript = SpeechTranscript(
        ref, 7, datetime.now(UTC), "provider", "r1", "spoken", segments=(segment,)
    )
    assert visual_semantic_source(analysis) == DenseRepresentationSource(
        ref, 4, "visual_semantic_text", "shot_analysis", 4, "summary"
    )
    assert speech_text_source(analysis, transcript) == DenseRepresentationSource(
        ref, 4, "speech_text", "speech_transcript", 7, "spoken"
    )


def test_candidates_keep_analysis_revision_and_restore_all_provenance(tmp_path) -> None:
    port = Embeddings()
    index = _index(tmp_path, port)
    records = index.rebuild(
        (_source("sht_b", 2, "visual_semantic_text", 2), _source("sht_a", 3, "speech_text", 8))
    )
    speech = index.search("match", representation="speech_text")[0]
    assert speech.analysis_revision == 3
    assert (
        next(x for x in records if x.descriptor.representation == "speech_text").source_revision
        == 8
    )
    reopened = _index(tmp_path, port)
    assert reopened.restore(tuple(x.artifact_id for x in records)) == records


def test_selective_refresh_and_invalidation_preserve_unrelated_artifacts(tmp_path) -> None:
    index = _index(tmp_path, Embeddings())
    original = index.rebuild(
        (_source("sht", 2, "visual_semantic_text", 2), _source("sht", 2, "speech_text", 7))
    )
    by_kind = {x.descriptor.representation: x for x in original}
    refreshed_speech = index.upsert(_source("sht", 2, "speech_text", 8, "new match"))
    assert refreshed_speech.artifact_id != by_kind["speech_text"].artifact_id
    assert (
        index._records[(EntityRevisionRef("sht", 1), "visual_semantic_text")].artifact_id
        == by_kind["visual_semantic_text"].artifact_id
    )
    refreshed_visual = index.upsert(_source("sht", 3, "visual_semantic_text", 3, "visual match"))
    assert refreshed_visual.descriptor.analysis_revision == 3
    assert (
        index._records[(EntityRevisionRef("sht", 1), "speech_text")].artifact_id
        == refreshed_speech.artifact_id
    )
    assert index.invalidate(EntityRevisionRef("sht", 1), "speech_text")
    assert index.search("match", representation="speech_text") == ()


def test_duplicate_identity_and_stale_model_fail_closed(tmp_path) -> None:
    port = Embeddings()
    index = _index(tmp_path, port)
    source = _source("sht", 1, "visual_semantic_text", 1)
    with pytest.raises(ValueError, match="duplicate"):
        index.rebuild((source, source))
    index.rebuild((source,))
    port.model_id = "other"
    with pytest.raises(ValueError, match="provenance mismatch"):
        index.search("match", representation="visual_semantic_text")


def test_provider_reports_configured_identity() -> None:
    class Model:
        def encode(self, texts, **kwargs):
            return ((1.0, 0.0),) * len(texts)

    port = SentenceTransformersTextEmbeddingPort(
        SentenceTransformersConfig("path", "configured/model", "revision", 2),
        model_factory=Model,
    )
    result = port.embed(TextEmbeddingRequest(("text",), EmbeddingIntent.DOCUMENT))
    assert (result.model_id, result.model_revision) == ("configured/model", "revision")


def test_optional_embedding_runtime_absence_is_clean(monkeypatch) -> None:
    def missing(package):
        raise importlib.metadata.PackageNotFoundError(package)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    port = SentenceTransformersTextEmbeddingPort(
        SentenceTransformersConfig("unused", "model", "revision")
    )
    with pytest.raises(SentenceTransformersUnavailableError, match="unavailable"):
        port.embed(TextEmbeddingRequest(("text",), EmbeddingIntent.DOCUMENT))
