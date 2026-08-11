import json
from datetime import UTC, datetime

from video_editing_agent.application.ports.shot_index import (
    EmbeddingNormalization,
    ShotIndexRepresentationDescriptor,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis
from video_editing_agent.storage.repositories.record_codec import (
    decode_shot_analysis,
    encode_shot_analysis,
)

NOW = datetime(2026, 8, 11, 3, 10, tzinfo=UTC)


def test_embedding_provenance_belongs_to_rebuildable_shot_index() -> None:
    descriptor = ShotIndexRepresentationDescriptor(
        shot_ref=EntityRevisionRef("sht_1", 1),
        analysis_revision=2,
        representation="visual_semantic",
        model_id="example/multilingual-embedding",
        model_revision="rev-1",
        dimension=384,
        normalization=EmbeddingNormalization.L2,
    )

    assert descriptor.analysis_revision == 2
    assert descriptor.dimension == 384


def test_new_shot_analysis_payload_contains_no_embedding_ownership() -> None:
    analysis = ShotAnalysis(
        shot_ref=EntityRevisionRef("sht_1", 1),
        revision=1,
        profile=AnalysisProfile.SEMANTIC,
        analyzed_at=NOW,
    )

    payload = json.loads(encode_shot_analysis(analysis))

    assert "embedding_ref" not in payload


def test_historical_embedding_ref_is_ignored_when_decoding_analysis() -> None:
    analysis = ShotAnalysis(
        shot_ref=EntityRevisionRef("sht_1", 1),
        revision=1,
        profile=AnalysisProfile.SEMANTIC,
        analyzed_at=NOW,
    )
    payload = json.loads(encode_shot_analysis(analysis))
    payload["codec_version"] = 1
    payload["embedding_ref"] = "emb_historical"

    loaded = decode_shot_analysis(json.dumps(payload))

    assert loaded == analysis
    assert not hasattr(loaded, "embedding_ref")
