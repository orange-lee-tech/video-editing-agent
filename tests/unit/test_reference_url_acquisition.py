from __future__ import annotations

import hashlib
import json
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
from video_editing_agent.providers.reference.bilibili import BilibiliHtmlReferenceResolver
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
        self.connections: list[FakeConnection] = []

    def __call__(self, hostname: str, pinned_ip: str, port: int, timeout: float) -> FakeConnection:
        self.calls.append((hostname, pinned_ip, port, timeout))
        connection = FakeConnection(self.responses.pop(0))
        self.connections.append(connection)
        return connection


def bilibili_html(
    media_url: str,
    *,
    code: int = 0,
    is_preview: int = 0,
    codec: str = "avc1.64001F",
) -> bytes:
    payload = {
        "code": code,
        "data": {
            "is_preview": is_preview,
            "dash": {
                "video": [
                    {
                        "baseUrl": media_url,
                        "mimeType": "video/mp4",
                        "codecs": codec,
                        "bandwidth": 500_000,
                    }
                ]
            },
        },
    }
    return f"<script>window.__playinfo__={json.dumps(payload)}</script>".encode()


def bilibili_playurl_json(media_url: str, *, code: int = 0) -> bytes:
    return json.dumps(
        {
            "code": code,
            "data": {
                "dash": {
                    "video": [
                        {
                            "baseUrl": media_url,
                            "mimeType": "video/mp4",
                            "codecs": "avc1.64001F",
                            "bandwidth": 500_000,
                        }
                    ]
                }
            },
        }
    ).encode()


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


class StaticVideoOnlyProbe:
    def probe(self, path: Path) -> MediaTechnicalMetadata:
        assert path.is_file()
        return MediaTechnicalMetadata(
            media_kind="video",
            duration_ms=1_000,
            width=852,
            height=480,
            fps=30.0,
            codec="h264",
            audio_channels=None,
            sample_rate_hz=None,
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
    queue = ConnectionQueue(FakeResponse(302, headers={"Location": "https://public.example/next"}))
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


def test_html_page_declared_video_is_resolved_through_bounded_https_policy(
    tmp_path: Path,
) -> None:
    page = b'<html><video controls><source src="/media/reference.mp4"></video></html>'
    video = b"reference-video"
    queue = ConnectionQueue(
        FakeResponse(
            headers={"Content-Type": "text/html", "Content-Length": str(len(page))},
            chunks=(page, b""),
        ),
        FakeResponse(
            headers={"Content-Type": "video/mp4", "Content-Length": str(len(video))},
            chunks=(video, b""),
        ),
    )

    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=public_resolver,
        connection_factory=queue,
        clock=lambda: NOW,
    ).acquire(ReferenceAcquisitionRequest("https://social.example/watch/123"))

    assert result.is_acquired and result.acquired is not None
    assert result.acquired.original_url == "https://social.example/watch/123"
    assert result.acquired.final_url == "https://social.example/media/reference.mp4"
    assert result.acquired.local_path.read_bytes() == video
    assert len(queue.calls) == 2


def test_html_discovery_remains_bounded_and_does_not_follow_arbitrary_links(
    tmp_path: Path,
) -> None:
    page = b'<html><a href="https://other.example/video.mp4">watch</a></html>'
    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        policy=DirectHttpsAcquisitionPolicy(max_html_bytes=len(page)),
        resolver=public_resolver,
        connection_factory=ConnectionQueue(
            FakeResponse(headers={"Content-Type": "text/html"}, chunks=(page, b""))
        ),
    ).acquire(ReferenceAcquisitionRequest("https://social.example/watch/123"))

    assert not result.is_acquired
    assert result.diagnostics[0].code is ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE


