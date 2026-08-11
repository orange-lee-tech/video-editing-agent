from __future__ import annotations

from dataclasses import dataclass

from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.script.model import ScriptPlan


@dataclass(frozen=True, slots=True)
class ScriptDurationAssessment:
    """Exact duration facts without inventing speech-rate or quality thresholds."""

    known_duration: MediaTime
    estimated_duration: MediaTime | None
    missing_section_ids: tuple[str, ...]
    brief_target_duration: MediaTime | None
    exact_delta_from_brief_target: MediaTime | None

    @property
    def is_complete(self) -> bool:
        return self.estimated_duration is not None


def assess_script_duration(brief: Brief, script_plan: ScriptPlan) -> ScriptDurationAssessment:
    """Compare explicit section targets with the exact Brief target, when both are available."""

    brief_ref = EntityRevisionRef(brief.envelope.id, brief.envelope.revision)
    if script_plan.brief_ref != brief_ref:
        raise ValueError("script_plan must reference the exact Brief revision being assessed")

    known_duration = MediaTime(0, 1)
    missing_section_ids: list[str] = []
    for section in script_plan.sections:
        if section.target_duration is None:
            missing_section_ids.append(section.section_id)
        else:
            known_duration = known_duration + section.target_duration

    estimated_duration = script_plan.estimated_duration
    exact_delta = None
    if estimated_duration is not None and brief.target_duration is not None:
        exact_delta = estimated_duration - brief.target_duration

    return ScriptDurationAssessment(
        known_duration=known_duration,
        estimated_duration=estimated_duration,
        missing_section_ids=tuple(missing_section_ids),
        brief_target_duration=brief.target_duration,
        exact_delta_from_brief_target=exact_delta,
    )
