from __future__ import annotations

import hashlib
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.application.ports.reference_acquisition import (
    ReferenceAcquisitionDiagnosticCode,
    ReferenceAcquisitionRequest,
)
from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.asset.policy import (
    AssetOrigin,
    AssetUsageRole,
    default_asset_usage_role,
    is_visual_resolver_eligible,
)
from video_editing_agent.media.ingest.probe import MediaTechnicalMetadata
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.providers.reference.direct_https import (
    DirectHttpsAcquisitionPolicy,
    DirectHttpsReferenceAcquirer,
)

PUBLIC_IP = "93.184.216.34"
NOW = datetime(2026, 8, 17, 9, 30, tzinfo=UTC)


class FakeResponse:
    def __init__(
        self,
        status: int = 200,
        *,
        headers: dict[str, str] | None = None,
        chunks: tuple[bytes, ...] = (b"reference-video", b""),
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


class StaticVideoProbe:
    def probe(self, path: Path) -> MediaTechnicalMetadata:
        assert path.is_file()
        return MediaTechnicalMetadata(
            media_kind="video",
            duration_ms=1_000,
            width=1080,
            height=1920,
            fps=30.0,
            codec="h264",
            audio_channels=2,
            sample_rate_hz=48_000,
        )


def public_resolver(hostname: str, port: int) -> tuple[str, ...]:
    assert hostname
    assert port > 0
    return (PUBLIC_IP,)


def test_direct_https_acquisition_is_content_addressed_and_deduplicated(tmp_path: Path) -> None:
    payload = b"reference-video"
    first_queue = ConnectionQueue(
        FakeResponse(
            headers={"Content-Type": "video/mp4", "Content-Length": str(len(payload))},
            chunks=(payload, b""),
        )
    )
    root = tmp_path / "reference_media"
    first = DirectHttpsReferenceAcquirer(
        root,
        resolver=public_resolver,
        connection_factory=first_queue,
        clock=lambda: NOW,
    ).acquire(ReferenceAcquisitionRequest("https://media.example/reference.mp4?token=public"))

    assert first.is_acquired and first.acquired is not None
    digest = hashlib.sha256(payload).hexdigest()
    assert first.acquired.content_hash == f"sha256:{digest}"
    assert first.acquired.byte_size == len(payload)
    assert first.acquired.local_path == (root / "sha256" / digest[:2] / f"{digest}.media").resolve()
    assert first.acquired.local_path.read_bytes() == payload
    assert first.acquired.original_url.endswith("reference.mp4?token=public")
    assert first.acquired.final_url == first.acquired.original_url
    assert first.acquired.provider == "direct_https"
    assert first.acquired.content_type == "video/mp4"
    assert first_queue.calls[0][1] == PUBLIC_IP

    second_queue = ConnectionQueue(
        FakeResponse(headers={"Content-Type": "video/mp4"}, chunks=(payload, b""))
    )
    second = DirectHttpsReferenceAcquirer(
        root,
        resolver=public_resolver,
        connection_factory=second_queue,
        clock=lambda: NOW,
    ).acquire(ReferenceAcquisitionRequest("https://other.example/not-the-local-name.exe"))

    assert second.is_acquired and second.acquired is not None
    assert second.acquired.local_path == first.acquired.local_path
    assert tuple((root / ".partial").iterdir()) == ()


@pytest.mark.parametrize(
    ("url", "expected"),
    (
        ("http://example.com/video.mp4", ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_SCHEME),
        (
            "https://user:password@example.com/video.mp4",
            ReferenceAcquisitionDiagnosticCode.CREDENTIALS_NOT_ALLOWED,
        ),
    ),
)
def test_url_shape_policy_fails_closed(
    tmp_path: Path,
    url: str,
    expected: ReferenceAcquisitionDiagnosticCode,
) -> None:
    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=public_resolver,
        connection_factory=ConnectionQueue(),
    ).acquire(ReferenceAcquisitionRequest(url))

    assert not result.is_acquired
    assert result.diagnostics[0].code is expected


def test_private_network_target_is_rejected_before_connection(tmp_path: Path) -> None:
    queue = ConnectionQueue()
    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=lambda _host, _port: ("127.0.0.1", "10.0.0.5"),
        connection_factory=queue,
    ).acquire(ReferenceAcquisitionRequest("https://localhost/video.mp4"))

    assert not result.is_acquired
    assert result.diagnostics[0].code is ReferenceAcquisitionDiagnosticCode.NETWORK_TARGET_REJECTED
    assert queue.calls == []


