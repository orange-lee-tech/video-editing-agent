from video_editing_agent.application.ports.artifact_store import StoredArtifactRef
from video_editing_agent.application.ports.visual_understanding import (
    VisualFrameReference,
    VisualProviderResponseError,
    VisualProviderTransientError,
    VisualSemanticsProposal,
    VisualUnderstandingRequest,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.analysis import AnalysisProfile
from video_editing_agent.providers.vision.retry import (
    RetryingVisualUnderstandingPort,
    VisualRetryPolicy,
)


def request() -> VisualUnderstandingRequest:
    digest = "1" * 64
    return VisualUnderstandingRequest(
        shot_ref=EntityRevisionRef("sht_retry", 1),
        profile=AnalysisProfile.SEMANTIC,
        frames=(
            VisualFrameReference(
                artifact_ref=StoredArtifactRef(
                    artifact_id=f"art_sha256_{digest}",
                    content_hash=f"sha256:{digest}",
                    media_type="image/png",
                    byte_size=10,
                ),
                ordinal=0,
                source_timestamp_ms=500,
            ),
        ),
    )


class FlakyProvider:
    def __init__(self, failures: int, *, retry_after_seconds: float | None = None) -> None:
        self.failures = failures
        self.retry_after_seconds = retry_after_seconds
        self.calls = 0

    def analyze(self, request: VisualUnderstandingRequest) -> VisualSemanticsProposal:
        del request
        self.calls += 1
        if self.calls <= self.failures:
            raise VisualProviderTransientError(
                "temporary",
                retry_after_seconds=self.retry_after_seconds,
            )
        return VisualSemanticsProposal(summary="ok")


class InvalidResponseProvider:
    def __init__(self) -> None:
        self.calls = 0

    def analyze(self, request: VisualUnderstandingRequest) -> VisualSemanticsProposal:
        del request
        self.calls += 1
        raise VisualProviderResponseError("invalid schema")


def test_transient_failures_retry_with_linear_backoff() -> None:
    provider = FlakyProvider(failures=2)
    delays: list[float] = []
    wrapped = RetryingVisualUnderstandingPort(
        provider,
        policy=VisualRetryPolicy(max_attempts=3, base_delay_seconds=0.3),
        sleeper=delays.append,
    )

    assert wrapped.analyze(request()).summary == "ok"
    assert provider.calls == 3
    assert delays == [0.3, 0.6]


def test_provider_retry_hint_overrides_shorter_local_backoff() -> None:
    provider = FlakyProvider(failures=1, retry_after_seconds=10.577)
    delays: list[float] = []
    wrapped = RetryingVisualUnderstandingPort(
        provider,
        policy=VisualRetryPolicy(max_attempts=3, base_delay_seconds=0.3),
        sleeper=delays.append,
    )

    assert wrapped.analyze(request()).summary == "ok"
    assert provider.calls == 2
    assert delays == [10.577]


def test_response_failure_is_not_retried() -> None:
    provider = InvalidResponseProvider()
    wrapped = RetryingVisualUnderstandingPort(provider, sleeper=lambda _: None)

    try:
        wrapped.analyze(request())
    except VisualProviderResponseError:
        pass
    else:
        raise AssertionError("expected VisualProviderResponseError")

    assert provider.calls == 1
