from importlib.machinery import ModuleSpec
from pathlib import Path

import pytest

from video_editing_agent.adapters.product.controller import (
    BriefForm,
    EditingForm,
    PlanningForm,
    expand_media_inputs,
)
from video_editing_agent.adapters.product.runtime import resolve_product_runtime
from video_editing_agent.application.use_cases.product_flow import PlanningReferenceKind


def _brief() -> BriefForm:
    return BriefForm(
        "Title",
        "Objective",
        "Audience",
        "Platform",
        "Message",
        ("Volume is 500 mL", "Lid screws on"),
    )


def test_controller_builds_planning_request_without_json_or_internal_refs(tmp_path: Path) -> None:
    reference = tmp_path / "reference.mp4"
    reference.write_bytes(b"original")
    request = PlanningForm(
        tmp_path / "project",
        _brief(),
        reference_url="https://example.test/direct.mp4",
        local_reference=reference,
    ).to_request()

    assert tuple(item.statement for item in request.brief.authoritative_facts) == (
        "Volume is 500 mL",
        "Lid screws on",
    )
    assert tuple(item.kind for item in request.reference_inputs) == (
        PlanningReferenceKind.DIRECT_HTTPS_VIDEO,
        PlanningReferenceKind.LOCAL_VIDEO,
    )
    assert all(not hasattr(item, "asset_ref") for item in request.reference_inputs)


def test_folder_expansion_is_stable_and_does_not_touch_originals(tmp_path: Path) -> None:
    folder = tmp_path / "media"
    folder.mkdir()
    second, first = folder / "B.MOV", folder / "a.mp4"
    second.write_bytes(b"second")
    first.write_bytes(b"first")
    (folder / "ignore.txt").write_text("ignore", encoding="utf-8")

    expanded = expand_media_inputs((second,), folder)
    request = EditingForm(
        tmp_path / "project", _brief(), tmp_path / "final.mp4", (second,), folder
    ).to_request()

    assert expanded == request.local_media_paths == (first.resolve(), second.resolve())
    assert first.read_bytes() == b"first" and second.read_bytes() == b"second"


def test_planning_without_reference_does_not_require_media_runtime() -> None:
    result = resolve_product_runtime(
        mode="planning",
        environment={"DEEPSEEK_API_KEY": "configured"},
        executable_locator=lambda name: None,
        module_finder=lambda name: None,
    )

    assert result.is_ready
    assert result.config is not None and result.config.transnet_weights is None


def test_missing_editing_runtime_is_an_understandable_diagnostic() -> None:
    result = resolve_product_runtime(
        mode="editing",
        environment={},
        executable_locator=lambda name: None,
        module_finder=lambda name: None,
    )

    assert not result.is_ready
    assert any("FFmpeg/ffprobe" in item for item in result.diagnostics)
    assert any("TransNetV2" in item for item in result.diagnostics)
    assert all("weights_path" not in item for item in result.diagnostics)


def test_reference_runtime_auto_resolves_package_weights(tmp_path: Path) -> None:
    package = tmp_path / "transnetv2_pytorch"
    package.mkdir()
    module = package / "__init__.py"
    module.write_text("", encoding="utf-8")
    (package / "transnetv2-pytorch-weights.pth").write_bytes(b"weights")
    result = resolve_product_runtime(
        mode="planning",
        reference_required=True,
        environment={"DEEPSEEK_API_KEY": "x", "GEMINI_API_KEY": "y"},
        executable_locator=lambda name: name,
        module_finder=lambda name: ModuleSpec(name, loader=None, origin=str(module)),
    )

    assert result.is_ready and result.config is not None
    assert result.config.transnet_weights.name == "transnetv2-pytorch-weights.pth"


def test_invalid_runtime_mode_fails_closed() -> None:
    with pytest.raises(ValueError, match="planning or editing"):
        resolve_product_runtime(mode="unknown")
