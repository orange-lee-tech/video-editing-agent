from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class EmbeddingIntent(StrEnum):
    QUERY = "query"
    DOCUMENT = "document"


@dataclass(frozen=True, slots=True)
class TextEmbeddingRequest:
    texts: tuple[str, ...]
    intent: EmbeddingIntent


@dataclass(frozen=True, slots=True)
class TextEmbeddingResult:
    model_id: str
    model_revision: str
    dimension: int
    vectors: tuple[tuple[float, ...], ...]


class TextEmbeddingPort(Protocol):
    def embed(self, request: TextEmbeddingRequest) -> TextEmbeddingResult: ...