def test_bilibili_public_page_resolves_media_through_existing_safe_transport(
    tmp_path: Path,
) -> None:
    page_url = "https://www.bilibili.com/video/BV1Mq4y187xR?share_source=copy_web"
    media_url = "https://public-cdn.example/video/reference.m4s?expires=bounded"
    page = bilibili_html(media_url)
    media = b"public-bilibili-video"
    queue = ConnectionQueue(
        FakeResponse(headers={"Content-Type": "text/html"}, chunks=(page, b"")),
        FakeResponse(headers={"Content-Type": "video/mp4"}, chunks=(media, b"")),
    )
    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=public_resolver,
        connection_factory=queue,
        html_media_resolvers=(BilibiliHtmlReferenceResolver(),),
        clock=lambda: NOW,
    ).acquire(ReferenceAcquisitionRequest(page_url))

    assert result.is_acquired and result.acquired is not None
    assert result.acquired.original_url == page_url
    assert result.acquired.final_url == media_url
    assert result.acquired.provider == "bilibili_public_page"
    assert result.acquired.provider_item_id == "BV1Mq4y187xR"
    assert result.acquired.local_path.read_bytes() == media
    assert queue.connections[1].requests[0][2]["Referer"] == (
        "https://www.bilibili.com/video/BV1Mq4y187xR"
    )


def test_bilibili_reduced_page_uses_bounded_anonymous_metadata_chain(tmp_path: Path) -> None:
    page_url = "https://www.bilibili.com/video/BV1Mq4y187xR?share_source=copy_web"
    media_url = "https://public-cdn.example/video/reference.m4s"
    page_list = json.dumps({"code": 0, "data": [{"cid": 17}]}).encode()
    media = b"public-bilibili-video"
    queue = ConnectionQueue(
        FakeResponse(headers={"Content-Type": "text/html"}, chunks=(b"<html></html>", b"")),
        FakeResponse(headers={"Content-Type": "application/json"}, chunks=(page_list, b"")),
        FakeResponse(
            headers={"Content-Type": "application/json"},
            chunks=(bilibili_playurl_json(media_url), b""),
        ),
        FakeResponse(headers={"Content-Type": "video/mp4"}, chunks=(media, b"")),
    )

    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=public_resolver,
        connection_factory=queue,
        html_media_resolvers=(BilibiliHtmlReferenceResolver(),),
        clock=lambda: NOW,
    ).acquire(ReferenceAcquisitionRequest(page_url))

    assert result.is_acquired and result.acquired is not None
    assert result.acquired.final_url == media_url
    assert result.acquired.provider_item_id == "BV1Mq4y187xR"
    assert [call[0] for call in queue.calls] == [
        "www.bilibili.com",
        "api.bilibili.com",
        "api.bilibili.com",
        "public-cdn.example",
    ]
    assert all(
        connection.requests[0][2].get("Referer") == "https://www.bilibili.com/video/BV1Mq4y187xR"
        for connection in queue.connections[1:]
    )


def test_bilibili_acquired_video_only_media_is_valid_for_reference_ingest(tmp_path: Path) -> None:
    media_url = "https://public-cdn.example/video/reference.m4s"
    queue = ConnectionQueue(
        FakeResponse(
            headers={"Content-Type": "text/html"},
            chunks=(bilibili_html(media_url), b""),
        ),
        FakeResponse(headers={"Content-Type": "video/mp4"}, chunks=(b"video-only", b"")),
    )
    acquired = (
        DirectHttpsReferenceAcquirer(
            tmp_path / "reference_media",
            resolver=public_resolver,
            connection_factory=queue,
            html_media_resolvers=(BilibiliHtmlReferenceResolver(),),
            clock=lambda: NOW,
        )
        .acquire(ReferenceAcquisitionRequest("https://www.bilibili.com/video/BV1Mq4y187xR"))
        .acquired
    )
    assert acquired is not None

    asset = AssetIngestService(StaticVideoOnlyProbe()).ingest(
        LocalMediaSource(
            acquired.local_path,
            "reference_https",
            AssetProvenance(
                origin_type="reference_https",
                source_page=acquired.original_url,
                provider=acquired.provider,
                provider_asset_id=acquired.provider_item_id,
                retrieved_at=acquired.retrieved_at,
            ),
            AssetUsageRole.REFERENCE_ANALYSIS_ONLY,
        ),
        created_by="test",
    )

    assert asset.media_kind == "video"
    assert asset.audio_channels is None
    assert asset.usage_role is AssetUsageRole.REFERENCE_ANALYSIS_ONLY


