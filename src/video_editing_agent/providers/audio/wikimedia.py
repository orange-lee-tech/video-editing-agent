from __future__ import annotations

import hashlib
import html
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from html.parser import HTMLParser
from typing import cast
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from video_editing_agent.application.ports.artifact_store import ArtifactPayload, ArtifactStore
from video_editing_agent.domain.asset.rights import LicenseSnapshot, RightsEligibility

_COMMONS_API = "https://commons.wikimedia.org/w/api.php"
_COMMONS_PAGE_ID_PREFIX = "commons_pageid:"
_USER_AGENT = "video-editing-agent-bot/0.1 (https://github.com/orange-lee-tech/video-editing-agent)"
JsonObject = dict[str, object]
JsonFetcher = Callable[[str], JsonObject]
Clock = Callable[[], datetime]


class WikimediaRightsDiagnosticCode(StrEnum):
    SOURCE_MISSING = "source_missing"
    SOURCE_METADATA_INVALID = "source_metadata_invalid"
    UNSUPPORTED_MEDIA_TYPE = "unsupported_media_type"
    RIGHTS_INELIGIBLE = "rights_ineligible"
    RIGHTS_UNKNOWN = "rights_unknown"
    SOURCE_URL_REJECTED = "source_url_rejected"


@dataclass(frozen=True, slots=True)
class WikimediaRightsDiagnostic:
    code: WikimediaRightsDiagnosticCode
    message: str

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("Wikimedia rights diagnostic message must not be empty")


