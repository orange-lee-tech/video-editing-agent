from __future__ import annotations

from video_editing_agent.planning.policy.model import (
    CommercialSkill,
    CreativePrior,
    MarketingObjective,
    PlatformProfile,
)

GENERIC_VERTICAL_SHORT_FORM_V1 = PlatformProfile(
    profile_id="platform_generic_vertical_short_form",
    version="r0.7b-v1",
    platform_family="generic-short-form",
    output_context="vertical short-form video",
    aspect_ratio=(9, 16),
    technical_constraints=(
        "Treat 9:16 as this profile's selected output format, not as a universal platform law.",
        "Keep important text and subjects compatible with configurable safe-zone overlays.",
    ),
    creative_guidance=(
        "Prefer clear mobile-scale composition and readable on-screen information.",
        "Do not encode platform folklore as a hard creative rule without dated evidence.",
    ),
    evidence_notes=(
        "R0.7B baseline is deliberately generic; platform-specific official guidance is not frozen here.",
    ),
)

PERFORMANCE_PRODUCT_AD_V1 = CommercialSkill(
    skill_id="skill_performance_product_ad",
    version="r0.7b-v1",
    genre="performance_product_ad",
    supported_objectives=(
        MarketingObjective.AWARENESS,
        MarketingObjective.CONSIDERATION,
        MarketingObjective.CONVERSION,
        MarketingObjective.MIXED,
    ),
    creative_priors=(
        CreativePrior(
            "early_attention_value",
            "Prefer an early, clear reason for the intended viewer to keep watching.",
        ),
        CreativePrior(
            "product_brand_clarity",
            "Make the product or brand clear when the Brief requires commercial identification.",
        ),
        CreativePrior(
            "proof_demonstration",
            "Prefer practical proof or demonstration coverage over unsupported promotional claims.",
        ),
        CreativePrior(
            "focused_message",
            "Keep each narrative section focused on the Brief's approved message and facts.",
        ),
        CreativePrior(
            "brief_driven_cta",
            "Use an explicit call to action only when the Brief or marketing objective requires it.",
        ),
        CreativePrior(
            "energy_tolerance",
            "Allow stronger visual energy and cut density when clarity and proof remain intact.",
        ),
        CreativePrior(
            "action_music_opportunity",
            "Preserve useful action and music opportunities for later grounded editing stages.",
        ),
        CreativePrior(
            "speech_intelligibility",
            "Protect narration and dialogue intelligibility over decorative pacing choices.",
        ),
    ),
    review_dimensions=(
        "brief_and_fact_adherence",
        "hook",
        "product_brand_clarity",
        "value_and_proof",
        "cta_when_required",
        "pacing",
        "continuity",
        "watchability",
    ),
)

NATURAL_VLOG_V1 = CommercialSkill(
    skill_id="skill_natural_vlog",
    version="r0.7b-v1",
    genre="natural_vlog",
    creative_priors=(
        CreativePrior(
            "speech_completeness",
            "Prefer complete thoughts and understandable speech over aggressive shortening.",
        ),
        CreativePrior(
            "situational_chronology",
            "Preserve chronology and situational coherence when they help the viewer follow events.",
        ),
        CreativePrior(
            "emotional_continuity",
            "Preserve emotional continuity and meaningful reactions rather than optimizing only speed.",
        ),
        CreativePrior(
            "reaction_holds",
            "Allow natural reaction holds and breathing room when they improve authenticity.",
        ),
        CreativePrior(
            "source_audio_continuity",
            "Prefer coherent natural source audio when it contributes to the scene.",
        ),
        CreativePrior(
            "restrained_beat_forcing",
            "Do not force every cut to music beats when natural timing is stronger.",
        ),
        CreativePrior(
            "restrained_transitions",
            "Prefer restrained transition density unless the Brief explicitly asks for stylization.",
        ),
    ),
    review_dimensions=(
        "brief_adherence",
        "naturalness",
        "speech_completeness",
        "chronology",
        "emotional_continuity",
        "source_audio_continuity",
        "pacing_and_breathing_room",
    ),
)
