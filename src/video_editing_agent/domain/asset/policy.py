from __future__ import annotations

from enum import StrEnum


class AssetOrigin(StrEnum):
    """Active v0.2 origin categories. Origin answers where media came from, not how it may be used."""

    CAPTURED_LOCAL = "captured_local"
    IMPORTED_LOCAL = "imported_local"
    PROVIDER_ACQUIRED_AUDIO = "provider_acquired_audio"


class AssetUsageRole(StrEnum):
    """Declared role controlling how an Asset may participate in product workflows."""

    EDITABLE_VISUAL_FOOTAGE = "editable_visual_footage"
    REFERENCE_ANALYSIS_ONLY = "reference_analysis_only"
    MUSIC = "music"
    VOICEOVER = "voiceover"
    SOUND_EFFECT = "sound_effect"
    LOGO_GRAPHIC = "logo_graphic"
    OTHER_LOCAL_MEDIA = "other_local_media"


class LegacyVisualOriginDisposition(StrEnum):
    LOCAL_CANDIDATE = "local_candidate"
    RESTRICTED_REMOTE = "restricted_remote"
    RESTRICTED_GENERATED = "restricted_generated"
    RESTRICTED_UNKNOWN = "restricted_unknown"


_LOCAL_VISUAL_ORIGIN_ALIASES = frozenset(
    {
        "captured",
        "captured_local",
        "imported",
        "imported_local",
        "local",
        "local_only",
    }
)
_REMOTE_VISUAL_ORIGIN_ALIASES = frozenset(
    {
        "remote",
        "remote_allowed",
        "remote_only",
        "public_stock",
        "stock",
    }
)
_GENERATED_VISUAL_ORIGIN_ALIASES = frozenset(
    {
        "generated",
        "generated_allowed",
        "synthetic_visual",
    }
)


def classify_legacy_visual_origin(origin: str | AssetOrigin) -> LegacyVisualOriginDisposition:
    """Conservatively map old string origins without reviving remote/generated visual fallback."""

    normalized = str(origin).strip().casefold()
    if normalized in _LOCAL_VISUAL_ORIGIN_ALIASES:
        return LegacyVisualOriginDisposition.LOCAL_CANDIDATE
    if normalized in _REMOTE_VISUAL_ORIGIN_ALIASES:
        return LegacyVisualOriginDisposition.RESTRICTED_REMOTE
    if normalized in _GENERATED_VISUAL_ORIGIN_ALIASES:
        return LegacyVisualOriginDisposition.RESTRICTED_GENERATED
    return LegacyVisualOriginDisposition.RESTRICTED_UNKNOWN


def is_visual_resolver_eligible(
    *,
    media_kind: str,
    origin: str | AssetOrigin,
    usage_role: AssetUsageRole,
) -> bool:
    """Return the constitutional baseline eligibility before rights/locks/content constraints."""

    if media_kind.strip().casefold() not in {"video", "image"}:
        return False
    if usage_role is not AssetUsageRole.EDITABLE_VISUAL_FOOTAGE:
        return False
    return classify_legacy_visual_origin(origin) is LegacyVisualOriginDisposition.LOCAL_CANDIDATE
