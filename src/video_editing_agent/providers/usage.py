from __future__ import annotations

import math
import threading
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TokenUsage:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    reasoning_tokens: int = 0
    cached_input_tokens: int = 0
    source: str = "reported"


def _nonnegative_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _nested_int(value: object, key: str) -> int:
    if not isinstance(value, dict):
        return 0
    parsed = _nonnegative_int(value.get(key))
    return 0 if parsed is None else parsed


def _estimate_text_tokens(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, str):
        if value.startswith("data:") and ";base64," in value:
            return 0
        cjk = sum("\u3400" <= char <= "\u9fff" for char in value)
        non_cjk = max(0, len(value) - cjk)
        return cjk + math.ceil(non_cjk / 4)
    if isinstance(value, (int, float, bool)):
        return _estimate_text_tokens(str(value))
    if isinstance(value, list):
        return sum(_estimate_text_tokens(item) for item in value)
    if isinstance(value, dict):
        total = 0
        for key, item in value.items():
            total += _estimate_text_tokens(str(key))
            if key == "data" and isinstance(item, str) and len(item) > 256:
                continue
            total += _estimate_text_tokens(item)
        return total
    return 0


def extract_token_usage(
    provider: str,
    model: str,
    response: dict[str, Any],
    *,
    request_payload: dict[str, Any] | None = None,
) -> TokenUsage | None:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    reasoning_tokens = 0
    cached_input_tokens = 0

    if provider == "deepseek":
        usage = response.get("usage")
        if isinstance(usage, dict):
            input_tokens = _nonnegative_int(usage.get("prompt_tokens"))
            output_tokens = _nonnegative_int(usage.get("completion_tokens"))
            total_tokens = _nonnegative_int(usage.get("total_tokens"))
            reasoning_tokens = _nested_int(usage.get("completion_tokens_details"), "reasoning_tokens")
            cached_input_tokens = _nonnegative_int(usage.get("prompt_cache_hit_tokens")) or 0
    elif provider == "gemini":
        usage = response.get("usageMetadata")
        if isinstance(usage, dict):
            input_tokens = _nonnegative_int(usage.get("promptTokenCount"))
            output_tokens = _nonnegative_int(usage.get("candidatesTokenCount"))
            total_tokens = _nonnegative_int(usage.get("totalTokenCount"))
            reasoning_tokens = _nonnegative_int(usage.get("thoughtsTokenCount")) or 0
            cached_input_tokens = _nonnegative_int(usage.get("cachedContentTokenCount")) or 0
    elif provider == "openai":
        usage = response.get("usage")
        if isinstance(usage, dict):
            input_tokens = _nonnegative_int(usage.get("input_tokens"))
            output_tokens = _nonnegative_int(usage.get("output_tokens"))
            total_tokens = _nonnegative_int(usage.get("total_tokens"))
            reasoning_tokens = _nested_int(usage.get("output_tokens_details"), "reasoning_tokens")
            cached_input_tokens = _nested_int(usage.get("input_tokens_details"), "cached_tokens")
    else:
        return None

    if input_tokens is not None and output_tokens is not None and total_tokens is not None:
        return TokenUsage(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            reasoning_tokens=reasoning_tokens,
            cached_input_tokens=cached_input_tokens,
        )

    if request_payload is None:
        return None
    estimated_input = _estimate_text_tokens(request_payload)
    estimated_output = _estimate_text_tokens(response)
    return TokenUsage(
        provider=provider,
        model=model,
        input_tokens=estimated_input,
        output_tokens=estimated_output,
        total_tokens=estimated_input + estimated_output,
        source="estimated-text-only",
    )


class ConsoleTokenUsageMeter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._process_total = 0
        self._provider_totals: dict[str, int] = {}

    def record(self, usage: TokenUsage) -> None:
        with self._lock:
            self._process_total += usage.total_tokens
            provider_total = self._provider_totals.get(usage.provider, 0) + usage.total_tokens
            self._provider_totals[usage.provider] = provider_total
            details: list[str] = []
            if usage.cached_input_tokens:
                details.append(f"cached_in={usage.cached_input_tokens:,}")
            if usage.reasoning_tokens:
                details.append(f"reasoning={usage.reasoning_tokens:,}")
            suffix = "" if not details else " " + " ".join(details)
            estimate = "≈" if usage.source != "reported" else ""
            print(
                f"[AI usage] {usage.provider}/{usage.model} "
                f"input={estimate}{usage.input_tokens:,} "
                f"output={estimate}{usage.output_tokens:,} "
                f"total={estimate}{usage.total_tokens:,}{suffix} "
                f"provider_session={provider_total:,} process_session={self._process_total:,} "
                f"source={usage.source}"
            )


_CONSOLE_METER = ConsoleTokenUsageMeter()


def report_token_usage(
    provider: str,
    model: str,
    response: dict[str, Any],
    *,
    request_payload: dict[str, Any] | None = None,
) -> None:
    """Best-effort telemetry only; usage reporting must never break product execution."""
    try:
        usage = extract_token_usage(
            provider,
            model,
            response,
            request_payload=request_payload,
        )
        if usage is not None:
            _CONSOLE_METER.record(usage)
    except (TypeError, ValueError):
        return
