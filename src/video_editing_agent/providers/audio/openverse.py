from __future__ import annotations

import json
from collections.abc import Callable
from typing import cast
from urllib.parse import parse_qs, unquote, urlencode, urlsplit
from urllib.request import Request, urlopen

from video_editing_agent.application.ports.audio_material_provider import (
    AudioMaterialCandidate,
    MusicDiscoveryQuery,
)
from video_editing_agent.domain.asset.rights import RightsEligibility

_OPENVERSE_AUDIO_ENDPOINT = "https://api.openverse.org/v1/audio/"
_WIKIMEDIA_AUDIO_SOURCE = "wikimedia_audio"
_USER_AGENT = "video-editing-agent/public-music-r0.12"
JsonObject = dict[str, object]
JsonFetcher = Callable[[str], JsonObject]


def _default_json_fetcher(url: str) -> JsonObject:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": _USER_AGENT,
        },
        method="GET",
    )
    with urlopen(request, timeout=30.0) as response:  # noqa: S310 - fixed Openverse endpoint
        if response.status != 200:
            raise OSError(f"Openverse returned HTTP {response.status}")
        return cast(JsonObject, json.loads(response.read().decode("utf-8")))


def _text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _commons_title(result: JsonObject) -> str | None:
    landing = _text(result.get("foreign_landing_url"))
    if landing is not None:
        parts = urlsplit(landing)
        if parts.scheme.casefold() == "https" and parts.hostname == "commons.wikimedia.org":
            prefix = "/wiki/"
            if parts.path.startswith(prefix):
                title = unquote(parts.path.removeprefix(prefix)).replace("_", " ")
                if title.casefold().startswith("file:"):
                    return title

    foreign_identifier = _text(result.get("foreign_identifier"))
    if foreign_identifier is None:
        return None
    if foreign_identifier.casefold().startswith("file:"):
        return foreign_identifier
    return f"File:{foreign_identifier}"


class OpenverseWikimediaAudioProvider:
    """Discovery-only adapter; Openverse metadata never becomes rights authority."""

    def __init__(
        self,
        *,
        page_size: int = 20,
        json_fetcher: JsonFetcher = _default_json_fetcher,
    ) -> None:
        if isinstance(page_size, bool) or not isinstance(page_size, int):
            raise TypeError("page_size must be an int")
        if not 1 <= page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")
        self._page_size = page_size
        self._json_fetcher = json_fetcher

    def search_music(self, query: MusicDiscoveryQuery) -> tuple[AudioMaterialCandidate, ...]:
        parameters = {
            "q": query.query.strip(),
            "source": _WIKIMEDIA_AUDIO_SOURCE,
            "page_size": str(self._page_size),
            "filter_dead": "true",
        }
        if query.commercial_use_required:
            parameters["license_type"] = "commercial,modification"
        url = f"{_OPENVERSE_AUDIO_ENDPOINT}?{urlencode(parameters)}"
        payload = self._json_fetcher(url)
        raw_results = payload.get("results")
        if not isinstance(raw_results, list):
            return ()

        candidates: list[AudioMaterialCandidate] = []
        for raw in raw_results:
            if not isinstance(raw, dict):
                continue
            result = cast(JsonObject, raw)
            if _text(result.get("source")) != _WIKIMEDIA_AUDIO_SOURCE:
                continue
            file_title = _commons_title(result)
            if file_title is None:
                continue
            candidates.append(
                AudioMaterialCandidate(
                    provider="wikimedia_commons_via_openverse",
                    provider_item_id=file_title,
                    rights_eligibility=RightsEligibility.UNKNOWN,
                    title=_text(result.get("title")),
                    source_page=_text(result.get("foreign_landing_url")),
                    is_generated_audio=None,
                )
            )
        return tuple(candidates)


def openverse_query_parameters(url: str) -> dict[str, list[str]]:
    """Expose deterministic request parameters for diagnostics/probes without network access."""

    return parse_qs(urlsplit(url).query)
