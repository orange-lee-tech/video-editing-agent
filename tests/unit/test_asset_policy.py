from video_editing_agent.domain.asset.policy import (
    AssetOrigin,
    AssetUsageRole,
    LegacyVisualOriginDisposition,
    classify_legacy_visual_origin,
    is_visual_resolver_eligible,
)


def test_local_editable_visual_is_resolver_candidate() -> None:
    assert is_visual_resolver_eligible(
        media_kind="video",
        origin=AssetOrigin.IMPORTED_LOCAL,
        usage_role=AssetUsageRole.EDITABLE_VISUAL_FOOTAGE,
    )


def test_reference_video_is_never_eligible_by_locality_alone() -> None:
    assert not is_visual_resolver_eligible(
        media_kind="video",
        origin="captured",
        usage_role=AssetUsageRole.REFERENCE_ANALYSIS_ONLY,
    )


def test_audio_role_is_not_visual_resolver_eligible() -> None:
    assert not is_visual_resolver_eligible(
        media_kind="audio",
        origin=AssetOrigin.IMPORTED_LOCAL,
        usage_role=AssetUsageRole.MUSIC,
    )


def test_legacy_remote_and_generated_visual_origins_are_restricted() -> None:
    assert (
        classify_legacy_visual_origin("remote_allowed")
        is LegacyVisualOriginDisposition.RESTRICTED_REMOTE
    )
    assert (
        classify_legacy_visual_origin("generated_allowed")
        is LegacyVisualOriginDisposition.RESTRICTED_GENERATED
    )
    assert not is_visual_resolver_eligible(
        media_kind="video",
        origin="remote_allowed",
        usage_role=AssetUsageRole.EDITABLE_VISUAL_FOOTAGE,
    )


def test_unknown_legacy_visual_origin_fails_closed() -> None:
    assert (
        classify_legacy_visual_origin("mystery-provider")
        is LegacyVisualOriginDisposition.RESTRICTED_UNKNOWN
    )
