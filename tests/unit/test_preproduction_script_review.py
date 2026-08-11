from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    ScriptPlanningRequest,
    ScriptPlanProposal,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReview,
    ScriptProposalReviewRequest,
    ScriptProposalViolation,
)
from video_editing_agent.domain.brief.model import AuthoritativeFact
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.planning.brief.service import BriefContent, BriefService
from video_editing_agent.planning.script.service import ScriptPlanner
from video_editing_agent.planning.script.workflow import (
    ScriptPlanningWorkflow,
    ScriptProposalRejectedError,
)
from video_editing_agent.providers.llm.deepseek_chat import DeepSeekChatConfig
from video_editing_agent.providers.llm.deepseek_preproduction_review import (
    DeepSeekScriptProposalReviewPort,
)
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase

NOW = datetime(2026, 8, 12, 0, 30, tzinfo=UTC)


class CountingPlanningPort:
    def __init__(self, proposal: ScriptPlanProposal) -> None:
        self.proposal = proposal
        self.requests: list[ScriptPlanningRequest] = []

    def propose(self, request: ScriptPlanningRequest) -> ScriptPlanProposal:
        self.requests.append(request)
        return self.proposal


class StaticReviewPort:
    def __init__(self, review: ScriptProposalReview) -> None:
        self.result = review
        self.requests: list[ScriptProposalReviewRequest] = []

    def review(self, request: ScriptProposalReviewRequest) -> ScriptProposalReview:
        self.requests.append(request)
        return self.result


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


def repositories(path: Path):
    database = SqliteProjectDatabase(path)
    database.initialize()
    return SqliteBriefRepository(database), SqliteScriptPlanRepository(database)


def guarded_brief(briefs: SqliteBriefRepository):
    return BriefService(
        briefs,
        brief_id_factory=lambda: "brf_semantic_review",
        clock=lambda: NOW,
    ).create(
        BriefContent(
            title="Bottle product ad",
            objective="Create a factual short product ad.",
            audience="commuters",
            platform="vertical short-form",
            core_message="Show only supported product facts.",
            product_topic="bottle",
            authoritative_facts=(AuthoritativeFact("fact_lid", "The bottle has a screw-on lid."),),
            prohibited_content=("Do not claim leak resistance.",),
        )
    )


def planner(
    briefs: SqliteBriefRepository,
    scripts: SqliteScriptPlanRepository,
) -> ScriptPlanner:
    return ScriptPlanner(
        brief_repository=briefs,
        script_plan_repository=scripts,
        script_plan_id_factory=lambda: "scp_semantic_review",
        clock=lambda: NOW,
    )


def workflow(
    briefs: SqliteBriefRepository,
    scripts: SqliteScriptPlanRepository,
    planning_port: CountingPlanningPort,
    review_port: StaticReviewPort | None,
) -> ScriptPlanningWorkflow:
    return ScriptPlanningWorkflow(
        brief_repository=briefs,
        script_plan_repository=scripts,
        planning_port=planning_port,
        planner=planner(briefs, scripts),
        review_port=review_port,
    )


def safe_proposal() -> ScriptPlanProposal:
    return ScriptPlanProposal(
        (
            NarrativeSectionProposal(
                "hook",
                "hook",
                "Introduce the bottle without extra claims.",
                spoken_content="Show the screw-on lid clearly.",
                protected_fact_ids=("fact_lid",),
            ),
        )
    )


def leak_claim_proposal() -> ScriptPlanProposal:
    return ScriptPlanProposal(
        (
            NarrativeSectionProposal(
                "proof",
                "proof",
                "Demonstrate carrying the bottle.",
                spoken_content="Tighten the screw-on lid and it will not spill in your bag.",
                protected_fact_ids=("fact_lid",),
            ),
        )
    )


def test_guarded_brief_requires_reviewer_before_owner_commit(tmp_path: Path) -> None:
    briefs, scripts = repositories(tmp_path / "project.sqlite3")
    brief = guarded_brief(briefs)
    planning_port = CountingPlanningPort(safe_proposal())

    with pytest.raises(RuntimeError, match="requires ScriptProposalReviewPort"):
        workflow(briefs, scripts, planning_port, None).generate(
            EntityRevisionRef(brief.envelope.id, 1)
        )

    assert len(planning_port.requests) == 1
    with pytest.raises(KeyError):
        scripts.load(EntityRevisionRef("scp_semantic_review", 1))


