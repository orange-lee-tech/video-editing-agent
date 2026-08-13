from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from video_editing_agent.application.ports.text_embedding import (  # noqa: E402
    EmbeddingIntent,
    TextEmbeddingRequest,
)
from video_editing_agent.providers.embedding.sentence_transformers import (  # noqa: E402
    SentenceTransformersConfig,
    SentenceTransformersTextEmbeddingPort,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--model-revision", required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    port = SentenceTransformersTextEmbeddingPort(
        SentenceTransformersConfig(
            args.model_path, "intfloat/multilingual-e5-small", args.model_revision
        )
    )
    documents = (
        "A handheld product demonstration of a water bottle on a table, picked up and rotated.",
        "A quiet static view of an empty office table.",
    )
    docs = port.embed(TextEmbeddingRequest(documents, EmbeddingIntent.DOCUMENT)).vectors
    query = port.embed(
        TextEmbeddingRequest(("手持展示并旋转一瓶水",), EmbeddingIntent.QUERY)
    ).vectors[0]
    scores = [sum(a * b for a, b in zip(query, vector, strict=True)) for vector in docs]
    report = {"scores": scores, "intended_index": 0, "pass": scores[0] > scores[1]}
    args.output.write_text(json.dumps(report, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
