import pytest

from video_editing_agent.planning.policy.builtin import (
    GENERIC_VERTICAL_SHORT_FORM_V1,
    NATURAL_VLOG_V1,
    PERFORMANCE_PRODUCT_AD_V1,
)
from video_editing_agent.planning.policy.model import (
    CommercialPolicySelection,
    CommercialSkill,
    CreativePrior,
    MarketingObjective,
)


def test_product_ad_and_natural_vlog_are_distinct_policy_paths() -> None:
    ad = CommercialPolicySelection(
        platform_profile=GENERIC_VERTICAL_SHORT_FORM_V1,
        skill=PERFORMANCE_PRODUCT_AD_V1,
        marketing_objective=MarketingObjective.CONVERSION,
    )
    vlog = CommercialPolicySelection(
        platform_profile=GENERIC_VERTICAL_SHORT_FORM_V1,
        skill=NATURAL_VLOG_V1,
    )

    ad_prior_ids = {prior.prior_id for prior in ad.skill.creative_priors}
    vlog_prior_ids = {prior.prior_id for prior in vlog.skill.creative_priors}

    assert ad.platform_profile is vlog.platform_profile
    assert "proof_demonstration" in ad_prior_ids
    assert "brief_driven_cta" in ad_prior_ids
    assert "speech_completeness" in vlog_prior_ids
    assert "reaction_holds" in vlog_prior_ids
    assert ad_prior_ids != vlog_prior_ids


def test_policy_foundation_uses_qualitative_priors_without_magic_weights() -> None:
    all_priors = (
        *PERFORMANCE_PRODUCT_AD_V1.creative_priors,
        *NATURAL_VLOG_V1.creative_priors,
    )

    assert all(isinstance(prior.guidance, str) for prior in all_priors)
    assert all(not hasattr(prior, "weight") for prior in all_priors)
    assert all(not hasattr(prior, "score") for prior in all_priors)


def test_generic_platform_profile_labels_selected_format_without_claiming_platform_law() -> None:
    profile = GENERIC_VERTICAL_SHORT_FORM_V1

    assert profile.aspect_ratio == (9, 16)
    assert profile.platform_family == "generic-short-form"
    assert any("not as a universal platform law" in item for item in profile.technical_constraints)
    assert any("not frozen" in item for item in profile.evidence_notes)


def test_provider_guidance_composes_platform_skill_and_objective_without_flattened_weights() -> None:
    selection = CommercialPolicySelection(
        platform_profile=GENERIC_VERTICAL_SHORT_FORM_V1,
        skill=PERFORMANCE_PRODUCT_AD_V1,
        marketing_objective=MarketingObjective.CONSIDERATION,
    )

    guidance = selection.provider_guidance()

    assert "Marketing objective: consideration." in guidance
    assert any("proof or demonstration" in item for item in guidance)
    assert any("9:16" in item for item in guidance)


def test_commercial_skill_rejects_duplicate_prior_ids() -> None:
    duplicate = CreativePrior("same", "First direction")

    with pytest.raises(ValueError, match="unique prior_id"):
        CommercialSkill(
            skill_id="skill_invalid",
            version="test",
            genre="test",
            creative_priors=(duplicate, CreativePrior("same", "Second direction")),
            review_dimensions=("quality",),
        )


def test_selection_rejects_explicitly_unsupported_marketing_objective() -> None:
    restricted = CommercialSkill(
        skill_id="skill_awareness_only",
        version="test",
        genre="test",
        creative_priors=(CreativePrior("clarity", "Prefer clarity."),),
        review_dimensions=("clarity",),
        supported_objectives=(MarketingObjective.AWARENESS,),
    )

    with pytest.raises(ValueError, match="does not support objective"):
        CommercialPolicySelection(
            platform_profile=GENERIC_VERTICAL_SHORT_FORM_V1,
            skill=restricted,
            marketing_objective=MarketingObjective.CONVERSION,
        )
