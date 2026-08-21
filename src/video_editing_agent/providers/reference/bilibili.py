from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit

from video_editing_agent.application.ports.reference_acquisition import (
    ReferenceAcquisitionDiagnosticCode,
)
from video_editing_agent.providers.reference.direct_https import (
    DiscoveredReferenceMedia,
    HtmlReferenceResolutionError,
)

_BVID_PATH = re.compile(r"^/video/(?P<bvid>BV[0-9A-Za-z]+)(?:/)?$")
_PLAYINFO_MARKER = re.compile(rb"window\.__playinfo__\s*=\s*")
_PAGELIST_PATH = "/x/player/pagelist"
_PLAYURL_PATH = "/x/player/playurl"


def _playinfo(html: bytes) -> Mapping[str, Any] | None:
    marker = _PLAYINFO_MARKER.search(html)
    if marker is None:
        return None
    source = html[marker.end() :].decode("utf-8", errors="replace")
    try:
        value, _end = json.JSONDecoder().raw_decode(source)
    except (json.JSONDecodeError, UnicodeError) as error:
        raise HtmlReferenceResolutionError(
            ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE,
            f"Bilibili page playback metadata is malformed: {error}",
        ) from error
    return value if isinstance(value, Mapping) else None


def _text(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _candidate_url(value: Mapping[str, Any]) -> str | None:
    return _text(value.get("baseUrl")) or _text(value.get("base_url"))


def _bandwidth(value: Mapping[str, Any]) -> int:
    raw = value.get("bandwidth")
    return raw if isinstance(raw, int) and not isinstance(raw, bool) else 0


def _json_object(payload: bytes, *, label: str) -> Mapping[str, Any]:
    try:
        value = json.loads(payload)
    except (json.JSONDecodeError, UnicodeError) as error:
        raise HtmlReferenceResolutionError(
            ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE,
            f"Bilibili {label} metadata is malformed",
        ) from error
    if not isinstance(value, Mapping):
        raise HtmlReferenceResolutionError(
            ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE,
            f"Bilibili {label} metadata is not an object",
        )
    return value


def _bvid_from_query(page_url: str) -> str | None:
    values = parse_qs(urlsplit(page_url).query).get("bvid", ())
    if len(values) != 1 or _BVID_PATH.fullmatch(f"/video/{values[0]}") is None:
        return None
    return values[0]


def _referer(bvid: str) -> tuple[tuple[str, str], ...]:
    return (("Referer", f"https://www.bilibili.com/video/{bvid}"),)


def _metadata_candidate(url: str, bvid: str) -> DiscoveredReferenceMedia:
    return DiscoveredReferenceMedia(
        url,
        provider="bilibili_public_page",
        provider_item_id=bvid,
        request_headers=_referer(bvid),
        metadata=True,
    )


def _media_candidates(data: Mapping[str, Any], bvid: str) -> tuple[DiscoveredReferenceMedia, ...]:
    if data.get("is_preview") == 1:
        raise HtmlReferenceResolutionError(
            ReferenceAcquisitionDiagnosticCode.PROTECTED_CONTENT,
            "Bilibili page exposes preview-only protected media",
        )
    dash = data.get("dash")
    representations = dash.get("video") if isinstance(dash, Mapping) else None
    if not isinstance(representations, list):
        raise HtmlReferenceResolutionError(
            ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE,
            "Bilibili page did not expose a supported DASH video representation",
        )
    supported = tuple(
        item
        for item in representations
        if isinstance(item, Mapping)
        and _candidate_url(item) is not None
        and _text(item.get("mimeType")) == "video/mp4"
        and (_text(item.get("codecs")) or "").casefold().startswith("avc1")
    )
    if not supported:
        raise HtmlReferenceResolutionError(
            ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE,
            "Bilibili page has no anonymous AVC/MP4 video representation",
        )
    ordered = sorted(supported, key=lambda item: (-_bandwidth(item), _candidate_url(item) or ""))
    return tuple(
        DiscoveredReferenceMedia(
            _candidate_url(item) or "",
            provider="bilibili_public_page",
            provider_item_id=bvid,
            request_headers=_referer(bvid),
        )
        for item in ordered
    )


class BilibiliHtmlReferenceResolver:
    """Resolve anonymous public Bilibili page metadata without owning transport policy."""

    def resolve(self, page_url: str, html: bytes) -> tuple[DiscoveredReferenceMedia, ...]:
        parts = urlsplit(page_url)
        if parts.hostname == "api.bilibili.com" and parts.path == _PAGELIST_PATH:
            bvid = _bvid_from_query(page_url)
            payload = _json_object(html, label="page-list")
            data = payload.get("data")
            if payload.get("code") != 0 or not isinstance(data, list) or not data:
                raise HtmlReferenceResolutionError(
                    ReferenceAcquisitionDiagnosticCode.PROTECTED_CONTENT,
                    "Bilibili page-list metadata is unavailable anonymously",
                )
            cid = data[0].get("cid") if isinstance(data[0], Mapping) else None
            if bvid is None or isinstance(cid, bool) or not isinstance(cid, int) or cid <= 0:
                raise HtmlReferenceResolutionError(
                    ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE,
                    "Bilibili page-list metadata omitted a valid public part identifier",
                )
            query = urlencode(
                {"bvid": bvid, "cid": cid, "qn": 32, "fnval": 16, "fnver": 0, "fourk": 0}
            )
            return (_metadata_candidate(f"https://api.bilibili.com{_PLAYURL_PATH}?{query}", bvid),)
        if parts.hostname == "api.bilibili.com" and parts.path == _PLAYURL_PATH:
            bvid = _bvid_from_query(page_url)
            payload = _json_object(html, label="playback")
            if payload.get("code") != 0:
                raise HtmlReferenceResolutionError(
                    ReferenceAcquisitionDiagnosticCode.PROTECTED_CONTENT,
                    "Bilibili playback metadata is unavailable without additional authorization",
                )
            data = payload.get("data")
            if bvid is None or not isinstance(data, Mapping):
                raise HtmlReferenceResolutionError(
                    ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE,
                    "Bilibili playback metadata omitted media data",
                )
            return _media_candidates(data, bvid)
        if parts.hostname is None or parts.hostname.casefold() not in {
            "www.bilibili.com",
            "bilibili.com",
        }:
            return ()
        matched = _BVID_PATH.fullmatch(parts.path)
        if matched is None:
            return ()
        bvid = matched.group("bvid")
        playinfo = _playinfo(html)
        if playinfo is None:
            query = urlencode({"bvid": bvid})
            return (
                _metadata_candidate(
                    f"https://api.bilibili.com{_PAGELIST_PATH}?{query}",
                    bvid,
                ),
            )
        if playinfo.get("code") != 0:
            raise HtmlReferenceResolutionError(
                ReferenceAcquisitionDiagnosticCode.PROTECTED_CONTENT,
                "Bilibili playback metadata is unavailable without additional authorization",
            )
        data = playinfo.get("data")
        if not isinstance(data, Mapping):
            raise HtmlReferenceResolutionError(
                ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE,
                "Bilibili playback metadata omitted media data",
            )
        return _media_candidates(data, bvid)
