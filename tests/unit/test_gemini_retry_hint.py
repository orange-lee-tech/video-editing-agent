import io
import json
import urllib.error

import pytest

from video_editing_agent.application.ports.visual_understanding import (
    VisualProviderQuotaError,
    VisualProviderTransientError,
)
from video_editing_agent.providers.vision.gemini_generate_content import (
    UrllibGeminiGenerateContentTransport,
)


def test_gemini_429_propagates_structured_retry_info(monkeypatch: pytest.MonkeyPatch) -> None:
    body = json.dumps(
        {
            "error": {
                "code": 429,
                "message": "Quota exceeded. Please retry in 10.577272831s.",
                "status": "RESOURCE_EXHAUSTED",
                "details": [
                    {
                        "@type": "type.googleapis.com/google.rpc.RetryInfo",
                        "retryDelay": "10.577272831s",
                    }
                ],
            }
        }
    ).encode()

    def raise_429(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise urllib.error.HTTPError(
            "https://example.invalid",
            429,
            "rate limit",
            None,
            io.BytesIO(body),
        )

    monkeypatch.setattr("urllib.request.urlopen", raise_429)
    transport = UrllibGeminiGenerateContentTransport(
        api_key="secret",
        api_root="https://example.invalid",
    )

    with pytest.raises(VisualProviderTransientError, match="retryable HTTP 429") as captured:
        transport.generate_content("gemini-3.6-flash", {"contents": []})

    assert captured.value.retry_after_seconds == pytest.approx(10.577272831)


def test_gemini_429_uses_message_retry_hint_when_retry_info_is_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = json.dumps(
        {
            "error": {
                "code": 429,
                "message": "Quota exceeded. Please retry in 4.25s.",
                "status": "RESOURCE_EXHAUSTED",
            }
        }
    ).encode()

    def raise_429(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise urllib.error.HTTPError(
            "https://example.invalid",
            429,
            "rate limit",
            None,
            io.BytesIO(body),
        )

    monkeypatch.setattr("urllib.request.urlopen", raise_429)
    transport = UrllibGeminiGenerateContentTransport(
        api_key="secret",
        api_root="https://example.invalid",
    )

    with pytest.raises(VisualProviderTransientError) as captured:
        transport.generate_content("gemini-3.6-flash", {"contents": []})

    assert captured.value.retry_after_seconds == pytest.approx(4.25)


def test_gemini_daily_quota_is_classified_as_hard_quota(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = json.dumps(
        {
            "error": {
                "code": 429,
                "message": (
                    "You exceeded your current quota. "
                    "Quota exceeded for metric: "
                    "generativelanguage.googleapis.com/generate_content_free_tier_requests, "
                    "limit: 20, model: gemini-3.6-flash. Please retry in 59s."
                ),
                "status": "RESOURCE_EXHAUSTED",
                "details": [
                    {
                        "@type": "type.googleapis.com/google.rpc.QuotaFailure",
                        "violations": [
                            {
                                "quotaMetric": (
                                    "generativelanguage.googleapis.com/"
                                    "generate_content_free_tier_requests"
                                ),
                                "quotaId": (
                                    "GenerateRequestsPerDayPerProjectPerModel-FreeTier"
                                ),
                                "quotaValue": "20",
                            }
                        ],
                    },
                    {
                        "@type": "type.googleapis.com/google.rpc.RetryInfo",
                        "retryDelay": "59s",
                    },
                ],
            }
        }
    ).encode()

    def raise_429(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise urllib.error.HTTPError(
            "https://example.invalid",
            429,
            "quota",
            None,
            io.BytesIO(body),
        )

    monkeypatch.setattr("urllib.request.urlopen", raise_429)
    transport = UrllibGeminiGenerateContentTransport(
        api_key="secret",
        api_root="https://example.invalid",
    )

    with pytest.raises(VisualProviderQuotaError, match="daily request quota") as captured:
        transport.generate_content("gemini-3.6-flash", {"contents": []})

    assert captured.value.quota_ids == (
        "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
    )
    assert captured.value.retry_after_seconds == pytest.approx(59.0)
