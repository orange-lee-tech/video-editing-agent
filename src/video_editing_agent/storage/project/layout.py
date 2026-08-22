from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class WorkspaceWritableLayout:
    root: Path
    cache: Path
    work: Path
    logs: Path
    drafts: Path
    history: Path
    outputs: Path
    preview_outputs: Path
    final_outputs: Path

    @classmethod
    def ensure(cls, root: Path) -> WorkspaceWritableLayout:
        resolved = root.expanduser().resolve()
        paths = {
            "cache": resolved / "cache",
            "work": resolved / "work",
            "logs": resolved / "logs",
            "drafts": resolved / "drafts",
            "history": resolved / "history",
            "outputs": resolved / "outputs",
            "preview_outputs": resolved / "outputs" / "preview",
            "final_outputs": resolved / "outputs" / "final",
        }
        for path in paths.values():
            path.mkdir(parents=True, exist_ok=True)
        return cls(resolved, **paths)

    def default_final_output(self, stem: str = "final") -> Path:
        normalized = (
            "".join(
                character if character.isalnum() or character in {"-", "_"} else "-"
                for character in stem.strip()
            ).strip("-")
            or "final"
        )
        candidate = self.final_outputs / f"{normalized}.mp4"
        suffix = 1
        while candidate.exists():
            candidate = self.final_outputs / f"{normalized}-{suffix:03d}.mp4"
            suffix += 1
        return candidate