def test_unexpected_json_is_not_treated_as_provider_metadata(tmp_path: Path) -> None:
    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=public_resolver,
        connection_factory=ConnectionQueue(
            FakeResponse(headers={"Content-Type": "application/json"}, chunks=(b"{}", b""))
        ),
        html_media_resolvers=(BilibiliHtmlReferenceResolver(),),
    ).acquire(
        ReferenceAcquisitionRequest("https://api.bilibili.com/x/player/pagelist?bvid=BV1Mq4y187xR")
    )

    assert not result.is_acquired
    assert result.diagnostics[0].code is ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE


def test_bilibili_metadata_target_is_revalidated_before_request(tmp_path: Path) -> None:
    queue = ConnectionQueue(
        FakeResponse(headers={"Content-Type": "text/html"}, chunks=(b"<html></html>", b""))
    )

    def resolver(hostname: str, _port: int) -> tuple[str, ...]:
        return (PUBLIC_IP,) if hostname == "www.bilibili.com" else ("127.0.0.1",)

    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=resolver,
        connection_factory=queue,
        html_media_resolvers=(BilibiliHtmlReferenceResolver(),),
    ).acquire(ReferenceAcquisitionRequest("https://www.bilibili.com/video/BV1Mq4y187xR"))

    assert not result.is_acquired
    assert result.diagnostics[0].code is ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED
    assert len(queue.connections) == 1


def test_bilibili_discovered_private_target_is_revalidated_and_rejected(
    tmp_path: Path,
) -> None:
    page = bilibili_html("https://private.example/video.m4s")
    queue = ConnectionQueue(FakeResponse(headers={"Content-Type": "text/html"}, chunks=(page, b"")))

    def resolver(hostname: str, _port: int) -> tuple[str, ...]:
        return (PUBLIC_IP,) if hostname == "www.bilibili.com" else ("127.0.0.1",)

    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=resolver,
        connection_factory=queue,
        html_media_resolvers=(BilibiliHtmlReferenceResolver(),),
    ).acquire(ReferenceAcquisitionRequest("https://www.bilibili.com/video/BV1Mq4y187xR"))

    assert not result.is_acquired
    assert result.diagnostics[0].code is ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED
    assert len(queue.connections) == 1


@pytest.mark.parametrize(
    ("page", "expected"),
    (
        (
            bilibili_html("https://public.example/video.m4s", code=-10403),
            ReferenceAcquisitionDiagnosticCode.PROTECTED_CONTENT,
        ),
        (
            bilibili_html("https://public.example/video.m4s", is_preview=1),
            ReferenceAcquisitionDiagnosticCode.PROTECTED_CONTENT,
        ),
        (
            bilibili_html("https://public.example/video.m4s", codec="hev1.1.6.L120"),
            ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE,
        ),
    ),
)
def test_bilibili_protected_and_unsupported_states_fail_closed(
    tmp_path: Path,
    page: bytes,
    expected: ReferenceAcquisitionDiagnosticCode,
) -> None:
    result = DirectHttpsReferenceAcquirer(
        tmp_path / "reference_media",
        resolver=public_resolver,
        connection_factory=ConnectionQueue(
            FakeResponse(headers={"Content-Type": "text/html"}, chunks=(page, b""))
        ),
        html_media_resolvers=(BilibiliHtmlReferenceResolver(),),
    ).acquire(ReferenceAcquisitionRequest("https://www.bilibili.com/video/BV1Mq4y187xR"))

    assert not result.is_acquired
    assert result.diagnostics[0].code is expected


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
