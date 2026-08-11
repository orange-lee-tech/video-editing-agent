from __future__ import annotations

from datetime import UTC, datetime

import pytest

from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.script.model import NarrativeSection, ScriptPlan
from video_editing_agent.planning.script.duration import assess_script_duration

NOW = datetime(2026, 8, 11, 22, 0, tzinfo=UTC)


def envelope(entity_id: str) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=1,
        schema_version="0.2",
        status=EntityStatus.VALID,
        created_at=NOW,
        created_by="test",
    )


def brief(*, target_duration: MediaTime | None = MediaTime(30, 1)) -> Brief:
    return Brief(
        envelope=envelope("brf_duration"),
        title="Duration plan",
        objective="Fit a short-form plan to the declared target.",
        target_duration=target_duration,
    )


def script(*sections: NarrativeSection) -> ScriptPlan:
    return ScriptPlan(
        envelope=envelope("scp_duration"),
        brief_ref=EntityRevisionRef("brf_duration", 1),
        sections=sections,
    )


def test_duration_assessment_reports_exact_complete_sum_and_delta() -> None:
    plan = script(
        NarrativeSection("hook", "hook", "Open", target_duration=MediaTime(5, 1)),
        NarrativeSection("body", "body", "Explain", target_duration=MediaTime(41, 2)),
        NarrativeSection("close", "close", "Finish", target_duration=MediaTime(9, 2)),
    )

    assessment = assess_script_duration(brief(), plan)

    assert assessment.known_duration == MediaTime(30, 1)
    assert assessment.estimated_duration == MediaTime(30, 1)
    assert assessment.missing_section_ids == ()
    assert assessment.brief_target_duration == MediaTime(30, 1)
    assert assessment.exact_delta_from_brief_target == MediaTime(0, 1)
    assert assessment.is_complete


def test_duration_assessment_preserves_known_sum_without_guessing_missing_sections() -> None:
    plan = script(
        NarrativeSection("hook", "hook", "Open", target_duration=MediaTime(7, 2)),
        NarrativeSection("body", "body", "Explain"),
        NarrativeSection("close", "close", "Finish", target_duration=MediaTime(9, 2)),
    )

    assessment = assess_script_duration(brief(), plan)

    assert assessment.known_duration == MediaTime(8, 1)
    assert assessment.estimated_duration is None
    assert assessment.missing_section_ids == ("body",)
    assert assessment.exact_delta_from_brief_target is None
    assert not assessment.is_complete


def test_duration_assessment_does_not_invent_target_when_brief_has_none() -> None:
    plan = script(
        NarrativeSection("only", "body", "Explain", target_duration=MediaTime(12, 1)),
    )

    assessment = assess_script_duration(brief(target_duration=None), plan)

    assert assessment.estimated_duration == MediaTime(12, 1)
    assert assessment.brief_target_duration is None
    assert assessment.exact_delta_from_brief_target is None
    assert assessment.is_complete


def test_duration_assessment_requires_exact_brief_revision() -> None:
    mismatched = Brief(
        envelope=EntityEnvelope(
            id="brf_duration",
            revision=2,
            schema_version="0.2",
            status=EntityStatus.VALID,
            created_at=NOW,
            created_by="test",
        ),
        title="Updated duration plan",
        objective="Updated objective",
        target_duration=MediaTime(30, 1),
    )

    with pytest.raises(ValueError, match="exact Brief revision"):
        assess_script_duration(
            mismatched,
            script(NarrativeSection("only", "body", "Explain")),
        )
