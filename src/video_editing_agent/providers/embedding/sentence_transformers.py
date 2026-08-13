from __future__ import annotations

import importlib
import importlib.metadata
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from video_editing_agent.application.ports.text_embedding import (
    EmbeddingIntent,
    TextEmbeddingPort,
    TextEmbeddingRequest,
    TextEmbeddingResult,
)

RUNTIME_VERSION = "5.6.0"


class SentenceTransformersUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class SentenceTransformersConfig:
    model_path: str
    model_id: str
    model_revision: str
    dimension: int = 384

    def __post_init__(self) -> None:
        if (
            not self.model_path.strip()
            or not self.model_id.strip()
            or not self.model_revision.strip()
        ):
            raise ValueError("model path/id/revision must not be empty")
        if isinstance(self.dimension, bool) or not isinstance(self.dimension, int):
            raise TypeError("dimension must be an int")
        if self.dimension < 1:
            raise ValueError("dimension must be positive")


class SentenceTransformersTextEmbeddingPort(TextEmbeddingPort):
    def __init__(
        self,
        config: SentenceTransformersConfig,
        *,
        model_factory: Callable[[], Any] | None = None,
    ) -> None:
        self._config = config
        self._factory = model_factory or self._default_factory
        self._model: Any | None = None

    def _default_factory(self) -> Any:
        try:
            version = importlib.metadata.version("sentence-transformers")
            module = importlib.import_module("sentence_transformers")
        except (importlib.metadata.PackageNotFoundError, ModuleNotFoundError) as exc:
            raise SentenceTransformersUnavailableError(
                "optional sentence-transformers runtime is unavailable"
            ) from exc
        if version != RUNTIME_VERSION:
            raise SentenceTransformersUnavailableError(
                "sentence-transformers version mismatch: "
                f"expected {RUNTIME_VERSION}, found {version}"
            )
        return module.SentenceTransformer(
            self._config.model_path, device="cpu", local_files_only=True
        )

    def embed(self, request: TextEmbeddingRequest) -> TextEmbeddingResult:
        if not request.texts or any(not x.strip() for x in request.texts):
            raise ValueError("embedding texts must be non-empty")
        if self._model is None:
            self._model = self._factory()
        model = self._model
        prefix = "query: " if request.intent is EmbeddingIntent.QUERY else "passage: "
        vectors = model.encode(
            [prefix + x for x in request.texts],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        normalized = tuple(tuple(float(value) for value in vector) for vector in vectors)
        if any(len(x) != self._config.dimension for x in normalized):
            raise ValueError("sentence-transformers output dimension mismatch")
        return TextEmbeddingResult(
            self._config.model_id,
            self._config.model_revision,
            self._config.dimension,
            normalized,
        )
