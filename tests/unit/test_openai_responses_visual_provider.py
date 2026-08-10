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
from video_editing_agent.providers.vision.openai_responses import (
    OpenAIResponsesVisualConfig,
    OpenAIResponsesVisualUnderstanding,
    UrllibOpenAIResponsesTransport,
)


class FakeArtifactStore:
    def __init__(self, values: dict[str, bytes]) -> None:
        self._values = values

    def get(self, ref: StoredArtifactRef) -> bytes:
        return self._values[ref.artifact_id]


class FakeTransport:
    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response
        self.payload: dict[str, Any] | None = None

    def create_response(self, payload: dict[str, Any]) -> dict[str, Any]:
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
        shot_ref=EntityRevisionRef("sht_openai", 1),
        profile=AnalysisProfile.EDITORIAL,
        frames=(
            VisualFrameReference(first_ref, ordinal=0, source_timestamp_ms=100),
            VisualFrameReference(second_ref, ordinal=1, source_timestamp_ms=900),
        ),
    )
    return request, {first_ref.artifact_id: first, second_ref.artifact_id: second}


def completed_response(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "completed",
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(payload),
                    }
                ],
            }
        ],
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


def test_adapter_sends_local_pngs_as_data_urls_and_returns_proposal() -> None:
    request, values = request_with_two_frames()
    transport = FakeTransport(completed_response(valid_semantics_payload()))
    adapter = OpenAIResponsesVisualUnderstanding(
        artifact_store=FakeArtifactStore(values),  # type: ignore[arg-type]
        transport=transport,
        config=OpenAIResponsesVisualConfig(model="test-vision-model", image_detail="high"),
    )

    proposal = adapter.analyze(request)

    assert proposal.summary == "A craftsperson sands wood at a bench."
    assert proposal.tags == ("woodworking", "workbench")
    assert proposal.subjects == ("craftsperson",)
    assert proposal.actions == ("sanding",)
    assert proposal.quality_scores[0].name == "aesthetic"
    assert proposal.quality_scores[0].value == pytest.approx(0.82)

    assert transport.payload is not None
    payload = transport.payload
    assert payload["model"] == "test-vision-model"
    assert payload["store"] is False
    assert payload["text"]["format"]["type"] == "json_schema"
    assert payload["text"]["format"]["strict"] is True
    assert payload["text"]["format"]["schema"]["additionalProperties"] is False

    user_content = payload["input"][1]["content"]
    images = [item for item in user_content if item["type"] == "input_image"]
    assert len(images) == 2
    assert all(image["detail"] == "high" for image in images)
    assert images[0]["image_url"].startswith("data:image/png;base64,")
    encoded = images[0]["image_url"].split(",", 1)[1]
    assert base64.b64decode(encoded) == values[request.frames[0].artifact_ref.artifact_id]


def test_adapter_rejects_structured_output_with_missing_or_extra_fields() -> None:
    request, values = request_with_two_frames()
    malformed = valid_semantics_payload()
    del malformed["camera_motion"]
    malformed["editing_decision"] = "cut here"
    adapter = OpenAIResponsesVisualUnderstanding(
        artifact_store=FakeArtifactStore(values),  # type: ignore[arg-type]
        transport=FakeTransport(completed_response(malformed)),
        config=OpenAIResponsesVisualConfig(model="test-vision-model"),
    )

    with pytest.raises(VisualProviderResponseError, match="unexpected or missing"):
        adapter.analyze(request)


def test_adapter_rejects_non_completed_response() -> None:
    request, values = request_with_two_frames()
    adapter = OpenAIResponsesVisualUnderstanding(
        artifact_store=FakeArtifactStore(values),  # type: ignore[arg-type]
        transport=FakeTransport({"status": "incomplete", "output": []}),
        config=OpenAIResponsesVisualConfig(model="test-vision-model"),
    )

    with pytest.raises(VisualProviderResponseError, match="not completed"):
        adapter.analyze(request)


def test_transport_classifies_retryable_http_status(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_429(*args: object, **kwargs: object) -> FakeHttpResponse:
        del args, kwargs
        raise urllib.error.HTTPError("https://example.invalid", 429, "rate limit", None, None)

    monkeypatch.setattr("urllib.request.urlopen", raise_429)
    transport = UrllibOpenAIResponsesTransport(api_key="secret", endpoint="https://example.invalid")

    with pytest.raises(VisualProviderTransientError, match="retryable HTTP 429"):
        transport.create_response({"model": "test"})


def test_transport_classifies_non_retryable_http_status(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_400(*args: object, **kwargs: object) -> FakeHttpResponse:
        del args, kwargs
        raise urllib.error.HTTPError("https://example.invalid", 400, "bad request", None, None)

    monkeypatch.setattr("urllib.request.urlopen", raise_400)
    transport = UrllibOpenAIResponsesTransport(api_key="secret", endpoint="https://example.invalid")

    with pytest.raises(VisualProviderResponseError, match="HTTP 400"):
        transport.create_response({"model": "test"})


def test_transport_rejects_invalid_json_response(monkeypatch: pytest.MonkeyPatch) -> None:
    def return_invalid_json(*args: object, **kwargs: object) -> FakeHttpResponse:
        del args, kwargs
        return FakeHttpResponse(b"not-json")

    monkeypatch.setattr("urllib.request.urlopen", return_invalid_json)
    transport = UrllibOpenAIResponsesTransport(api_key="secret", endpoint="https://example.invalid")

    with pytest.raises(VisualProviderResponseError, match="invalid JSON"):
        transport.create_response({"model": "test"})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model", ""),
        ("image_detail", "ultra"),
        ("max_output_tokens", 0),
    ],
)
def test_config_rejects_invalid_values(field: str, value: object) -> None:
    kwargs: dict[str, object] = {"model": "test-vision-model"}
    kwargs[field] = value

    with pytest.raises((TypeError, ValueError)):
        OpenAIResponsesVisualConfig(**kwargs)  # type: ignore[arg-type]
