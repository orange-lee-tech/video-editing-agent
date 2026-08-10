from __future__ import annotations

import base64
import json
import re
import urllib.error
import urllib.parse
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

GEMINI_API_ROOT = "https://generativelanguage.googleapis.com/v1beta"
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
_STABLE_FLASH_LITE_PATTERN = re.compile(r"^gemini-(\d+)\.(\d+)-flash-lite$")

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

_SYSTEM_INSTRUCTION = (
    "Analyze sampled video frames as factual source footage. "
    "Describe only observable visual facts useful to later retrieval and editing. "
    "Do not select clips, make timeline decisions, or invent events outside the frames. "
    "Treat frame order and timestamps as temporal evidence. "
    "Return only the requested structured visual-semantics fields."
)


class GeminiGenerateContentTransport(Protocol):
    """Provider-internal seam for deterministic adapter tests."""

    def generate_content(self, model: str, payload: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True, slots=True)
class GeminiVisualConfig:
    model: str
    max_output_tokens: int = 1_200

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("model must not be empty")
        if self.model.startswith("models/"):
            raise ValueError("model must use the base model id without the models/ prefix")
        if isinstance(self.max_output_tokens, bool) or not isinstance(self.max_output_tokens, int):
            raise TypeError("max_output_tokens must be an int")
        if self.max_output_tokens < 1:
            raise ValueError("max_output_tokens must be >= 1")


