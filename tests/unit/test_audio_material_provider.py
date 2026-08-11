from video_editing_agent.application.ports.audio_material_provider import (
    AudioMaterialCandidate,
    MusicDiscoveryQuery,
)
from video_editing_agent.domain.asset.rights import RightsEligibility


def test_music_discovery_defaults_generated_audio_off() -> None:
    query = MusicDiscoveryQuery("warm acoustic product music")

    assert query.commercial_use_required
    assert not query.generated_audio_allowed


def test_audio_candidate_carries_rights_state_without_becoming_asset() -> None:
    candidate = AudioMaterialCandidate(
        provider="example",
        provider_item_id="track-1",
        rights_eligibility=RightsEligibility.WARNING,
        title="Example track",
    )

    assert candidate.rights_eligibility is RightsEligibility.WARNING
