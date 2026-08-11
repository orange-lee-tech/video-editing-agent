from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pytest

from video_editing_agent.application.ports.artifact_store import StoredArtifactRef
from video_editing_agent.application.ports.preproduction_planning import (
    ReferenceStyleGuidance,
    ScriptPlanningRequest,
    ShootingPlanningRequest,
)
from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.script.model import NarrativeSection, ScriptPlan
from video_editing_agent.domain.shooting.model import ProductionConstraints
from video_editing_agent.planning.reference.guidance import to_reference_style_guidance
from video_editing_agent.planning.reference.service import (
    ReferenceStyleEvidence,
    ReferenceStyleEvidenceResult,
)
from video_editing_agent.providers.llm.deepseek_chat import (
    DeepSeekScriptPlanningPort,
    DeepSeekShootingPlanningPort,
)

NOW = datetime(2026, 8, 11, 21, 30, tzinfo=UTC)


class FakeTransport:
    def __init__(self, content: dict[str, Any]) -> None:
        self.content = content
        self.payloads: list[dict[str, Any]] = []

    def create_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.payloads.append(payload)
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(self.content)},
                }
            ]
        }


def envelope(entity_id: str) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=1,
        schema_version="0.2",
        status=EntityStatus.VALID,
        created_at=NOW,
        created_by="test",
    )


def brief() -> Brief:
    return Brief(
        envelope=envelope("brf_reference_guidance"),
        title="Reference-aware plan",
        objective="Create an original short video plan.",
        audience="general audience",
        platform="vertical short-form",
        core_message="Keep the message simple.",
    )


def script_plan() -> ScriptPlan:
    return ScriptPlan(
        envelope=envelope("scp_reference_guidance"),
        brief_ref=EntityRevisionRef("brf_reference_guidance", 1),
        sections=(NarrativeSection("hook", "hook", "Earn attention"),),
    )


def reference_guidance() -> ReferenceStyleGuidance:
    return ReferenceStyleGuidance(
        reference_asset_ref=EntityRevisionRef("ast_reference", 2),
        evidence_artifact_id="art_sha256_reference",
        observations=(
            "Observed a close static opening and short early shot cadence.",
            "Use the observation as abstract technique only; do not copy expression.",
        ),
        unavailable_dimensions=("music_cut_relationship", "caption_density"),
    )


def test_reference_evidence_projects_into_provider_neutral_guidance() -> None:
    evidence = ReferenceStyleEvidence(
        reference_asset_ref=EntityRevisionRef("ast_reference", 2),
        shot_refs=(EntityRevisionRef("sht_reference", 1),),
        analysis_refs=(),
        total_duration=MediaTime(2, 1),
        minimum_shot_duration=MediaTime(2, 1),
        median_shot_duration=MediaTime(2, 1),
        maximum_shot_duration=MediaTime(2, 1),
        opening_framing="close",
        opening_camera_motion="static",
        framing_sequence=("close",),
        camera_motion_sequence=("static",),
        framing_patterns=(),
        camera_motion_patterns=(),
        action_patterns=(),
        subject_patterns=(),
        environment_patterns=(),
    )
    artifact = StoredArtifactRef(
        artifact_id="art_sha256_reference",
        content_hash="sha256:reference",
        media_type="application/json",
        byte_size=128,
    )
    result = ReferenceStyleEvidenceResult(
        evidence=evidence,
        artifact_ref=artifact,
        planning_guidance=("Abstract close/static opening observation.",),
    )

    guidance = to_reference_style_guidance(result)

    assert guidance.reference_asset_ref == EntityRevisionRef("ast_reference", 2)
    assert guidance.evidence_artifact_id == "art_sha256_reference"
    assert guidance.observations == ("Abstract close/static opening observation.",)
    assert "music_cut_relationship" in guidance.unavailable_dimensions


def test_planning_request_rejects_conflicting_guidance_for_same_reference_revision() -> None:
    first = reference_guidance()
    second = ReferenceStyleGuidance(
        reference_asset_ref=first.reference_asset_ref,
        evidence_artifact_id="art_sha256_other",
        observations=("Conflicting observation.",),
    )

    with pytest.raises(ValueError, match="at most one item"):
        ScriptPlanningRequest(
            brief=brief(),
            reference_guidance=(first, second),
        )


def test_deepseek_script_context_serializes_reference_evidence_without_source_authority() -> None:
    transport = FakeTransport(
        {
            "sections": [
                {
                    "section_id": "hook",
                    "narrative_role": "hook",
                    "information_goal": "Earn attention",
                }
            ]
        }
    )
    adapter = DeepSeekScriptPlanningPort(transport=transport)

    adapter.propose(
        ScriptPlanningRequest(
            brief=brief(),
            reference_guidance=(reference_guidance(),),
        )
    )

    payload = transport.payloads[0]
    system_prompt = payload["messages"][0]["content"]
    assert "abstract technique" in system_prompt
    assert "never copy" in system_prompt
    assert "marked unavailable" in system_prompt

    context = json.loads(payload["messages"][1]["content"])
    serialized = context["reference_style_guidance"][0]
    assert serialized["reference_asset_ref"] == {
        "entity_id": "ast_reference",
        "revision": 2,
    }
    assert serialized["evidence_artifact_id"] == "art_sha256_reference"
    assert serialized["unavailable_dimensions"] == [
        "music_cut_relationship",
        "caption_density",
    ]
    assert "source_window" not in serialized
    assert "editable" not in serialized


def test_deepseek_shooting_context_keeps_reference_separate_from_constraints() -> None:
    transport = FakeTransport(
        {
            "requirements": [
                {
                    "requirement_id": "req_hook",
                    "script_section_ref": "hook",
                    "purpose": "Capture an original close opening.",
                    "subject": "product",
                }
            ],
            "notes": [],
        }
    )
    constraints = ProductionConstraints(
        camera_or_phone="user phone",
        stabilizer="none",
        people_count=1,
        locations=("home",),
    )
    adapter = DeepSeekShootingPlanningPort(transport=transport)

    adapter.propose(
        ShootingPlanningRequest(
            brief=brief(),
            script_plan=script_plan(),
            constraints=constraints,
            reference_guidance=(reference_guidance(),),
        )
    )

    context = json.loads(transport.payloads[0]["messages"][1]["content"])
    assert context["production_constraints"]["camera_or_phone"] == "user phone"
    assert context["reference_style_guidance"][0]["evidence_artifact_id"] == (
        "art_sha256_reference"
    )
