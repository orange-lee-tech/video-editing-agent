from __future__ import annotations

import hashlib
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from video_editing_agent.application.ports.audio_acquisition import (
    AudioAcquisitionDiagnosticCode,
    AudioAcquisitionRequest,
)
from video_editing_agent.application.ports.audio_material_provider import MusicDiscoveryQuery
from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.asset.policy import AssetOrigin, AssetUsageRole
from video_editing_agent.domain.asset.rights import RightsEligibility
from video_editing_agent.media.ingest.probe import MediaTechnicalMetadata
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.providers.audio.openverse import OpenverseWikimediaAudioProvider
from video_editing_agent.providers.audio.wikimedia import (
    WikimediaAudioRightsVerifier,
    WikimediaRightsDiagnosticCode,
)
from video_editing_agent.providers.audio.wikimedia_acquisition import WikimediaAudioAcquirer
from video_editing_agent.providers.reference.direct_https import DirectHttpsAcquisitionPolicy
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore

PUBLIC_IP = "93.184.216.34"
NOW = datetime(2026, 8, 17, 11, 0, tzinfo=UTC)
AUDIO = b"stage-a-public-music"
AUDIO_SHA1 = hashlib.sha1(AUDIO).hexdigest()
SOURCE_URL = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.ogg"
SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:Example.ogg"


class FakeResponse:
    def __init__(
        self,
        status: int = 200,
        *,
        headers: dict[str, str] | None = None,
        chunks: tuple[bytes, ...] = (AUDIO, b""),
    ) -> None:
        self.status = status
        self.headers = headers or {}
        self._chunks: Iterator[bytes] = iter(chunks)

    def getheader(self, name: str, default: str | None = None) -> str | None:
        return self.headers.get(name, default)

    def read(self, amt: int | None = None) -> bytes:
        del amt
        return next(self._chunks, b"")

    def close(self) -> None:
        return None


class FakeConnection:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.requests: list[tuple[str, str, dict[str, str]]] = []

    def request(self, method: str, target: str, *, headers: dict[str, str]) -> None:
        self.requests.append((method, target, headers))

    def getresponse(self) -> FakeResponse:
        return self.response

    def close(self) -> None:
        return None


class ConnectionQueue:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, str, int, float]] = []

    def __call__(self, hostname: str, pinned_ip: str, port: int, timeout: float) -> FakeConnection:
        self.calls.append((hostname, pinned_ip, port, timeout))
        return FakeConnection(self.responses.pop(0))


class StaticAudioProbe:
    def probe(self, path: Path) -> MediaTechnicalMetadata:
        assert path.is_file()
        return MediaTechnicalMetadata(
            media_kind="audio",
            duration_ms=2_000,
            codec="opus",
            audio_channels=2,
            sample_rate_hz=48_000,
        )


def public_resolver(hostname: str, port: int) -> tuple[str, ...]:
    assert hostname == "upload.wikimedia.org"
    assert port == 443
    return (PUBLIC_IP,)


def ext(value: str) -> dict[str, str]:
    return {"value": value, "source": "commons-desc-page"}


def commons_payload(
    *,
    license_short: str = "CC BY 4.0",
    license_url: str = "https://creativecommons.org/licenses/by/4.0/",
    non_free: str = "False",
    restrictions: str | None = None,
    mime_type: str = "audio/ogg",
    size: int = len(AUDIO),
    sha1: str = AUDIO_SHA1,
) -> dict[str, object]:
    metadata: dict[str, object] = {
        "Artist": ext("Example Artist"),
        "Credit": ext("Example Artist / Wikimedia Commons"),
        "AttributionRequired": ext("True"),
        "LicenseShortName": ext(license_short),
        "LicenseUrl": ext(license_url),
        "UsageTerms": ext(license_short),
        "Copyrighted": ext("True"),
        "NonFree": ext(non_free),
    }
    if restrictions is not None:
        metadata["Restrictions"] = ext(restrictions)
    return {
        "query": {
            "pages": [
                {
                    "pageid": 123,
                    "title": "File:Example.ogg",
                    "imageinfo": [
                        {
                            "url": SOURCE_URL,
                            "descriptionurl": SOURCE_PAGE,
                            "sha1": sha1,
                            "size": size,
                            "mime": mime_type,
                            "mediatype": "AUDIO",
                            "extmetadata": metadata,
                        }
                    ],
                }
            ]
        }
    }


def verified_request(
    rights_ref: str,
    *,
    eligibility: RightsEligibility = RightsEligibility.WARNING,
    source_url: str = SOURCE_URL,
    source_sha1: str = AUDIO_SHA1,
) -> AudioAcquisitionRequest:
    return AudioAcquisitionRequest(
        provider="wikimedia_commons",
        provider_item_id="File:Example.ogg",
        approved_source_url=source_url,
        source_page=SOURCE_PAGE,
        license_snapshot_ref=rights_ref,
        rights_eligibility=eligibility,
        expected_source_sha1=source_sha1,
        expected_byte_size=len(AUDIO),
        expected_content_type="audio/ogg",
    )