def test_redirect_revalidates_target_and_rejects_private_destination(tmp_path: Path) -> None:
    queue = ConnectionQueue(
        FakeResponse(302, headers={"Location": "https://private.example/video.mp4"})
    )

    def resolver(hostname: str, _port: int) -> tuple[str, ...]:
        return (PUBLIC_IP,) if hostname == "public.example" else ("192.168.1.2",)

    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=resolver,
        connection_factory=queue,
    ).acquire(ReferenceAcquisitionRequest("https://public.example/reference"))

    assert not result.is_acquired
    assert result.diagnostics[0].code is ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED
    assert len(queue.calls) == 1


def test_redirect_limit_is_fail_closed(tmp_path: Path) -> None:
    queue = ConnectionQueue(
        FakeResponse(302, headers={"Location": "https://public.example/next"})
    )
    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        policy=DirectHttpsAcquisitionPolicy(max_redirects=0),
        resolver=public_resolver,
        connection_factory=queue,
    ).acquire(ReferenceAcquisitionRequest("https://public.example/reference"))

    assert not result.is_acquired
    assert result.diagnostics[0].code is ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED


def test_declared_and_streaming_size_limits_fail_and_cleanup(tmp_path: Path) -> None:
    root = tmp_path / "reference_media"
    declared = DirectHttpsReferenceAcquirer(
        root,
        policy=DirectHttpsAcquisitionPolicy(max_bytes=5),
        resolver=public_resolver,
        connection_factory=ConnectionQueue(
            FakeResponse(
                headers={"Content-Type": "video/mp4", "Content-Length": "6"},
                chunks=(b"123456", b""),
            )
        ),
    ).acquire(ReferenceAcquisitionRequest("https://example.com/declared.mp4"))
    assert declared.diagnostics[0].code is ReferenceAcquisitionDiagnosticCode.SIZE_LIMIT_EXCEEDED

    streaming = DirectHttpsReferenceAcquirer(
        root,
        policy=DirectHttpsAcquisitionPolicy(max_bytes=5),
        resolver=public_resolver,
        connection_factory=ConnectionQueue(
            FakeResponse(headers={"Content-Type": "video/mp4"}, chunks=(b"1234", b"56", b""))
        ),
    ).acquire(ReferenceAcquisitionRequest("https://example.com/stream.mp4"))
    assert streaming.diagnostics[0].code is ReferenceAcquisitionDiagnosticCode.SIZE_LIMIT_EXCEEDED
    assert tuple((root / ".partial").iterdir()) == ()
    assert not any((root / "sha256").rglob("*.media"))


def test_html_page_is_not_treated_as_direct_reference_media(tmp_path: Path) -> None:
    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=public_resolver,
        connection_factory=ConnectionQueue(
            FakeResponse(headers={"Content-Type": "text/html; charset=utf-8"})
        ),
    ).acquire(ReferenceAcquisitionRequest("https://social.example/watch/123"))

    assert not result.is_acquired
    assert result.diagnostics[0].code is ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE


def test_acquired_reference_ingests_with_remote_origin_and_analysis_only_role(
    tmp_path: Path,
) -> None:
    payload = b"reference-video"
    acquisition = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=public_resolver,
        connection_factory=ConnectionQueue(
            FakeResponse(headers={"Content-Type": "video/mp4"}, chunks=(payload, b""))
        ),
        clock=lambda: NOW,
    ).acquire(ReferenceAcquisitionRequest("https://media.example/reference.mp4"))
    assert acquisition.is_acquired and acquisition.acquired is not None
    acquired = acquisition.acquired

    asset = AssetIngestService(
        StaticVideoProbe(),
        asset_id_factory=lambda: "ast_reference_acquired",
        clock=lambda: NOW,
    ).ingest(
        LocalMediaSource(
            acquired.local_path,
            AssetOrigin.REFERENCE_ACQUIRED,
            AssetProvenance(
                origin_type=AssetOrigin.REFERENCE_ACQUIRED,
                provider=acquired.provider,
                source_page=acquired.original_url,
                retrieved_at=acquired.retrieved_at,
            ),
            AssetUsageRole.REFERENCE_ANALYSIS_ONLY,
        ),
        created_by="reference-acquisition",
    )

    assert asset.origin == AssetOrigin.REFERENCE_ACQUIRED
    assert asset.usage_role is AssetUsageRole.REFERENCE_ANALYSIS_ONLY
    assert asset.provenance.source_page == acquired.original_url
    assert asset.content_hash == acquired.content_hash
    assert not is_visual_resolver_eligible(
        media_kind=asset.media_kind,
        origin=asset.origin,
        usage_role=asset.usage_role,
    )
    assert (
        default_asset_usage_role(media_kind="video", origin=AssetOrigin.REFERENCE_ACQUIRED)
        is AssetUsageRole.RESTRICTED_LEGACY_VISUAL
    )
