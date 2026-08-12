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
from video_editing_agent.providers.llm.deepseek_chat import (
    DeepSeekChatConfig,
    DeepSeekPlanningResponseError,
)
from video_editing_agent.providers.llm.deepseek_preproduction_review import (
    REVIEW_CAPACITY_RECOVERY_MAX_TOKENS,
    REVIEW_INITIAL_MAX_TOKENS,
    DeepSeekReviewCapacityError,
    DeepSeekScriptProposalReviewPort,
)
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase

NOW = datetime(2026, 8, 12, 0, 30, tzinfo=UTC)


class CountingPlanningPort:
    def __init__(self, proposal: ScriptPlanProposal | list[ScriptPlanProposal]) -> None:
        self.proposals = proposal if isinstance(proposal, list) else [proposal]
        self.requests: list[ScriptPlanningRequest] = []

    def propose(self, request: ScriptPlanningRequest) -> ScriptPlanProposal:
        self.requests.append(request)
        return self.proposals[min(len(self.requests) - 1, len(self.proposals) - 1)]


class StaticReviewPort:
    def __init__(self, review: ScriptProposalReview | list[ScriptProposalReview]) -> None:
        self.results = review if isinstance(review, list) else [review]
        self.requests: list[ScriptProposalReviewRequest] = []

    def review(self, request: ScriptProposalReviewRequest) -> ScriptProposalReview:
        self.requests.append(request)
        return self.results[min(len(self.requests) - 1, len(self.results) - 1)]


class FakeTransport:
    def __init__(self, content: dict[str, Any] | str | list[dict[str, Any] | str]) -> None:
        self.contents = content if isinstance(content, list) else [content]
        self.payloads: list[dict[str, Any]] = []

    def create_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.payloads.append(payload)
        content = self.contents[min(len(self.payloads) - 1, len(self.contents) - 1)]
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": content if isinstance(content, str) else json.dumps(content)
                    },
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
    review_port = StaticReviewPort(ScriptProposalReview(accepted=False, violations=(violation,)))

    with pytest.raises(ScriptProposalRejectedError) as captured:
        workflow(briefs, scripts, planning_port, review_port).generate(
            EntityRevisionRef(brief.envelope.id, 1)
        )

    assert captured.value.review.violations == (violation,)
    assert len(review_port.requests) == 2
    assert len(planning_port.requests) == 2
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


def test_script_semantic_veto_repairs_once_then_commits(tmp_path: Path) -> None:
    briefs, scripts = repositories(tmp_path / "project.sqlite3")
    brief = guarded_brief(briefs)
    violation = ScriptProposalViolation(
        code="unsupported_claim",
        section_id="proof",
        excerpt="will not spill",
        reason="Leak resistance is not authoritative.",
    )
    planning_port = CountingPlanningPort([leak_claim_proposal(), safe_proposal()])
    review_port = StaticReviewPort(
        [ScriptProposalReview(False, (violation,)), ScriptProposalReview(True)]
    )

    script = workflow(briefs, scripts, planning_port, review_port).generate(
        EntityRevisionRef(brief.envelope.id, 1)
    )

    assert len(planning_port.requests) == 2
    assert len(review_port.requests) == 2
    assert script.sections[0].spoken_content == safe_proposal().sections[0].spoken_content
    repair = planning_port.requests[1].instruction or ""
    assert "code=unsupported_claim" in repair
    assert "section_id=proof" in repair
    assert "not an authoritative product fact" in repair
    assert planning_port.requests[1].brief.authoritative_facts == brief.authoritative_facts


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
    assert len(transport.payloads) == 1
    payload = transport.payloads[0]
    assert payload["thinking"] == {"type": "enabled"}
    assert payload["max_tokens"] == REVIEW_INITIAL_MAX_TOKENS
    assert "does not imply a performance property" in payload["messages"][0]["content"]
    assert "500 mL does not prove" in payload["messages"][0]["content"]
    assert "screw-on lid does not prove one-hand operation" in payload["messages"][0]["content"]
    context = json.loads(payload["messages"][1]["content"])
    assert context["brief"]["authoritative_facts"] == [
        {"fact_id": "fact_lid", "statement": "The bottle has a screw-on lid."}
    ]
    assert context["brief"]["prohibited_content"] == ["Do not claim leak resistance."]
    prompt = payload["messages"][0]["content"]
    assert "{'accepted'" not in prompt
    assert '{"accepted":true,"violations":[]}' in prompt
    assert '"section_id"' in prompt
    assert "Never rewrite the proposal" in prompt
    assert payload["response_format"] == {"type": "json_object"}


