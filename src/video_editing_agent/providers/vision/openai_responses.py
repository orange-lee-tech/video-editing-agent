from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from video_editing_agent.application.ports.artifact_store import ArtifactStore
from video_editing_agent.application.ports.visual_understanding import (
    VisualProviderResponseError,
    VisualProviderTransientError,
    VisualQualityScoreProposal,
    VisualSemanticsProposal,
    VisualUnderstandingPort,
    VisualUnderstandingRequest,
)

OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"
_SUPPORTED_IMAGE_DETAIL = frozenset({"auto", "low", "high"})
_PROPOSAL_KEYS = frozenset(
    {
        "summary",
        "tags",
        "subjects",
        "actions",
        "environment",
        "framing",
        "camera_motion",
        "quality_scores",
    }
)

_VISUAL_PROPOSAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "summary": {"type": ["string", "null"]},
        "tags": {"type": "array", "items": {"type": "string"}},
        "subjects": {"type": "array", "items": {"type": "string"}},
        "actions": {"type": "array", "items": {"type": "string"}},
        "environment": {"type": ["string", "null"]},
        "framing": {"type": ["string", "null"]},
        "camera_motion": {"type": ["string", "null"]},
        "quality_scores": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                },
                "required": ["name", "value"],
            },
        },
    },
    "required": [
        "summary",
        "tags",
        "subjects",
        "actions",
        "environment",
        "framing",
        "camera_motion",
        "quality_scores",
    ],
}

_DEVELOPER_INSTRUCTION = """Analyze the supplied sampled video frames as factual source footage.
Describe only observable visual facts useful to later retrieval and editing. Do not select clips, do not
make timeline decisions, and do not invent events outside the frames. Treat frame order and timestamps
as temporal evidence. Return only the requested structured visual-semantics fields."""


class OpenAIResponsesTransport(Protocol):
    """Provider-internal seam so adapter behavior is testable without live network calls."""

    def create_response(self, payload: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True, slots=True)
class OpenAIResponsesVisualConfig:
    model: str
    image_detail: str = "auto"
    max_output_tokens: int = 1_200

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("model must not be empty")
        if self.image_detail not in _SUPPORTED_IMAGE_DETAIL:
            raise ValueError("image_detail must be one of: auto, low, high")
        if isinstance(self.max_output_tokens, bool) or not isinstance(self.max_output_tokens, int):
            raise TypeError("max_output_tokens must be an int")
        if self.max_output_tokens < 1:
            raise ValueError("max_output_tokens must be >= 1")