class UrllibGeminiGenerateContentTransport(GeminiGenerateContentTransport):
    """Minimal stdlib transport for Gemini generateContent and models.list."""

    def __init__(
        self,
        *,
        api_key: str,
        api_root: str = GEMINI_API_ROOT,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key must not be empty")
        if not api_root.strip():
            raise ValueError("api_root must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0")
        self._api_key = api_key
        self._api_root = api_root.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def generate_content(self, model: str, payload: dict[str, Any]) -> dict[str, Any]:
        encoded_model = urllib.parse.quote(model, safe="-._")
        endpoint = f"{self._api_root}/models/{encoded_model}:generateContent"
        return self._request_json(endpoint, method="POST", payload=payload)

    def list_models(self) -> tuple[dict[str, Any], ...]:
        models: list[dict[str, Any]] = []
        page_token: str | None = None
        while True:
            query = {"pageSize": "1000"}
            if page_token is not None:
                query["pageToken"] = page_token
            endpoint = f"{self._api_root}/models?{urllib.parse.urlencode(query)}"
            response = self._request_json(endpoint, method="GET")
            page = response.get("models")
            if not isinstance(page, list):
                raise VisualProviderResponseError("Gemini models.list returned no models array")
            for item in page:
                if isinstance(item, dict):
                    models.append(item)
            next_token = response.get("nextPageToken")
            if next_token is None:
                break
            if not isinstance(next_token, str) or not next_token:
                raise VisualProviderResponseError(
                    "Gemini models.list returned an invalid page token"
                )
            page_token = next_token
        return tuple(models)

    def _request_json(
        self,
        endpoint: str,
        *,
        method: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        request = urllib.request.Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self._api_key,
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                response_body = response.read()
        except urllib.error.HTTPError as exc:
            if exc.code in {408, 409, 429} or 500 <= exc.code <= 599:
                raise VisualProviderTransientError(
                    f"Gemini request returned retryable HTTP {exc.code}"
                ) from exc
            raise VisualProviderResponseError(
                f"Gemini request returned HTTP {exc.code}"
            ) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise VisualProviderTransientError("Gemini request failed in transport") from exc

        try:
            decoded: Any = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise VisualProviderResponseError("Gemini returned invalid JSON") from exc
        if not isinstance(decoded, dict):
            raise VisualProviderResponseError("Gemini returned a non-object JSON payload")
        return decoded


class GeminiGenerateContentVisualUnderstanding(VisualUnderstandingPort):
    """Map local sampled-frame artifacts to a Gemini structured proposal only."""

    def __init__(
        self,
        *,
        artifact_store: ArtifactStore,
        transport: GeminiGenerateContentTransport,
        config: GeminiVisualConfig,
    ) -> None:
        self._artifact_store = artifact_store
        self._transport = transport
        self._config = config

    def analyze(self, request: VisualUnderstandingRequest) -> VisualSemanticsProposal:
        payload = self._build_request_payload(request)
        response = self._transport.generate_content(self._config.model, payload)
        return _parse_response(response)

    def _build_request_payload(self, request: VisualUnderstandingRequest) -> dict[str, Any]:
        parts: list[dict[str, Any]] = [
            {
                "text": (
                    f"Shot {request.shot_ref.entity_id}@{request.shot_ref.revision}; "
                    f"analysis profile={request.profile.value}. "
                    "Analyze the following sampled frames in temporal order."
                )
            }
        ]
        for frame in request.frames:
            content = self._artifact_store.get(frame.artifact_ref)
            encoded = base64.b64encode(content).decode("ascii")
            parts.append(
                {"text": f"Frame {frame.ordinal} at source {frame.source_timestamp_ms} ms."}
            )
            parts.append(
                {
                    "inlineData": {
                        "mimeType": frame.artifact_ref.media_type,
                        "data": encoded,
                    }
                }
            )

        return {
            "systemInstruction": {"parts": [{"text": _SYSTEM_INSTRUCTION}]},
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "temperature": 0,
                "maxOutputTokens": self._config.max_output_tokens,
                "responseMimeType": "application/json",
                "responseJsonSchema": _VISUAL_PROPOSAL_SCHEMA,
            },
        }


def select_stable_flash_lite_model(models: tuple[dict[str, Any], ...]) -> str:
    """Choose the highest-version stable Flash-Lite model exposed by models.list."""

    candidates: dict[tuple[int, int], str] = {}
    for model in models:
        methods = model.get("supportedGenerationMethods")
        if not isinstance(methods, list) or "generateContent" not in methods:
            continue
        base_model_id = model.get("baseModelId")
        if not isinstance(base_model_id, str):
            continue
        match = _STABLE_FLASH_LITE_PATTERN.fullmatch(base_model_id)
        if match is None:
            continue
        version = (int(match.group(1)), int(match.group(2)))
        candidates[version] = base_model_id

    if not candidates:
        raise VisualProviderResponseError(
            "Gemini models.list exposed no stable gemini-X.Y-flash-lite generateContent model"
        )
    return candidates[max(candidates)]


def _parse_response(response: dict[str, Any]) -> VisualSemanticsProposal:
    candidates = response.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise VisualProviderResponseError("Gemini response contained no candidates")

    first = candidates[0]
    if not isinstance(first, dict):
        raise VisualProviderResponseError("Gemini candidate must be an object")
    content = first.get("content")
    if not isinstance(content, dict):
        raise VisualProviderResponseError("Gemini candidate contained no content")
    parts = content.get("parts")
    if not isinstance(parts, list):
        raise VisualProviderResponseError("Gemini candidate content contained no parts")

    output_text: str | None = None
    for part in parts:
        if not isinstance(part, dict):
            continue
        text = part.get("text")
        if isinstance(text, str):
            output_text = text
            break
    if output_text is None:
        raise VisualProviderResponseError("Gemini response contained no text output")

    try:
        decoded: Any = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise VisualProviderResponseError("Gemini structured output was not valid JSON") from exc
    if not isinstance(decoded, dict):
        raise VisualProviderResponseError("Gemini structured output must be a JSON object")
    if set(decoded) != _PROPOSAL_KEYS:
        raise VisualProviderResponseError(
            "Gemini structured output had unexpected or missing fields"
        )

    try:
        return VisualSemanticsProposal(
            summary=_optional_string(decoded["summary"], "summary"),
            tags=_string_tuple(decoded["tags"], "tags"),
            subjects=_string_tuple(decoded["subjects"], "subjects"),
            actions=_string_tuple(decoded["actions"], "actions"),
            environment=_optional_string(decoded["environment"], "environment"),
            framing=_optional_string(decoded["framing"], "framing"),
            camera_motion=_optional_string(decoded["camera_motion"], "camera_motion"),
            quality_scores=_parse_quality_scores(decoded["quality_scores"]),
        )
    except (TypeError, ValueError) as exc:
        raise VisualProviderResponseError(
            "Gemini structured output failed local validation"
        ) from exc


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
