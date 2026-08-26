from __future__ import annotations

from datetime import UTC, datetime

from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    ScriptPlanningRequest,
    ScriptPlanProposal,
    ShootingPlanningRequest,
    ShootingPlanProposal,
    ShotRequirementProposal,
)
from video_editing_agent.domain.brief.model import AuthoritativeFact, Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.script.model import NarrativeSection, ScriptPlan
from video_editing_agent.domain.shooting.model import ProductionConstraints
from video_editing_agent.providers.llm.preproduction_refinement import (
    EditoriallyRefinedScriptPlanningPort,
    EditoriallyRefinedShootingPlanningPort,
    _target_language,
)

NOW = datetime(2026, 8, 26, tzinfo=UTC)


def _brief(*, chinese: bool) -> Brief:
    return Brief(
        EntityEnvelope("brf_refine", 1, "0.2", EntityStatus.VALID, NOW, "test"),
        "小小的水瓶" if chinese else "Small Bottle",
        "告诉人们这水瓶方便携带" if chinese else "Introduce the bottle for commuters",
        "上班族" if chinese else "commuters",
        "抖音" if chinese else "TikTok",
        "便携" if chinese else "portable positioning",
        authoritative_facts=(
            AuthoritativeFact(
                "fact_capacity",
                "容量350ml" if chinese else "The bottle capacity is 350ml.",
            ),
        ),
    )


class ScriptDelegate:
    def __init__(self, *responses: ScriptPlanProposal) -> None:
        self.responses = list(responses)
        self.requests: list[ScriptPlanningRequest] = []

    def propose(self, request: ScriptPlanningRequest) -> ScriptPlanProposal:
        self.requests.append(request)
        return self.responses.pop(0)


class ShootingDelegate:
    def __init__(self, *responses: ShootingPlanProposal) -> None:
        self.responses = list(responses)
        self.requests: list[ShootingPlanningRequest] = []

    def propose(self, request: ShootingPlanningRequest) -> ShootingPlanProposal:
        self.requests.append(request)
        return self.responses.pop(0)


def test_script_refinement_spends_second_pass_on_quality_and_chinese_language() -> None:
    draft = ScriptPlanProposal(
        tuple(
            NarrativeSectionProposal(
                section_id,
                role,
                "重复容量信息",
                spoken_content="容量350ml",
                protected_fact_ids=("fact_capacity",),
            )
            for section_id, role in (
                ("hook", "hook"),
                ("body", "body"),
                ("close", "closing"),
            )
        )
    )
    refined = ScriptPlanProposal(
        (
            NarrativeSectionProposal("hook", "hook", "快速建立主体", spoken_content="今天来看一只水瓶。"),
            NarrativeSectionProposal(
                "body",
                "body",
                "呈现已确认容量",
                spoken_content="它确认的容量参数是350ml。",
                protected_fact_ids=("fact_capacity",),
            ),
            NarrativeSectionProposal(
                "close",
                "closing",
                "无新增产品声明地收尾",
                spoken_content="更多已确认参数，可以继续查看产品信息。",
            ),
        )
    )
    delegate = ScriptDelegate(draft, refined)
    port = EditoriallyRefinedScriptPlanningPort(delegate)

    result = port.propose(ScriptPlanningRequest(_brief(chinese=True)))

    assert result is refined
    assert len(delegate.requests) == 2
    assert "所有面向普通用户的自然语言字段必须使用简体中文" in (
        delegate.requests[0].instruction or ""
    )
    second = delegate.requests[1].instruction or ""
    assert "draft_proposal=" in second
    assert "Do not mechanically repeat the same authoritative fact" in second


def test_output_language_inference_tracks_ordinary_brief_language() -> None:
    assert _target_language(_brief(chinese=True)) == "zh-CN"
    assert _target_language(_brief(chinese=False)) == "en"


def test_shooting_refinement_requests_beginner_detail_without_new_resources() -> None:
    brief = _brief(chinese=True)
    script = ScriptPlan(
        EntityEnvelope("scp_refine", 1, "0.2", EntityStatus.VALID, NOW, "test"),
        EntityRevisionRef(brief.envelope.id, brief.envelope.revision),
        (NarrativeSection("hook", "hook", "快速建立主体"),),
    )
    draft = ShootingPlanProposal(
        (
            ShotRequirementProposal(
                "req_hook",
                "hook",
                "展示水瓶",
                "水瓶",
                capture_instruction="拍摄水瓶三秒。",
            ),
        )
    )
    refined = ShootingPlanProposal(
        (
            ShotRequirementProposal(
                "req_hook",
                "hook",
                "展示水瓶",
                "水瓶",
                framing="close",
                camera_motion="static",
                capture_instruction="手机竖直放稳，与水瓶大致同高；开拍先停一秒，再保持主体清晰三秒。",
                alternate_coverage=("再补一个稍宽的静态镜头。",),
            ),
        )
    )
    delegate = ShootingDelegate(draft, refined)
    port = EditoriallyRefinedShootingPlanningPort(delegate)

    result = port.propose(
        ShootingPlanningRequest(brief, script, ProductionConstraints(camera_or_phone="手机"))
    )

    assert result is refined
    assert len(delegate.requests) == 2
    second = delegate.requests[1].instruction or ""
    assert "所有面向普通用户的自然语言字段必须使用简体中文" in second
    assert "Do not require a physical label, measuring tool, prop, location, or person" in second
    assert "draft_proposal=" in second
