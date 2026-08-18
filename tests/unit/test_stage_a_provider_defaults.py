from importlib.machinery import ModuleSpec
from pathlib import Path

from video_editing_agent.adapters.product.runtime import resolve_product_runtime


def test_stage_a_gemini_default_uses_current_stable_visual_model(tmp_path: Path) -> None:
    package = tmp_path / "transnetv2_pytorch"
    package.mkdir()
    module = package / "__init__.py"
    module.write_text("", encoding="utf-8")
    (package / "transnetv2-pytorch-weights.pth").write_bytes(b"weights")

    resolution = resolve_product_runtime(
        mode="planning",
        reference_required=True,
        environment={"DEEPSEEK_API_KEY": "thinking", "GEMINI_API_KEY": "visual"},
        executable_locator=lambda name: name,
        module_finder=lambda name: ModuleSpec(name, loader=None, origin=str(module)),
    )

    assert resolution.is_ready
    assert resolution.config is not None
    assert resolution.config.visual_provider == "gemini"
    assert resolution.config.visual_model == "gemini-3.6-flash"
