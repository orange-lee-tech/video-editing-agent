from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from video_editing_agent.adapters.product import component_update
from video_editing_agent.adapters.product.component_update import plan_component_update
from video_editing_agent.adapters.product.update_check import UpdateComponent, UpdateManifest
from video_editing_agent.adapters.product.update_state import (
    InstalledComponentState,
    InstalledUpdateState,
    UpdateFileRecord,
)


def test_released_protocol_1_client_falls_back_for_protocol_2_release(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    installed = InstalledUpdateState(
        application_version="1.0.0",
        updater_version=1,
        components=(
            InstalledComponentState(
                "app-core",
                "1.0.0",
                (
                    UpdateFileRecord(
                        PurePosixPath("VideoEditingAgent.exe"),
                        "a" * 64,
                        1,
                    ),
                ),
            ),
        ),
    )
    manifest = UpdateManifest(
        version="1.0.1",
        published_at="2026-09-15T00:00:00Z",
        release_notes_url="https://example.invalid/notes",
        download_url="https://example.invalid/setup.exe",
        installer_sha256="b" * 64,
        mandatory=False,
        layout_version=1,
        minimum_updater_version=2,
        components=(
            UpdateComponent(
                "app-core",
                "1.0.1",
                "https://example.invalid/app-core.zip",
                "c" * 64,
                100,
            ),
        ),
    )

    monkeypatch.setattr(component_update, "UPDATER_PROTOCOL_VERSION", 1)
    plan = plan_component_update(installed, manifest)

    assert plan.patch_available is False
    assert plan.full_installer_required is True
    assert plan.reason == "release requires a newer updater"
