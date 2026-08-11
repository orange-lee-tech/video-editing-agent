from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.application.ports.artifact_store import ArtifactPayload, ArtifactStore
from video_editing_agent.application.ports.visual_understanding import VisualFrameReference
from video_editing_agent.media.understanding.frame_extraction import ExtractedFrameSample
from video_editing_agent.media.understanding.sampling import FrameSampleSpec


@dataclass(frozen=True, slots=True)
class StoredFrameSample:
    sample: FrameSampleSpec
    visual_ref: VisualFrameReference

    def __post_init__(self) -> None:
        if self.visual_ref.ordinal != self.sample.ordinal:
            raise ValueError("stored visual frame ordinal must match the sampling plan")
        if self.visual_ref.source_timestamp != self.sample.source_timestamp:
            raise ValueError("stored visual frame timestamp must match the sampling plan")


def persist_extracted_frame_samples(
    extracted_frames: tuple[ExtractedFrameSample, ...],
    artifact_store: ArtifactStore,
) -> tuple[StoredFrameSample, ...]:
    stored: list[StoredFrameSample] = []
    for extracted in extracted_frames:
        artifact_ref = artifact_store.put(
            ArtifactPayload(
                media_type=extracted.media_type,
                content=extracted.content,
            )
        )
        stored.append(
            StoredFrameSample(
                sample=extracted.sample,
                visual_ref=VisualFrameReference(
                    artifact_ref=artifact_ref,
                    ordinal=extracted.sample.ordinal,
                    source_timestamp=extracted.sample.source_timestamp,
                ),
            )
        )
    return tuple(stored)
