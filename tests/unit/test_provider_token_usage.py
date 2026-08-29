from video_editing_agent.providers.usage import (
    ConsoleTokenUsageMeter,
    TokenUsage,
    TokenUsageSnapshot,
    extract_token_usage,
    report_token_usage,
    set_thread_token_usage_sink,
)


def test_extracts_deepseek_reported_usage() -> None:
    usage = extract_token_usage(
        "deepseek",
        "deepseek-v4-flash",
        {
            "usage": {
                "prompt_tokens": 120,
                "completion_tokens": 30,
                "total_tokens": 150,
                "prompt_cache_hit_tokens": 40,
                "completion_tokens_details": {"reasoning_tokens": 12},
            }
        },
    )

    assert usage == TokenUsage(
        provider="deepseek",
        model="deepseek-v4-flash",
        input_tokens=120,
        output_tokens=30,
        total_tokens=150,
        reasoning_tokens=12,
        cached_input_tokens=40,
    )


def test_extracts_gemini_reported_usage() -> None:
    usage = extract_token_usage(
        "gemini",
        "gemini-3.6-flash",
        {
            "usageMetadata": {
                "promptTokenCount": 200,
                "candidatesTokenCount": 50,
                "thoughtsTokenCount": 10,
                "cachedContentTokenCount": 20,
                "totalTokenCount": 260,
            }
        },
    )

    assert usage is not None
    assert usage.input_tokens == 200
    assert usage.output_tokens == 50
    assert usage.reasoning_tokens == 10
    assert usage.cached_input_tokens == 20
    assert usage.total_tokens == 260
    assert usage.source == "reported"


def test_extracts_openai_reported_usage() -> None:
    usage = extract_token_usage(
        "openai",
        "gpt-5-mini",
        {
            "usage": {
                "input_tokens": 300,
                "input_tokens_details": {"cached_tokens": 100},
                "output_tokens": 80,
                "output_tokens_details": {"reasoning_tokens": 24},
                "total_tokens": 380,
            }
        },
    )

    assert usage is not None
    assert usage.input_tokens == 300
    assert usage.output_tokens == 80
    assert usage.reasoning_tokens == 24
    assert usage.cached_input_tokens == 100
    assert usage.total_tokens == 380


def test_missing_usage_uses_clearly_labeled_text_estimate() -> None:
    usage = extract_token_usage(
        "deepseek",
        "example-model",
        {"choices": [{"message": {"content": "short answer"}}]},
        request_payload={"messages": [{"content": "hello world"}]},
    )

    assert usage is not None
    assert usage.source == "estimated-text-only"
    assert usage.input_tokens > 0
    assert usage.output_tokens > 0
    assert usage.total_tokens == usage.input_tokens + usage.output_tokens


def test_console_meter_reports_call_and_cumulative_totals(capsys) -> None:
    meter = ConsoleTokenUsageMeter()
    first = meter.record(TokenUsage("deepseek", "model-a", 10, 5, 15))
    second = meter.record(TokenUsage("openai", "model-b", 20, 10, 30))

    assert first.provider_session_tokens == 15
    assert first.process_session_tokens == 15
    assert second.provider_session_tokens == 30
    assert second.process_session_tokens == 45
    output = capsys.readouterr().out
    assert "[AI usage] deepseek/model-a" in output
    assert "provider_session=15 process_session=15" in output
    assert "[AI usage] openai/model-b" in output
    assert "provider_session=30 process_session=45" in output


def test_report_token_usage_can_emit_to_task_local_sink() -> None:
    observed: list[TokenUsageSnapshot] = []
    previous = set_thread_token_usage_sink(observed.append)
    try:
        report_token_usage(
            "deepseek",
            "deepseek-v4-flash",
            {
                "usage": {
                    "prompt_tokens": 12,
                    "completion_tokens": 3,
                    "total_tokens": 15,
                }
            },
        )
    finally:
        set_thread_token_usage_sink(previous)

    assert len(observed) == 1
    assert observed[0].usage.provider == "deepseek"
    assert observed[0].usage.total_tokens == 15
    assert observed[0].provider_session_tokens >= 15
    assert observed[0].process_session_tokens >= 15
