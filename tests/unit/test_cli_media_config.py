from pathlib import Path

import pytest

from video_editing_agent.adapters.cli.main import main
from video_editing_agent.adapters.cli.media_config import (
    transnetv2_detector,
    visual_understanding_port,
)
from video_editing_agent.providers.vision.retry import RetryingVisualUnderstandingPort
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore
from video_editing_agent.storage.project import ProjectWorkspace


def test_transnet_composition_requires_existing_model_before_detection(tmp_path: Path) -> None:
    workspace = ProjectWorkspace.open(tmp_path / "project")

    with pytest.raises(FileNotFoundError):
        transnetv2_detector(
            workspace.assets,
            model_path=tmp_path / "missing.pth",
            device="cpu",
            ffmpeg_executable="ffmpeg",
        )

    assert workspace.status()["counts"]["shots"] == 0


def test_visual_provider_composition_retries_transient_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "configured")

    port = visual_understanding_port(
        "gemini",
        model="gemini-3.6-flash",
        artifacts=LocalArtifactStore(tmp_path / "artifacts"),
    )

    assert isinstance(port, RetryingVisualUnderstandingPort)


@pytest.mark.parametrize(
    ("provider", "variable"), (("gemini", "GEMINI_API_KEY"), ("openai", "OPENAI_API_KEY"))
)
def test_analysis_missing_key_is_concise_and_has_no_mutation(
    tmp_path: Path, capsys, monkeypatch, provider: str, variable: str
) -> None:
    monkeypatch.delenv(variable, raising=False)
    root = tmp_path / "project"

    code = main(
        [
            "--project",
            str(root),
            "analysis",
            "run",
            "sht_missing",
            "1",
            "--provider",
            provider,
            "--model",
            "test-model",
        ]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert captured.out == ""
    assert captured.err.startswith("error: ")
    assert variable in captured.err
    assert ProjectWorkspace.open(root).status()["counts"]["shot_analyses"] == 0


def test_visual_configuration_error_never_contains_secret(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    secret = "secret-must-not-leak"
    monkeypatch.setenv("GEMINI_API_KEY", secret)
    root = tmp_path / "project"

    code = main(
        [
            "--project",
            str(root),
            "analysis",
            "run",
            "sht_missing",
            "1",
            "--provider",
            "gemini",
            "--model",
            "models/invalid",
        ]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert secret not in captured.out + captured.err
    assert secret.encode() not in ProjectWorkspace.open(root).database.path.read_bytes()
