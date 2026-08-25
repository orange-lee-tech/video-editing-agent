from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol

from video_editing_agent.storage.project.layout import WorkspaceWritableLayout

_FORM_STATE_SCHEMA = "video-editing-agent-form-state-v1"


class ProjectBoundContext(Protocol):
    @property
    def project(self) -> Path: ...


class OutputPathOwnership(StrEnum):
    WORKSPACE_DEFAULT = "workspace_default"
    EXPLICIT = "explicit"


def require_selected_workspace(value: str) -> Path:
    """Reject an absent UI selection before any project-opening side effect."""
    if not value.strip():
        raise ValueError("A Project Workspace must be selected before running this workflow.")
    return Path(value).expanduser().resolve(strict=False)


def context_for_workspace[T: ProjectBoundContext](context: T | None, workspace: Path) -> T | None:
    if context is None:
        return None
    resolved = workspace.expanduser().resolve(strict=False)
    return context if context.project.expanduser().resolve(strict=False) == resolved else None


def restored_output_ownership(
    stored_value: str | None,
    output_path: str,
    layout: WorkspaceWritableLayout,
) -> OutputPathOwnership:
    if stored_value is not None:
        try:
            return OutputPathOwnership(stored_value)
        except ValueError:
            pass
    if output_path.strip():
        candidate = Path(output_path).expanduser().resolve(strict=False)
        if candidate.parent == layout.final_outputs:
            return OutputPathOwnership.WORKSPACE_DEFAULT
    return OutputPathOwnership.EXPLICIT


def output_path_for_workspace(
    current_value: str,
    ownership: OutputPathOwnership,
    layout: WorkspaceWritableLayout,
) -> Path:
    if ownership is OutputPathOwnership.WORKSPACE_DEFAULT:
        return layout.default_final_output()
    return Path(current_value).expanduser().resolve(strict=False)


@dataclass(slots=True)
class BoundedFormHistory:
    current: dict[str, str]
    undo_stack: list[dict[str, str]]
    redo_stack: list[dict[str, str]]
    limit: int = 50

    @classmethod
    def create(cls, initial: dict[str, str], *, limit: int = 50) -> BoundedFormHistory:
        if limit < 1:
            raise ValueError("form history limit must be >= 1")
        return cls(dict(initial), [], [], limit)

    def record(self, values: dict[str, str]) -> bool:
        snapshot = dict(values)
        if snapshot == self.current:
            return False
        self.undo_stack.append(dict(self.current))
        del self.undo_stack[: max(0, len(self.undo_stack) - self.limit)]
        self.current = snapshot
        self.redo_stack.clear()
        return True

    def undo(self) -> dict[str, str] | None:
        if not self.undo_stack:
            return None
        self.redo_stack.append(dict(self.current))
        self.current = self.undo_stack.pop()
        return dict(self.current)

    def redo(self) -> dict[str, str] | None:
        if not self.redo_stack:
            return None
        self.undo_stack.append(dict(self.current))
        self.current = self.redo_stack.pop()
        return dict(self.current)

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": _FORM_STATE_SCHEMA,
            "limit": self.limit,
            "current": self.current,
            "undo": self.undo_stack,
            "redo": self.redo_stack,
        }

    @classmethod
    def from_payload(cls, payload: object, *, limit: int = 50) -> BoundedFormHistory:
        if not isinstance(payload, dict) or payload.get("schema") != _FORM_STATE_SCHEMA:
            raise ValueError("unsupported form-state schema")

        def snapshot(value: object) -> dict[str, str]:
            if not isinstance(value, dict) or any(
                not isinstance(key, str) or not isinstance(item, str) for key, item in value.items()
            ):
                raise ValueError("invalid form-state snapshot")
            return dict(value)

        current = snapshot(payload.get("current"))
        raw_undo, raw_redo = payload.get("undo", []), payload.get("redo", [])
        if not isinstance(raw_undo, list) or not isinstance(raw_redo, list):
            raise ValueError("invalid form-state history")
        return cls(
            current,
            [snapshot(item) for item in raw_undo[-limit:]],
            [snapshot(item) for item in raw_redo[-limit:]],
            limit,
        )


class WorkspaceFormStateStore:
    def __init__(self, layout: WorkspaceWritableLayout, workflow: str) -> None:
        if workflow not in {"planning", "editing"}:
            raise ValueError("workflow must be planning or editing")
        self._draft = layout.drafts / f"{workflow}.json"
        self._history = layout.history / f"{workflow}.json"

    def save(self, history: BoundedFormHistory) -> None:
        encoded = json.dumps(
            history.to_payload(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        for path in (self._draft, self._history):
            path.write_text(encoded + "\n", encoding="utf-8")

    def load(self, *, limit: int = 50) -> BoundedFormHistory | None:
        if not self._history.exists():
            return None
        return BoundedFormHistory.from_payload(
            json.loads(self._history.read_text(encoding="utf-8")), limit=limit
        )
