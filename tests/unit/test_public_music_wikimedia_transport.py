from __future__ import annotations

from pathlib import Path

from video_editing_agent.application.ports.audio_acquisition import (
    AudioAcquisitionDiagnosticCode,
    AudioAcquisitionRequest,
)
from video_editing_agent.domain.asset.rights import RightsEligibility
from video_editing_agent.providers.audio.wikimedia_acquisition import WikimediaAudioAcquirer

PUBLIC_IP = "93.184.216.34"
SOURCE_URL = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.flac"
SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:Example.flac"
RIGHTS_REF = "art_sha256_" + "a" * 64


class FakeResponse:
    def __init__(self, status: int, headers: dict[str, str]) -> None:
        self.status = status
        self._headers = headers

    def getheader(self, name: str, default: str | None = None) -> str | None:
        return self._headers.get(name, default)

    def read(self, amt: int | None = None) -> bytes:
        del amt
        return b""

    def close(self) -> None:
        return None


class RecordingConnection:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.requests: list[tuple[str, str, dict[str, str]]] = []

    def request(self, method: str, target: str, *, headers: dict[str, str]) -> None:
        self.requests.append((method, target, headers))

    def getresponse(self) -> FakeResponse:
        return self.response

    def close(self) -> None:
        return None


class ConnectionFactory:
    def __init__(self, response: FakeResponse) -> None:
        self.connection = RecordingConnection(response)

    def __call__(self, hostname: str, pinned_ip: str, port: int, timeout: float) -> RecordingConnection:
        assert hostname == "upload.wikimedia.org"
        assert pinned_ip == PUBLIC_IP
        assert port == 443
        assert timeout > 0
        return self.connection


def resolver(hostname: str, port: int) -> tuple[str, ...]:
    assert hostname == "upload.wikimedia.org"
    assert port == 443
    return (PUBLIC_IP,)


def request(*, expected_content_type: str = "audio/flac") -> AudioAcquisitionRequest:
    return AudioAcquisitionRequest(
        provider="wikimedia_commons",
        provider_item_id="File:Example.flac",
        approved_source_url=SOURCE_URL,
        source_page=SOURCE_PAGE,
        license_snapshot_ref=RIGHTS_REF,
        rights_eligibility=RightsEligibility.WARNING,
        expected_source_sha1="a" * 40,
        expected_content_type=expected_content_type,
    )


def test_429_is_retryable_preserves_retry_after_and_uses_identified_bot_user_agent(
    tmp_path: Path,
) -> None:
    factory = ConnectionFactory(FakeResponse(429, {"Retry-After": "120"}))

    result = WikimediaAudioAcquirer(
        tmp_path / "provider_audio",
        resolver=resolver,
        connection_factory=factory,
    ).acquire(request())

    assert not result.is_acquired
    diagnostic = result.diagnostics[0]
    assert diagnostic.code is AudioAcquisitionDiagnosticCode.TRANSPORT_FAILED
    assert diagnostic.retryable
    assert "HTTP 429" in diagnostic.message
    assert "Retry-After=120" in diagnostic.message
    headers = factory.connection.requests[0][2]
    assert "video-editing-agent-bot/" in headers["User-Agent"]
    assert "github.com/orange-lee-tech/video-editing-agent" in headers["User-Agent"]


def test_mime_mismatch_reports_expected_and_received_types(tmp_path: Path) -> None:
    factory = ConnectionFactory(
        FakeResponse(
            200,
            {
                "Content-Type": "audio/x-flac",
            },
        )
    )

    result = WikimediaAudioAcquirer(
        tmp_path / "provider_audio",
        resolver=resolver,
        connection_factory=factory,
    ).acquire(request(expected_content_type="audio/flac"))

    assert not result.is_acquired
    diagnostic = result.diagnostics[0]
    assert diagnostic.code is AudioAcquisitionDiagnosticCode.SOURCE_METADATA_CHANGED
    assert not diagnostic.retryable
    assert "expected=audio/flac" in diagnostic.message
    assert "received=audio/x-flac" in diagnostic.message
