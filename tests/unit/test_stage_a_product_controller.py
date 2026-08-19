from importlib.machinery import ModuleSpec
from pathlib import Path

import pytest

from video_editing_agent.adapters.product.api_settings import (
    ApiCapabilitySettings,
    apply_settings_to_environment,
    settings_from_environment,
)
from video_editing_agent.adapters.product.controller import (
    BriefForm,
    EditingForm,
    PlanningForm,
    PlanningSessionContext,
    expand_media_inputs,
)
from video_editing_agent.adapters.product.runtime import resolve_product_runtime
from video_editing_agent.application.use_cases.product_flow import (
    OUTPUT_PROFILE_HORIZONTAL_1080P,
    EditingOutputProfile,
    PlanningProductResult,
    PlanningReferenceKind,
    ProductFlowOutcome,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef


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


def test_controller_extracts_first_https_url_from_share_text(tmp_path: Path) -> None:
    request = PlanningForm(
        tmp_path / "project",
        _brief(),
        reference_url=(
            "复制分享 https://cdn.example.test/first.mp4，另一个 "
            "https://cdn.example.test/second.mp4"
        ),
    ).to_request()

    assert request.reference_inputs[0].url == "https://cdn.example.test/first.mp4"


def test_controller_rejects_reference_share_text_without_https_url(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="HTTPS URL"):
        PlanningForm(
            tmp_path / "project", _brief(), reference_url="只有分享文案，没有链接"
        ).to_request()


def test_folder_expansion_is_stable_and_does_not_touch_originals(tmp_path: Path) -> None:
    folder = tmp_path / "media"
    folder.mkdir()
    second, first = folder / "B.MOV", folder / "a.mp4"
    second.write_bytes(b"second")
    first.write_bytes(b"first")
    (folder / "ignore.txt").write_text("ignore", encoding="utf-8")

    expanded = expand_media_inputs((second,), folder)
    request = EditingForm(
        tmp_path / "project",
        _brief(),
        tmp_path / "final.mp4",
        (second,),
        folder,
        output_profile=OUTPUT_PROFILE_HORIZONTAL_1080P,
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


def _planning_context(project: Path) -> PlanningSessionContext:
    result = PlanningProductResult(
        ProductFlowOutcome.COMPLETED,
        project,
        EntityRevisionRef("brief", 1),
        EntityRevisionRef("script", 2),
        EntityRevisionRef("shooting", 3),
        (),
    )
    context = PlanningSessionContext.from_result(result)
    assert context is not None
    return context


def test_same_project_combined_opt_in_forwards_exact_session_refs(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    context = _planning_context(tmp_path / "project")

    request = EditingForm(
        tmp_path / "project",
        _brief(),
        tmp_path / "final.mp4",
        (source,),
        use_planning_result=True,
        planning_context=context,
        output_profile=OUTPUT_PROFILE_HORIZONTAL_1080P,
    ).to_request()

    assert request.script_plan_ref == EntityRevisionRef("script", 2)
    assert request.shooting_plan_ref == EntityRevisionRef("shooting", 3)


def test_editing_form_forwards_explicit_output_profile(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    profile = EditingOutputProfile("vertical_test", 1080, 1920, 30)

    request = EditingForm(
        tmp_path / "project",
        _brief(),
        tmp_path / "final.mp4",
        (source,),
        output_profile=profile,
    ).to_request()

    assert request.output_profile == profile


def test_editing_only_has_no_planning_refs_or_internal_id_inputs(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    form = EditingForm(
        tmp_path / "project",
        _brief(),
        tmp_path / "final.mp4",
        (source,),
        output_profile=OUTPUT_PROFILE_HORIZONTAL_1080P,
    )

    request = form.to_request()

    assert request.script_plan_ref is None and request.shooting_plan_ref is None
    assert not hasattr(form, "script_plan_ref") and not hasattr(form, "shooting_plan_ref")


def test_different_project_planning_context_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    form = EditingForm(
        tmp_path / "editing-project",
        _brief(),
        tmp_path / "final.mp4",
        (source,),
        use_planning_result=True,
        planning_context=_planning_context(tmp_path / "planning-project"),
        output_profile=OUTPUT_PROFILE_HORIZONTAL_1080P,
    )

    with pytest.raises(ValueError, match="different project"):
        form.to_request()


@pytest.mark.parametrize(
    ("form", "message"),
    [
        (PlanningForm(Path(""), _brief()), "Planning project directory"),
        (
            EditingForm(
                Path(""),
                _brief(),
                Path("final.mp4"),
                (Path("source.mp4"),),
                output_profile=OUTPUT_PROFILE_HORIZONTAL_1080P,
            ),
            "Editing project directory",
        ),
        (
            EditingForm(
                Path("project"),
                _brief(),
                Path(""),
                (Path("source.mp4"),),
                output_profile=OUTPUT_PROFILE_HORIZONTAL_1080P,
            ),
            "output path",
        ),
        (
            EditingForm(
                Path("project"),
                _brief(),
                Path("final.mov"),
                (Path("source.mp4"),),
                output_profile=OUTPUT_PROFILE_HORIZONTAL_1080P,
            ),
            "MP4 destination",
        ),
    ],
)
def test_blank_or_non_mp4_paths_fail_before_composition(form, message: str) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(ValueError, match=message):
        form.to_request()


def test_planning_reference_diagnostics_name_the_correct_context() -> None:
    result = resolve_product_runtime(
        mode="planning",
        reference_required=True,
        environment={"DEEPSEEK_API_KEY": "configured"},
        executable_locator=lambda name: None,
        module_finder=lambda name: None,
    )

    assert not result.is_ready
    assert all("for Editing" not in item for item in result.diagnostics)
    assert any("Planning reference-video analysis" in item for item in result.diagnostics)


def test_api_capability_settings_allow_same_key_for_both_roles() -> None:
    environment: dict[str, str] = {}
    settings = ApiCapabilitySettings(
        thinking_key="same-key",
        visual_key="same-key",
        visual_provider="gemini",
    )

    apply_settings_to_environment(settings, environment)

    assert environment["DEEPSEEK_API_KEY"] == "same-key"
    assert environment["GEMINI_API_KEY"] == "same-key"
    assert "OPENAI_API_KEY" not in environment


def test_visual_provider_switch_clears_stale_provider_key() -> None:
    environment = {
        "DEEPSEEK_API_KEY": "thinking",
        "GEMINI_API_KEY": "old-visual",
    }

    apply_settings_to_environment(
        ApiCapabilitySettings("thinking", "new-visual", "openai"), environment
    )

    assert environment["DEEPSEEK_API_KEY"] == "thinking"
    assert environment["OPENAI_API_KEY"] == "new-visual"
    assert "GEMINI_API_KEY" not in environment


def test_api_capability_settings_import_existing_environment() -> None:
    settings = settings_from_environment(
        {"DEEPSEEK_API_KEY": "thinking", "OPENAI_API_KEY": "visual"}
    )

    assert settings == ApiCapabilitySettings("thinking", "visual", "openai")
