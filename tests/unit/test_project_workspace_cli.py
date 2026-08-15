from __future__ import annotations

import json

from video_editing_agent.adapters.cli.main import main
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.planning.brief.service import BriefContent
from video_editing_agent.storage.project import ProjectWorkspace


def test_workspace_open_reopen_and_read_are_deterministic(tmp_path) -> None:
    root = tmp_path / "project"
    first = ProjectWorkspace.open(root)
    brief = first.brief_service.create(
        BriefContent("Title", "Objective", "Audience", "vertical", "Message")
    )
    before = first.database.path.stat().st_size

    reopened = ProjectWorkspace.open(root)
    loaded = reopened.briefs.load(EntityRevisionRef(brief.envelope.id, 1))

    assert loaded == brief
    assert reopened.status() == first.status()
    assert reopened.database.path.stat().st_size == before
    assert (root / "artifacts").is_dir()
    assert reopened.status()["counts"] == {
        "assets": 0,
        "shots": 0,
        "shot_analyses": 0,
        "briefs": 1,
        "script_plans": 0,
        "shooting_plans": 0,
        "edit_plans": 0,
    }
    assert reopened.status()["capabilities"]["external_provider_configured"] is False


def test_cli_init_create_show_and_failure_without_mutation(tmp_path, capsys) -> None:
    root = tmp_path / "cli-project"
    assert main(["--project", str(root), "project", "init"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["schema_version"] == 6

    args = [
        "--project",
        str(root),
        "brief",
        "create",
        "--title",
        "Ad",
        "--objective",
        "Explain",
        "--audience",
        "commuters",
        "--platform",
        "vertical",
        "--core-message",
        "500 mL bottle",
    ]
    assert main(args) == 0
    created = json.loads(capsys.readouterr().out)
    entity_id = created["envelope"]["id"]
    assert main(["--project", str(root), "brief", "show", entity_id, "1"]) == 0
    assert json.loads(capsys.readouterr().out) == created

    assert main(["--project", str(root), "brief", "show", "brf_missing", "1"]) == 2
    assert "error:" in capsys.readouterr().err
    reopened = ProjectWorkspace.open(root)
    assert reopened.briefs.load(EntityRevisionRef(entity_id, 1)).title == "Ad"


def test_cli_bad_asset_json_has_no_mutation(tmp_path, capsys) -> None:
    root = tmp_path / "cli-project"
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")

    assert main(["--project", str(root), "asset", "ingest", "--json", str(bad)]) == 2
    assert "error:" in capsys.readouterr().err
    assert ProjectWorkspace.open(root).status()["counts"]["assets"] == 0
