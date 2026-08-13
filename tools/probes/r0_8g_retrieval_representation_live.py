from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import sys
import tempfile
import time

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from video_editing_agent.domain.common.entity import EntityRevisionRef  # noqa: E402
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
    parser.add_argument("--model-path", type=pathlib.Path, required=True)
    parser.add_argument("--model-revision", required=True)
    args = parser.parse_args()
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1")
    workspace = pathlib.Path(tempfile.mkdtemp(prefix="r0_8g_"))
    try:
        store = LocalArtifactStore(workspace / "artifacts")
        lifecycle = LocalArtifactLifecycleRepository(workspace / "artifacts")
        port = SentenceTransformersTextEmbeddingPort(
            SentenceTransformersConfig(str(args.model_path.resolve()), args.model_revision)
        )
        sources = (
            DenseRepresentationSource(
                EntityRevisionRef("sht_zh_wood", 1),
                "visual_semantic_text",
                3,
                "一名木匠正在工作台旁用砂纸打磨木桌。",
            ),
            DenseRepresentationSource(
                EntityRevisionRef("sht_en_bike", 1),
                "visual_semantic_text",
                2,
                "An astronaut plays a guitar while floating in outer space.",
            ),
            DenseRepresentationSource(
                EntityRevisionRef("sht_speech", 1),
                "speech_text",
                5,
                "Please tighten the camera tripod before filming.",
            ),
            DenseRepresentationSource(
                EntityRevisionRef("sht_tie_b", 1), "visual_semantic_text", 1, "quiet ocean"
            ),
            DenseRepresentationSource(
                EntityRevisionRef("sht_tie_a", 1), "visual_semantic_text", 1, "quiet ocean"
            ),
        )
        index = DenseShotIndex(
            embedding_port=port,
            artifact_store=store,
            artifact_lifecycle_repository=lifecycle,
        )
        started = time.perf_counter()
        records = index.rebuild(sources)
        indexing_ms = (time.perf_counter() - started) * 1000

        def query(text: str):
            begin = time.perf_counter()
            result = index.search(text, representation="visual_semantic_text")
            return result, (time.perf_counter() - begin) * 1000

        english, english_ms = query("a woodworker sanding a wooden table")
        chinese, chinese_ms = query("一名宇航员在太空漂浮时弹吉他")
        ties, tie_ms = query("quiet ocean")
        reopened = DenseShotIndex(
            embedding_port=port,
            artifact_store=store,
            artifact_lifecycle_repository=lifecycle,
        )
        restored = reopened.restore(tuple(record.artifact_id for record in records))
        restart_equal = reopened.search(
            "quiet ocean", representation="visual_semantic_text"
        ) == index.search("quiet ocean", representation="visual_semantic_text")
        tie_order = [
            item.shot_ref.entity_id
            for item in ties
            if item.shot_ref.entity_id.startswith("sht_tie")
        ]
        gates = {
            "english_to_chinese": english[0].shot_ref.entity_id == "sht_zh_wood",
            "chinese_to_english": chinese[0].shot_ref.entity_id == "sht_en_bike",
            "stable_tie": tie_order == ["sht_tie_a", "sht_tie_b"],
            "visual_and_speech_provenance": {
                (x.descriptor.representation, x.source_revision) for x in records
            }
            >= {("visual_semantic_text", 3), ("speech_text", 5)},
            "restart_equal": restart_equal and restored == records,
            "offline_inference": os.environ["HF_HUB_OFFLINE"] == "1",
        }
        report = {
            "classification": "engineering_probe",
            "model_id": "intfloat/multilingual-e5-small",
            "model_revision": args.model_revision,
            "corpus_size": len(sources),
            "indexing_ms": round(indexing_ms, 3),
            "query_latency_ms": {
                "english": round(english_ms, 3),
                "chinese": round(chinese_ms, 3),
                "tie": round(tie_ms, 3),
            },
            "artifact_ids": [x.artifact_id for x in records],
            "gates": gates,
            "pass": all(gates.values()),
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["pass"] else 1
    finally:
        shutil.rmtree(workspace)


if __name__ == "__main__":
    raise SystemExit(main())
