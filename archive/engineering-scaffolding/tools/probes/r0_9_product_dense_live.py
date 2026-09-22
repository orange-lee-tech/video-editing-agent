from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from video_editing_agent.application.ports.shot_index import ShotCandidate  # noqa: E402
from video_editing_agent.domain.common.entity import EntityRevisionRef  # noqa: E402
from video_editing_agent.editing.director.retrieval import reciprocal_rank_fusion  # noqa: E402
from video_editing_agent.media.indexing.dense import (  # noqa: E402
    DenseRepresentationSource,
    DenseShotIndex,
)
from video_editing_agent.providers.embedding.sentence_transformers import (  # noqa: E402
    SentenceTransformersConfig,
    SentenceTransformersTextEmbeddingPort,
)
from video_editing_agent.storage.artifact.lifecycle_repository import (  # noqa: E402
    LocalArtifactLifecycleRepository,
)
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--artifacts", type=pathlib.Path, required=True)
    parser.add_argument("--model-path", type=pathlib.Path, required=True)
    parser.add_argument("--model-revision", required=True)
    args = parser.parse_args()
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1")
    request = json.loads(args.input.read_text(encoding="utf-8"))
    port = SentenceTransformersTextEmbeddingPort(
        SentenceTransformersConfig(
            str(args.model_path.resolve()),
            "intfloat/multilingual-e5-small",
            args.model_revision,
        )
    )
    index = DenseShotIndex(
        embedding_port=port,
        artifact_store=LocalArtifactStore(args.artifacts),
        artifact_lifecycle_repository=LocalArtifactLifecycleRepository(args.artifacts),
    )
    records = index.rebuild(
        tuple(
            DenseRepresentationSource(
                EntityRevisionRef(item["shot_id"], 1),
                1,
                "visual_semantic_text",
                "shot_analysis",
                1,
                item["text"],
            )
            for item in request["documents"]
        )
    )
    searches = {
        slot_id: [
            {
                "shot_id": candidate.shot_ref.entity_id,
                "analysis_revision": candidate.analysis_revision,
                "score": candidate.retrieval_score,
            }
            for candidate in index.search(query, representation="visual_semantic_text")
        ]
        for slot_id, query in request["queries"].items()
    }
    hybrid = {
        slot_id: [
            {
                "shot_id": candidate.shot_ref.entity_id,
                "analysis_revision": candidate.analysis_revision,
                "score": candidate.fused_score,
                "channel_ranks": candidate.channel_ranks,
            }
            for candidate in reciprocal_rank_fusion(
                tuple(
                    ShotCandidate(
                        EntityRevisionRef(item["shot_id"], 1),
                        item["analysis_revision"],
                        item["score"],
                        tuple(item["matched_terms"]),
                    )
                    for item in request["lexical"][slot_id]
                ),
                index.search(query, representation="visual_semantic_text"),
            )
        ]
        for slot_id, query in request["queries"].items()
    }
    reopened = DenseShotIndex(
        embedding_port=port,
        artifact_store=LocalArtifactStore(args.artifacts),
        artifact_lifecycle_repository=LocalArtifactLifecycleRepository(args.artifacts),
    )
    reopened.restore(tuple(record.artifact_id for record in records))
    restart_equal = all(
        [
            item.shot_ref.entity_id
            for item in reopened.search(query, representation="visual_semantic_text")
        ]
        == [item["shot_id"] for item in searches[slot_id]]
        for slot_id, query in request["queries"].items()
    )
    args.output.write_text(
        json.dumps(
            {
                "model_id": "intfloat/multilingual-e5-small",
                "model_revision": args.model_revision,
                "searches": searches,
                "hybrid": hybrid,
                "artifact_ids": [record.artifact_id for record in records],
                "restart_equal": restart_equal,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