def test_openverse_discovery_is_filtered_and_never_promotes_rights() -> None:
    requested: list[str] = []

    def fetcher(url: str) -> dict[str, object]:
        requested.append(url)
        return {
            "results": [
                {
                    "id": "openverse-id",
                    "source": "wikimedia_audio",
                    "title": "Example",
                    "foreign_landing_url": SOURCE_PAGE,
                    "license": "by",
                }
            ]
        }

    candidates = OpenverseWikimediaAudioProvider(json_fetcher=fetcher).search_music(
        MusicDiscoveryQuery("warm acoustic")
    )

    assert len(candidates) == 1
    assert candidates[0].provider_item_id == "File:Example.ogg"
    assert candidates[0].rights_eligibility is RightsEligibility.UNKNOWN
    assert candidates[0].is_generated_audio is None
    params = parse_qs(urlsplit(requested[0]).query)
    assert params["source"] == ["wikimedia_audio"]
    assert params["license_type"] == ["commercial,modification"]
    assert params["filter_dead"] == ["true"]


def test_wikimedia_cc_by_verification_persists_raw_and_normalized_evidence(
    tmp_path: Path,
) -> None:
    artifacts = LocalArtifactStore(tmp_path / "artifacts")
    result = WikimediaAudioRightsVerifier(
        artifacts,
        json_fetcher=lambda _url: commons_payload(),
        clock=lambda: NOW,
    ).verify("File:Example.ogg")

    assert result.is_verified and result.verified is not None
    verified = result.verified
    assert verified.snapshot.eligibility is RightsEligibility.WARNING
    assert verified.snapshot.license_identifier == "CC BY 4.0"
    assert verified.source_url == SOURCE_URL
    assert verified.source_sha1 == AUDIO_SHA1
    assert verified.rights_artifact_ref.startswith("art_sha256_")
    assert len(verified.snapshot.evidence_artifact_refs) == 2
    for artifact_id in verified.snapshot.evidence_artifact_refs:
        assert artifacts.get_by_id(artifact_id)


def test_wikimedia_cc0_is_automatically_eligible(tmp_path: Path) -> None:
    result = WikimediaAudioRightsVerifier(
        LocalArtifactStore(tmp_path / "artifacts"),
        json_fetcher=lambda _url: commons_payload(
            license_short="CC0 1.0",
            license_url="https://creativecommons.org/publicdomain/zero/1.0/",
        ),
        clock=lambda: NOW,
    ).verify("File:Example.ogg")

    assert result.is_verified and result.verified is not None
    assert result.verified.snapshot.eligibility is RightsEligibility.ELIGIBLE


