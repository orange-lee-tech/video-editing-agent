from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pytest

from video_editing_agent.application.ports.director import (
    DirectorFootageEvidence,
    DirectorRequest,
)
from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shot.analysis import AnalysisProfile
from video_editing_agent.providers.llm.deepseek_chat import (
    DeepSeekChatConfig,
    DeepSeekPlanningResponseError,
)
from video_editing_agent.providers.llm.deepseek_director import DeepSeekDirectorPort

NOW = datetime(2026, 8, 18, tzinfo=UTC)


def _request() -> DirectorRequest:
    brief = Brief(
        EntityEnvelope("brief", 1, "0.2", EntityStatus.VALID, NOW, "test"),
        "Small bottle",
        "Explain portability",
        "commuters",
        "short video",
        "compact and convenient",
    )
    evidence = DirectorFootageEvidence(
        EntityRevisionRef("shot", 1),
        EntityRevisionRef("asset", 1),
        1,
        AnalysisProfile.SEMANTIC,
        "small bottle on a desk",
        ("bottle",),
        ("bottle",),
        (),
    )
    return DirectorRequest(brief, (evidence,))


def _slot(*, scale: int, semantic_query: str = "small bottle close-up") -> dict[str, object]:
    return {
        "slot_id": "hook",
        "order": 0,
        "narrative_role": "hook",
        "purpose": "show the bottle",
        "semantic_query": semantic_query,
        "minimum_duration": {"value": 1, "scale": scale},
        "maximum_duration": {"value": 2, "scale": 1},
        "pacing": "quick",
        "continuity_hint": None,
        "allow_reuse": False,
        "importance": 3,
    }


def _completion(content: dict[str, object]) -> dict[str, object]:
    return {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": json.dumps(content)},
            }
        ]
    }


class SequenceTransport:
    def __init__(self, responses: list[dict[str, object]]) -> None:
        self.responses = responses
        self.payloads: list[dict[str, Any]] = []

    def create_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.payloads.append(payload)
        return self.responses.pop(0)


def test_director_repairs_one_locally_invalid_duration_proposal() -> None:
    transport = SequenceTransport(
        [
            _completion({"slots": [_slot(scale=0)]}),
            _completion({"slots": [_slot(scale=1)]}),
        ]
    )
    port = DeepSeekDirectorPort(transport=transport, config=DeepSeekChatConfig())

    proposal = port.propose(_request())

    assert proposal.slots[0].minimum_duration == MediaTime(1, 1)
    assert len(transport.payloads) == 2
    repair_context = json.loads(transport.payloads[1]["messages"][1]["content"])
    assert repair_context["repair_feedback"]["local_validation_error"] == (
        "minimum_duration.scale must be > 0"
    )


def test_director_repairs_query_language_to_match_footage_evidence() -> None:
    transport = SequenceTransport(
        [
            _completion({"slots": [_slot(scale=1, semantic_query="小水杯产品特写")]}),
            _completion({"slots": [_slot(scale=1, semantic_query="small bottle close-up")]}),
        ]
    )
    port = DeepSeekDirectorPort(transport=transport, config=DeepSeekChatConfig())

    proposal = port.propose(_request())

    assert proposal.slots[0].semantic_query == "small bottle close-up"
    assert len(transport.payloads) == 2
    repair_context = json.loads(transport.payloads[1]["messages"][1]["content"])
    error = repair_context["repair_feedback"]["local_validation_error"]
    assert "evidence is Latin-script but the query is CJK-only" in error
    instruction = repair_context["repair_feedback"]["instruction"]
    assert "preserve the evidence language" in instruction


def test_director_repair_is_bounded_to_one_extra_proposal() -> None:
    transport = SequenceTransport(
        [
            _completion({"slots": [_slot(scale=0)]}),
            _completion({"slots": [_slot(scale=0)]}),
        ]
    )
    port = DeepSeekDirectorPort(transport=transport, config=DeepSeekChatConfig())

    with pytest.raises(DeepSeekPlanningResponseError, match=r"minimum_duration\.scale must be > 0"):
        port.propose(_request())

    assert len(transport.payloads) == 2
