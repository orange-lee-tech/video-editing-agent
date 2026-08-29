from datetime import UTC, datetime
from pathlib import Path

from video_editing_agent.adapters.product.presentation import (
    _format_time,
    _framing_label,
    _motion_label,
    _role_label,
    editing_presentation,
    token_usage_presentation,
)
from video_editing_agent.application.use_cases.product_flow import (
    EditingProductResult,
    ProductFlowOutcome,
)
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.review.model import (
    ReviewCorrectionRoute,
    ReviewDisposition,
    ReviewReport,
    ReviewStage,
    ReviewVerdict,
)
from video_editing_agent.providers.usage import TokenUsage, TokenUsageSnapshot


def test_chinese_planning_helpers_hide_machine_facing_labels() -> None:
    assert _format_time(MediaTime(3, 1), zh=True) == "3 秒"
    assert _format_time(MediaTime(3, 2), zh=True) == "1.5 秒"
    assert _role_label("hook", zh=True, ordinal=1) == "开场"
    assert _role_label("body", zh=True, ordinal=2) == "主体"
    assert _role_label("closing", zh=True, ordinal=3) == "收尾"
    assert _framing_label("close", zh=True) == "近景"
    assert _framing_label("medium", zh=True) == "中景"
    assert _motion_label("static", zh=True) == "固定"
    assert _motion_label("handheld", zh=True) == "手持"


def test_english_presentation_helpers_preserve_english_values() -> None:
    assert _format_time(MediaTime(3, 1), zh=False) == "3 s"
    assert _role_label("hook", zh=False, ordinal=1) == "hook"
    assert _framing_label("close", zh=False) == "close"
    assert _motion_label("static", zh=False) == "static"


def test_token_usage_presentation_is_localized_for_product_log() -> None:
    snapshot = TokenUsageSnapshot(
        TokenUsage(
            "deepseek",
            "deepseek-v4-flash",
            120,
            30,
            150,
            reasoning_tokens=12,
            cached_input_tokens=40,
        ),
        provider_session_tokens=300,
        process_session_tokens=500,
    )
    chinese = token_usage_presentation(snapshot, "zh-CN")
    assert "[AI 用量]" in chinese
    assert "输入=120" in chinese
    assert "缓存输入=40" in chinese
    assert "本次程序累计=500" in chinese

    english = token_usage_presentation(snapshot, "en")
    assert "[AI usage]" in english
    assert "input=120" in english
    assert "cached_in=40" in english
    assert "process_session=500" in english


def test_review_correction_presentation_exposes_candidate_without_calling_it_final() -> None:
    edl_ref = EntityRevisionRef("edl_present", 1)
    report = ReviewReport(
        EntityEnvelope(
            "review_present",
            1,
            "test",
            EntityStatus.VALID,
            datetime.now(UTC),
            "test",
        ),
        ReviewStage.FINAL_TECHNICAL_QC,
        edl_ref,
        False,
        (),
    )
    verdict = ReviewVerdict(
        ReviewDisposition.CORRECTION_REQUIRED,
        report,
        ReviewCorrectionRoute.RETURN_TO_AUDIO_EDITORIAL,
        0,
    )
    candidate = Path("candidate.mp4")
    result = EditingProductResult(
        ProductFlowOutcome.CORRECTION_REQUIRED,
        Path("."),
        None,
        None,
        edl_ref,
        candidate,
        verdict,
        (),
        verdict.correction_route.value,
    )

    chinese = editing_presentation(result, "zh-CN")
    assert "候选视频（未通过最终检查）" in chinese
    assert "音频质量检查未通过" in chinese
    assert "已完成\n最终视频" not in chinese