@pytest.mark.parametrize(
    ("license_short", "license_url"),
    (
        ("CC BY-NC 4.0", "https://creativecommons.org/licenses/by-nc/4.0/"),
        ("CC BY-ND 4.0", "https://creativecommons.org/licenses/by-nd/4.0/"),
        ("CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    ),
)
def test_wikimedia_disallowed_licenses_fail_closed(
    tmp_path: Path,
    license_short: str,
    license_url: str,
) -> None:
    result = WikimediaAudioRightsVerifier(
        LocalArtifactStore(tmp_path / "artifacts"),
        json_fetcher=lambda _url: commons_payload(
            license_short=license_short,
            license_url=license_url,
        ),
    ).verify("File:Example.ogg")

    assert not result.is_verified
    assert result.diagnostics[0].code is WikimediaRightsDiagnosticCode.RIGHTS_INELIGIBLE


@pytest.mark.parametrize(
    "payload",
    (
        commons_payload(non_free="True"),
        commons_payload(restrictions="Trademarked performance restrictions"),
        {"query": {"pages": [{"title": "File:Example.ogg", "missing": True}]}}
    ),
)
def test_wikimedia_nonfree_restricted_or_missing_sources_fail_closed(
    tmp_path: Path,
    payload: dict[str, object],
) -> None:
    result = WikimediaAudioRightsVerifier(
        LocalArtifactStore(tmp_path / "artifacts"),
        json_fetcher=lambda _url: payload,
    ).verify("File:Example.ogg")

    assert not result.is_verified
    assert result.diagnostics[0].code in {
        WikimediaRightsDiagnosticCode.RIGHTS_INELIGIBLE,
        WikimediaRightsDiagnosticCode.SOURCE_MISSING,
    }


def test_acquisition_refuses_unknown_rights_before_network(tmp_path: Path) -> None:
    queue = ConnectionQueue()
    result = WikimediaAudioAcquirer(
        tmp_path / "provider_audio",
        resolver=public_resolver,
        connection_factory=queue,
    ).acquire(
        verified_request(
            "art_sha256_" + "a" * 64,
            eligibility=RightsEligibility.UNKNOWN,
        )
    )

    assert not result.is_acquired
    assert result.diagnostics[0].code is AudioAcquisitionDiagnosticCode.RIGHTS_UNKNOWN
    assert queue.calls == []


def test_acquisition_rejects_non_wikimedia_host_before_network(tmp_path: Path) -> None:
    queue = ConnectionQueue()
    result = WikimediaAudioAcquirer(
        tmp_path / "provider_audio",
        resolver=public_resolver,
        connection_factory=queue,
    ).acquire(
        verified_request(
            "art_sha256_" + "a" * 64,
            source_url="https://example.com/Example.ogg",
        )
    )

    assert not result.is_acquired
    assert result.diagnostics[0].code is AudioAcquisitionDiagnosticCode.NETWORK_TARGET_REJECTED
    assert queue.calls == []


def test_acquisition_hash_mismatch_fails_and_cleans_partial(tmp_path: Path) -> None:
    root = tmp_path / "provider_audio"
    result = WikimediaAudioAcquirer(
        root,
        resolver=public_resolver,
        connection_factory=ConnectionQueue(
            FakeResponse(
                headers={"Content-Type": "audio/ogg", "Content-Length": str(len(AUDIO))}
            )
        ),
    ).acquire(
        verified_request(
            "art_sha256_" + "a" * 64,
            source_sha1="0" * 40,
        )
    )

    assert not result.is_acquired
    assert result.diagnostics[0].code is AudioAcquisitionDiagnosticCode.SOURCE_HASH_MISMATCH
    assert tuple((root / ".partial").iterdir()) == ()
    assert not any((root / "sha256").rglob("*.media"))


def test_verified_audio_acquires_deduplicates_and_ingests_as_music(tmp_path: Path) -> None:
    artifacts = LocalArtifactStore(tmp_path / "artifacts")
    verification = WikimediaAudioRightsVerifier(
        artifacts,
        json_fetcher=lambda _url: commons_payload(),
        clock=lambda: NOW,
    ).verify("File:Example.ogg")
    assert verification.is_verified and verification.verified is not None
    verified = verification.verified
    request = AudioAcquisitionRequest(
        provider="wikimedia_commons",
        provider_item_id=verified.provider_item_id,
        approved_source_url=verified.source_url,
        source_page=verified.source_page,
        license_snapshot_ref=verified.rights_artifact_ref,
        rights_eligibility=verified.snapshot.eligibility,
        expected_source_sha1=verified.source_sha1,
        expected_byte_size=verified.byte_size,
        expected_content_type=verified.mime_type,
    )
    root = tmp_path / "provider_audio"

    def acquire_once() -> object:
        return WikimediaAudioAcquirer(
            root,
            resolver=public_resolver,
            connection_factory=ConnectionQueue(
                FakeResponse(
                    headers={"Content-Type": "audio/ogg", "Content-Length": str(len(AUDIO))}
                )
            ),
            clock=lambda: NOW,
        ).acquire(request)

    first = acquire_once()
    second = acquire_once()
    assert hasattr(first, "is_acquired") and first.is_acquired
    assert hasattr(second, "is_acquired") and second.is_acquired
    assert first.acquired is not None and second.acquired is not None
    assert first.acquired.local_path == second.acquired.local_path
    assert first.acquired.local_path.parent.parent.parent == root.resolve()
    assert tuple((root / ".partial").iterdir()) == ()

    asset = AssetIngestService(
        StaticAudioProbe(),
        asset_id_factory=lambda: "ast_public_music",
        clock=lambda: NOW,
    ).ingest(
        LocalMediaSource(
            first.acquired.local_path,
            AssetOrigin.PROVIDER_ACQUIRED_AUDIO,
            AssetProvenance(
                origin_type=AssetOrigin.PROVIDER_ACQUIRED_AUDIO,
                provider=first.acquired.provider,
                provider_asset_id=first.acquired.provider_item_id,
                source_page=first.acquired.source_page,
                creator=verified.creator,
                retrieved_at=first.acquired.acquired_at,
                license_information=verified.license_identifier,
                attribution=verified.attribution_text,
            ),
            AssetUsageRole.MUSIC,
        ),
        created_by="public-music-acquisition",
    )

    assert asset.origin == AssetOrigin.PROVIDER_ACQUIRED_AUDIO
    assert asset.usage_role is AssetUsageRole.MUSIC
    assert asset.provenance.provider_asset_id == "File:Example.ogg"
    assert asset.content_hash == first.acquired.local_sha256