@dataclass(frozen=True, slots=True)
class VerifiedWikimediaAudio:
    provider_item_id: str
    source_page: str
    source_url: str
    source_sha1: str
    byte_size: int
    mime_type: str
    creator: str | None
    license_identifier: str
    license_url: str | None
    attribution_text: str | None
    attribution_required: bool
    snapshot: LicenseSnapshot
    rights_artifact_ref: str

    def __post_init__(self) -> None:
        for name, value in (
            ("provider_item_id", self.provider_item_id),
            ("source_page", self.source_page),
            ("source_url", self.source_url),
            ("source_sha1", self.source_sha1),
            ("mime_type", self.mime_type),
            ("license_identifier", self.license_identifier),
            ("rights_artifact_ref", self.rights_artifact_ref),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if isinstance(self.byte_size, bool) or not isinstance(self.byte_size, int):
            raise TypeError("byte_size must be an int")
        if self.byte_size <= 0:
            raise ValueError("byte_size must be > 0")


@dataclass(frozen=True, slots=True)
class WikimediaVerificationResult:
    verified: VerifiedWikimediaAudio | None
    diagnostics: tuple[WikimediaRightsDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        if self.verified is None and not self.diagnostics:
            raise ValueError("failed Wikimedia verification requires diagnostics")
        if self.verified is not None and self.diagnostics:
            raise ValueError("successful Wikimedia verification must not contain diagnostics")

    @property
    def is_verified(self) -> bool:
        return self.verified is not None and not self.diagnostics


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if value:
            self.parts.append(value)


def _plain_text(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parser = _TextExtractor()
    parser.feed(html.unescape(value))
    normalized = " ".join(parser.parts).strip()
    return normalized or None


def _metadata_value(metadata: JsonObject, key: str) -> str | None:
    raw = metadata.get(key)
    if not isinstance(raw, dict):
        return None
    return _plain_text(cast(JsonObject, raw).get("value"))


def _truthy_metadata(metadata: JsonObject, key: str) -> bool:
    value = _metadata_value(metadata, key)
    return value is not None and value.casefold() in {"1", "true", "yes"}


def _default_clock() -> datetime:
    return datetime.now(UTC)


def _default_json_fetcher(url: str) -> JsonObject:
    if urlsplit(url).hostname != "commons.wikimedia.org":
        raise ValueError("Wikimedia verifier only permits the Commons API host")
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": _USER_AGENT},
        method="GET",
    )
    with urlopen(request, timeout=30.0) as response:  # noqa: S310 - fixed Commons API host
        if response.status != 200:
            raise OSError(f"Wikimedia Commons returned HTTP {response.status}")
        return cast(JsonObject, json.loads(response.read().decode("utf-8")))


def _license_decision(
    *,
    license_short_name: str | None,
    license_url: str | None,
    non_free: bool,
    restrictions: str | None,
) -> tuple[RightsEligibility, str | None]:
    if non_free:
        return RightsEligibility.INELIGIBLE, "Commons metadata marks the file NonFree"
    if restrictions is not None:
        return RightsEligibility.INELIGIBLE, "Commons metadata contains reuse restrictions"
    if license_short_name is None:
        return RightsEligibility.UNKNOWN, "Commons metadata omitted LicenseShortName"

    name = license_short_name.casefold().replace("_", " ")
    url = "" if license_url is None else license_url.casefold()
    disallowed_markers = ("by-sa", "by-nc", "by-nd", "noncommercial", "no derivatives")
    if any(marker in name or marker in url for marker in disallowed_markers):
        return RightsEligibility.INELIGIBLE, "license is outside the automatic Stage-A whitelist"

    if "cc0" in name or "/publicdomain/zero/" in url:
        return RightsEligibility.ELIGIBLE, None
    if name in {"public domain", "public domain mark", "pdm"} or "/publicdomain/mark/" in url:
        return RightsEligibility.ELIGIBLE, None
    if "cc by" in name or "/licenses/by/" in url:
        return RightsEligibility.WARNING, None
    return RightsEligibility.UNKNOWN, "license is not recognized by the automatic Stage-A whitelist"


def _verification_url(provider_item_id: str) -> str:
    identity = provider_item_id.strip()
    parameters = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
        "prop": "imageinfo",
        "iiprop": "url|sha1|size|mime|mediatype|extmetadata",
        "iiextmetadatalanguage": "en",
        "iiextmetadatafilter": (
            "Artist|Credit|Attribution|AttributionRequired|LicenseShortName|LicenseUrl|"
            "UsageTerms|Copyrighted|NonFree|Restrictions"
        ),
    }
    if identity.casefold().startswith("file:"):
        parameters["titles"] = identity
    elif identity.casefold().startswith(_COMMONS_PAGE_ID_PREFIX):
        page_id = identity[len(_COMMONS_PAGE_ID_PREFIX) :]
        if not page_id.isdigit() or int(page_id) <= 0:
            raise ValueError("Commons page identity contains an invalid page ID")
        parameters["pageids"] = page_id
    else:
        raise ValueError(
            "Commons identity must be a File: title or commons_pageid:<positive integer>"
        )
    return f"{_COMMONS_API}?{urlencode(parameters)}"


class WikimediaAudioRightsVerifier:
    """Re-verify one Commons file against current source metadata and persist evidence."""

    def __init__(
        self,
        artifact_store: ArtifactStore,
        *,
        json_fetcher: JsonFetcher = _default_json_fetcher,
        clock: Clock = _default_clock,
    ) -> None:
        self._artifact_store = artifact_store
        self._json_fetcher = json_fetcher
        self._clock = clock

    def verify(self, provider_item_id: str) -> WikimediaVerificationResult:
        discovery_identity = provider_item_id.strip()
        try:
            verification_url = _verification_url(discovery_identity)
        except ValueError as error:
            return self._failure(
                WikimediaRightsDiagnosticCode.SOURCE_METADATA_INVALID,
                str(error),
            )

        payload = self._json_fetcher(verification_url)
        raw_artifact = self._artifact_store.put(
            ArtifactPayload(
                "application/json",
                json.dumps(
                    payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ).encode("utf-8"),
            )
        )
        page = self._page(payload)
        if page is None or "missing" in page:
            return self._failure(
                WikimediaRightsDiagnosticCode.SOURCE_MISSING,
                "Wikimedia Commons file is missing or unavailable",
            )
        page_title = page.get("title")
        if (
            not isinstance(page_title, str)
            or not page_title.strip()
            or not page_title.casefold().startswith("file:")
        ):
            return self._failure(
                WikimediaRightsDiagnosticCode.SOURCE_METADATA_INVALID,
                "Wikimedia response did not resolve the identity to a canonical File: title",
            )
        raw_imageinfo = page.get("imageinfo")
        if (
            not isinstance(raw_imageinfo, list)
            or not raw_imageinfo
            or not isinstance(raw_imageinfo[0], dict)
        ):
            return self._failure(
                WikimediaRightsDiagnosticCode.SOURCE_MISSING,
                "Wikimedia response omitted current file imageinfo",
            )
        imageinfo = cast(JsonObject, raw_imageinfo[0])
        source_url = imageinfo.get("url")
        source_page = imageinfo.get("descriptionurl")
        source_sha1 = imageinfo.get("sha1")
        mime_type = imageinfo.get("mime")
        byte_size = imageinfo.get("size")
        if not all(
            isinstance(value, str) and value.strip()
            for value in (source_url, source_page, source_sha1, mime_type)
        ):
            return self._failure(
                WikimediaRightsDiagnosticCode.SOURCE_METADATA_INVALID,
                "Wikimedia response omitted required source URL/hash/MIME metadata",
            )
        assert isinstance(source_url, str)
        assert isinstance(source_page, str)
        assert isinstance(source_sha1, str)
        assert isinstance(mime_type, str)
        if isinstance(byte_size, bool) or not isinstance(byte_size, int) or byte_size <= 0:
            return self._failure(
                WikimediaRightsDiagnosticCode.SOURCE_METADATA_INVALID,
                "Wikimedia response omitted a valid file size",
            )
        if not mime_type.casefold().startswith("audio/"):
            return self._failure(
                WikimediaRightsDiagnosticCode.UNSUPPORTED_MEDIA_TYPE,
                f"Wikimedia source is not audio media ({mime_type})",
            )
        source_parts = urlsplit(source_url)
        if (
            source_parts.scheme.casefold() != "https"
            or source_parts.hostname != "upload.wikimedia.org"
            or source_parts.username is not None
            or source_parts.password is not None
        ):
            return self._failure(
                WikimediaRightsDiagnosticCode.SOURCE_URL_REJECTED,
                "verified Wikimedia file URL is outside the approved upload host",
            )

        raw_extmetadata = imageinfo.get("extmetadata")
        if not isinstance(raw_extmetadata, dict):
            return self._failure(
                WikimediaRightsDiagnosticCode.RIGHTS_UNKNOWN,
                "Wikimedia response omitted extended license metadata",
            )
        extmetadata = cast(JsonObject, raw_extmetadata)
        license_short = _metadata_value(extmetadata, "LicenseShortName")
        license_url = _metadata_value(extmetadata, "LicenseUrl")
        restrictions = _metadata_value(extmetadata, "Restrictions")
        eligibility, reason = _license_decision(
            license_short_name=license_short,
            license_url=license_url,
            non_free=_truthy_metadata(extmetadata, "NonFree"),
            restrictions=restrictions,
        )
        if eligibility is RightsEligibility.INELIGIBLE:
            return self._failure(
                WikimediaRightsDiagnosticCode.RIGHTS_INELIGIBLE,
                reason or "Wikimedia license is not automatically eligible",
            )
        if eligibility is RightsEligibility.UNKNOWN:
            return self._failure(
                WikimediaRightsDiagnosticCode.RIGHTS_UNKNOWN,
                reason or "Wikimedia rights metadata is insufficient",
            )
        assert license_short is not None

        creator = _metadata_value(extmetadata, "Artist")
        credit = _metadata_value(extmetadata, "Credit")
        attribution = _metadata_value(extmetadata, "Attribution")
        attribution_required = _truthy_metadata(extmetadata, "AttributionRequired")
        attribution_text = attribution or credit or creator
        captured_at = self._clock()
        snapshot_seed = f"{page_title}|{source_sha1}|{captured_at.isoformat()}".encode()
        snapshot_id = f"lic_wikimedia_{hashlib.sha256(snapshot_seed).hexdigest()[:24]}"
        snapshot = LicenseSnapshot(
            snapshot_id=snapshot_id,
            provider="wikimedia_commons",
            provider_item_id=page_title,
            captured_at=captured_at,
            eligibility=eligibility,
            license_identifier=license_short,
            terms_ref=license_url,
            attribution_text=attribution_text,
            commercial_scope="verified_stage_a_commercial_reuse",
            advertising_scope="verified_stage_a_commercial_reuse",
            evidence_artifact_refs=(raw_artifact.artifact_id,),
        )
        normalized = {
            "snapshot_id": snapshot.snapshot_id,
            "captured_at": captured_at.isoformat(),
            "provider": snapshot.provider,
            "discovery_provider_item_id": discovery_identity,
            "provider_item_id": snapshot.provider_item_id,
            "eligibility": snapshot.eligibility.value,
            "license_identifier": snapshot.license_identifier,
            "license_url": license_url,
            "usage_terms": _metadata_value(extmetadata, "UsageTerms"),
            "creator": creator,
            "credit": credit,
            "attribution": attribution,
            "attribution_required": attribution_required,
            "restrictions": restrictions,
            "non_free": _truthy_metadata(extmetadata, "NonFree"),
            "copyrighted": _metadata_value(extmetadata, "Copyrighted"),
            "source_page": source_page,
            "source_url": source_url,
            "source_sha1": source_sha1.casefold(),
            "byte_size": byte_size,
            "mime_type": mime_type.casefold(),
            "raw_evidence_ref": raw_artifact.artifact_id,
        }
        normalized_artifact = self._artifact_store.put(
            ArtifactPayload(
                "application/json",
                json.dumps(
                    normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ).encode("utf-8"),
            )
        )
        snapshot = LicenseSnapshot(
            snapshot_id=snapshot.snapshot_id,
            provider=snapshot.provider,
            provider_item_id=snapshot.provider_item_id,
            captured_at=snapshot.captured_at,
            eligibility=snapshot.eligibility,
            license_identifier=snapshot.license_identifier,
            terms_ref=snapshot.terms_ref,
            attribution_text=snapshot.attribution_text,
            commercial_scope=snapshot.commercial_scope,
            advertising_scope=snapshot.advertising_scope,
            evidence_artifact_refs=(raw_artifact.artifact_id, normalized_artifact.artifact_id),
        )
        return WikimediaVerificationResult(
            VerifiedWikimediaAudio(
                provider_item_id=page_title,
                source_page=source_page,
                source_url=source_url,
                source_sha1=source_sha1.casefold(),
                byte_size=byte_size,
                mime_type=mime_type.casefold(),
                creator=creator,
                license_identifier=license_short,
                license_url=license_url,
                attribution_text=attribution_text,
                attribution_required=attribution_required,
                snapshot=snapshot,
                rights_artifact_ref=normalized_artifact.artifact_id,
            )
        )

    @staticmethod
    def _page(payload: JsonObject) -> JsonObject | None:
        raw_query = payload.get("query")
        if not isinstance(raw_query, dict):
            return None
        raw_pages = cast(JsonObject, raw_query).get("pages")
        if not isinstance(raw_pages, list) or not raw_pages or not isinstance(raw_pages[0], dict):
            return None
        return cast(JsonObject, raw_pages[0])

    @staticmethod
    def _failure(
        code: WikimediaRightsDiagnosticCode,
        message: str,
    ) -> WikimediaVerificationResult:
        return WikimediaVerificationResult(None, (WikimediaRightsDiagnostic(code, message),))