def test_script_review_recovers_once_from_malformed_json(tmp_path: Path) -> None:
    transport = FakeTransport(
        ["{'accepted': True, 'violations': []}", {"accepted": True, "violations": []}]
    )
    briefs, _ = repositories(tmp_path / "project.sqlite3")
    adapter = DeepSeekScriptProposalReviewPort(transport=transport)

    review = adapter.review(
        ScriptProposalReviewRequest(brief=guarded_brief(briefs), proposal=safe_proposal())
    )

    assert review.accepted
    assert len(transport.payloads) == 2
    assert "previous response did not satisfy" in transport.payloads[1]["messages"][2]["content"]


class ResponseTransport:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = responses
        self.payloads: list[dict[str, Any]] = []

    def create_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.payloads.append(payload)
        return self.responses[len(self.payloads) - 1]


def response(finish_reason: str, content: dict[str, Any], *, reasoning: str = "private"):
    return {
        "choices": [
            {
                "finish_reason": finish_reason,
                "message": {"content": json.dumps(content), "reasoning_content": reasoning},
            }
        ],
        "usage": {
            "prompt_tokens": 101,
            "completion_tokens": 202,
            "completion_tokens_details": {"reasoning_tokens": 199},
        },
    }


@pytest.mark.parametrize(
    "decision",
    [
        {"accepted": True, "violations": []},
        {
            "accepted": False,
            "violations": [
                {
                    "code": "unsupported",
                    "section_id": "demo",
                    "excerpt": None,
                    "reason": "unsupported",
                }
            ],
        },
    ],
)
def test_script_review_recovers_once_from_length(tmp_path: Path, decision) -> None:
    transport = ResponseTransport([response("length", decision), response("stop", decision)])
    briefs, _ = repositories(tmp_path / "project.sqlite3")

    review = DeepSeekScriptProposalReviewPort(transport=transport).review(
        ScriptProposalReviewRequest(guarded_brief(briefs), safe_proposal())
    )

    assert review.accepted is decision["accepted"]
    assert len(transport.payloads) == 2
    assert transport.payloads[0]["max_tokens"] == REVIEW_INITIAL_MAX_TOKENS
    assert transport.payloads[1]["max_tokens"] == REVIEW_CAPACITY_RECOVERY_MAX_TOKENS
    assert len(transport.payloads[1]["messages"]) == 2


def test_script_review_length_twice_raises_safe_capacity_error(tmp_path: Path) -> None:
    decision = {"accepted": True, "violations": []}
    transport = ResponseTransport([response("length", decision), response("length", decision)])
    briefs, _ = repositories(tmp_path / "project.sqlite3")

    with pytest.raises(DeepSeekReviewCapacityError) as captured:
        DeepSeekScriptProposalReviewPort(transport=transport).review(
            ScriptProposalReviewRequest(guarded_brief(briefs), safe_proposal())
        )

    assert len(transport.payloads) == 2
    assert captured.value.diagnostics.reasoning_tokens == 199
    assert captured.value.diagnostics.capacity_recovery_attempted
    assert "private" not in str(captured.value)


def test_script_review_malformed_twice_fails_closed(tmp_path: Path) -> None:
    transport = FakeTransport(["{'accepted': True}", "{'accepted': True}"])
    briefs, _ = repositories(tmp_path / "project.sqlite3")
    adapter = DeepSeekScriptProposalReviewPort(transport=transport)

    with pytest.raises(DeepSeekPlanningResponseError, match="not valid JSON"):
        adapter.review(
            ScriptProposalReviewRequest(brief=guarded_brief(briefs), proposal=safe_proposal())
        )
    assert len(transport.payloads) == 2


def test_script_review_schema_failure_recovers_once(tmp_path: Path) -> None:
    transport = FakeTransport([{"accepted": True}, {"accepted": True, "violations": []}])
    briefs, _ = repositories(tmp_path / "project.sqlite3")
    adapter = DeepSeekScriptProposalReviewPort(transport=transport)

    review = adapter.review(
        ScriptProposalReviewRequest(brief=guarded_brief(briefs), proposal=safe_proposal())
    )

    assert review.accepted
    assert len(transport.payloads) == 2


def test_deepseek_reviewer_respects_explicit_non_thinking_configuration(
    tmp_path: Path,
) -> None:
    transport = FakeTransport({"accepted": True, "violations": []})
    briefs, _ = repositories(tmp_path / "project.sqlite3")
    brief = guarded_brief(briefs)
    adapter = DeepSeekScriptProposalReviewPort(
        transport=transport,
        config=DeepSeekChatConfig(thinking_enabled=False, max_tokens=1_000),
    )

    review = adapter.review(ScriptProposalReviewRequest(brief=brief, proposal=safe_proposal()))

    assert review.accepted
    assert transport.payloads[0]["thinking"] == {"type": "disabled"}
    assert transport.payloads[0]["max_tokens"] == 1_000
