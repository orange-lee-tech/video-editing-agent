from __future__ import annotations

import json
import urllib.error
from datetime import UTC, datetime
from typing import Any

import pytest

from video_editing_agent.application.ports.preproduction_planning import (
    PlanningPolicyGuidance,
    ScriptPlanningRequest,
    ShootingPlanningRequest,
)
from video_editing_agent.domain.brief.model import AuthoritativeFact, Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.script.model import NarrativeSection, ScriptPlan
from video_editing_agent.domain.shooting.model import ProductionConstraints, ProductionLocation
from video_editing_agent.providers.llm.deepseek_chat import (
    DeepSeekChatConfig,
    DeepSeekPlanningResponseError,
    DeepSeekPlanningTransientError,
    DeepSeekScriptPlanningPort,
    DeepSeekShootingPlanningPort,
    UrllibDeepSeekChatTransport,
)

NOW = datetime(2026, 8, 11, 20, 10, tzinfo=UTC)


class FakeTransport:
    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response
        self.payloads: list[dict[str, Any]] = []

    def create_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.payloads.append(payload)
        return self.response


class FakeHttpResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> FakeHttpResponse:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        del exc_type, exc, traceback

    def read(self) -> bytes:
        return self._body


def envelope(entity_id: str) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=1,
        schema_version="0.2",
        status=EntityStatus.DRAFT,
        created_at=NOW,
        created_by="test",
    )


def brief() -> Brief:
    return Brief(
        envelope=envelope("brf_deepseek"),
        title="Product launch",
        objective="Drive consideration",
        audience="First-time buyers",
        platform="vertical short-form",
        core_message="Simple to use",
        target_duration=MediaTime(30, 1),
        authoritative_facts=(AuthoritativeFact("fact_price", "Price is 99 USD."),),
    )


def policy() -> PlanningPolicyGuidance:
    return PlanningPolicyGuidance(
        platform_profile_id="platform_generic_vertical_short_form",
        platform_profile_version="r0.7b-v1",
        skill_id="skill_performance_product_ad",
        skill_version="r0.7b-v1",
        marketing_objective="conversion",
        guidance=("Prefer practical proof or demonstration coverage.",),
    )


def completed(content: dict[str, Any], *, finish_reason: str = "stop") -> dict[str, Any]:
    return {
        "choices": [
            {
                "finish_reason": finish_reason,
                "message": {"role": "assistant", "content": json.dumps(content)},
            }
        ]
    }


def script_content() -> dict[str, Any]:
    return {
        "sections": [
            {
                "section_id": "hook",
                "narrative_role": "hook",
                "information_goal": "Earn attention",
                "spoken_content": "At 99 USD, show the approved offer clearly.",
                "visual_requirement": "Show the product in use.",
                "target_duration": {"value": 3, "scale": 1},
                "protected_fact_ids": ["fact_price"],
                "locked": False,
            }
        ]
    }


def shooting_content() -> dict[str, Any]:
    return {
        "requirements": [
            {
                "requirement_id": "req_demo",
                "script_section_ref": "hook",
                "purpose": "Show the product working",
                "subject": "product and hand",
                "action": "operate",
                "location_ref": "loc_home_desk",
                "environment_description": "fixed phone position beside the home desk",
                "target_duration": {"value": 4, "scale": 1},
                "minimum_duration": {"value": 2, "scale": 1},
                "priority": "required",
                "capture_instruction": "Hold the phone still and operate the product once.",
            }
        ],
        "notes": ["Capture a backup take."],
    }


def test_config_defaults_to_current_cost_focused_flash_model_and_non_thinking() -> None:
    config = DeepSeekChatConfig()

    assert config.model == "deepseek-v4-flash"
    assert config.thinking_enabled is False
    assert config.max_tokens == 6_000


@pytest.mark.parametrize("retired", ["deepseek-chat", "deepseek-reasoner"])
def test_config_rejects_retired_model_aliases(retired: str) -> None:
    with pytest.raises(ValueError, match="deprecated DeepSeek model alias"):
        DeepSeekChatConfig(model=retired)


def test_script_adapter_uses_json_mode_and_preserves_authority_context() -> None:
    transport = FakeTransport(completed(script_content()))
    adapter = DeepSeekScriptPlanningPort(transport=transport)

    proposal = adapter.propose(
        ScriptPlanningRequest(
            brief=brief(),
            instruction="Make the opening clearer.",
            policy_guidance=policy(),
        )
    )

    assert proposal.sections[0].section_id == "hook"
    assert proposal.sections[0].target_duration == MediaTime(3, 1)
    assert proposal.sections[0].protected_fact_ids == ("fact_price",)

    payload = transport.payloads[0]
    assert payload["model"] == "deepseek-v4-flash"
    assert payload["thinking"] == {"type": "disabled"}
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["stream"] is False
    assert "json" in payload["messages"][0]["content"].lower()
    context = json.loads(payload["messages"][1]["content"])
    assert context["brief"]["authoritative_facts"][0]["fact_id"] == "fact_price"
    assert context["policy_guidance"]["skill_id"] == "skill_performance_product_ad"
    assert context["instruction"] == "Make the opening clearer."


def test_script_revision_serializes_locked_current_section_as_untrusted_data() -> None:
    current = ScriptPlan(
        envelope=envelope("scp_deepseek"),
        brief_ref=EntityRevisionRef("brf_deepseek", 1),
        sections=(
            NarrativeSection(
                "hook",
                "hook",
                "Earn attention",
                spoken_content="Approved hook",
                locked=True,
            ),
        ),
    )
    transport = FakeTransport(completed(script_content()))
    adapter = DeepSeekScriptPlanningPort(transport=transport)

    adapter.propose(
        ScriptPlanningRequest(
            brief=brief(),
            current_script=current,
            instruction="Improve the body only.",
            policy_guidance=policy(),
        )
    )

    context = json.loads(transport.payloads[0]["messages"][1]["content"])
    assert context["task"] == "revise_script"
    assert context["current_script"]["sections"][0]["locked"] is True
    assert context["current_script"]["sections"][0]["spoken_content"] == "Approved hook"


