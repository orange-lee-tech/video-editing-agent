from __future__ import annotations

from video_editing_agent.adapters.product.workspace_ui import (
    BoundedFormHistory,
    WorkspaceFormStateStore,
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
