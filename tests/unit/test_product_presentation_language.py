from video_editing_agent.adapters.product.presentation import (
    _format_time,
    _framing_label,
    _motion_label,
    _role_label,
)
from video_editing_agent.domain.common.media_time import MediaTime


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
