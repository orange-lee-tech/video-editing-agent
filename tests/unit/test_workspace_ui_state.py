from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from video_editing_agent.adapters.product.workspace_ui import (
    BoundedFormHistory,
    OutputPathOwnership,
    WorkspaceFormStateStore,
    context_for_workspace,
    output_path_for_workspace,
    require_selected_workspace,
    restored_output_ownership,
)
from video_editing_agent.storage.project.layout import WorkspaceWritableLayout
from video_editing_agent.storage.project.workspace import ProjectWorkspace


def test_workspace_owns_explicit_writable_layout_and_collision_safe_output(tmp_path) -> None:
    workspace = ProjectWorkspace.open(tmp_path / "project")

    assert workspace.writable.root == workspace.root
    assert all(
        path.is_dir()
        for path in (
            workspace.writable.cache,
            workspace.writable.work,
            workspace.writable.logs,
            workspace.writable.drafts,
            workspace.writable.history,
            workspace.writable.preview_outputs,
            workspace.writable.final_outputs,
        )
    )
    first = workspace.writable.default_final_output("My video")
    assert first == workspace.root / "outputs" / "final" / "My-video.mp4"
    first.write_bytes(b"existing")
    assert workspace.writable.default_final_output("My video").name == "My-video-001.mp4"


def test_bounded_form_history_undo_redo_clear_state_and_persistence(tmp_path) -> None:
    history = BoundedFormHistory.create({"title": "one"}, limit=2)
    history.record({"title": "two"})
    history.record({"title": "three"})
    history.record({"title": "four"})

    assert len(history.undo_stack) == 2
    assert history.undo() == {"title": "three"}
    assert history.undo() == {"title": "two"}
    assert history.undo() is None
    assert history.redo() == {"title": "three"}
    history.record({"title": ""})
    assert history.redo() is None

    store = WorkspaceFormStateStore(WorkspaceWritableLayout.ensure(tmp_path), "planning")
    store.save(history)
    reopened = store.load(limit=2)
    assert reopened is not None
    assert reopened.current == {"title": ""}
    assert len(reopened.undo_stack) <= 2


def test_workspace_form_state_rejects_unknown_workflow(tmp_path) -> None:
    layout = WorkspaceWritableLayout.ensure(tmp_path)
    try:
        WorkspaceFormStateStore(layout, "unknown")
    except ValueError as error:
        assert "planning or editing" in str(error)
    else:
        raise AssertionError("unknown workflow must fail closed")


def test_no_workspace_guard_causes_zero_project_mutation(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="Project Workspace"):
        require_selected_workspace("   ")

    assert tuple(tmp_path.iterdir()) == ()


def test_workspace_drafts_and_history_remain_scoped_across_a_b_a(tmp_path: Path) -> None:
    workspace_a = ProjectWorkspace.open(tmp_path / "a")
    workspace_b = ProjectWorkspace.open(tmp_path / "b")
    store_a = WorkspaceFormStateStore(workspace_a.writable, "editing")
    store_b = WorkspaceFormStateStore(workspace_b.writable, "editing")
    store_a.save(BoundedFormHistory.create({"media_files": "a.mp4"}))
    store_b.save(BoundedFormHistory.create({"media_files": "b.mp4"}))

    reopened_a = store_a.load()
    reopened_b = store_b.load()
    assert reopened_a is not None and reopened_a.current == {"media_files": "a.mp4"}
    assert reopened_b is not None and reopened_b.current == {"media_files": "b.mp4"}
    reopened_a_again = store_a.load()
    assert reopened_a_again is not None
    assert reopened_a_again.current == {"media_files": "a.mp4"}


def test_output_default_ownership_rebases_but_explicit_save_as_survives(tmp_path: Path) -> None:
    workspace_a = ProjectWorkspace.open(tmp_path / "a")
    workspace_b = ProjectWorkspace.open(tmp_path / "b")
    auto_a = str(workspace_a.writable.default_final_output())

    assert (
        restored_output_ownership(None, auto_a, workspace_a.writable)
        is OutputPathOwnership.WORKSPACE_DEFAULT
    )
    assert (
        restored_output_ownership(
            OutputPathOwnership.WORKSPACE_DEFAULT.value, auto_a, workspace_b.writable
        )
        is OutputPathOwnership.WORKSPACE_DEFAULT
    )
    auto_b = output_path_for_workspace(
        auto_a, OutputPathOwnership.WORKSPACE_DEFAULT, workspace_b.writable
    )
    auto_a_again = output_path_for_workspace(
        str(auto_b), OutputPathOwnership.WORKSPACE_DEFAULT, workspace_a.writable
    )
    assert auto_b.parent == workspace_b.writable.final_outputs
    assert auto_a_again.parent == workspace_a.writable.final_outputs
    explicit = str(tmp_path / "chosen" / "result.mp4")
    assert (
        restored_output_ownership(
            OutputPathOwnership.EXPLICIT.value, explicit, workspace_b.writable
        )
        is OutputPathOwnership.EXPLICIT
    )
    assert (
        output_path_for_workspace(explicit, OutputPathOwnership.EXPLICIT, workspace_b.writable)
        == Path(explicit).resolve()
    )


def test_cleared_output_restores_workspace_default_ownership(tmp_path: Path) -> None:
    workspace = ProjectWorkspace.open(tmp_path / "project")

    assert (
        restored_output_ownership("", "", workspace.writable)
        is OutputPathOwnership.WORKSPACE_DEFAULT
    )
    assert (
        restored_output_ownership(None, "", workspace.writable)
        is OutputPathOwnership.WORKSPACE_DEFAULT
    )


@dataclass(frozen=True)
class _PlanningContext:
    project: Path


def test_planning_context_cannot_cross_workspace_boundary(tmp_path: Path) -> None:
    workspace_a = (tmp_path / "a").resolve()
    workspace_b = (tmp_path / "b").resolve()
    context = _PlanningContext(workspace_a)

    assert context_for_workspace(context, workspace_a) is context
    assert context_for_workspace(context, workspace_b) is None


def test_history_keeps_file_checkbox_and_planning_use_state_coherent() -> None:
    initial = {
        "media_files": "a.mp4;b.mp4",
        "music_rights_attested": "1",
        "use_planning": "1",
    }
    cleared = {key: "" for key in initial}
    history = BoundedFormHistory.create(initial)
    history.record(cleared)

    assert history.undo() == initial
    assert history.redo() == cleared
