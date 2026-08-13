from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))
probe = importlib.import_module("tools.probes.r0_8c_visual_motion_live")


def test_visual_motion_probe_refuses_nonempty_output(tmp_path: Path) -> None:
    output = tmp_path / "existing"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("do not overwrite", encoding="utf-8")

    with pytest.raises(FileExistsError, match="fresh path"):
        probe._prepare_output(output)

    assert sentinel.read_text(encoding="utf-8") == "do not overwrite"


def test_visual_motion_probe_accepts_new_or_empty_output(tmp_path: Path) -> None:
    new_output = tmp_path / "new"
    probe._prepare_output(new_output)
    assert new_output.is_dir()

    empty_output = tmp_path / "empty"
    empty_output.mkdir()
    probe._prepare_output(empty_output)
    assert list(empty_output.iterdir()) == []
