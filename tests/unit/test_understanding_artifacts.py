from pathlib import Path

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.understanding.artifacts import persist_extracted_frame_samples
from video_editing_agent.media.understanding.frame_extraction import (
    PNG_MEDIA_TYPE,
    PNG_SIGNATURE,
    ExtractedFrameSample,
)
from video_editing_agent.media.understanding.sampling import FrameSampleSpec
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore


def test_persisted_frames_keep_sampling_traceability(tmp_path: Path) -> None:
    shot_ref = EntityRevisionRef("sht_1", 2)
    extracted = tuple(
        ExtractedFrameSample(
            sample=FrameSampleSpec(
                shot_ref=shot_ref,
                ordinal=index,
                source_timestamp_ms=timestamp_ms,
            ),
            media_type=PNG_MEDIA_TYPE,
            content=PNG_SIGNATURE + bytes([index + 1]),
        )
        for index, timestamp_ms in enumerate((333, 1_000, 1_666))
    )

    stored = persist_extracted_frame_samples(extracted, LocalArtifactStore(tmp_path / "artifacts"))

    assert [item.sample for item in stored] == [item.sample for item in extracted]
    assert [item.visual_ref.ordinal for item in stored] == [0, 1, 2]
    assert [item.visual_ref.source_timestamp_ms for item in stored] == [333, 1_000, 1_666]
    assert all(item.visual_ref.artifact_ref.artifact_id.startswith("art_sha256_") for item in stored)
