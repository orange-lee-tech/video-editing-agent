from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest

from video_editing_agent.adapters.product.ux_support import (
    EtaEstimator,
    ProtectedCredentialStore,
    default_profile_root,
    extract_first_https_url,
    format_eta,
    load_api_profile,
    localized_error,
    localized_stage,
    parse_profile,
    save_api_profile,
    serialize_profile,
    write_utf8_export,
)
from video_editing_agent.application.use_cases.product_flow import ProductFlowStage


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("https://cdn.example.test/reference.mp4", "https://cdn.example.test/reference.mp4"),
        (
            "复制打开抖音，参考链接 https://v.example.test/share/abc?x=1 其余文字",
            "https://v.example.test/share/abc?x=1",
        ),
        ("only prose without a link", None),
        (
            "first https://one.example/a.mp4 second https://two.example/b.mp4",
            "https://one.example/a.mp4",
        ),
    ],
)
def test_share_text_extracts_first_bounded_https_url(source: str, expected: str | None) -> None:
    assert extract_first_https_url(source) == expected


def test_form_profile_is_deterministic_human_readable_and_rejects_secrets() -> None:
    first = serialize_profile("form", {"title": "水瓶", "project": "D:/project", "empty": ""})
    second = serialize_profile("form", {"empty": "", "project": "D:/project", "title": "水瓶"})

    assert first == second
    assert parse_profile(first, "form") == {"project": "D:/project", "title": "水瓶"}
    with pytest.raises(ValueError, match="plaintext secret"):
        serialize_profile("api", {"api_key": "must-not-appear"})


def test_non_windows_credential_store_fails_closed_without_plaintext(tmp_path: Path) -> None:
    store = ProtectedCredentialStore(tmp_path, platform="linux")

    with pytest.raises(RuntimeError, match="unavailable"):
        store.save("secret")
    assert tuple(tmp_path.rglob("*")) == ()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows DPAPI contract")
def test_windows_api_profile_contains_only_opaque_refs_and_round_trips(tmp_path: Path) -> None:
    store = ProtectedCredentialStore(tmp_path)
    profile = tmp_path / "API.txt"

    save_api_profile(
        profile,
        visual_provider="gemini",
        thinking_key="thinking-secret",
        visual_key="visual-secret",
        credentials=store,
    )

    content = profile.read_text(encoding="utf-8")
    assert "thinking-secret" not in content and "visual-secret" not in content
    assert load_api_profile(profile, store) == (
        "gemini",
        "thinking-secret",
        "visual-secret",
    )


def test_profile_root_and_utf8_export_are_ordinary_user_paths(tmp_path: Path) -> None:
    assert default_profile_root(tmp_path) == (
        tmp_path / "Documents" / "Video Editing Agent" / "Profiles"
    )
    output = tmp_path / "visible.txt"
    write_utf8_export(output, "精确可见输出\nSecond line")
    assert output.read_bytes() == "精确可见输出\nSecond line".encode()


def test_eta_is_estimating_without_evidence_and_uses_observed_stage_history() -> None:
    started = datetime(2026, 8, 18, 20, 51)
    empty = EtaEstimator({}, started)
    observed = EtaEstimator({"rendering": 420.0}, started)

    assert empty.estimate(ProductFlowStage.RENDERING) is None
    assert format_eta(None, "zh-CN") == "正在估算…"
    estimate = observed.estimate(ProductFlowStage.RENDERING)
    assert estimate == datetime(2026, 8, 18, 20, 58)
    assert format_eta(estimate, "zh-CN", now=started) == "预计 20:58 完成（约 7 分钟）"


def test_stable_stage_and_quota_error_present_localized_primary_text() -> None:
    assert localized_stage(ProductFlowStage.RENDERING, "zh-CN") == "正在渲染视频"
    primary, detail = localized_error(
        RuntimeError("Gemini HTTP 429 quota exceeded; model=gemini-2.5-flash"), "zh-CN"
    )
    assert "配额限制" in primary
    assert "Gemini HTTP 429" in detail
    assert "API key" not in primary
