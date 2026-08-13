from __future__ import annotations

import json
import math
from dataclasses import dataclass

from video_editing_agent.application.ports.artifact_lifecycle import (
    ArtifactLifecycleDescriptor,
    ArtifactLifecycleRepository,
    ArtifactRetentionClass,
)
from video_editing_agent.application.ports.artifact_store import ArtifactPayload, ArtifactStore
from video_editing_agent.application.ports.shot_index import (
    EmbeddingNormalization,
    ShotCandidate,
    ShotIndexRepresentationDescriptor,
)
from video_editing_agent.application.ports.text_embedding import (
    EmbeddingIntent,
    TextEmbeddingPort,
    TextEmbeddingRequest,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.evidence.speech import SpeechTranscript
from video_editing_agent.domain.shot.analysis import ShotAnalysis


@dataclass(frozen=True, slots=True)
class DenseRepresentationSource:
    shot_ref: EntityRevisionRef
    representation: str
    source_revision: int
    text: str


@dataclass(frozen=True, slots=True)
class DenseRepresentation:
    descriptor: ShotIndexRepresentationDescriptor
    source_revision: int
    artifact_id: str
    vector: tuple[float, ...]


def visual_semantic_source(analysis: ShotAnalysis) -> DenseRepresentationSource | None:
    if analysis.visual is None:
        return None
    visual = analysis.visual
    parts = [
        visual.summary,
        *visual.tags,
        *visual.subjects,
        *visual.actions,
        visual.environment,
        visual.framing,
        visual.camera_motion,
    ]
    text = "\n".join(x.strip() for x in parts if x and x.strip())
    return (
        None
        if not text
        else DenseRepresentationSource(
            analysis.shot_ref, "visual_semantic_text", analysis.revision, text
        )
    )


def speech_text_source(transcript: SpeechTranscript) -> DenseRepresentationSource | None:
    return (
        None
        if not transcript.text.strip()
        else DenseRepresentationSource(
            transcript.shot_ref, "speech_text", transcript.revision, transcript.text.strip()
        )
    )


def _normalize(vector: tuple[float, ...]) -> tuple[float, ...]:
    if not vector or any(not math.isfinite(x) for x in vector):
        raise ValueError("embedding vector must be non-empty and finite")
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        raise ValueError("embedding vector must not be zero")
    return tuple(x / norm for x in vector)


class DenseShotIndex:
    def __init__(
        self,
        *,
        embedding_port: TextEmbeddingPort,
        artifact_store: ArtifactStore,
        artifact_lifecycle_repository: ArtifactLifecycleRepository,
    ) -> None:
        self._port = embedding_port
        self._artifacts = artifact_store
        self._lifecycle = artifact_lifecycle_repository
        self._records: dict[tuple[EntityRevisionRef, str], DenseRepresentation] = {}

    def rebuild(
        self, sources: tuple[DenseRepresentationSource, ...]
    ) -> tuple[DenseRepresentation, ...]:
        texts = tuple(x.text for x in sources)
        result = self._port.embed(TextEmbeddingRequest(texts, EmbeddingIntent.DOCUMENT))
        if len(result.vectors) != len(sources) or result.dimension < 1:
            raise ValueError("embedding provider returned incompatible batch/dimension")
        rebuilt = {}
        for source, raw in zip(sources, result.vectors, strict=True):
            if len(raw) != result.dimension:
                raise ValueError("embedding dimension mismatch")
            vector = _normalize(raw)
            descriptor = ShotIndexRepresentationDescriptor(
                source.shot_ref,
                source.source_revision,
                source.representation,
                result.model_id,
                result.model_revision,
                result.dimension,
                EmbeddingNormalization.L2,
            )
            payload = json.dumps(
                {
                    "schema_version": "r0.8g-dense-v1",
                    "descriptor": {
                        "shot_ref": {
                            "entity_id": source.shot_ref.entity_id,
                            "revision": source.shot_ref.revision,
                        },
                        "source_revision": source.source_revision,
                        "representation": source.representation,
                        "model_id": result.model_id,
                        "model_revision": result.model_revision,
                        "dimension": result.dimension,
                        "normalization": "l2",
                    },
                    "vector": vector,
                },
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode()
            artifact = self._artifacts.put(ArtifactPayload("application/json", payload))
            self._lifecycle.add(
                ArtifactLifecycleDescriptor(
                    artifact.artifact_id,
                    ArtifactRetentionClass.REBUILDABLE_CACHE,
                    "shot_dense_representation",
                    (
                        f"shot:{source.shot_ref.entity_id}@{source.shot_ref.revision}",
                        f"{source.representation}:{source.source_revision}",
                    ),
                )
            )
            record = DenseRepresentation(
                descriptor, source.source_revision, artifact.artifact_id, vector
            )
            rebuilt[(source.shot_ref, source.representation)] = record
        self._records = rebuilt
        return tuple(
            sorted(
                rebuilt.values(),
                key=lambda x: (x.descriptor.shot_ref.entity_id, x.descriptor.representation),
            )
        )

    def restore(self, artifact_ids: tuple[str, ...]) -> tuple[DenseRepresentation, ...]:
        restored: dict[tuple[EntityRevisionRef, str], DenseRepresentation] = {}
        for artifact_id in artifact_ids:
            try:
                root = json.loads(self._artifacts.get_by_id(artifact_id))
                if root.get("schema_version") != "r0.8g-dense-v1":
                    raise ValueError("unknown dense representation schema")
                value = root["descriptor"]
                shot = value["shot_ref"]
                vector = tuple(float(x) for x in root["vector"])
                descriptor = ShotIndexRepresentationDescriptor(
                    EntityRevisionRef(str(shot["entity_id"]), int(shot["revision"])),
                    int(value["source_revision"]),
                    str(value["representation"]),
                    str(value["model_id"]),
                    str(value["model_revision"]),
                    int(value["dimension"]),
                    EmbeddingNormalization(str(value["normalization"])),
                )
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                raise ValueError("invalid dense representation artifact") from exc
            if (
                len(vector) != descriptor.dimension
                or any(not math.isfinite(x) for x in vector)
                or not math.isclose(sum(x * x for x in vector), 1.0, abs_tol=1e-9)
            ):
                raise ValueError("dense representation dimension mismatch")
            record = DenseRepresentation(
                descriptor, descriptor.analysis_revision, artifact_id, vector
            )
            key = (descriptor.shot_ref, descriptor.representation)
            if key in restored:
                raise ValueError("duplicate dense representation identity")
            restored[key] = record
        self._records = restored
        return tuple(
            sorted(
                restored.values(),
                key=lambda x: (x.descriptor.shot_ref.entity_id, x.descriptor.representation),
            )
        )

    def search(
        self, query: str, *, representation: str, limit: int = 20
    ) -> tuple[ShotCandidate, ...]:
        result = self._port.embed(TextEmbeddingRequest((query,), EmbeddingIntent.QUERY))
        records = [
            x for x in self._records.values() if x.descriptor.representation == representation
        ]
        if len(result.vectors) != 1:
            raise ValueError("query embedding provider returned wrong batch")
        query_vector = _normalize(result.vectors[0])
        candidates = []
        for record in records:
            descriptor = record.descriptor
            if (
                result.model_id != descriptor.model_id
                or result.model_revision != descriptor.model_revision
                or result.dimension != descriptor.dimension
                or len(query_vector) != descriptor.dimension
                or descriptor.normalization is not EmbeddingNormalization.L2
            ):
                raise ValueError("query/document embedding provenance mismatch")
            cosine = sum(a * b for a, b in zip(query_vector, record.vector, strict=True))
            candidates.append(
                ShotCandidate(
                    descriptor.shot_ref, descriptor.analysis_revision, (cosine + 1) / 2, ()
                )
            )
        candidates.sort(
            key=lambda x: (-x.retrieval_score, x.shot_ref.entity_id, x.shot_ref.revision)
        )
        return tuple(candidates[:limit])
