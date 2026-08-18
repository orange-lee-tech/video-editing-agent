from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass

from video_editing_agent.application.ports.visual_understanding import (
    VisualProviderTransientError,
    VisualSemanticsProposal,
    VisualUnderstandingPort,
    VisualUnderstandingRequest,
)


@dataclass(frozen=True, slots=True)
class VisualRetryPolicy:
    """Retry only explicit transient provider failures using bounded backoff."""

    max_attempts: int = 3
    base_delay_seconds: float = 0.3

    def __post_init__(self) -> None:
        if isinstance(self.max_attempts, bool) or not isinstance(self.max_attempts, int):
            raise TypeError("max_attempts must be an int")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if isinstance(self.base_delay_seconds, bool) or not isinstance(
            self.base_delay_seconds, (int, float)
        ):
            raise TypeError("base_delay_seconds must be a number")
        delay = float(self.base_delay_seconds)
        if not math.isfinite(delay) or delay < 0:
            raise ValueError("base_delay_seconds must be finite and >= 0")


class RetryingVisualUnderstandingPort:
    """Retry decorator that does not convert failures into fake semantic output."""

    def __init__(
        self,
        inner: VisualUnderstandingPort,
        *,
        policy: VisualRetryPolicy | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self._inner = inner
        self._policy = policy or VisualRetryPolicy()
        self._sleeper = sleeper

    def analyze(self, request: VisualUnderstandingRequest) -> VisualSemanticsProposal:
        for attempt in range(1, self._policy.max_attempts + 1):
            try:
                return self._inner.analyze(request)
            except VisualProviderTransientError as exc:
                if attempt >= self._policy.max_attempts:
                    raise
                policy_delay = float(self._policy.base_delay_seconds) * attempt
                provider_delay = exc.retry_after_seconds or 0.0
                self._sleeper(max(policy_delay, provider_delay))
        raise AssertionError("unreachable retry loop")
