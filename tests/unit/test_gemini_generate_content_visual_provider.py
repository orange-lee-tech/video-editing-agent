import base64
import json
import urllib.error
from typing import Any

import pytest

from video_editing_agent.application.ports.artifact_store import StoredArtifactRef
from video_editing_agent.application.ports.visual_understanding import (
    VisualFrameReference,
    VisualProviderResponseError,
    VisualProviderTransientError,
    VisualUnderstandingRequest,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import AnalysisProfile
from video_editing_agent.providers.vision.gemini_generate_content import (
    GeminiGenerateContentVisualUnderstanding,
    GeminiVisualConfig,
    UrllibGeminiGenerateContentTransport,
)


class FakeArtifactStore:
    def __init__(self, values: dict[str, bytes]) -> None:
        self._values = values

    def get(self, ref: StoredArtifactRef) -> bytes:
        return self._values[ref.artifact_id]


class FakeTransport:
    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response
        self.model: str | None = None
        self.payload: dict[str, Any] | None = None

    def generate_content(self, model: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.model = model
        self.payload = payload
        return self.response


class FakeHttpResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> "FakeHttpResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        del exc_type, exc, traceback

    def read(self) -> bytes:
        return self._body


def artifact_ref(digest_character: str, *, byte_size: int) -> StoredArtifactRef:
    digest = digest_character * 64
    return StoredArtifactRef(
        artifact_id=f"art_sha256_{digest}",
        content_hash=f"sha256:{digest}",
        media_type="image/png",
        byte_size=byte_size,
    )


def request_with_two_frames() -> tuple[VisualUnderstandingRequest, dict[str, bytes]]:
    first = b"png-frame-one"
    second = b"png-frame-two"
    first_ref = artifact_ref("1", byte_size=len(first))
    second_ref = artifact_ref("2", byte_size=len(second))
    request = VisualUnderstandingRequest(
        shot_ref=EntityRevisionRef("sht_gemini", 1),
        profile=AnalysisProfile.EDITORIAL,
        frames=(
            VisualFrameReference(first_ref, ordinal=0, source_timestamp_ms=100),
            VisualFrameReference(second_ref, ordinal=1, source_timestamp_ms=900),
        ),
    )
    return request, {first_ref.artifact_id: first, second_ref.artifact_id: second}


def completed_response(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [{"text": json.dumps(payload)}],
                },
                "finishReason": "STOP",
            }
        ]
    }


def valid_semantics_payload() -> dict[str, Any]:
    return {
        "summary": "A craftsperson sands wood at a bench.",
        "tags": ["woodworking", "workbench"],
        "subjects": ["craftsperson"],
        "actions": ["sanding"],
        "environment": "workshop",
        "framing": "medium",
        "camera_motion": "static",
        "quality_scores": [{"name": "aesthetic", "value": 0.82}],
    }


def test_adapter_sends_inline_pngs_and_returns_proposal() -> None:
    request, values = request_with_two_frames()
    transport = FakeTransport(completed_response(valid_semantics_payload()))
    adapter = GeminiGenerateContentVisualUnderstanding(
        artifact_store=FakeArtifactStore(values),  # type: ignore[arg-type]
        transport=transport,
        config=GeminiVisualConfig(model="gemini-3.5-flash-lite"),
    )

    proposal = adapter.analyze(request)

    assert proposal.summary == "A craftsperson sands wood at a bench."
    assert proposal.tags == ("woodworking", "workbench")
    assert proposal.subjects == ("craftsperson",)
    assert proposal.actions == ("sanding",)
    assert proposal.quality_scores[0].value == pytest.approx(0.82)

    assert transport.model == "gemini-3.5-flash-lite"
    assert transport.payload is not None
    generation_config = transport.payload["generationConfig"]
    assert generation_config["responseMimeType"] == "application/json"
    assert generation_config["responseJsonSchema"]["additionalProperties"] is False
    assert "temperature" not in generation_config

    parts = transport.payload["contents"][0]["parts"]
    images = [item["inlineData"] for item in parts if "inlineData" in item]
    assert len(images) == 2
    assert images[0]["mimeType"] == "image/png"
    assert base64.b64decode(images[0]["data"]) == values[request.frames[0].artifact_ref.artifact_id]


def test_adapter_rejects_structured_output_with_missing_or_extra_fields() -> None:
    request, values = request_with_two_frames()
    malformed = valid_semantics_payload()
    del malformed["camera_motion"]
    malformed["editing_decision"] = "cut here"
    adapter = GeminiGenerateContentVisualUnderstanding(
        artifact_store=FakeArtifactStore(values),  # type: ignore[arg-type]
        transport=FakeTransport(completed_response(malformed)),
        config=GeminiVisualConfig(model="gemini-3.5-flash-lite"),
    )

    with pytest.raises(VisualProviderResponseError, match="unexpected or missing"):
        adapter.analyze(request)


def test_adapter_rejects_response_without_candidates() -> None:
    request, values = request_with_two_frames()
    adapter = GeminiGenerateContentVisualUnderstanding(
        artifact_store=FakeArtifactStore(values),  # type: ignore[arg-type]
        transport=FakeTransport({"promptFeedback": {"blockReason": "SAFETY"}}),
        config=GeminiVisualConfig(model="gemini-3.5-flash-lite"),
    )

    with pytest.raises(VisualProviderResponseError, match="no candidates"):
        adapter.analyze(request)


def test_transport_classifies_retryable_http_status(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_429(*args: object, **kwargs: object) -> FakeHttpResponse:
        del args, kwargs
        raise urllib.error.HTTPError("https://example.invalid", 429, "rate limit", None, None)

    monkeypatch.setattr("urllib.request.urlopen", raise_429)
    transport = UrllibGeminiGenerateContentTransport(
        api_key="secret",
        api_root="https://example.invalid",
    )

    with pytest.raises(VisualProviderTransientError, match="retryable HTTP 429"):
        transport.generate_content("gemini-3.5-flash-lite", {"contents": []})


def test_transport_classifies_non_retryable_http_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_400(*args: object, **kwargs: object) -> FakeHttpResponse:
        del args, kwargs
        raise urllib.error.HTTPError("https://example.invalid", 400, "bad request", None, None)

    monkeypatch.setattr("urllib.request.urlopen", raise_400)
    transport = UrllibGeminiGenerateContentTransport(
        api_key="secret",
        api_root="https://example.invalid",
    )

    with pytest.raises(VisualProviderResponseError, match="HTTP 400"):
        transport.generate_content("gemini-3.5-flash-lite", {"contents": []})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model", ""),
        ("model", "models/gemini-3.5-flash-lite"),
        ("max_output_tokens", 0),
    ],
)
def test_config_rejects_invalid_values(field: str, value: object) -> None:
    kwargs: dict[str, object] = {"model": "gemini-3.5-flash-lite"}
    kwargs[field] = value

    with pytest.raises((TypeError, ValueError)):
        GeminiVisualConfig(**kwargs)  # type: ignore[arg-type]
