from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class MaterialQuery:
    query: str


@dataclass(frozen=True, slots=True)
class RemoteMaterialCandidate:
    provider: str
    provider_asset_id: str
    source_page: str | None = None


class MaterialProvider(Protocol):
    def search(self, query: MaterialQuery) -> list[RemoteMaterialCandidate]: ...
