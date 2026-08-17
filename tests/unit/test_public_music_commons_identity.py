from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from video_editing_agent.application.ports.audio_material_provider import MusicDiscoveryQuery
from video_editing_agent.domain.asset.rights import RightsEligibility
from video_editing_agent.providers.audio.openverse import OpenverseWikimediaAudioProvider
from video_editing_agent.providers.audio.wikimedia import WikimediaAudioRightsVerifier
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore

NOW = datetime(2026, 8, 17, 11, 23, tzinfo=UTC)
SOURCE_URL = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.flac"
SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:Example.flac"


def _ext(value: str) -> dict[str, str]:
    return {"value": value, "source": "commons-desc-page"}


def test_openverse_maps_observed_commons_curid_landing_shape() -> None:
    provider = OpenverseWikimediaAudioProvider(
        json_fetcher=lambda _url: {
            "results": [
                {
                    "id": "7b77669a-afee-440c-b5d3-dd3dc71bb4cc",
                    "source": "wikimedia_audio",
                    "title": "Relaxing Piano Instrumental",
                    "foreign_landing_url": (
                        "https://commons.wikimedia.org/w/index.php?curid=196809597"
                    ),
                    "foreign_identifier": None,
                    "license": "by",
                    "license_url": "https://creativecommons.org/licenses/by/4.0/",
                    "filetype": "flac",
                }
            ]
        }
    )

    candidates = provider.search_music(MusicDiscoveryQuery("piano instrumental"))

    assert len(candidates) == 1
    assert candidates[0].provider_item_id == "commons_pageid:196809597"
    assert candidates[0].rights_eligibility is RightsEligibility.UNKNOWN
    assert candidates[0].is_generated_audio is None


def test_wikimedia_page_id_verification_resolves_canonical_file_title(tmp_path: Path) -> None:
    requested: list[str] = []

    def fetcher(url: str) -> dict[str, object]:
        requested.append(url)
        return {
            "query": {
                "pages": [
                    {
                        "pageid": 196809597,
                        "title": "File:Example.flac",
                        "imageinfo": [
                            {
                                "url": SOURCE_URL,
                                "descriptionurl": SOURCE_PAGE,
                                "sha1": "a" * 40,
                                "size": 4096,
                                "mime": "audio/flac",
                                "mediatype": "AUDIO",
                                "extmetadata": {
                                    "Artist": _ext("Example Artist"),
                                    "Credit": _ext("Example Artist / Wikimedia Commons"),
                                    "AttributionRequired": _ext("True"),
                                    "LicenseShortName": _ext("CC BY 4.0"),
                                    "LicenseUrl": _ext(
                                        "https://creativecommons.org/licenses/by/4.0/"
                                    ),
                                    "UsageTerms": _ext("CC BY 4.0"),
                                    "Copyrighted": _ext("True"),
                                    "NonFree": _ext("False"),
                                },
                            }
                        ],
                    }
                ]
            }
        }

    result = WikimediaAudioRightsVerifier(
        LocalArtifactStore(tmp_path / "artifacts"),
        json_fetcher=fetcher,
        clock=lambda: NOW,
    ).verify("commons_pageid:196809597")

    assert result.is_verified and result.verified is not None
    assert result.verified.provider_item_id == "File:Example.flac"
    assert result.verified.snapshot.provider_item_id == "File:Example.flac"
    assert result.verified.snapshot.eligibility is RightsEligibility.WARNING
    params = parse_qs(urlsplit(requested[0]).query)
    assert params["pageids"] == ["196809597"]
    assert "titles" not in params
