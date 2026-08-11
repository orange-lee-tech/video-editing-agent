from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pytest

from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    ScriptPlanProposal,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReview,
    ScriptProposalViolation,
)
from video_editing_agent.domain.brief.model import AuthoritativeFact, Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.planning.script.service import ScriptPlanner
from video_editing_agent.planning.script.workflow import (
    ScriptPlanningWorkflow,
    ScriptProposalRejectedError,
)
from video_editing_agent.providers.llm.deepseek_chat import DeepSeekChatConfig
from video_editing_agent.providers.llm.deepseek_preproduction_review import (
    DeepSeekScriptProposalReviewPort,
)

NOW = datetime(2026, 8, 11, 22, 30, tzinfo=UTC)


class BriefRepo:
    def __init__(self, brief: Brief) -> None:
        self.brief = brief

    def load(self, brief_ref: EntityRevisionRef) -> Brief:
        assert brief_ref == EntityRevisionRef(self.brief.envelope.id, self.brief.envelope.revision)
        return self.brief

    def save(self, brief: Brief) -> None:
        self.brief = brief


class ScriptRepo:
    def __init__(self) -> None:
        self.saved: list[Any] = []

    def load(self, script_plan_ref: EntityRevisionRef) -> Any:
        for item in self.saved:
            if EntityRevisionRef(item.envelope.id, item.envelope.revision) == script_plan_ref:
                return item
        raise KeyError(script_plan_ref)

    def save(self, script_plan: Any) -> None:
        self.saved.append(script_plan)


class PlanningPort:
    def __init__(self, proposal: ScriptPlanProposal) -> None:
        self.proposal = proposal

    def propose(self, request: Any) -> ScriptPlanProposal:
        return self.proposal


class ReviewPort:
    def __init__(self, review: ScriptProposalReview) -> None:
        self.result = review
        self.calls = 0

    def review(self, request: Any) -> ScriptProposalReview:
        self.calls += 1
        return self.result


class FakeTransport:
    def __init__(self, response_content: dict[str, Any]) -> None:
        self.response_content = response_content
        self.payloads: list[dict[str, Any]] = []

    def create_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.payloads.append(payload)
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(self.response_content)},
                }
            ]
        }


def guarded_brief() -> Brief:
    return Brief(
        envelope=EntityEnvelope(
            id="brf_guarded",
            revision=1,
            schema_version="0.2",
            status=EntityStatus.DRAFT,
            created_at=NOW,
            created_by="test",
        ),
        title="Guarded product plan",
        objective="Create a factual product script.",
        audience="commuters",
        platform="vertical short-form",
        core_message="Show only supported product facts.",
        product_topic="bottle",
        authoritative_facts=(
            AuthoritativeFact("fact_lid", "The bottle has a screw-on lid."),
        ),
        prohibited_content=("Do not claim leak resistance.",),
    )


def proposal() -> ScriptPlanProposal:
    return ScriptPlanProposal(
        sections=(
            NarrativeSectionProposal(
                section_id="hook",
                narrative_role="hook",
                information_goal="Introduce the product.",
                spoken_content="The screw-on lid keeps spills away.",
                protected_fact_ids=("fact_lid",),
            ),
        )
    )


def workflow(*, review_port: ReviewPort | None) -> tuple[ScriptPlanningWorkflow, ScriptRepo]:
    brief = guarded_brief()
    brief_repo = BriefRepo(brief)
    script_repo = ScriptRepo()
    planner = ScriptPlanner(
        brief_repository=brief_repo,
        script_plan_repository=script_repo,
        script_plan_id_factory=lambda: "scp_guarded",
        clock=lambda: NOW,
    )
    return (
        ScriptPlanningWorkflow(
            brief_repository=brief_repo,
            script_plan_repository=script_repo,
            planning_port=PlanningPort(proposal()),
            planner=planner,
            review_port=review_port,
        ),
        script_repo,
    )


def test_guarded_brief_requires_review_port_before_owner_commit() -> None:
    planning, repository = workflow(review_port=None)

    with pytest.raises(RuntimeError, match="requires ScriptProposalReviewPort"):
        planning.generate(EntityRevisionRef("brf_guarded", 1))

    assert repository.saved == []


def test_rejected_semantic_review_never_reaches_script_owner() -> None:
    reviewer = ReviewPort(
        ScriptProposalReview(
            accepted=False,
            violations=(
                ScriptProposalViolation(
                    code="unsupported_claim",
                    section_id="hook",
                    excerpt="keeps spills away",
                    reason="A screw-on lid does not entail leak resistance.",
                ),
            ),
        )
    )
    planning, repository = workflow(review_port=reviewer)

    with pytest.raises(ScriptProposalRejectedError, match="unsupported_claim@hook"):
        planning.generate(EntityRevisionRef("brf_guarded", 1))

    assert reviewer.calls == 1
    assert repository.saved == []


def test_accepted_semantic_review_allows_owner_commit() -> None:
    reviewer = ReviewPort(ScriptProposalReview(accepted=True))
    planning, repository = workflow(review_port=reviewer)

    result = planning.generate(EntityRevisionRef("brf_guarded", 1))

    assert reviewer.calls == 1
    assert result.envelope.id == "scp_guarded"
    assert repository.saved == [result]


def test_deepseek_reviewer_returns_veto_only_structured_result() -> None:
    transport = FakeTransport(
        {
            "accepted": False,
            "violations": [
                {
                    "code": "unsupported_claim",
                    "section_id": "hook",
                    "excerpt": "keeps spills away",
                    "reason": "The Brief provides a lid fact but no leak-resistance fact.",
                }
            ],
        }
    )
    reviewer = DeepSeekScriptProposalReviewPort(transport=transport)

    result = reviewer.review(
        type(
            "Request",
            (),
            {
                "brief": guarded_brief(),
                "proposal": proposal(),
                "policy_guidance": None,
            },
        )()
    )

    assert not result.accepted
    assert result.violations[0].code == "unsupported_claim"
    payload = transport.payloads[0]
    assert payload["thinking"] == {"type": "enabled"}
    assert payload["response_format"] == {"type": "json_object"}
    assert "veto-only" in payload["messages"][0]["content"]
    assert "does not imply a performance property" in payload["messages"][0]["content"]


def test_deepseek_reviewer_can_use_explicit_nonthinking_config() -> None:
    transport = FakeTransport({"accepted": True, "violations": []})
    reviewer = DeepSeekScriptProposalReviewPort(
        transport=transport,
        config=DeepSeekChatConfig(thinking_enabled=False, max_tokens=500),
    )

    result = reviewer.review(
        type(
            "Request",
            (),
            {
                "brief": guarded_brief(),
                "proposal": proposal(),
                "policy_guidance": None,
            },
        )()
    )

    assert result.accepted
    assert transport.payloads[0]["thinking"] == {"type": "disabled"}
