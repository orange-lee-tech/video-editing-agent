from __future__ import annotations

from typing import Any

import pytest

from video_editing_agent.adapters.cli.provider_config import (
    ProviderConfigurationError,
    deepseek_preproduction_ports,
)
from video_editing_agent.storage.project import ProjectWorkspace


class RecordingTransport:
    def __init__(self) -> None:
        self.payloads: list[dict[str, Any]] = []

    def create_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.payloads.append(payload)
        return {"choices": [{"message": {"content": '{"sections": []}'}}]}


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


def test_deepseek_composition_accepts_injected_transport_without_key(monkeypatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    transport = RecordingTransport()

    ports = deepseek_preproduction_ports(model="deepseek-v4-flash", transport=transport)

    assert ports.script_planning is not None
    assert ports.script_review is not None
