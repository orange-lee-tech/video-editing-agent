from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path

from video_editing_agent.application.ports.audio_acquisition import (
    AudioAcquisitionDiagnosticCode,
    AudioAcquisitionRequest,
)
from video_editing_agent.domain.asset.rights import RightsEligibility
from video_editing_agent.providers.audio.wikimedia_acquisition import WikimediaAudioAcquirer

PUBLIC_IP = "93.184.216.34"
SOURCE_URL = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.audio"
SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:Example.audio"
RIGHTS_REF = "art_sha256_" + "a" * 64
AUDIO = b"stage-a-mime-alias-audio"
AUDIO_SHA1 = hashlib.sha1(AUDIO).hexdigest()


class FakeResponse:
    def __init__(self, content_type: str, *, body: bytes = AUDIO) -> None:
        self.status = 200
        self._headers = {
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
        }
        self._chunks: Iterator[bytes] = iter((body, b""))

    def getheader(self, name: str, default: str | None = None) -> str | None:
        return self._headers.get(name, default)

    def read(self, amt: int | None = None) -> bytes:
        del amt
        return next(self._chunks, b"")

    def close(self) -> None:
        return None


class FakeConnection:
    def __init__(self, response: FakeResponse) -> None:
        self._response = response

    def request(self, method: str, target: str, *, headers: dict[str, str]) -> None:
        assert method == "GET"
        assert target.startswith("/wikipedia/commons/")
        assert headers["User-Agent"].startswith("video-editing-agent-bot/")

    def getresponse(self) -> FakeResponse:
        return self._response

    def close(self) -> None:
        return None


class ConnectionFactory:
    def __init__(self, response: FakeResponse) -> None:
        self._response = response

    def __call__(self, hostname: str, pinned_ip: str, port: int, timeout: float) -> FakeConnection:
        assert hostname == "upload.wikimedia.org"
        assert pinned_ip == PUBLIC_IP
        assert port == 443
        assert timeout > 0
        return FakeConnection(self._response)


def resolver(hostname: str, port: int) -> tuple[str, ...]:
    assert hostname == "upload.wikimedia.org"
    assert port == 443
    return (PUBLIC_IP,)


def request(expected_content_type: str) -> AudioAcquisitionRequest:
    return AudioAcquisitionRequest(
        provider="wikimedia_commons",
        provider_item_id="File:Example.audio",
        approved_source_url=SOURCE_URL,
        source_page=SOURCE_PAGE,
        license_snapshot_ref=RIGHTS_REF,
        rights_eligibility=RightsEligibility.WARNING,
        expected_source_sha1=AUDIO_SHA1,
        expected_byte_size=len(AUDIO),
        expected_content_type=expected_content_type,
    )


def acquire(tmp_path: Path, *, expected: str, received: str):
    return WikimediaAudioAcquirer(
        tmp_path / "provider_audio",
        resolver=resolver,
        connection_factory=ConnectionFactory(FakeResponse(received)),
    ).acquire(request(expected))


def test_flac_alias_reaches_integrity_commit_and_preserves_actual_http_mime(tmp_path: Path) -> None:
    result = acquire(tmp_path, expected="audio/flac", received="audio/x-flac")

    assert result.is_acquired and result.acquired is not None
    assert result.acquired.content_type == "audio/x-flac"
    assert result.acquired.source_sha1 == AUDIO_SHA1
    assert result.acquired.local_path.read_bytes() == AUDIO


def test_ogg_alias_reaches_integrity_commit_and_preserves_actual_http_mime(tmp_path: Path) -> None:
    result = acquire(tmp_path, expected="audio/ogg", received="application/ogg")

    assert result.is_acquired and result.acquired is not None
    assert result.acquired.content_type == "application/ogg"
    assert result.acquired.source_sha1 == AUDIO_SHA1
    assert result.acquired.local_path.read_bytes() == AUDIO


def test_unrelated_audio_mime_still_fails_closed(tmp_path: Path) -> None:
    result = acquire(tmp_path, expected="audio/flac", received="audio/mpeg")

    assert not result.is_acquired
    diagnostic = result.diagnostics[0]
    assert diagnostic.code is AudioAcquisitionDiagnosticCode.SOURCE_METADATA_CHANGED
    assert "expected=audio/flac" in diagnostic.message
    assert "received=audio/mpeg" in diagnostic.message