class UrllibOpenAIResponsesTransport(OpenAIResponsesTransport):
    """Minimal stdlib transport for the OpenAI Responses endpoint."""

    def __init__(
        self,
        *,
        api_key: str,
        endpoint: str = OPENAI_RESPONSES_ENDPOINT,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key must not be empty")
        if not endpoint.strip():
            raise ValueError("endpoint must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0")
        self._api_key = api_key
        self._endpoint = endpoint
        self._timeout_seconds = timeout_seconds

    def create_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        request = urllib.request.Request(
            self._endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                response_body = response.read()
        except urllib.error.HTTPError as exc:
            if exc.code in {408, 409, 429} or 500 <= exc.code <= 599:
                raise VisualProviderTransientError(
                    f"OpenAI Responses request returned retryable HTTP {exc.code}"
                ) from exc
            raise VisualProviderResponseError(
                f"OpenAI Responses request returned HTTP {exc.code}"
            ) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise VisualProviderTransientError("OpenAI Responses request failed in transport") from exc

        try:
            decoded: Any = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise VisualProviderResponseError("OpenAI Responses returned invalid JSON") from exc
        if not isinstance(decoded, dict):
            raise VisualProviderResponseError("OpenAI Responses returned a non-object JSON payload")
        return decoded


class OpenAIResponsesVisualUnderstanding(VisualUnderstandingPort):
    """Map local sampled-frame artifacts to an OpenAI structured proposal only."""

    def __init__(
        self,
        *,
        artifact_store: ArtifactStore,
        transport: OpenAIResponsesTransport,
        config: OpenAIResponsesVisualConfig,
    ) -> None:
        self._artifact_store = artifact_store
        self._transport = transport
        self._config = config

    def analyze(self, request: VisualUnderstandingRequest) -> VisualSemanticsProposal:
        payload = self._build_request_payload(request)
        response = self._transport.create_response(payload)
        return _parse_response(response)

    def _build_request_payload(self, request: VisualUnderstandingRequest) -> dict[str, Any]:
        user_content: list[dict[str, Any]] = [
            {
                "type": "input_text",
                "text": (
                    f"Shot {request.shot_ref.entity_id}@{request.shot_ref.revision}; "
                    f"analysis profile={request.profile.value}. "
                    "Analyze the following sampled frames in temporal order."
                ),
            }
        ]
        for frame in request.frames:
            content = self._artifact_store.get(frame.artifact_ref)
            encoded = base64.b64encode(content).decode("ascii")
            user_content.append(
                {
                    "type": "input_text",
                    "text": f"Frame {frame.ordinal} at source {frame.source_timestamp_ms} ms.",
                }
            )
            user_content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:{frame.artifact_ref.media_type};base64,{encoded}",
                    "detail": self._config.image_detail,
                }
            )

        return {
            "model": self._config.model,
            "store": False,
            "max_output_tokens": self._config.max_output_tokens,
            "input": [
                {
                    "role": "developer",
                    "content": [{"type": "input_text", "text": _DEVELOPER_INSTRUCTION}],
                },
                {"role": "user", "content": user_content},
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "visual_semantics_proposal",
                    "strict": True,
                    "schema": _VISUAL_PROPOSAL_SCHEMA,
                }
            },
        }


def _parse_response(response: dict[str, Any]) -> VisualSemanticsProposal:
    if response.get("status") != "completed":
        raise VisualProviderResponseError(
            f"OpenAI Responses result was not completed: {response.get('status')!r}"
        )

    output = response.get("output")
    if not isinstance(output, list):
        raise VisualProviderResponseError("OpenAI Responses output must be a list")

    output_text: str | None = None
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if isinstance(part, dict) and part.get("type") == "output_text":
                text = part.get("text")
                if isinstance(text, str):
                    output_text = text
                    break
        if output_text is not None:
            break

    if output_text is None:
        raise VisualProviderResponseError("OpenAI Responses contained no output_text")

    try:
        decoded: Any = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise VisualProviderResponseError("OpenAI structured output was not valid JSON") from exc
    if not isinstance(decoded, dict):
        raise VisualProviderResponseError("OpenAI structured output must be a JSON object")
    if set(decoded) != _PROPOSAL_KEYS:
        raise VisualProviderResponseError("OpenAI structured output had unexpected or missing fields")

    try:
        quality_scores = _parse_quality_scores(decoded["quality_scores"])
        return VisualSemanticsProposal(
            summary=_optional_string(decoded["summary"], "summary"),
            tags=_string_tuple(decoded["tags"], "tags"),
            subjects=_string_tuple(decoded["subjects"], "subjects"),
            actions=_string_tuple(decoded["actions"], "actions"),
            environment=_optional_string(decoded["environment"], "environment"),
            framing=_optional_string(decoded["framing"], "framing"),
            camera_motion=_optional_string(decoded["camera_motion"], "camera_motion"),
            quality_scores=quality_scores,
        )
    except (TypeError, ValueError) as exc:
        raise VisualProviderResponseError("OpenAI structured output failed local validation") from exc


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string or null")
    return value


def _string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise TypeError(f"{field_name} must be an array of strings")
    return tuple(value)


def _parse_quality_scores(value: Any) -> tuple[VisualQualityScoreProposal, ...]:
    if not isinstance(value, list):
        raise TypeError("quality_scores must be an array")

    result: list[VisualQualityScoreProposal] = []
    for item in value:
        if not isinstance(item, dict) or set(item) != {"name", "value"}:
            raise TypeError("quality_scores items must contain exactly name and value")
        result.append(VisualQualityScoreProposal(name=item["name"], value=item["value"]))
    return tuple(result)
