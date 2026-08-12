from __future__ import annotations

import pytest

from video_editing_agent.adapters.cli.provider_config import (
    ProviderConfigurationError,
    deepseek_preproduction_ports,
)
from video_editing_agent.storage.project import ProjectWorkspace


def test_missing_deepseek_key_fails_before_workspace_mutation(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    workspace = ProjectWorkspace.open(tmp_path / "project")
    before = workspace.status()["counts"]

    with pytest.raises(ProviderConfigurationError, match="DEEPSEEK_API_KEY"):
        deepseek_preproduction_ports()

    assert ProjectWorkspace.open(tmp_path / "project").status()["counts"] == before


def test_deepseek_composition_does_not_persist_or_print_secret(tmp_path, monkeypatch) -> None:
    secret = "test-secret-never-sent"
    monkeypatch.setenv("DEEPSEEK_API_KEY", secret)
    workspace = ProjectWorkspace.open(tmp_path / "project")

    ports = deepseek_preproduction_ports()

    assert ports.script_planning is not None
    assert secret not in str(workspace.status())
    assert secret.encode() not in workspace.database.path.read_bytes()
