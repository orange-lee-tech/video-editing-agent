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
            SentenceTransformersConfig(
                str(args.model_path.resolve()),
                "intfloat/multilingual-e5-small",
                args.model_revision,
            )
        )
        sources = (
            DenseRepresentationSource(
                EntityRevisionRef("sht_zh_wood", 1),
                3,
                "visual_semantic_text",
                "shot_analysis",
                3,
                "一名木匠正在工作台旁用砂纸打磨木桌。",
            ),
            DenseRepresentationSource(
                EntityRevisionRef("sht_en_bike", 1),
                2,
                "visual_semantic_text",
                "shot_analysis",
                2,
                "An astronaut plays a guitar while floating in outer space.",
            ),
            DenseRepresentationSource(
                EntityRevisionRef("sht_speech", 1),
                4,
                "speech_text",
                "speech_transcript",
                5,
                "Please tighten the camera tripod before filming.",
            ),
            DenseRepresentationSource(
                EntityRevisionRef("sht_tie_b", 1),
                1,
                "visual_semantic_text",
                "shot_analysis",
                1,
                "quiet ocean",
            ),
            DenseRepresentationSource(
                EntityRevisionRef("sht_tie_a", 1),
                1,
                "visual_semantic_text",
                "shot_analysis",
                1,
                "quiet ocean",
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
        original = {
            (record.descriptor.shot_ref, record.descriptor.representation): record
            for record in records
        }
        speech_refreshed = index.upsert(
            DenseRepresentationSource(
                EntityRevisionRef("sht_speech", 1),
                4,
                "speech_text",
                "speech_transcript",
                6,
                "Please secure the camera tripod before recording.",
            )
        )
        selective_speech = (
            speech_refreshed.source_revision == 6
            and speech_refreshed.descriptor.analysis_revision == 4
            and index._records[
                (EntityRevisionRef("sht_zh_wood", 1), "visual_semantic_text")
            ].artifact_id
            == original[(EntityRevisionRef("sht_zh_wood", 1), "visual_semantic_text")].artifact_id
        )
        visual_refreshed = index.upsert(
            DenseRepresentationSource(
                EntityRevisionRef("sht_zh_wood", 1),
                4,
                "visual_semantic_text",
                "shot_analysis",
                4,
                "一位木匠在工作台旁打磨木桌。",
            )
        )
        selective_visual = (
            visual_refreshed.descriptor.analysis_revision == 4
            and index._records[
                (EntityRevisionRef("sht_en_bike", 1), "visual_semantic_text")
            ].artifact_id
            == original[(EntityRevisionRef("sht_en_bike", 1), "visual_semantic_text")].artifact_id
        )
        port._config = SentenceTransformersConfig(
            str(args.model_path.resolve()), "wrong/model", args.model_revision
        )
        try:
            index.search("woodworker", representation="visual_semantic_text")
        except ValueError as exc:
            model_mismatch = "provenance mismatch" in str(exc)
        else:
            model_mismatch = False
        gates = {
            "english_to_chinese": english[0].shot_ref.entity_id == "sht_zh_wood",
            "chinese_to_english": chinese[0].shot_ref.entity_id == "sht_en_bike",
            "stable_tie": tie_order == ["sht_tie_a", "sht_tie_b"],
            "visual_analysis_provenance": any(
                x.source_kind == "shot_analysis"
                and x.source_revision == x.descriptor.analysis_revision == 3
                for x in records
            ),
            "speech_transcript_provenance": any(
                x.source_kind == "speech_transcript"
                and x.source_revision == 5
                and x.descriptor.analysis_revision == 4
                for x in records
            ),
            "selective_visual_source_refresh": selective_visual,
            "selective_speech_source_refresh": selective_speech,
            "model_provenance_mismatch_rejected": model_mismatch,
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