def test_deterministic_preflight_runs_before_semantic_review(tmp_path: Path) -> None:
    briefs, scripts = repositories(tmp_path / "project.sqlite3")
    brief = guarded_brief(briefs)
    planning_port = CountingPlanningPort(
        ScriptPlanProposal(
            (
                NarrativeSectionProposal(
                    "proof",
                    "proof",
                    "State a fact.",
                    protected_fact_ids=("fact_missing",),
                ),
            )
        )
    )
    review_port = StaticReviewPort(ScriptProposalReview(accepted=True))

    with pytest.raises(ValueError, match="unknown protected facts"):
        workflow(briefs, scripts, planning_port, review_port).generate(
            EntityRevisionRef(brief.envelope.id, 1)
        )

    assert len(planning_port.requests) == 1
    assert review_port.requests == []
    with pytest.raises(KeyError):
        scripts.load(EntityRevisionRef("scp_semantic_review", 1))


def test_semantic_veto_rejects_implied_leak_resistance_without_owner_commit(
    tmp_path: Path,
) -> None:
    briefs, scripts = repositories(tmp_path / "project.sqlite3")
    brief = guarded_brief(briefs)
    planning_port = CountingPlanningPort(leak_claim_proposal())
    violation = ScriptProposalViolation(
        code="unsupported_performance_claim",
        section_id="proof",
        excerpt="will not spill in your bag",
        reason="A screw-on lid does not establish leak resistance.",
    )
    review_port = StaticReviewPort(
        ScriptProposalReview(accepted=False, violations=(violation,))
    )

    with pytest.raises(ScriptProposalRejectedError) as captured:
        workflow(briefs, scripts, planning_port, review_port).generate(
            EntityRevisionRef(brief.envelope.id, 1)
        )

    assert captured.value.review.violations == (violation,)
    assert len(review_port.requests) == 1
    assert review_port.requests[0].proposal == planning_port.proposal
    with pytest.raises(KeyError):
        scripts.load(EntityRevisionRef("scp_semantic_review", 1))


def test_accepted_semantic_review_allows_owner_commit(tmp_path: Path) -> None:
    briefs, scripts = repositories(tmp_path / "project.sqlite3")
    brief = guarded_brief(briefs)
    planning_port = CountingPlanningPort(safe_proposal())
    review_port = StaticReviewPort(ScriptProposalReview(accepted=True))

    script = workflow(briefs, scripts, planning_port, review_port).generate(
        EntityRevisionRef(brief.envelope.id, 1)
    )

    assert len(review_port.requests) == 1
    assert scripts.load(EntityRevisionRef(script.envelope.id, script.envelope.revision)) == script


def test_review_result_is_veto_only_and_internally_consistent() -> None:
    violation = ScriptProposalViolation(code="unsupported_claim", reason="Unsupported claim.")

    with pytest.raises(ValueError, match="accepted.*cannot contain violations"):
        ScriptProposalReview(accepted=True, violations=(violation,))
    with pytest.raises(ValueError, match="rejected.*must contain"):
        ScriptProposalReview(accepted=False)


def test_deepseek_reviewer_detects_structural_feature_does_not_imply_performance(
    tmp_path: Path,
) -> None:
    transport = FakeTransport(
        {
            "accepted": False,
            "violations": [
                {
                    "code": "unsupported_performance_claim",
                    "section_id": "proof",
                    "excerpt": "will not spill in your bag",
                    "reason": "The Brief supports a screw-on lid but not leak resistance.",
                }
            ],
        }
    )
    briefs, _ = repositories(tmp_path / "project.sqlite3")
    brief = guarded_brief(briefs)
    adapter = DeepSeekScriptProposalReviewPort(transport=transport)

    review = adapter.review(
        ScriptProposalReviewRequest(brief=brief, proposal=leak_claim_proposal())
    )

    assert not review.accepted
    assert review.violations[0].code == "unsupported_performance_claim"
    payload = transport.payloads[0]
    assert payload["thinking"] == {"type": "disabled"}
    assert payload["max_tokens"] == 2_000
    assert "does not imply a performance property" in payload["messages"][0]["content"]
    context = json.loads(payload["messages"][1]["content"])
    assert context["brief"]["authoritative_facts"] == [
        {"fact_id": "fact_lid", "statement": "The bottle has a screw-on lid."}
    ]
    assert context["brief"]["prohibited_content"] == ["Do not claim leak resistance."]


def test_deepseek_reviewer_respects_explicit_thinking_configuration(tmp_path: Path) -> None:
    transport = FakeTransport({"accepted": True, "violations": []})
    briefs, _ = repositories(tmp_path / "project.sqlite3")
    brief = guarded_brief(briefs)
    adapter = DeepSeekScriptProposalReviewPort(
        transport=transport,
        config=DeepSeekChatConfig(thinking_enabled=True, max_tokens=1_000),
    )

    review = adapter.review(
        ScriptProposalReviewRequest(brief=brief, proposal=safe_proposal())
    )

    assert review.accepted
    assert transport.payloads[0]["thinking"] == {"type": "enabled"}
    assert transport.payloads[0]["max_tokens"] == 1_000
