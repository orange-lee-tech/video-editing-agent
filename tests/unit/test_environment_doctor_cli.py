from __future__ import annotations

import json

from video_editing_agent.adapters.cli import entrypoint
from video_editing_agent.application.ports.environment_doctor import (
    CapabilityStatus,
    EnvironmentCapabilityCheck,
    ProductCapability,
)
from video_editing_agent.application.use_cases.environment_doctor import EnvironmentDoctor


class FakeProbe:
    def __init__(self, check: EnvironmentCapabilityCheck) -> None:
        self._check = check

    def probe(self) -> tuple[EnvironmentCapabilityCheck, ...]:
        return (self._check,)


def test_doctor_cli_is_project_independent_and_structured(tmp_path, capsys, monkeypatch) -> None:
    project = tmp_path / "must-not-be-created"
    check = EnvironmentCapabilityCheck(
        ProductCapability.MEDIA_PROBE_RENDER,
        "ffmpeg_toolchain",
        CapabilityStatus.READY,
        "toolchain ready",
        ("ffmpeg_probe=ready", "ffprobe_probe=ready"),
    )
    doctor = EnvironmentDoctor((FakeProbe(check),))
    monkeypatch.setattr(entrypoint, "_build_environment_doctor", lambda preview_runtime: doctor)

    assert entrypoint.main(["doctor"]) == 0
    output = json.loads(capsys.readouterr().out)

    assert output["schema_version"] == 1
    assert output["checks"][0]["capability"] == "media_probe_render"
    assert output["checks"][0]["status"] == "ready"
    assert "rerun video-editing-agent doctor" in output["repair_report"]
    assert not project.exists()


def test_entrypoint_delegates_existing_project_cli_unchanged(tmp_path, capsys) -> None:
    project = tmp_path / "project"

    assert entrypoint.main(["--project", str(project), "project", "init"]) == 0
    output = json.loads(capsys.readouterr().out)

    assert output["schema_version"] == 6
    assert (project / "project.sqlite3").is_file()
