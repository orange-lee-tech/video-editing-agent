import json
from typing import Any

import pytest

from video_editing_agent.application.ports.artifact_store import StoredArtifactRef
from video_editing_agent.application.ports.visual_understanding import (
    VisualFrameReference,
    VisualUnderstandingRequest,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shot.analysis import AnalysisProfile
from video_editing_agent.providers.vision.gemini_generate_content import (
    GeminiGenerateContentVisualUnderstanding,
    GeminiVisualConfig,
)
from video_editing_agent.providers.vision.openai_responses import (
    OpenAIResponsesVisualConfig,
    OpenAIResponsesVisualUnderstanding,
)


class FakeArtifactStore:
    def get(self, ref: StoredArtifactRef) -> bytes:
        del ref
        return b"png"


class CapturingGeminiTransport:
    def __init__(self) -> None:
        self.payload: dict[str, Any] | None = None

    def generate_content(self, model: str, payload: dict[str, Any]) -> dict[str, Any]:
        del model
        self.payload = payload
        return {"candidates": [{"content": {"parts": [{"text": json.dumps(_valid_semantics())}]}}]}


class CapturingOpenAITransport:
    def __init__(self) -> None:
        self.payload: dict[str, Any] | None = None

    def create_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.payload = payload
        return {
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": json.dumps(_valid_semantics())}],
                }
            ],
        }


def _valid_semantics() -> dict[str, Any]:
    return {
        "summary": None,
        "tags": [],
        "subjects": [],
        "actions": [],
        "environment": None,
        "framing": None,
        "camera_motion": None,
        "quality_scores": [],
    }


def _fractional_request() -> VisualUnderstandingRequest:
    digest = "1" * 64
    artifact = StoredArtifactRef(
        artifact_id=f"art_sha256_{digest}",
        content_hash=f"sha256:{digest}",
        media_type="image/png",
        byte_size=3,
    )
    frame = VisualFrameReference(
        artifact_ref=artifact,
        ordinal=0,
        source_timestamp=MediaTime(1, 24),
    )
    return VisualUnderstandingRequest(
        shot_ref=EntityRevisionRef("sht_fractional", 1),
        profile=AnalysisProfile.SEMANTIC,
        frames=(frame,),
    )


def test_gemini_prompt_accepts_non_millisecond_exact_timestamp() -> None:
    request = _fractional_request()
    transport = CapturingGeminiTransport()
    adapter = GeminiGenerateContentVisualUnderstanding(
        artifact_store=FakeArtifactStore(),  # type: ignore[arg-type]
        transport=transport,
        config=GeminiVisualConfig(model="gemini-3.6-flash"),
    )

    adapter.analyze(request)

    assert request.frames[0].source_timestamp == MediaTime(1, 24)
    with pytest.raises(ValueError, match="exact integer millisecond"):
        _ = request.frames[0].source_timestamp_ms
    assert transport.payload is not None
    parts = transport.payload["contents"][0]["parts"]
    assert {"text": "Frame 0 at source 0.041666667 s."} in parts


def test_openai_prompt_accepts_non_millisecond_exact_timestamp() -> None:
    request = _fractional_request()
    transport = CapturingOpenAITransport()
    adapter = OpenAIResponsesVisualUnderstanding(
        artifact_store=FakeArtifactStore(),  # type: ignore[arg-type]
        transport=transport,
        config=OpenAIResponsesVisualConfig(model="gpt-5-mini"),
    )

    adapter.analyze(request)

    assert request.frames[0].source_timestamp == MediaTime(1, 24)
    assert transport.payload is not None
    user_content = transport.payload["input"][1]["content"]
    assert {
        "type": "input_text",
        "text": "Frame 0 at source 0.041666667 s.",
    } in user_content