def test_shooting_adapter_receives_structured_locations_but_cannot_output_constraints() -> None:
    current_script = ScriptPlan(
        envelope=envelope("scp_deepseek_shoot"),
        brief_ref=EntityRevisionRef("brf_deepseek", 1),
        sections=(NarrativeSection("hook", "hook", "Earn attention"),),
    )
    constraints = ProductionConstraints(
        camera_or_phone="user phone",
        stabilizer="none",
        people_count=1,
        locations=(
            ProductionLocation(
                "loc_home_desk",
                "home desk",
                "Use the desk area; camera may sit beside it.",
            ),
        ),
    )
    transport = FakeTransport(completed(shooting_content()))
    adapter = DeepSeekShootingPlanningPort(transport=transport)

    proposal = adapter.propose(
        ShootingPlanningRequest(
            brief=brief(),
            script_plan=current_script,
            constraints=constraints,
            policy_guidance=policy(),
        )
    )

    assert proposal.requirements[0].priority == "required"
    assert proposal.requirements[0].target_duration == MediaTime(4, 1)
    assert proposal.requirements[0].location_ref == "loc_home_desk"
    assert proposal.requirements[0].environment_description == (
        "fixed phone position beside the home desk"
    )
    payload = transport.payloads[0]
    context = json.loads(payload["messages"][1]["content"])
    assert context["production_constraints"]["camera_or_phone"] == "user phone"
    assert context["production_constraints"]["locations"] == [
        {
            "location_id": "loc_home_desk",
            "label": "home desk",
            "notes": "Use the desk area; camera may sit beside it.",
        }
    ]
    assert "location_ref must be exactly one location_id" in payload["messages"][0]["content"]

    bad = shooting_content()
    bad["constraints"] = {"camera_or_phone": "expensive cinema camera"}
    bad_adapter = DeepSeekShootingPlanningPort(transport=FakeTransport(completed(bad)))
    with pytest.raises(DeepSeekPlanningResponseError, match="unexpected fields"):
        bad_adapter.propose(
            ShootingPlanningRequest(
                brief=brief(),
                script_plan=current_script,
                constraints=constraints,
            )
        )


def test_response_rejects_truncated_or_malformed_structured_output() -> None:
    length_adapter = DeepSeekScriptPlanningPort(
        transport=FakeTransport(completed(script_content(), finish_reason="length"))
    )
    with pytest.raises(DeepSeekPlanningResponseError, match="did not finish normally"):
        length_adapter.propose(ScriptPlanningRequest(brief=brief()))

    malformed = completed({"sections": [{"section_id": "hook", "surprise": "bad"}]})
    malformed_adapter = DeepSeekScriptPlanningPort(transport=FakeTransport(malformed))
    with pytest.raises(DeepSeekPlanningResponseError, match="unexpected fields"):
        malformed_adapter.propose(ScriptPlanningRequest(brief=brief()))


def test_empty_content_and_resource_exhaustion_are_retryable() -> None:
    empty = {"choices": [{"finish_reason": "stop", "message": {"content": ""}}]}
    empty_adapter = DeepSeekScriptPlanningPort(transport=FakeTransport(empty))
    with pytest.raises(DeepSeekPlanningTransientError, match="empty content"):
        empty_adapter.propose(ScriptPlanningRequest(brief=brief()))

    resource = {
        "choices": [
            {
                "finish_reason": "insufficient_system_resource",
                "message": {"content": None},
            }
        ]
    }
    resource_adapter = DeepSeekScriptPlanningPort(transport=FakeTransport(resource))
    with pytest.raises(DeepSeekPlanningTransientError, match="system resources"):
        resource_adapter.propose(ScriptPlanningRequest(brief=brief()))


def test_transport_classifies_retryable_and_non_retryable_http(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_429(*args: object, **kwargs: object) -> FakeHttpResponse:
        del args, kwargs
        raise urllib.error.HTTPError("https://example.invalid", 429, "rate limit", None, None)

    monkeypatch.setattr("urllib.request.urlopen", raise_429)
    transport = UrllibDeepSeekChatTransport(api_key="secret", endpoint="https://example.invalid")
    with pytest.raises(DeepSeekPlanningTransientError, match="retryable HTTP 429"):
        transport.create_chat_completion({"model": "test"})

    def raise_400(*args: object, **kwargs: object) -> FakeHttpResponse:
        del args, kwargs
        raise urllib.error.HTTPError("https://example.invalid", 400, "bad request", None, None)

    monkeypatch.setattr("urllib.request.urlopen", raise_400)
    with pytest.raises(DeepSeekPlanningResponseError, match="HTTP 400"):
        transport.create_chat_completion({"model": "test"})


def test_transport_rejects_invalid_json_response(monkeypatch: pytest.MonkeyPatch) -> None:
    def invalid_json(*args: object, **kwargs: object) -> FakeHttpResponse:
        del args, kwargs
        return FakeHttpResponse(b"not-json")

    monkeypatch.setattr("urllib.request.urlopen", invalid_json)
    transport = UrllibDeepSeekChatTransport(api_key="secret", endpoint="https://example.invalid")

    with pytest.raises(DeepSeekPlanningResponseError, match="invalid JSON"):
        transport.create_chat_completion({"model": "test"})
