from __future__ import annotations

from video_editing_agent.application.ports.preproduction_planning import PlanningPolicyGuidance
from video_editing_agent.planning.policy.model import CommercialPolicySelection


def to_planning_policy_guidance(
    selection: CommercialPolicySelection,
) -> PlanningPolicyGuidance:
    """Project a concrete policy selection into the provider-neutral planning Port DTO."""

    return PlanningPolicyGuidance(
        platform_profile_id=selection.platform_profile.profile_id,
        platform_profile_version=selection.platform_profile.version,
        skill_id=selection.skill.skill_id,
        skill_version=selection.skill.version,
        marketing_objective=(
            None if selection.marketing_objective is None else selection.marketing_objective.value
        ),
        guidance=selection.provider_guidance(),
    )
