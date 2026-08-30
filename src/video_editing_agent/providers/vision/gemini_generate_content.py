from __future__ import annotations

import base64
import json
import math
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from video_editing_agent.application.ports.artifact_store import ArtifactStore
from video_editing_agent.application.ports.visual_understanding import (
    VisualProviderQuotaError,
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
_RETRY_DELAY_PATTERN = re.compile(r"^([0-9]+(?:\.[0-9]+)?)s$")
_RETRY_MESSAGE_PATTERN = re.compile(r"retry\s+in\s+([0-9]+(?:\.[0-9]+)?)s", re.IGNORECASE)

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


def _parse_retry_delay(value: object) -> float | None:
    if not isinstance(value, str):
        return None
    match = _RETRY_DELAY_PATTERN.fullmatch(value.strip())
    if match is None:
        return None
    delay = float(match.group(1))
    return delay if math.isfinite(delay) else None


def _http_error_metadata(
    exc: urllib.error.HTTPError,
) -> tuple[str | None, float | None, tuple[str, ...]]:
    try:
        body = exc.read()
    except (OSError, ValueError):
        return None, None, ()
    if not body:
        return None, None, ()
    try:
        decoded: Any = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, None, ()
    if not isinstance(decoded, dict):
        return None, None, ()
    error = decoded.get("error")
    if not isinstance(error, dict):
        return None, None, ()

    detail: str | None = None
    message = error.get("message")
    if isinstance(message, str):
        normalized = " ".join(message.split())
        detail = normalized[:500] or None

    retry_after_seconds: float | None = None
    quota_ids: list[str] = []
    details = error.get("details")
    if isinstance(details, list):
        for item in details:
            if not isinstance(item, dict):
                continue
            item_type = item.get("@type")
            if item_type == "type.googleapis.com/google.rpc.RetryInfo":
                if retry_after_seconds is None:
                    retry_after_seconds = _parse_retry_delay(item.get("retryDelay"))
                continue
            if item_type != "type.googleapis.com/google.rpc.QuotaFailure":
                continue
            violations = item.get("violations")
            if not isinstance(violations, list):
                continue
            for violation in violations:
                if not isinstance(violation, dict):
                    continue
                quota_id = violation.get("quotaId")
                if isinstance(quota_id, str) and quota_id.strip():
                    quota_ids.append(quota_id.strip())

    if retry_after_seconds is None and isinstance(message, str):
        match = _RETRY_MESSAGE_PATTERN.search(message)
        if match is not None:
            candidate = float(match.group(1))
            if math.isfinite(candidate):
                retry_after_seconds = candidate

    return detail, retry_after_seconds, tuple(dict.fromkeys(quota_ids))


def _transport_error_detail(exc: urllib.error.URLError) -> str | None:
    reason = getattr(exc, "reason", None)
    value = reason if reason is not None else exc
    normalized = " ".join(str(value).split())
    return normalized[:300] or None


class UrllibGeminiGenerateContentTransport(GeminiGenerateContentTransport):
    """Minimal stdlib transport for Gemini generateContent."""

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
        return self._request_json(endpoint, payload)

    def _request_json(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        request = urllib.request.Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self._api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                response_body = response.read()
        except urllib.error.HTTPError as exc:
            detail, retry_after_seconds, quota_ids = _http_error_metadata(exc)
            suffix = "" if detail is None else f": {detail}"
            hard_daily_quota = exc.code == 429 and any(
                "perday" in quota_id.casefold() for quota_id in quota_ids
            )
            if hard_daily_quota:
                quota_text = ", ".join(quota_ids)
                raise VisualProviderQuotaError(
                    (
                        "Gemini daily request quota is exhausted "
                        f"({quota_text}){suffix}. Short-term automatic retries cannot resolve a "
                        "per-day quota; wait for quota reset, enable higher Gemini quota, or "
                        "switch the Visual API Provider to OpenAI."
                    ),
                    quota_ids=quota_ids,
                    retry_after_seconds=retry_after_seconds,
                ) from exc
            if exc.code in {408, 409, 429} or 500 <= exc.code <= 599:
                raise VisualProviderTransientError(
                    f"Gemini request returned retryable HTTP {exc.code}{suffix}",
                    retry_after_seconds=retry_after_seconds,
                ) from exc
            raise VisualProviderResponseError(
                f"Gemini request returned HTTP {exc.code}{suffix}"
            ) from exc
        except TimeoutError as exc:
            raise VisualProviderTransientError(
                f"Gemini request timed out after {self._timeout_seconds:g} seconds"
            ) from exc
        except urllib.error.URLError as exc:
            detail = _transport_error_detail(exc)
            suffix = "" if detail is None else f": {detail}"
            raise VisualProviderTransientError(
                f"Gemini request failed in transport{suffix}"
            ) from exc

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
            timestamp_text = frame.source_timestamp.to_decimal_seconds_string()
            parts.append({"text": f"Frame {frame.ordinal} at source {timestamp_text} s."})
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
                "maxOutputTokens": self._config.max_output_tokens,
                "responseFormat": {
                    "text": {
                        "mimeType": "APPLICATION_JSON",
                        "schema": _VISUAL_PROPOSAL_SCHEMA,
                    }
                },
            },
        }


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
